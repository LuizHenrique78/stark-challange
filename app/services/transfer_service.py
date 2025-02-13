# starkbank_transfer/services/transfer_service.py
import starkbank
from ..repositories.transfer_repository import TransferRepository
from ..models.transfer import Transfer


class TransferService:
    def __init__(self, transfer_repository: TransferRepository):
        self.transfer_repository = transfer_repository

    def calculate_net_amount(self, invoice: dict) -> int:
        amount = invoice.get("amount", 0)
        fee = invoice.get("fee", 0)
        fine_amount = invoice.get("fineAmount", 0)
        interest_amount = invoice.get("interestAmount", 0)
        net_amount = amount - fee - fine_amount - interest_amount
        return max(net_amount, 0)

    def create_transfer(self, invoice: dict) -> Transfer:
        net_amount = self.calculate_net_amount(invoice)

        transfer = starkbank.transfer.create([
            starkbank.Transfer(
                amount=net_amount,
                bank_code="20018183",
                branch_code="0001",
                account_number="6341320293482496",
                tax_id="20.018.183/0001-80",
                name="Stark Bank S.A.",
                account_type="payment",
                external_id=f"transfer-{invoice['id']}",
                tags=["webhook-transfer"],
            )
        ])

        transfer_data = {
            "invoice_id": invoice["id"],
            "amount": invoice["amount"],
            "fee": invoice["fee"],
            "fine_amount": invoice["fineAmount"],
            "interest_amount": invoice["interestAmount"],
            "net_amount": net_amount,
            "transfer_id": transfer[0].id,
            "external_id": f"transfer-{invoice['id']}",
            "status": "created",
            "payload": invoice,
        }
        return self.transfer_repository.create_transfer(transfer_data)
