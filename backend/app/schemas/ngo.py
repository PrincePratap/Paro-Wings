from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional
from uuid import UUID



class NGO(BaseModel):

    # NGO Information
    id: UUID
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    # Owner Details
    owner_name: Optional[str] = None
    owner_email: Optional[EmailStr] = None
    owner_phone: Optional[str] = None

    # Address
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    landmark: Optional[str] = None

    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None

    # Location
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # NGO Details
    website: Optional[HttpUrl] = None
    description: Optional[str] = None

    # Operations
    emergency_contact: Optional[str] = None
    accepts_rescue_requests: Optional[bool] = None