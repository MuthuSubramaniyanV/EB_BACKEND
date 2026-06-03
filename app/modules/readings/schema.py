from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ReadingCreate(BaseModel):
    user_id: Optional[int] = None
    upload_id: Optional[int] = None
    reading_value: float
    ocr_confidence: Optional[float] = 0.0


class ReadingUpdate(BaseModel):
    reading_value: Optional[float] = None
    ocr_confidence: Optional[float] = None
    verified: Optional[bool] = None
    verification_note: Optional[str] = None


class ReadingRead(BaseModel):
    id: int
    user_id: int
    upload_id: Optional[int]
    reading_value: float
    ocr_confidence: float
    verified: bool
    verified_by: Optional[int]
    verification_note: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True
