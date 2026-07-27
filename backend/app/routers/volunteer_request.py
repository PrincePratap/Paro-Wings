from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.dependency import get_db

from models.volunteer import Volunteer 

from schemas.volunteer_request import (
    VolunteerJoinRequest,
    VolunteerJoinResponse
)

from service.volunteer import get_current_volunteer
from service.volunteer_request import send_join_request


router = APIRouter(
    prefix="/volunteer",
    tags=["Volunteer"]
)




@router.post("/join-ngo", response_model=VolunteerJoinResponse)
def join_ngo(
    data: VolunteerJoinRequest,
    volunteer: Volunteer = Depends(get_current_volunteer),
    db: Session = Depends(get_db)
):
    return send_join_request(
        db,
        volunteer,
        data
    )