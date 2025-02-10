import pika
import time
import random
from app.services.invoice_service import issue_invoices
from app.core.config import settings


def main():
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue="invoice-queue", durable=True)

    def callback(ch, method, properties, body):
        """
        This callback is triggered when a new message arrives in 'invoice-queue'.
        We'll parse how many invoices to create, then call `issue_invoices`.
        """
        try:
            count = int(body.decode())
            issue_invoices(count)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print("Error in workers callback:", e)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="invoice-queue", on_message_callback=callback)
    # TODO: subistiruir print para logger.
    print(" [*] Waiting for messages in invoice-queue. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    main()
