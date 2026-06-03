from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(sa_column=Column(String, unique=True, index=True))
    password_hash: str
    role: str = Field(default="consumer")
    phone: Optional[str] = None
    consumer_number: Optional[str] = None
    app_state: Optional[str] = Field(default=None) 
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
