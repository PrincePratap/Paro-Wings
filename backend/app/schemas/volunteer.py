from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional
from uuid import UUID
from typing import Optional, Any




from enum import Enum
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl, Field
import re
from typing import Optional

class VolunteerRegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str

class VolunteerLoginRequest(BaseModel):
    email: EmailStr
    password: str

class VolunteerLoginData(BaseModel):
    volunteer_id: str
    full_name: str
    email: str
    phone: str
    total_rescues: int = 0
    access_token: str
    token_type: str = "bearer"

class VolunteerLoginResponse(BaseModel):
    success: bool
    message: str
    data: VolunteerLoginData

class VerifyVolunteerOTPRequest(BaseModel):
    volunteer_id: UUID
    otp: str


class VerifyVolunteerOTPResponse(BaseModel):
    success: bool
    message: str
    data: dict

