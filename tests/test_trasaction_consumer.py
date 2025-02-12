import unittest
from unittest.mock import MagicMock, patch
import json

from app.services.transaction_consumer import TransactionConsumer
from message_bus.message_bus import IMessageBusConnection
import starkbank


class TestTransactionConsumer(unittest.TestCase):

    def setUp(self):
        self.mock_connection = MagicMock(spec=IMessageBusConnection)
        self.mock_channel = MagicMock()
        self.mock_connection.get_channel.return_value = self.mock_channel

        self.consumer = TransactionConsumer(self.mock_connection)

    def test_init(self):
        """Test if the queue is declared correctly during initialization."""
        self.mock_connection.get_channel.assert_called_once()

        self.mock_channel.queue_declare.assert_called_once_with(name='transactions', durable=True)

    def test_consume(self):
        """Test if the consume method calls the callback with the correct data."""
        mock_callback = MagicMock()

        mock_body = json.dumps({
            'amount': 100,
            'tax_id': '123.456.789-09',
            'name': 'John Doe',
            'bank_code': '001',
            'branch_code': '0001',
            'account_number': '12345-6',
            'external_id': '123456',
            'tags': ['tag1', 'tag2'],
            'rules': [{'key': 'rule1', 'value': 'value1'}],
            'account_type': 'checking'
        }).encode('utf-8')

        self.mock_channel.consume_messages.side_effect = lambda queue_name, callback: callback(mock_body)

        self.consumer.consume(mock_callback)

        mock_callback.assert_called_once_with({
            'amount': 100,
            'tax_id': '123.456.789-09',
            'name': 'John Doe',
            'bank_code': '001',
            'branch_code': '0001',
            'account_number': '12345-6',
            'external_id': '123456',
            'tags': ['tag1', 'tag2'],
            'rules': [{'key': 'rule1', 'value': 'value1'}],
            'account_type': 'checking'
        })

    @patch('starkbank.transfer.create')
    def test_process_transfer(self, mock_transfer_create):
        """Test if the process_transfer method calls starkbank.transfer.create with the correct data."""
        transfer_data = {
            'amount': 100,
            'tax_id': '123.456.789-09',
            'name': 'John Doe',
            'bank_code': '001',
            'branch_code': '0001',
            'account_number': '12345-6',
            'external_id': '123456',
            'tags': ['tag1', 'tag2'],
            'rules': [{'key': 'rule1', 'value': 'value1'}],
            'account_type': 'checking'
        }

        mock_transfer_create.return_value = [MagicMock(id='123', amount=100, external_id='123456')]

        self.consumer.process_transfer(transfer_data)

        mock_transfer_create.assert_called_once()

        args, kwargs = mock_transfer_create.call_args
        created_transfer = args[0][0]

        self.assertEqual(created_transfer.amount, 100)
        self.assertEqual(created_transfer.tax_id, '123.456.789-09')
        self.assertEqual(created_transfer.name, 'John Doe')
        self.assertEqual(created_transfer.bank_code, '001')
        self.assertEqual(created_transfer.branch_code, '0001')
        self.assertEqual(created_transfer.account_number, '12345-6')
        self.assertEqual(created_transfer.external_id, '123456')
        self.assertEqual(created_transfer.tags, ['tag1', 'tag2'])
        self.assertEqual(created_transfer.rules[0].key, 'rule1')
        self.assertEqual(created_transfer.rules[0].value, 'value1')
        self.assertEqual(created_transfer.account_type, 'checking')


if __name__ == '__main__':
    unittest.main()
