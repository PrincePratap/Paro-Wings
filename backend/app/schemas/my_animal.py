from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class MyAnimalCreate(BaseModel):
    owner_id: UUID

    name: str
    animal_type: str
    breed: str
    gender: str

    age: int
    weight: float

    color: Optional[str] = None

    vaccinated: bool = False
    sterilized: bool = False

    medical_notes: Optional[str] = None

    photo_url: Optional[str] = None


class MyAnimalResponse(BaseModel):
    id: UUID
    owner_id: UUID

    name: str
    animal_type: str
    breed: str
    gender: str

    age: int
    weight: float

    color: Optional[str]

    vaccinated: bool
    sterilized: bool

    medical_notes: Optional[str]

    photo_url: Optional[str]

    created_at: datetime

    class Config:
        from_attributes = True


class MyAnimalUpdate(BaseModel):
    name: Optional[str] = None
    animal_type: Optional[str] = None
    breed: Optional[str] = None
    gender: Optional[str] = None

    age: Optional[int] = None
    weight: Optional[float] = None

    color: Optional[str] = None

    vaccinated: Optional[bool] = None
    sterilized: Optional[bool] = None

    medical_notes: Optional[str] = None

    photo_url: Optional[str] = None