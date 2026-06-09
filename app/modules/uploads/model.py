from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone


class MeterUpload(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    file_name: str
    image_url: str
    timestamp: datetime
    status: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
