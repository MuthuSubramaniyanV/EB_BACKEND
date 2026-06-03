from pydantic import BaseModel


class OcrResponse(BaseModel):
    reading: float
    confidence: float
