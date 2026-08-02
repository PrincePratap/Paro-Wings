import re
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class SendOTPRequest(BaseModel):
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID | None = None
    ngo_id: UUID | None = None
    role: str | None = None
    otp: str

    @field_validator("otp")
    @classmethod
    def validate_otp(cls, value: str) -> str:
        cleaned = value.strip()
        if not re.fullmatch(r"\d{6}", cleaned):
            raise ValueError("OTP must be a 6-digit string")
        return cleaned


class VerifyOTPData(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    role: str
    account_type: str
    access_token: str
    token_type: str = "bearer"


class VerifyOTPResponse(BaseModel):
    success: bool
    message: str
    data: VerifyOTPData


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class LoginResponseData(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    role: str
    account_type: str
    access_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    success: bool
    message: str
    data: LoginResponseData


class VerifyNGOOTPRequest(BaseModel):
    ngo_id: UUID
    otp: str


class VerifyNGOOTPResponse(BaseModel):
    success: bool
    message: str
    data: dict
