
import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Float,
    Boolean,
    Text,
    DateTime,
    Integer,
    ForeignKey

)

from database.base import Base



class Volunteer(Base):
    __tablename__ = "volunteers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    full_name = Column(String(255), nullable=False)
    ngo_id = Column(
        String(36),
        ForeignKey("ngos.id"),
        nullable=True
    )

    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=False)

    password_hash = Column(String(255), nullable=False)

    profile_image = Column(String(500), nullable=True)

    address_line_1 = Column(String(255), nullable=True)
    landmark = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="India")
    postal_code = Column(String(20), nullable=True)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    total_rescues = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)