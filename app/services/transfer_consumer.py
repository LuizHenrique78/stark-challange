# starkbank_transfer/consumers/transaction_consumer.py
import json
import logging
from typing import Callable
from ..services.transfer_service import TransferService
from ..repositories.transfer_repository import TransferRepository
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransferConsumer:
    def __init__(self, connection, db: Session, routing_key: str = "transactions"):
        self.connection = connection
        self.routing_key = routing_key
        self.db = db
        self.transfer_service = TransferService(TransferRepository(db))

    def consume(self, callback: Callable[[dict], None]) -> None:
        def wrapper(body: bytes):
            data = json.loads(body.decode("utf-8"))
            callback(data)

        channel = self.connection.get_channel()
        channel.queue_declare(name=self.routing_key, durable=True)
        channel.consume_messages(queue_name=self.routing_key, callback=wrapper)
        channel.start_consuming()

    def process_transfer(self, transfer_data: dict) -> None:
        try:
            self.transfer_service.create_transfer(transfer_data)
        except Exception as e:
            logger.info(f"Error processing transfer: {str(e)}")
