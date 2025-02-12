from app.core.config import settings
from app.services.transaction_consumer import TransactionConsumer
from message_bus.rabbitmq.message_bus_impl import RabbitMQMessageBusConnection

connection = RabbitMQMessageBusConnection(settings.RABBITMQ_URL)
consumer = TransactionConsumer(connection)


def worker_main():
    """Função principal do worker"""

    def callback(transfer_data: dict):
        consumer.process_transfer(transfer_data)

    consumer.consume(callback)


if __name__ == '__main__':
    worker_main()
