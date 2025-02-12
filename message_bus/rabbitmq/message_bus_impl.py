from typing import Callable
import pika

from message_bus.message_bus import IMessageBusConnection, IMessageBusChannel


class RabbitMQMessageBusChannel(IMessageBusChannel):
    def __init__(self, connection: pika.BlockingConnection):
        self.connection = connection
        self.channel = self.connection.channel()
        self._consumer_registered = False

    def queue_declare(self, name: str, durable: bool = True) -> None:
        self.channel.queue_declare(queue=name, durable=durable)

    def publish_message(self, routing_key: str, message_body: bytes) -> None:
        self.channel.basic_publish(
            exchange='',
            routing_key=routing_key,
            body=message_body,
            properties=pika.BasicProperties(delivery_mode=2)  # mensagem persistente
        )

    def consume_messages(self, queue_name: str, callback: Callable[[bytes], None]) -> None:
        # registra o callback de consumo
        def _on_message(ch, method, properties, body):
            callback(body)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        self.channel.basic_consume(queue=queue_name, on_message_callback=_on_message)
        self._consumer_registered = True

    def start_consuming(self) -> None:
        if not self._consumer_registered:
            raise RuntimeError("Nenhum consumidor registrado antes de iniciar o consumo.")
        self.channel.start_consuming()


class RabbitMQMessageBusConnection(IMessageBusConnection):
    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url
        self._connection = None

    def get_channel(self) -> IMessageBusChannel:
        if not self._connection or self._connection.is_closed:
            self._connection = pika.BlockingConnection(pika.URLParameters(self.amqp_url))
        return RabbitMQMessageBusChannel(self._connection)