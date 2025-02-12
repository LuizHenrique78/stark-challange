import starkbank
import random
from datetime import datetime, timedelta
from faker import Faker
from app.services.starkbank_client import get_starkbank_user

get_starkbank_user()

fake = Faker("pt_BR")


def generate_random_invoices():
    num_invoices = random.randint(8, 12)
    invoices = []

    for _ in range(num_invoices):
        amount = random.randint(10000, 500000)
        due_date = datetime.utcnow() + timedelta(days=random.randint(1, 5))
        name = fake.name()
        tax_id = fake.cpf()

        invoice = starkbank.Invoice(
            amount=amount,
            descriptions=[{"key": "Service", "value": "Payment for service"}],
            due=due_date,
            expiration=86400,
            fine=2.5,
            interest=1.3,
            name=name,
            tax_id=tax_id,
            tags=["Invoice", "Auto-generated"],
        )
        invoices.append(invoice)

    return invoices


if __name__ == "__main__":
    invoices = generate_random_invoices()
    created_invoices = starkbank.invoice.create(invoices)

    for invoice in created_invoices:
        print(
            f"Invoice ID: {invoice.id}, Name: {invoice.name}, CPF: {invoice.tax_id}, Amount: {invoice.amount}, Due: {invoice.due}")
