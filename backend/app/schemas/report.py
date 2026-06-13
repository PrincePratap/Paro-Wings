from pydantic import BaseModel

class AnimalReportCreate(BaseModel):
    animal_type: str
    description: str
    latitude: str
    longitude: str