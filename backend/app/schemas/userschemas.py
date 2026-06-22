from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    CITIZEN = "citizen"
    RESCUER = "rescuer"
    NGO_ADMIN = "ngo_admin"
    SUPER_ADMIN = "super_admin"


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str


class GoogleLoginRequest(BaseModel):
    firebase_uid: str
    full_name: str
    email: EmailStr
    photo_url: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    role: UserRole
    is_verified: bool
    photo_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True