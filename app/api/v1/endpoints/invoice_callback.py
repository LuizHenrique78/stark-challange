import logging

import starkbank
from fastapi import APIRouter, status, Response, Request, HTTPException
from app.api.deps import SessionDep
from app.core.config import settings
from app.models.invoice import Invoice
from app.services.transaction_producer import TransactionProducer
from message_bus.rabbitmq.message_bus_impl import RabbitMQMessageBusConnection

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

connection = RabbitMQMessageBusConnection(settings.RABBITMQ_URL)
producer = TransactionProducer(connection)


def process_transfer_event(event, db: SessionDep):
    """
    Processes a transfer event from Stark Bank.
    Marks the invoice as paid and publishes a transfer for the net amount.
    """
    if not hasattr(event.log, 'transfer') or not hasattr(event.log.transfer, 'external_id'):
        logger.error("Invalid event: missing transfer or external_id")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid event")

    invoice = db.query(Invoice).filter(Invoice.external_id == event.log.transfer.external_id).first()

    if invoice:
        if invoice.is_paid:
            logger.info(f"Invoice {invoice.external_id} is already paid. No action taken.")
            return

        try:
            invoice.is_paid = True
            db.commit()
            logger.info(f"Invoice {invoice.external_id} marked as paid")
            producer.publish(event.log.transfer)
            logger.info(f"Transfer published for invoice {invoice.external_id}")
        except Exception as e:
            logger.error(f"Error updating invoice or publishing transfer: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )


@router.post(
    "/invoice-callback",
    response_description="Webhook callback response",
    status_code=status.HTTP_200_OK
)
async def invoice_callback(request: Request, db: SessionDep):
    """
    Receives invoice updates from Stark Bank.
    When the invoice is paid, create a transfer for the net amount.
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
            event = starkbank.event.parse(content=event_data.decode("utf-8"), signature=signature)
        except starkbank.error.InvalidSignatureError as e:
            logger.error(f"Invalid signature: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid signature"
            )

        if event.subscription != "transfer":
            logger.info(f"Ignoring event of type: {event.subscription}")
            return {"message": "Webhook received successfully"}

        process_transfer_event(event, db)

        return {"message": "Webhook received successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing invoice callback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
