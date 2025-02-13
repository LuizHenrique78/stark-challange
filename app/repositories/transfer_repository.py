from sqlalchemy.orm import Session
from ..models.transfer import Transfer


class TransferRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_transfer(self, transfer_data: dict) -> Transfer:
        db_transfer = Transfer(**transfer_data)
        self.db.add(db_transfer)
        self.db.commit()
        self.db.refresh(db_transfer)
        return db_transfer

    def update_transfer_status(self, transfer_id: int, status: str) -> Transfer:
        db_transfer = self.db.query(Transfer).filter(Transfer.id == transfer_id).first()
        if db_transfer:
            db_transfer.status = status
            self.db.commit()
            self.db.refresh(db_transfer)
        return db_transfer
