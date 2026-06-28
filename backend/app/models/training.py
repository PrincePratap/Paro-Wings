# models/training_animal.py

import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class TrainingAnimal(Base):
    __tablename__ = "training_animals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    icon = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)