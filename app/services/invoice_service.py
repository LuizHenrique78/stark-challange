import starkbank
import random
import time
from app.services.starkbank_client import get_starkbank_user
from app.models.invoice import Invoice
from app.core.database import SessionLocal


def issue_invoices(count: int):
    """
    Issue `count` invoices using StarkBank API to random people.
    """
    get_starkbank_user()
    invoice_list = []
    for i in range(count):
        random_amount = random.randint(100, 1000)
        name = f"Random Person {i}"
        tax_id = "012.345.678-90"
        # TODO: Gerar nome e cpf aleatórios
        invoice_list.append(
            starkbank.Invoice(
                amount=random_amount,
                tax_id=tax_id,
                name=name,
            )
        )
    created_invoices = starkbank.invoice.create(invoice_list)
    db = SessionLocal()
    try:
        for inv in created_invoices:
            new_invoice = Invoice(
                external_id=inv.external_id,
                name=inv.name,
                tax_id=inv.tax_id,
                amount=inv.amount,
                is_paid=False
            )
            db.add(new_invoice)
        db.commit()
    finally:
        db.close()

    return created_invoices
