import unittest
from unittest.mock import MagicMock, patch
import json
from sqlalchemy.orm import Session

from app.repositories.transfer_repository import TransferRepository
from app.services.transfer_consumer import TransferConsumer
from app.services.transfer_service import TransferService
from message_bus.message_bus import IMessageBusConnection


class TestTransactionConsumer(unittest.TestCase):

    def setUp(self):
        self.mock_connection = MagicMock(spec=IMessageBusConnection)
        self.mock_channel = MagicMock()
        self.mock_connection.get_channel.return_value = self.mock_channel

        self.mock_db = MagicMock(spec=Session)

        self.mock_transfer_repository = MagicMock(spec=TransferRepository)
        self.mock_transfer_service = MagicMock(spec=TransferService)

        self.consumer = TransferConsumer(
            connection=self.mock_connection,
            db=self.mock_db,
            routing_key="transactions"
        )

        self.consumer.transfer_service = self.mock_transfer_service

    def test_consume(self):
        """Testa se o método consume chama o callback com os dados corretos."""
        mock_callback = MagicMock()

        mock_body = json.dumps({
            "invoice": {
                "id": "12345",
                "amount": 10000,
                "fee": 100,
                "fineAmount": 50,
                "interestAmount": 30,
                "net_amount": 9820,
                "external_id": "external-12345",
                "status": "created",
                "payload": {"key": "value"}
            }
        }).encode("utf-8")

        self.mock_channel.consume_messages.side_effect = lambda queue_name, callback: callback(mock_body)

        self.consumer.consume(mock_callback)

        mock_callback.assert_called_once_with({
            "invoice": {
                "id": "12345",
                "amount": 10000,
                "fee": 100,
                "fineAmount": 50,
                "interestAmount": 30,
                "net_amount": 9820,
                "external_id": "external-12345",
                "status": "created",
                "payload": {"key": "value"}
            }
        })

    def test_process_transfer(self):
        """Testa se o método process_transfer chama o TransferService corretamente."""

        transfer_data = {
            "invoice": {
                "id": "12345",
                "amount": 10000,
                "fee": 100,
                "fineAmount": 50,
                "interestAmount": 30,
                "net_amount": 9820,
                "external_id": "external-12345",
                "status": "created",
                "payload": {"key": "value"}
            }
        }

        self.consumer.process_transfer(transfer_data)

        self.mock_transfer_service.create_transfer.assert_called_once_with(transfer_data["invoice"])

    @patch("builtins.print")
    def test_process_transfer_exception(self, mock_print):
        """Testa se exceções no process_transfer são tratadas corretamente."""

        transfer_data = {
            "invoice": {
                "id": "12345",
                "amount": 10000,
                "fee": 100,
                "fineAmount": 50,
                "interestAmount": 30,
                "net_amount": 9820,
                "external_id": "external-12345",
                "status": "created",
                "payload": {"key": "value"}
            }
        }

        self.mock_transfer_service.create_transfer.side_effect = Exception("Erro simulado")

        self.consumer.process_transfer(transfer_data)


if __name__ == "__main__":
    unittest.main()