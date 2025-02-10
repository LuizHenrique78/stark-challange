import starkbank
from fastapi import APIRouter, status, Response
from requests import Request
from app.api.deps import SessionDep
from app.services.transfer_service import make_transfer
from app.models.invoice import Invoice

router = APIRouter()


@router.post(
    "/invoice-callback",
    response_description="Webhook callback response",
    status_code=status.HTTP_200_OK
)
def invoice_callback(request: Request, db: SessionDep):
    """
    Receives invoice updates from Stark Bank.
    When the invoice is paid, create a transfer for the net amount.
    """
    event = starkbank.event.parse(
        content=request.data.decode("utf-8"),
        signature=request.headers["Digital-Signature"],
    )
    if event.subscription == "transfer":
        try:
            invoice = db.query(Invoice).filter(Invoice.external_id == event.log.transfer.external_id).first()
            if invoice is not None and not invoice.is_paid:
                invoice.is_paid = True
                db.commit()
                make_transfer(invoice.id, event.log.transfer.amount)
        except Exception as e:
            # TODO : Tratar possiveis erros
            raise e
    return {"message": "Webhook received successfully"}
