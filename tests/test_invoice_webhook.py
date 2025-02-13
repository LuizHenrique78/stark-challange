import unittest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from app.main import app
from app.api.v1.endpoints.credit_invoice_callback import process_transfer_event, Event, Invoice, EventLog
from message_bus.rabbitmq.message_bus_impl import RabbitMQMessageBusConnection
from app.services.transfer_producer import TransferProducer
import logging
import starkbank

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mock_producer = MagicMock(spec=TransferProducer)
mock_connection = MagicMock(spec=RabbitMQMessageBusConnection)

client = TestClient(app)


class TestInvoiceEndpoint(unittest.TestCase):

    def setUp(self):
        app.dependency_overrides[TransferProducer] = lambda: mock_producer

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_process_transfer_event_valid(self):
        """Tests processing a valid transfer event."""
        invoice = Invoice(
            amount=10000,
            brcode="00020101021226890014br.gov.bcb.pix2567brcode-h.sandbox.starkbank.com/v2/ee87e7ce19544b11be5a6de65b97091a5204000053039865802BR5925Stark Bank S.A. - Institu6009Sao Paulo62070503***630442BE",
            created="2024-01-31T21:15:16.701209+00:00",
            descriptions=[{"key": "Product A", "value": "R$10,00"}],
            discountAmount=0,
            discounts=[{"due": "2024-11-25T17:59:26+00:00", "percentage": 10.5}],
            due="2024-11-30T02:06:26.249976+00:00",
            expiration=1,
            fee=0,
            fine=2.5,
            fineAmount=0,
            id="5807638394699776",
            interest=1.3,
            interestAmount=0,
            link="https://starkv2.sandbox.starkbank.com/invoicelink/ee87e7ce19544b11be5a6de65b97091a",
            name="Iron Bank S.A.",
            nominalAmount=10000,
            pdf="https://sandbox.api.starkbank.com/v2/invoice/ee87e7ce19544b11be5a6de65b97091a.pdf",
            rules=[],
            splits=[],
            status="paid",
            tags=["war supply", "invoice #1234"],
            taxId="20.018.183/0001-80",
            transactionIds=[],
            updated="2024-01-31T21:15:16.852309+00:00"
        )
        event = Event(
            created="2024-01-31T21:15:17.463956+00:00",
            id="6046987522670592",
            log=EventLog(
                created="2024-01-31T21:15:16.852263+00:00",
                errors=[],
                id="5244688441278464",
                invoice=invoice,
                type="credited"
            ),
            subscription="invoice",
            workspaceId="6341320293482496"
        )

        process_transfer_event(event)

    def test_process_transfer_event_invalid_type(self):
        """Tests processing an event with an invalid type."""
        invoice = Invoice(
            amount=10000,
            brcode="00020101021226890014br.gov.bcb.pix2567brcode-h.sandbox.starkbank.com/v2/ee87e7ce19544b11be5a6de65b97091a5204000053039865802BR5925Stark Bank S.A. - Institu6009Sao Paulo62070503***630442BE",
            created="2024-01-31T21:15:16.701209+00:00",
            descriptions=[{"key": "Product A", "value": "R$10,00"}],
            discountAmount=0,
            discounts=[{"due": "2024-11-25T17:59:26+00:00", "percentage": 10.5}],
            due="2024-11-30T02:06:26.249976+00:00",
            expiration=1,
            fee=0,
            fine=2.5,
            fineAmount=0,
            id="5807638394699776",
            interest=1.3,
            interestAmount=0,
            link="https://starkv2.sandbox.starkbank.com/invoicelink/ee87e7ce19544b11be5a6de65b97091a",
            name="Iron Bank S.A.",
            nominalAmount=10000,
            pdf="https://sandbox.api.starkbank.com/v2/invoice/ee87e7ce19544b11be5a6de65b97091a.pdf",
            rules=[],
            splits=[],
            status="paid",
            tags=["war supply", "invoice #1234"],
            taxId="20.018.183/0001-80",
            transactionIds=[],
            updated="2024-01-31T21:15:16.852309+00:00"
        )
        event = Event(
            created="2024-01-31T21:15:17.463956+00:00",
            id="6046987522670592",
            log=EventLog(
                created="2024-01-31T21:15:16.852263+00:00",
                errors=[],
                id="5244688441278464",
                invoice=invoice,
                type="invalid"  # Tipo inválido
            ),
            subscription="invoice",
            workspaceId="6341320293482496"
        )

        process_transfer_event(event)

        mock_producer.publish.assert_not_called()

    @patch("starkbank.event.parse")
    def test_invoice_callback_valid(self, mock_parse):
        """Tests the /invoice-callback endpoint with a valid event."""
        invoice = Invoice(
            amount=10000,
            brcode="00020101021226890014br.gov.bcb.pix2567brcode-h.sandbox.starkbank.com/v2/ee87e7ce19544b11be5a6de65b97091a5204000053039865802BR5925Stark Bank S.A. "
                   "- Institu6009Sao Paulo62070503***630442BE",
            created="2024-01-31T21:15:16.701209+00:00",
            descriptions=[{"key": "Product A", "value": "R$10,00"}],
            discountAmount=0,
            discounts=[{"due": "2024-11-25T17:59:26+00:00", "percentage": 10.5}],
            due="2024-11-30T02:06:26.249976+00:00",
            expiration=1,
            fee=0,
            fine=2.5,
            fineAmount=0,
            id="5807638394699776",
            interest=1.3,
            interestAmount=0,
            link="https://starkv2.sandbox.starkbank.com/invoicelink/ee87e7ce19544b11be5a6de65b97091a",
            name="Iron Bank S.A.",
            nominalAmount=10000,
            pdf="https://sandbox.api.starkbank.com/v2/invoice/ee87e7ce19544b11be5a6de65b97091a.pdf",
            rules=[],
            splits=[],
            status="paid",
            tags=["war supply", "invoice #1234"],
            taxId="20.018.183/0001-80",
            transactionIds=[],
            updated="2024-01-31T21:15:16.852309+00:00"
        )
        event = Event(
            created="2024-01-31T21:15:17.463956+00:00",
            id="6046987522670592",
            log=EventLog(
                created="2024-01-31T21:15:16.852263+00:00",
                errors=[],
                id="5244688441278464",
                invoice=invoice,
                type="credited"
            ),
            subscription="invoice",
            workspaceId="6341320293482496"
        )
        mock_parse.return_value = event.model_dump()

        response = client.post(
            "/api/v1/invoice-callback",
            headers={"Digital-Signature": "valid-signature"},
            content=event.json()
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"message": "Webhook received successfully"})

    @patch("starkbank.event.parse")
    def test_invoice_callback_missing_signature(self, mock_parse):
        """Tests the /invoice-callback endpoint with a missing signature."""
        response = client.post(
            "/api/v1/invoice-callback",
            content=b'{"log": {"invoice": {"id": "12345"}}}'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"detail": "Missing Digital-Signature header"})

    @patch("starkbank.event.parse")
    def test_invoice_callback_invalid_signature(self, mock_parse):
        """Tests the /invoice-callback endpoint with an invalid signature."""
        mock_parse.side_effect = starkbank.error.InvalidSignatureError("Invalid signature")

        response = client.post(
            "/api/v1/invoice-callback",
            headers={"Digital-Signature": "invalid-signature"},
            content=b'{"log": {"invoice": {"id": "12345"}}}'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"detail": "Invalid signature"})

    @patch("starkbank.event.parse")
    def test_invoice_callback_invalid_subscription(self, mock_parse):
        """Tests the /invoice-callback endpoint with an invalid subscription."""
        invoice = Invoice(
            amount=10000,
            brcode="00020101021226890014br.gov.bcb.pix2567brcode-h.sandbox.starkbank.com/v2/ee87e7ce19544b11be5a6de65b97091a5204000053039865802BR5925Stark Bank S.A. - Institu6009Sao Paulo62070503***630442BE",
            created="2024-01-31T21:15:16.701209+00:00",
            descriptions=[{"key": "Product A", "value": "R$10,00"}],
            discountAmount=0,
            discounts=[{"due": "2024-11-25T17:59:26+00:00", "percentage": 10.5}],
            due="2024-11-30T02:06:26.249976+00:00",
            expiration=1,
            fee=0,
            fine=2.5,
            fineAmount=0,
            id="5807638394699776",
            interest=1.3,
            interestAmount=0,
            link="https://starkv2.sandbox.starkbank.com/invoicelink/ee87e7ce19544b11be5a6de65b97091a",
            name="Iron Bank S.A.",
            nominalAmount=10000,
            pdf="https://sandbox.api.starkbank.com/v2/invoice/ee87e7ce19544b11be5a6de65b97091a.pdf",
            rules=[],
            splits=[],
            status="paid",
            tags=["war supply", "invoice #1234"],
            taxId="20.018.183/0001-80",
            transactionIds=[],
            updated="2024-01-31T21:15:16.852309+00:00"
        )
        event = Event(
            created="2024-01-31T21:15:17.463956+00:00",
            id="6046987522670592",
            log=EventLog(
                created="2024-01-31T21:15:16.852263+00:00",
                errors=[],
                id="5244688441278464",
                invoice=invoice,
                type="credited"
            ),
            subscription="invalid",  # Assinatura inválida
            workspaceId="6341320293482496"
        )
        mock_parse.return_value = event.dict()

        response = client.post(
            "/api/v1/invoice-callback",
            headers={"Digital-Signature": "valid-signature"},
            content=event.json()
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"message": "Webhook received successfully"})
        mock_producer.publish.assert_not_called()

    @patch("starkbank.event.parse")
    def test_invoice_callback_unexpected_error(self, mock_parse):
        """Tests the /invoice-callback endpoint with an unexpected error."""
        mock_parse.side_effect = Exception("Unexpected error")

        response = client.post(
            "/api/v1/invoice-callback",
            headers={"Digital-Signature": "valid-signature"},
            content=b'{"log": {"invoice": {"id": "12345"}}}'
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json(), {"detail": "Internal server error"})


if __name__ == "__main__":
    unittest.main()
