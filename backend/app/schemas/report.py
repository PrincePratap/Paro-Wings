from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AnimalReportCreate(BaseModel):
    # Animal Information
    animal_type: str
    animal_count: int = 1
    animal_color: Optional[str] = None
    animal_age: Optional[str] = None
    animal_gender: Optional[str] = None

    # Emergency Information
    situation_type: str  # Injured, Sick, Trapped, Abandoned, etc.
    severity: str        # Low, Medium, High, Critical
    description: str

    # Location
    latitude: float
    longitude: float

    # Detailed Address
    address_line_1: str
    address_line_2: Optional[str] = None
    landmark: Optional[str] = None

    locality: str          # e.g. Mayur Vihar
    city: str              # e.g. Delhi
    state: str             # e.g. Delhi
    postal_code: str       # e.g. 110091
    country: str = "India"

    # Media
    image_urls: Optional[List[str]] = []
    video_url: Optional[str] = None

    # Reporter Information
    current_user_id: int
    reporter_name: Optional[str] = None
    reporter_phone: Optional[str] = None
    anonymous_report: bool = False

    # Status Information
    status: str = "Pending"

    # NGO Assignment
    ngo_id: Optional[int] = None

    # Timestamps
    created_at: Optional[datetime] = None