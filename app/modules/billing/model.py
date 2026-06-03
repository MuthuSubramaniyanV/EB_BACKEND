from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Bill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    month: str
    start_reading: float
    end_reading: float
    units_consumed: float
    tariff_amount: float
    gst_amount: float
    fixed_charge: float
    additional_charge: float
    total_amount: float
    status: str = Field(default="draft")
    generated_by: Optional[int] = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
