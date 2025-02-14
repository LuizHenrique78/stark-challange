import pytest
from datetime import datetime
from pydantic import ValidationError
from app.api.v1.schemas.invoice_schema import Description, Invoice, Log, Event


def test_description_model():
    data = {"key": "item1", "value": "value1"}
    description = Description(**data)
    assert description.key == "item1"
    assert description.value == "value1"


def test_invoice_model():
    data = {
        "amount": 1000,
        "brcode": "1234567890",
        "created": "2023-10-01T00:00:00Z",
        "descriptions": [{"key": "item1", "value": "value1"}],
        "discountAmount": 100,
        "discounts": [],
        "displayDescription": "Test Invoice",
        "due": "2023-10-10T00:00:00Z",
        "expiration": 3600,
        "fee": 10,
        "fine": 0.5,
        "fineAmount": 50,
        "id": "inv_123",
        "interest": 0.1,
        "interestAmount": 10,
        "link": "https://example.com/invoice/123",
        "name": "Invoice 123",
        "nominalAmount": 900,
        "pdf": "https://example.com/invoice/123/pdf",
        "rules": [],
        "splits": [],
        "status": "paid",
        "tags": ["tag1", "tag2"],
        "taxId": "123456789",
        "transactionIds": ["txn_123"],
        "updated": "2023-10-01T00:00:00Z"
    }
    invoice = Invoice(**data)
    assert invoice.amount == 1000
    assert invoice.brcode == "1234567890"
    assert invoice.status == "paid"


def test_log_model():
    data = {
        "authentication": "auth123",
        "created": "2023-10-01T00:00:00Z",
        "errors": [],
        "id": "log_123",
        "invoice": {
            "amount": 1000,
            "brcode": "1234567890",
            "created": "2023-10-01T00:00:00Z",
            "descriptions": [{"key": "item1", "value": "value1"}],
            "discountAmount": 100,
            "discounts": [],
            "displayDescription": "Test Invoice",
            "due": "2023-10-10T00:00:00Z",
            "expiration": 3600,
            "fee": 10,
            "fine": 0.5,
            "fineAmount": 50,
            "id": "inv_123",
            "interest": 0.1,
            "interestAmount": 10,
            "link": "https://example.com/invoice/123",
            "name": "Invoice 123",
            "nominalAmount": 900,
            "pdf": "https://example.com/invoice/123/pdf",
            "rules": [],
            "splits": [],
            "status": "paid",
            "tags": ["tag1", "tag2"],
            "taxId": "123456789",
            "transactionIds": ["txn_123"],
            "updated": "2023-10-01T00:00:00Z"
        },
        "type": "paid"
    }
    log = Log(**data)
    assert log.type == "paid"
    assert log.invoice.id == "inv_123"


def test_event_model():
    data = {
        "created": "2023-10-01T00:00:00Z",
        "id": "event_123",
        "log": {
            "authentication": "auth123",
            "created": "2023-10-01T00:00:00Z",
            "errors": [],
            "id": "log_123",
            "invoice": {
                "amount": 1000,
                "brcode": "1234567890",
                "created": "2023-10-01T00:00:00Z",
                "descriptions": [{"key": "item1", "value": "value1"}],
                "discountAmount": 100,
                "discounts": [],
                "displayDescription": "Test Invoice",
                "due": "2023-10-10T00:00:00Z",
                "expiration": 3600,
                "fee": 10,
                "fine": 0.5,
                "fineAmount": 50,
                "id": "inv_123",
                "interest": 0.1,
                "interestAmount": 10,
                "link": "https://example.com/invoice/123",
                "name": "Invoice 123",
                "nominalAmount": 900,
                "pdf": "https://example.com/invoice/123/pdf",
                "rules": [],
                "splits": [],
                "status": "paid",
                "tags": ["tag1", "tag2"],
                "taxId": "123456789",
                "transactionIds": ["txn_123"],
                "updated": "2023-10-01T00:00:00Z"
            },
            "type": "paid"
        },
        "subscription": "invoice",
        "workspaceId": "ws_123"
    }
    event = Event(**data)
    assert event.subscription == "invoice"
    assert event.log.type == "paid"
