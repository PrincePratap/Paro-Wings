from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class AnimalReportCreate(BaseModel):
    animal_type: str
    animal_count: int = Field(default=1, ge=1)

    situation_type: str
    severity: str
    description: str

    latitude: float
    longitude: float

    address_line_1: str
    locality: str
    city: str
    state: str
    postal_code: str

    image_urls: List[str] = Field(default_factory=list)
    anonymous_report: bool = False
    created_at: Optional[datetime] = None

class UpdateStatusRequest(BaseModel):
    status: str