import unittest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from tests.confest import create_mock_invoice

from app.api.v1.schemas.invoice_schema import Invoice, Event, Log
from app.main import app

from message_bus.rabbitmq.message_bus_impl import RabbitMQMessageBusConnection
from app.services.transfer_producer import TransferProducer
import logging
import starkbank

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mock_connection = MagicMock(spec=RabbitMQMessageBusConnection)

client = TestClient(app)


@patch("starkbank.event.parse")
def test_invoice_callback_paid(mock_parse, create_mock_invoice):
    # Simulando uma resposta válida do Stark Bank
    mock_parse.return_value = None  # O método `parse` apenas valida a assinatura, então pode ser None

    headers = {
        "Digital-Signature": "fake-signature"
    }

    response = client.post("api/v1/invoice-callback",
                           json={"event": create_mock_invoice.model_dump(by_alias=True)},
                           headers=headers)

    assert response.status_code == 200
    assert response.json() == {"message": "Webhook received successfully"}


def test_invoice_callback_paid_missing_signature(create_mock_invoice):
    response = client.post("api/v1/invoice-callback",
                           json={"event": create_mock_invoice.model_dump(by_alias=True)},
                           )

    assert response.status_code == 400
    assert response.json() == {"detail": "Missing Signature"}


def test_invoice_callback_paid_invalid_signature(create_mock_invoice):
    response = client.post("api/v1/invoice-callback",
                           json={"event": create_mock_invoice.model_dump(by_alias=True)},
                           headers={"Digital-Signature": "invalid-signature"})

    assert response.status_code == 403
    assert response.json() == {'detail': 'Invalid signature'}

@patch("starkbank.event.parse")
def test_invoice_callback_paid_invalid_event(mock_parse):
    mock_parse.return_value = None

    headers = {
        "Digital-Signature": "fake-signature"
    }

    response = client.post("api/v1/invoice-callback",
                           json={"event": {"invalid": "event"}},
                           headers=headers)

    assert response.status_code == 400
    assert response.json() == {'detail': 'Invalid event data'}