from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from enum import Enum

class AdoptionRequestStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"


class UpdateAdoptionRequestStatus(BaseModel):
    status: AdoptionRequestStatus


class AdoptionCreate(BaseModel):
    owner_id: UUID
    owner_name: str

    animal_name: str
    animal_type: str
    breed: str
    age: int
    gender: str
    description: str

    vaccinated: bool
    sterilized: bool

    photo_url: str | None = None

    city: str
    state: str
    contact_number: str


class AdoptionResponse(BaseModel):
    id: UUID

    owner_id: UUID
    owner_name: str

    animal_name: str
    animal_type: str
    breed: str
    age: int
    gender: str
    description: str

    vaccinated: bool
    sterilized: bool

    adoption_status: str

    photo_url: str | None

    city: str
    state: str
    contact_number: str

    created_at: datetime

    class Config:
        from_attributes = True





class AdoptionRequestCreate(BaseModel):
    animal_id: UUID
    user_id: UUID
    message: str


class AdoptionRequestResponse(BaseModel):
    id: UUID
    animal_id: UUID
    user_id: UUID
    message: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True




class AdoptionRequestStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"


class UpdateAdoptionRequestStatus(BaseModel):
    status: AdoptionRequestStatus