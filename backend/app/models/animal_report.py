from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime

from app.database.base import Base

class AnimalReport(Base):
    __tablename__ = "animal_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)

    animal_type = Column(String(100))
    description = Column(Text)

    image_url = Column(String(500))

    latitude = Column(String(50))
    longitude = Column(String(50))

    status = Column(String(50), default="pending")

    created_at = Column(DateTime, default=datetime.utcnow)