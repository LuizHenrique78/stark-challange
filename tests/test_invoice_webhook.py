import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.api.deps import SessionDep
from app.models.invoice import Invoice
from app.services.transaction_producer import TransactionProducer
from message_bus.rabbitmq.message_bus_impl import RabbitMQMessageBusConnection
import starkbank
from app.main import app  # Importar a aplicação FastAPI

# Configuração de logging
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestInvoiceCallback(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.client = TestClient(app)

        self.mock_db = MagicMock(spec=Session)
        self.mock_request = MagicMock(spec=Request)
        self.mock_request.headers = {"Digital-Signature": "valid-signature"}
        self.mock_request.body = AsyncMock(return_value=b'{"event": "valid-event"}')

        self.mock_event = MagicMock()
        self.mock_event.subscription = "transfer"
        self.mock_event.log.transfer.external_id = "12345"

        self.mock_invoice = MagicMock(spec=Invoice)
        self.mock_invoice.is_paid = False
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_invoice

        self.mock_producer = MagicMock(spec=TransactionProducer)
        self.mock_connection = MagicMock(spec=RabbitMQMessageBusConnection)
        self.mock_producer.publish = MagicMock()

        app.dependency_overrides[SessionDep] = lambda: self.mock_db

    async def test_invoice_callback_success(self):
        """Test if the invoice webhook is processed successfully."""
        with patch("starkbank.event.parse", return_value=self.mock_event):
            response = self.client.post(
                "/api/v1/invoice-callback",
                headers={"Digital-Signature": "valid-signature"},
                content=b'{"event": "valid-event"}'
            )

            starkbank.event.parse.assert_called_once_with(
                content='{"event": "valid-event"}',
                signature="valid-signature"
            )

            self.mock_db.commit.assert_called_once()

            self.mock_producer.publish.assert_called_once_with(self.mock_event.log.transfer)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json(), {"message": "Webhook received successfully"})

    async def test_invoice_callback_missing_signature(self):
        """Test if the webhook is missing the Digital-Signature header."""
        response = self.client.post(
            "/api/v1/invoice-callback",
            content=b'{"event": "valid-event"}'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"detail": "Missing Digital-Signature header"})

    async def test_invoice_callback_invalid_signature(self):
        """Test if the webhook has an invalid signature."""
        with patch("starkbank.event.parse", side_effect=starkbank.error.InvalidSignatureError("Invalid signature")):
            response = self.client.post(
                "/api/v1/invoice-callback",
                headers={"Digital-Signature": "valid-signature"},
                content=b'{"event": "valid-event"}'
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.json(), {"detail": "Invalid signature"})

    async def test_invoice_callback_not_transfer_event(self):
        """Test if the webhook is not a transfer event"""
        self.mock_event.subscription = "invoice"

        with patch("starkbank.event.parse", return_value=self.mock_event):
            response = self.client.post(
                "/api/v1/invoice-callback",
                headers={"Digital-Signature": "valid-signature"},
                content=b'{"event": "valid-event"}'
            )

            self.mock_db.commit.assert_not_called()

            self.mock_producer.publish.assert_not_called()

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json(), {"message": "Webhook received successfully"})

    async def test_invoice_callback_invalid_event(self):
        """Test if the webhook has an invalid event."""
        delattr(self.mock_event.log, 'transfer')

        with patch("starkbank.event.parse", return_value=self.mock_event):
            response = self.client.post(
                "/api/v1/invoice-callback",
                headers={"Digital-Signature": "valid-signature"},
                content=b'{"event": "valid-event"}'
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.json(), {"detail": "Invalid event"})


    async def test_invoice_callback_already_paid(self):
        """Test if the invoice is already paid."""
        self.mock_invoice.is_paid = True

        with patch("starkbank.event.parse", return_value=self.mock_event):
            response = self.client.post(
                "/api/v1/invoice-callback",
                headers={"Digital-Signature": "valid-signature"},
                content=b'{"event": "valid-event"}'
            )

            self.mock_db.commit.assert_not_called()

            self.mock_producer.publish.assert_not_called()
            print(response.status_code)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json(), {"message": "Webhook received successfully"})

    async def test_invoice_callback_db_error(self):
        """Test and error in the database."""
        self.mock_db.commit.side_effect = Exception("Database error")

        with patch("starkbank.event.parse", return_value=self.mock_event):
            response = self.client.post(
                "/api/v1/invoice-callback",
                headers={"Digital-Signature": "valid-signature"},
                content=b'{"event": "valid-event"}'
            )

            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(response.json(), {"detail": "Internal server error"})

    async def test_invoice_callback_publish_error(self):
        """Test queue publish error."""
        self.mock_producer.publish.side_effect = Exception("Publish error")

        with patch("starkbank.event.parse", return_value=self.mock_event):
            response = self.client.post(
                "/api/v1/invoice-callback",
                headers={"Digital-Signature": "valid-signature"},
                content=b'{"event": "valid-event"}'
            )

            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(response.json(), {"detail": "Internal server error"})

    async def test_invoice_callback_unexpected_error(self):
        """Test unexpected error."""
        with patch("starkbank.event.parse", side_effect=Exception("Unexpected error")):
            response = self.client.post(
                "/api/v1/invoice-callback",
                headers={"Digital-Signature": "valid-signature"},
                content=b'{"event": "valid-event"}'
            )

            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(response.json(), {"detail": "Internal server error"})

    def tearDown(self):
        app.dependency_overrides.clear()


if __name__ == "__main__":
    unittest.main()
