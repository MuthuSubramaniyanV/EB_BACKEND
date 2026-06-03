from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional


class UploadRead(BaseModel):
    id: int
    user_id: int
    file_name: str
    image_url: HttpUrl
    timestamp: datetime
    status: str
    created_at: datetime

    class Config:
        orm_mode = True


class UploadResponse(BaseModel):
    id: int
    image_url: HttpUrl
    timestamp: datetime
    status: str


class UploadCreateResponse(BaseModel):
    id: int
    image_url: HttpUrl
    timestamp: datetime
    status: str
