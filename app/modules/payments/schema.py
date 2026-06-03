from datetime import datetime
from pydantic import BaseModel, HttpUrl
from typing import Optional


class PaymentCreate(BaseModel):
    bill_id: int
    receipt_url: HttpUrl


class PaymentRead(BaseModel):
    id: int
    bill_id: int
    receipt_url: HttpUrl
    payment_status: str
    verified_by: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True


class PaymentVerify(BaseModel):
    payment_status: str = "verified"
