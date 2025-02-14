from datetime import datetime
from typing import List

from pydantic import BaseModel, HttpUrl, Field


class Description(BaseModel):
    key: str
    value: str

    class config:
        validate_assignment = True


class Invoice(BaseModel):
    amount: int
    brcode: str
    created: datetime | str
    descriptions: List[Description]
    discount_amount: int = Field(alias="discountAmount")
    discounts: List
    display_description: str = Field(alias="displayDescription")
    due: datetime | str
    expiration: int
    fee: int
    fine: float
    fine_amount: int = Field(alias="fineAmount")
    id: str
    interest: float
    interest_amount: int = Field(alias="interestAmount")
    link: HttpUrl | str
    name: str
    nominal_amount: int = Field(alias="nominalAmount")
    pdf: HttpUrl | str
    rules: List
    splits: List
    status: str
    tags: List[str]
    tax_id: str = Field(alias="taxId")
    transaction_ids: List[str] = Field(alias="transactionIds")
    updated: datetime | str

    class config:
        validate_assignment = True
        populate_by_name = True


class Log(BaseModel):
    authentication: str
    created: datetime | str
    errors: List
    id: str
    invoice: Invoice
    type: str

    class config:
        validate_assignment = True


class Event(BaseModel):
    created: datetime | str
    id: str
    log: Log
    subscription: str
    workspaceId: str

    class config:
        validate_assignment = True