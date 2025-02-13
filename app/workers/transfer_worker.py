import logging

from app.core.config import settings
from app.services.starkbank_client import get_starkbank_user
from app.services.transfer_service import TransferService
from app.repositories.transfer_repository import TransferRepository
from app.services.transfer_consumer import TransferConsumer
from message_bus.rabbitmq.message_bus_impl import RabbitMQMessageBusConnection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

get_starkbank_user()


connection = RabbitMQMessageBusConnection(settings.RABBITMQ_URL)
db = SessionLocal()
transfer_repository = TransferRepository(db)
transfer_service = TransferService(transfer_repository)
consumer = TransferConsumer(connection, db)


def worker_main():
    """Função principal do worker"""

    def callback(transfer_data: dict):
        consumer.process_transfer(transfer_data)
        logger.info(f"Transfer data consumed: {transfer_data}")

    consumer.consume(callback)


if __name__ == '__main__':
    worker_main()
