from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.ngo import NGOInfo
from models.volunteer import Volunteer
from models.volunteer_request import VolunteerRequest
from schemas.volunteer_request import VolunteerJoinRequest
from service.volunteer import get_current_volunteer
from service.auth_service import success_response
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session





def send_join_request(
    session: Session,
    volunteer: Volunteer,
    data: VolunteerJoinRequest
) -> dict[str, Any]:

    ngo = (
        session.query(NGOInfo)
        .filter(NGOInfo.id == data.ngo_id)
        .first()
    )

    if not ngo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NGO not found."
        )

    existing = (
        session.query(VolunteerRequest)
        .filter(
            VolunteerRequest.volunteer_id == volunteer.id,
            VolunteerRequest.ngo_id == ngo.id,
            VolunteerRequest.status == "pending"
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Request already pending."
        )

    request = VolunteerRequest(
        volunteer_id=volunteer.id,
        volunteer_name=volunteer.full_name,
        volunteer_email=volunteer.email,
        volunteer_phone=volunteer.phone,
        ngo_id=ngo.id,
        ngo_name=ngo.name,
        message=data.message,
        experience=data.experience,
        available_days=data.available_days,
        preferred_role=data.preferred_role,
        status="pending"
    )

    session.add(request)
    session.commit()
    session.refresh(request)

    return success_response(
    "Join request sent successfully.",
    {
        "request_id": str(request.id),

        "volunteer": {
            "volunteer_id": str(request.volunteer_id),
            "volunteer_name": request.volunteer_name,
            "volunteer_email": request.volunteer_email,
            "volunteer_phone": request.volunteer_phone
        },

        "ngo": {
            "ngo_id": str(request.ngo_id),
            "ngo_name": request.ngo_name
        },

        "message": request.message,
        "experience": request.experience,
        "available_days": request.available_days,
        "preferred_role": request.preferred_role,

        "status": request.status,

        "reviewed_by": request.reviewed_by,
        "reviewed_at": request.reviewed_at,
        "rejection_reason": request.rejection_reason,

        "created_at": request.created_at,
        "updated_at": request.updated_at
    }
)





   