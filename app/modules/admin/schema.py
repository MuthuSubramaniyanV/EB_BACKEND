from pydantic import BaseModel
from typing import Optional


class ConsumerSummary(BaseModel):
    id: int
    name: str
    email: str
    consumer_number: Optional[str]


class ConsumerMonthImages(BaseModel):
    first_day_image: Optional[str]
    last_day_image: Optional[str]
    first_reading: Optional[float]
    last_reading: Optional[float]


class ApproveReadingPayload(BaseModel):
    reading_id: int
    verification_note: Optional[str] = None


class ModifyReadingPayload(BaseModel):
    reading_id: int
    reading_value: float
    verification_note: Optional[str] = None
