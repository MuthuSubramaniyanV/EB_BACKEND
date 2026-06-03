from datetime import datetime
from pydantic import BaseModel


class PredictionCreate(BaseModel):
    user_id: int
    prediction_month: str


class PredictionRead(BaseModel):
    id: int
    user_id: int
    predicted_units: float
    predicted_bill: float
    prediction_month: str
    created_at: datetime

    class Config:
        orm_mode = True
