import re
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class SendOTPRequest(BaseModel):
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str
    full_name: str
    phone: str
    password: str

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not 3 <= len(cleaned) <= 100:
            raise ValueError("Full name must be between 3 and 100 characters")
        return cleaned

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        cleaned = value.strip()
        if not re.fullmatch(r"^[6-9]\d{9}$", cleaned):
            raise ValueError("Phone must be a valid Indian mobile number")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain an uppercase character")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain a lowercase character")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain a number")
        if not re.search(r"[^A-Za-z0-9]", value):
            raise ValueError("Password must contain a special character")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


