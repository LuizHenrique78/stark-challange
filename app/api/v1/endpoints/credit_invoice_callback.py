import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, status, Request, HTTPException
from pydantic import BaseModel, ValidationError, HttpUrl

from app.core.config import settings
from app.services.starkbank_client import get_starkbank_user
from app.services.transfer_producer import TransferProducer
from message_bus.rabbitmq.message_bus_impl import RabbitMQMessageBusConnection
import starkbank

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

connection = RabbitMQMessageBusConnection(settings.RABBITMQ_URL)
producer = TransferProducer(connection)

get_starkbank_user()


class Description(BaseModel):
    key: str
    value: str


class Invoice(BaseModel):
    amount: int
    brcode: str
    created: datetime | str
    descriptions: List[Description]
    discountAmount: int
    discounts: List
    displayDescription: str
    due: datetime | str
    expiration: int
    fee: int
    fine: float
    fineAmount: int
    id: str
    interest: float
    interestAmount: int
    link: HttpUrl | str
    name: str
    nominalAmount: int
    pdf: HttpUrl | str
    rules: List
    splits: List
    status: str
    tags: List[str]
    taxId: str
    transactionIds: List[str]
    updated: datetime | str


class Log(BaseModel):
    authentication: str
    created: datetime | str
    errors: List
    id: str
    invoice: Invoice
    type: str


class Event(BaseModel):
    created: datetime | str
    id: str
    log: Log
    subscription: str
    workspaceId: str


def process_transfer_event(event: Event):
    """
    Processes a transfer event from Stark Bank.
    Publishes the invoice data to a queue for further processing.
    """
    logger.info(f"Processing event of type: {event.log.type}")
    if event.log.type != "credited":
        logger.info(f"Ignoring event of type: {event.log.type}")
        return

    try:
        producer.publish(event.log.invoice.model_dump())
        logger.info(f"Invoice {event.log.invoice.id} published to queue")
    except Exception as e:
        logger.error(f"Error publishing invoice to queue: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post(
    "/invoice-callback",
    response_description="Webhook callback response",
    status_code=status.HTTP_200_OK,
    description=Path(
        "docs/credited-webhook-example.md",
    ).read_text(),
)
async def invoice_callback(request: Request):
    """
    Receives invoice updates from Stark Bank.
    When the invoice is paid, publishes the invoice to a queue for further processing.
    """
    try:
        event_data = await request.body()
        signature = request.headers.get("Digital-Signature")

        if not signature:
            logger.error("Missing Digital-Signature header")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing Digital-Signature header"
            )
        try:
            starkbank.event.parse(content=event_data.decode("utf-8"), signature=signature)
        except starkbank.error.InvalidSignatureError as e:
            logger.error(f"Invalid signature: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid signature"
            )
        logger.info(f"Received event: {event_data.decode('utf-8')}")

        try:
            event_received_data = json.loads(event_data.decode("utf-8"))
            event_data = event_received_data.get("event")
            event_model = Event(**event_data)
        except ValidationError as e:
            logger.error(f"Invalid event data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event data"
            )

        if event_model.subscription != "invoice":
            logger.info(f"Ignoring event of type: {event_model.subscription}")
            return {"message": "Webhook received successfully"}

        process_transfer_event(event_model)

        return {"message": "Webhook received successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing invoice callback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
