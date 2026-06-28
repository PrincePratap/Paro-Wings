# schemas/training_animal.py

from uuid import UUID
from pydantic import BaseModel


class TrainingAnimalCreate(BaseModel):
    name: str
    icon: str | None = None


class TrainingAnimalUpdate(BaseModel):
    name: str
    icon: str | None = None
    is_active: bool


class TrainingAnimalResponse(BaseModel):
    id: UUID
    name: str
    icon: str | None
    is_active: bool

    class Config:
        from_attributes = True