from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from enum import Enum



# -----------------------------
# Create Join Request
# -----------------------------

class VolunteerJoinRequest(BaseModel):
    ngo_id: str
    message: Optional[str] = None
    experience: Optional[str] = None
    available_days: Optional[str] = None
    preferred_role: Optional[str] = None


# -----------------------------
# Volunteer Details
# -----------------------------

class VolunteerRequestVolunteer(BaseModel):
    volunteer_id: str
    volunteer_name: str
    volunteer_email: str
    volunteer_phone: str


# -----------------------------
# NGO Details
# -----------------------------

class VolunteerRequestNGO(BaseModel):
    ngo_id: str
    ngo_name: str


# -----------------------------
# Response Data
# -----------------------------

class VolunteerRequestData(BaseModel):
    request_id: str

    volunteer: VolunteerRequestVolunteer
    ngo: VolunteerRequestNGO

    message: Optional[str] = None
    experience: Optional[str] = None
    available_days: Optional[str] = None
    preferred_role: Optional[str] = None

    status: str

    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

    created_at: datetime
    updated_at: datetime


# -----------------------------
# Create Response
# -----------------------------

class VolunteerJoinResponse(BaseModel):
    success: bool
    message: str
    data: VolunteerRequestData

class VolunteerRequestAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"


class VolunteerRequestActionRequest(BaseModel):
    action: VolunteerRequestAction
