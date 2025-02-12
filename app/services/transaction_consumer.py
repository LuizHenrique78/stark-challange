import json
import starkbank

from typing import Callable
import pika

from message_bus.message_bus import IMessageBusConnection


class TransactionConsumer:
    def __init__(self, connection: IMessageBusConnection, routing_key: str = 'transactions'):
        self.connection = connection
        self.routing_key = routing_key
        channel = self.connection.get_channel()
        channel.queue_declare(name=self.routing_key, durable=True)

    def consume(self, callback: Callable[[dict], None]) -> None:
        """Consome as mensagens e processa a transferência"""

        def wrapper(body: bytes):
            data = json.loads(body.decode("utf-8"))
            callback(data)

        channel = self.connection.get_channel()
        channel.consume_messages(queue_name=self.routing_key, callback=wrapper)
        channel.start_consuming()

    def process_transfer(self, transfer_data: dict) -> None:
        """Processa a transferência usando a API do Stark Bank"""
        try:
            transfer = starkbank.transfer.create([
                starkbank.Transfer(
                    amount=transfer_data['amount'],
                    tax_id=transfer_data['tax_id'],
                    name=transfer_data['name'],
                    bank_code=transfer_data['bank_code'],
                    branch_code=transfer_data['branch_code'],
                    account_number=transfer_data['account_number'],
                    external_id=transfer_data['external_id'],
                    tags=transfer_data['tags'],
                    rules=[starkbank.transfer.Rule(key=rule['key'], value=rule['value']) for rule in
                           transfer_data['rules']],
                    account_type=transfer_data['account_type']
                )
            ])

            for t in transfer:
                print(f"Transfer ID: {t.id}, Amount: {t.amount}, External ID: {t.external_id}")
        except Exception as e:
            print(f"Error processing transfer: {e}")