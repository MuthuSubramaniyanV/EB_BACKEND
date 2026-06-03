from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, ForeignKey


class Prediction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    predicted_units: float
    predicted_bill: float
    prediction_month: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
