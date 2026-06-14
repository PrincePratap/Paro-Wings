from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Enum as SqlEnum
)
from sqlalchemy.dialects.postgresql import UUID

from database.base import Base


class UserRole(str, Enum):
    CITIZEN = "citizen"
    RESCUER = "rescuer"
    NGO_ADMIN = "ngo_admin"
    SUPER_ADMIN = "super_admin"


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    full_name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False
    )

    phone = Column(
        String(20),
        nullable=False
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    role = Column(
        SqlEnum(UserRole),
        default=UserRole.CITIZEN,
        nullable=False
    )

    is_verified = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )