from pydantic import BaseModel
from typing import Optional


class OcrResponse(BaseModel):
    reading: float
    confidence: float
    upload_id: Optional[int] = None
    image_url: Optional[str] = None
