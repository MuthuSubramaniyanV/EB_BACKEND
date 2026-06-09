from datetime import datetime
from pydantic import BaseModel, HttpUrl


class MeterCaptureResponse(BaseModel):
    upload_id: int
    image_url: HttpUrl
    timestamp: datetime
    status: str
