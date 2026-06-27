from typing import Optional

from pydantic import BaseModel, EmailStr


class SendOTPRequest(BaseModel):
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str
    user_id : str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


