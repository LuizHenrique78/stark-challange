import unittest
from unittest.mock import MagicMock, patch
import json

from app.services.transaction_producer import TransactionProducer
from message_bus.message_bus import IMessageBusConnection


class TestTransactionProducer(unittest.TestCase):

    def setUp(self):
        self.mock_connection = MagicMock(spec=IMessageBusConnection)
        self.mock_channel = MagicMock()
        self.mock_connection.get_channel.return_value = self.mock_channel

        self.producer = TransactionProducer(self.mock_connection)

    def test_init(self):
        """Initialization test."""
        self.mock_connection.get_channel.assert_called_once()

        self.mock_channel.queue_declare.assert_called_once_with(name='transactions', durable=True)

    def test_publish(self):
        """Test if the message is published correctly."""
        transfer_data = {
            'from_account': '12345',
            'to_account': '67890',
            'amount': 100.0
        }

        self.producer.publish(transfer_data)

        self.mock_connection.get_channel.assert_called_once()

        expected_body = json.dumps(transfer_data).encode("utf-8")
        self.mock_channel.publish_message.assert_called_once_with(
            routing_key='transactions',
            message_body=expected_body
        )


if __name__ == '__main__':
    unittest.main()
