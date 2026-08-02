from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional
from uuid import UUID



from enum import Enum
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl, Field
import re
from typing import Optional


class UserRole(str, Enum):
    RESCUER = "rescuer"
    NGO_ADMIN = "ngo_admin"
    VETERINARIAN = "veterinarian"
    VOLUNTEER = "volunteer"


class NGOStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"




from pydantic import (
    BaseModel,
    EmailStr,
    HttpUrl,
    field_validator
)


class NGOOwnerRegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str
    ngo_name: str

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str):
        value = value.strip()

        if len(value) < 3 or len(value) > 100:
            raise ValueError("Full name must be between 3 and 100 characters.")

        return value

    @field_validator("ngo_name")
    @classmethod
    def validate_ngo_name(cls, value: str):
        value = value.strip()

        if len(value) < 3 or len(value) > 200:
            raise ValueError("NGO name must be between 3 and 200 characters.")

        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr):
        return str(value).strip().lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str):
        value = value.strip()

        if not re.fullmatch(r"^[6-9]\d{9}$", value):
            raise ValueError("Phone must be a valid Indian mobile number.")

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):

        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters.")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain an uppercase letter.")

        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain a lowercase letter.")

        if not re.search(r"\d", value):
            raise ValueError("Password must contain a number.")

        if not re.search(r"[^A-Za-z0-9]", value):
            raise ValueError("Password must contain a special character.")

        return value

  
class UpdateNGOStatusRequest(BaseModel):
    status: str


class VerifyNGOOTPRequest(BaseModel):
    ngo_id: UUID
    otp: str


class VerifyNGOOTPResponse(BaseModel):
    success: bool
    message: str
    data: dict


class OwnerDetails(BaseModel):
    owner_name: str
    owner_email: str
    owner_phone: str


class UpdateNGOLocationData(BaseModel):
    address_line_1: Optional[str] = None
    landmark: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None


class UpdateNGOBasicInfo(BaseModel):
    ngo_name: Optional[str] = None
    registration_number: Optional[str] = None
    description: Optional[str] = None


class UpdateNGOLocationResponse(BaseModel):
    success: bool
    message: str
    data: UpdateNGOLocationData


class UpdateNGOLocationRequest(BaseModel):
    address_line_1: Optional[str] = None
    landmark: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
 

class NGOLoginRequest(BaseModel):
    email: EmailStr
    password: str

class NGOLoginData(BaseModel):
    ngo_id: str
    ngo_name: str
    owner_name: str
    owner_email: str
    owner_phone: str
    total_volunteers: int = 0
    access_token: str
    token_type: str = "bearer"

class NGOLoginResponse(BaseModel):
    success: bool
    message: str
    data: NGOLoginData

class UpdateContactInfo(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[HttpUrl] = None
    emergency_contact : Optional[str] = None

class updateNGOOwnerInfo(BaseModel):
    owner_name: Optional[str] = None
    owner_email: Optional[EmailStr] = None
    owner_phone: Optional[str] = None

class UpdateNGOMapInfo(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class UpdateNGOSettings(BaseModel):
    ngo_id: str
    is_active: Optional[bool] = True
    is_verified: Optional[bool] = False
    is_suspended: Optional[bool] = False

class UpdateNGOStatistics(BaseModel):
    total_reports: Optional[int] = 0
    total_rescues: Optional[int] = 0
    rating: Optional[float] = 0.0
    total_volunteers : Optional[int] = 0

    
  

class UpdateNGOResponse(BaseModel):
    success: bool
    message: str
    ngo_settings: UpdateNGOSettings
    ngo_statistics: UpdateNGOStatistics
    ngo_basic_info: UpdateNGOBasicInfo
    ngo_locations : UpdateNGOLocationData
    ngo_contact_info: UpdateContactInfo
    ngo_owner_info: updateNGOOwnerInfo
    ngo_map : UpdateNGOMapInfo



