from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "consumer"
    phone: Optional[str] = None
    consumer_number: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    role: str = "consumer"


class AuthTokens(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int


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
