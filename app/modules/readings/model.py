from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class MeterReading(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    upload_id: Optional[int] = Field(default=None, foreign_key="meterupload.id")
    reading_value: float
    ocr_confidence: float = 0.0
    verified: bool = Field(default=False)
    verified_by: Optional[int] = Field(default=None, foreign_key="users.id")
    verification_note: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
