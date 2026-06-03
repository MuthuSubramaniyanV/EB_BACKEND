from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column, ForeignKey


class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bill_id: int = Field(foreign_key="bill.id")
    receipt_url: str
    payment_status: str = Field(default="pending")
    verified_by: Optional[int] = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
