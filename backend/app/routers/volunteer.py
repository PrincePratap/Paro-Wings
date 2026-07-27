import traceback

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.dependency import get_db
from service.volunteer import authenticate_volunteer , verify_and_create_volunteer, register_volunteer

from schemas.volunteer import (
    VolunteerRegisterRequest,
    VerifyVolunteerOTPResponse,
    VerifyVolunteerOTPRequest,
    VolunteerLoginRequest,
    VolunteerLoginResponse
)

router = APIRouter(
    prefix="/volunteer",
    tags=["Volunteer"]
)


@router.post("/register")
async def register(
    volunteer: VolunteerRegisterRequest,
    db: Session = Depends(get_db)
):
    try:
        return await register_volunteer(db, volunteer)

    except HTTPException as exc:
        raise exc

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/verify-otp", response_model=VerifyVolunteerOTPResponse)
def verify_volunteer_otp(
    data: VerifyVolunteerOTPRequest,
    db: Session = Depends(get_db)
):
    try:
        return verify_and_create_volunteer(db, data)

    except HTTPException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.detail
            },
        )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": str(e)
            },
        )

@router.post("/login", response_model=VolunteerLoginResponse)
def login(
    data: VolunteerLoginRequest,
    db: Session = Depends(get_db)
):
    try:
        return authenticate_volunteer(db, data)

    except HTTPException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.detail
            },
        )

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": str(e)
            },
        )