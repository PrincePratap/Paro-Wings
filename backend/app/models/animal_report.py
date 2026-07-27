from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime

from database.base import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID


class AnimalReport(Base):
    __tablename__ = "animal_reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True),nullable=False)
    user_name = Column(String(100), nullable=True)  # Optional: Store the user's name
    user_phone = Column(String(20), nullable=True)  # Optional: Store the user's phone number
    user_email = Column(String(255), nullable=True)  # Optional: Store the user's email
    animal_type = Column(String(100))
    animal_count = Column(Integer, default=1)

    situation_type = Column(String(100))
    severity = Column(String(50))

    description = Column(Text)

    latitude = Column(Float)
    longitude = Column(Float)

    address_line_1 = Column(String(255))
    locality = Column(String(100))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))

    image_urls = Column(JSON)

    anonymous_report = Column(Boolean, default=False)

    status = Column(String(50), default="Pending")

    created_at = Column(DateTime, default=datetime.utcnow)