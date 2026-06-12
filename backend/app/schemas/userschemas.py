from datetime import datetime
from enum import Enum
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


class UserResponse(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    phone: str
    role: UserRole
    is_verified: bool
    created_at: datetime