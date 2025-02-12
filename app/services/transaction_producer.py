import json
from message_bus.message_bus import IMessageBusConnection


class TransactionProducer:
    def __init__(self, connection: IMessageBusConnection, routing_key: str = 'transactions'):
        self.connection = connection
        self.routing_key = routing_key
        channel = self.connection.get_channel()
        channel.queue_declare(name=self.routing_key, durable=True)

    def publish(self, transfer_data: dict) -> None:
        """Publica a mensagem de transferência na fila do RabbitMQ"""
        channel = self.connection.get_channel()
        body = json.dumps(transfer_data).encode("utf-8")
        channel.publish_message(routing_key=self.routing_key, message_body=body)