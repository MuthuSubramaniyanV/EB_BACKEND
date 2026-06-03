from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    phone: Optional[str] = None
    consumer_number: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    consumer_number: Optional[str] = None
    role: Optional[str] = None


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    consumer_number: Optional[str] = None
    role: Optional[str] = "consumer"
