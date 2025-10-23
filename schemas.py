from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    @validator('phone')
    def phone_validation(cls, v):
        if v and not v.startswith('+'):
            raise ValueError('Phone must start with +')
        return v


class UserCreate(UserBase):
    pass


class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    @validator('phone')
    def phone_validation(cls, v):
        if v and not v.startswith('+'):
            raise ValueError('Phone must start with +')
        return v


class VerifyCode(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    code: int


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: Optional[str] = None
    phone: Optional[str] = None


class SMSResponse(BaseModel):
    success: bool
    message: str
    message_id: Optional[str] = None