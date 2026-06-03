from datetime import datetime
from pydantic import BaseModel


class AnomalyCreate(BaseModel):
    user_id: int


class AnomalyRead(BaseModel):
    id: int
    user_id: int
    reading_id: int
    anomaly_type: str
    description: str
    severity: str
    created_at: datetime

    class Config:
        orm_mode = True
