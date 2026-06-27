from uuid import uuid4

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from database.base import Base


class MyAnimal(Base):
    __tablename__ = "my_animals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    name = Column(String(100), nullable=False)
    animal_type = Column(String(50), nullable=False)
    breed = Column(String(100), nullable=False)
    gender = Column(String(20), nullable=False)

    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)

    color = Column(String(50))

    vaccinated = Column(Boolean, default=False)
    sterilized = Column(Boolean, default=False)

    medical_notes = Column(Text)

    photo_url = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )