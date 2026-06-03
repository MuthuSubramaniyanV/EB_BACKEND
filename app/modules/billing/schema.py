from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class BillCreate(BaseModel):
    user_id: int
    month: str
    gst: float
    fixed_charge: float
    additional_charge: float


class BillRead(BaseModel):
    id: int
    user_id: int
    month: str
    start_reading: float
    end_reading: float
    units_consumed: float
    tariff_amount: float
    gst_amount: float
    fixed_charge: float
    additional_charge: float
    total_amount: float
    status: str
    generated_by: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True
