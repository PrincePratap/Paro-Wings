import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Float,
    Boolean,
    Text,
    DateTime,
    Integer
)

from database.base import Base


class NGOInfo(Base):
    __tablename__ = "ngos"

    # ======================================
    # Primary Key
    # ======================================
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # ======================================
    # NGO Information
    # ======================================
    name = Column(String(255), nullable=False)
    registration_number = Column(String(100), unique=True, nullable=True)

    email = Column(String(255), unique=True, nullable=True)
    phone = Column(String(20), nullable=True)

    website = Column(String(500))
    description = Column(Text)

    # ======================================
    # Owner / Admin Information
    # ======================================
    owner_name = Column(String(255), nullable=False)
    owner_email = Column(String(255), nullable=False)
    owner_phone = Column(String(20), nullable=False)

    password_hash = Column(
        String(255),
        nullable=False
    )


    # ======================================
    # Address
    # ======================================
    address_line_1 = Column(String(255), nullable=True)
    landmark = Column(String(255))

    city = Column(String(100), nullable=True)
    district = Column(String(100))
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="India")
    postal_code = Column(String(20), nullable=True)

    # ======================================
    # Location
    # ======================================
    latitude = Column(Float,nullable= True)
    longitude = Column(Float, nullable= True)

    # ======================================
    # Emergency Contact
    # ======================================
    emergency_contact = Column(String(20) , nullable= True)

    # ======================================
    # NGO Settings
    # ======================================
    accepts_rescue_requests = Column(
        Boolean,
        default=True
    )

    is_verified = Column(
        Boolean,
        default=False
    )

    is_active = Column(
        Boolean,
        default=True
    )

    # pending | approved | rejected | suspended
    status = Column(
        String(20),
        default="pending"
    )

    # ======================================
    # Statistics
    # ======================================
    total_reports = Column(
        Integer,
        default=0
    )

    total_rescues = Column(
        Integer,
        default=0
    )

    total_volunteers = Column(
        Integer,
        default=0
    )

    total_veterinarians = Column(
        Integer,
        default=0
    )

    rating = Column(
        Float,
        default=0.0
    )

    # ======================================
    # Metadata
    # ======================================
    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )