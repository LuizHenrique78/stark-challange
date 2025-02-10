import random
import pika
from app.core.config import settings


def schedule_invoices():
    """
    Schedules tasks
    This will push messages to RabbitMQ which the 'invoice_issuer.py' will consume.
    """
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue="invoice-queue", durable=True)
    count = random.randint(8, 12)
    channel.basic_publish(
        exchange="",
        routing_key="invoice-queue",
        body=str(count),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()


if __name__ == "__main__":
    schedule_invoices()
