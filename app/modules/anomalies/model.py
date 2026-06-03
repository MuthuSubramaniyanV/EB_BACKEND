from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Anomaly(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    reading_id: int = Field(foreign_key="meterreading.id")
    anomaly_type: str
    description: str
    severity: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
