from pydantic import BaseModel
from datetime import datetime


class MeterReadingResponse(BaseModel):
    id: int
    image_url: str
    timestamp: datetime
    status: str
