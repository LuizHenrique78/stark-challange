from unittest.mock import patch
from faker import Faker
from datetime import datetime, timedelta
from app.workers.invoice_scheduler import generate_random_invoices

fake = Faker("pt_BR")


def test_generate_random_invoices_length():
    """test if the number of invoices generated is between 8 and 12"""
    invoices = generate_random_invoices()
    assert 8 <= len(invoices) <= 12


def test_generate_random_invoices_structure():
    """Test if the invoices generated have the correct structure"""
    invoices = generate_random_invoices()
    for invoice in invoices:
        assert isinstance(invoice.amount, int)
        assert invoice.amount > 0
        assert isinstance(invoice.name, str)
        assert isinstance(invoice.tax_id, str)
        assert len(invoice.tax_id) > 10
        assert isinstance(invoice.due, datetime)
        assert invoice.due > datetime.utcnow()
        assert isinstance(invoice.expiration, timedelta)
        assert invoice.expiration == timedelta(seconds=86400)
        assert isinstance(invoice.tags, list)
        assert "Invoice" in invoice.tags


@patch("starkbank.invoice.create")
def test_starkbank_invoice_creation(mock_create):
    """Test if the invoices are created in Stark Bank"""
    mock_create.return_value = [
        {"id": "123456", "name": fake.name(), "tax_id": fake.cpf(), "amount": 200000, "due": datetime.utcnow()}
    ]

    invoices = generate_random_invoices()
    created_invoices = mock_create(invoices)

    mock_create.assert_called_once()
    assert len(created_invoices) == 1
    assert "id" in created_invoices[0]
    assert isinstance(created_invoices[0]["id"], str)
