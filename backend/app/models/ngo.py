import uuid

from sqlalchemy import (
    Column,
    String,
    Float,
    Boolean,
    Text,
    DateTime
)

from datetime import datetime

from app.database.base import Base


class NGOInFo(Base):
    __tablename__ = "ngos"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # NGO Information
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)

    # Owner Details
    owner_name = Column(String(255), nullable=False)
    owner_email = Column(String(255), nullable=False)
    owner_phone = Column(String(20), nullable=False)

    # Address
    address_line_1 = Column(String(255))
    address_line_2 = Column(String(255))
    landmark = Column(String(255))

    city = Column(String(100))
    district = Column(String(100))
    state = Column(String(100))
    country = Column(String(100), default="India")
    postal_code = Column(String(20))

    # Location
    latitude = Column(Float)
    longitude = Column(Float)

    # NGO Details
    website = Column(String(500))
    description = Column(Text)

    # Operations
    emergency_contact = Column(String(20))
    accepts_rescue_requests = Column(
        Boolean,
        default=True
    )

    # Verification
    is_verified = Column(
        Boolean,
        default=False
    )

    is_active = Column(
        Boolean,
        default=True
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