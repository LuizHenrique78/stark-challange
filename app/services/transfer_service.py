import starkbank
from app.services.starkbank_client import get_starkbank_user
from app.core.database import SessionLocal
from app.models.transfer import Transfer


def make_transfer(invoice_id: int, amount: float):
    """
    Transfer the paid amount (minus fees) to the provided account.
    For simplicity, assume no fees or a small fee.
    In production, you would fetch the actual fee from the invoice info.
    """
    get_starkbank_user()  # sets starkbank.user

    # Let's define a small random fee or zero.
    # Replace with the real fee from invoice if necessary:
    fee = 1.0  # e.g., R$1.00
    net_amount = amount - fee
    if net_amount < 0:
        net_amount = 0

    # The destination account is from the spec:
    # bank code: 20018183, branch: 0001, ...
    # account type: "payment"
    transfer_object = starkbank.Transfer(
        amount=int(net_amount * 100),  # convert to cents
        bank_code="20018183",
        branch_code="0001",
        account_number="6341320293482496",
        tax_id="20.018.183/0001-80",
        name="Stark Bank S.A.",
        account_type="payment"
    )
    result = starkbank.transfer.create([transfer_object])

    # Store the transfer in DB
    db = SessionLocal()
    try:
        transfer_record = Transfer(
            invoice_id=invoice_id,
            amount=net_amount,
            status="created"
        )
        db.add(transfer_record)
        db.commit()
    finally:
        db.close()

    return result