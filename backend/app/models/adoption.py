from uuid import uuid4
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Integer,
    Text
)
from sqlalchemy.dialects.postgresql import UUID

from database.base import Base




class Adoption(Base):
    __tablename__ = "adoptions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    owner_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True
    )

    owner_name = Column(
        String,
        nullable=False
    )

    animal_name = Column(
        String,
        nullable=False
    )

    animal_type = Column(
        String,
        nullable=False
    )

    breed = Column(
        String,
        nullable=True
    )

    age = Column(
        Integer,
        nullable=False
    )

    gender = Column(
        String,
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    vaccinated = Column(
        Boolean,
        default=False
    )

    sterilized = Column(
        Boolean,
        default=False
    )

    adoption_status = Column(
        String,
        default="available"
    )

    photo_url = Column(
        String,
        nullable=True
    )

    city = Column(
        String,
        nullable=False
    )

    state = Column(
        String,
        nullable=False
    )

    contact_number = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class AdoptionRequest(Base):
    __tablename__ = "adoption_requests"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    animal_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True
    )

    user_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True
    )

    message = Column(
        Text,
        nullable=True
    )

    status = Column(
        String,
        default="pending"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )