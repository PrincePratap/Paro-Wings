from datetime import datetime
import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey
)

from database.base import Base


class VolunteerRequest(Base):
    __tablename__ = "volunteer_requests"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Volunteer
    volunteer_id = Column(
        String(36),
        ForeignKey("volunteers.id"),
        nullable=False
    )

    volunteer_name = Column(
        String(150),
        nullable=False
    )

    volunteer_email = Column(
        String(255),
        nullable=False
    )

    volunteer_phone = Column(
        String(20),
        nullable=False
    )

    # NGO
    ngo_id = Column(
        String(36),
        ForeignKey("ngos.id"),
        nullable=False
    )

    ngo_name = Column(
        String(255),
        nullable=False
    )

    # Request Details
    message = Column(
        Text,
        nullable=True
    )

    experience = Column(
        Text,
        nullable=True
    )

    available_days = Column(
        String(100),
        nullable=True
    )

    preferred_role = Column(
        String(100),
        nullable=True
    )  # Rescue / Transport / Foster / Fundraising / Admin

    # Status
    status = Column(
        String(20),
        default="pending"
    )  # pending | approved | rejected | cancelled

    reviewed_by = Column(
        String(36),
        nullable=True
    )

    reviewed_at = Column(
        DateTime,
        nullable=True
    )

    rejection_reason = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )