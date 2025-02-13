from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Transfer(Base):
    __tablename__ = "transfers"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    fee = Column(Integer, nullable=False)
    fine_amount = Column(Integer, nullable=False)
    interest_amount = Column(Integer, nullable=False)
    net_amount = Column(Integer, nullable=False)
    transfer_id = Column(String, nullable=True)
    external_id = Column(String, nullable=False)
    status = Column(String, nullable=False, default="created")
    created_at = Column(DateTime, default=datetime.utcnow)
    payload = Column(JSON, nullable=True)