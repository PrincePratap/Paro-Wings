from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.dependency  import get_db
from models.ngo import NGOInfo
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.dependency import get_db
from models.ngo import NGOInfo
from schemas.ngo import (
    NGOOwnerRegisterRequest,
    UpdateNGOLocationResponse,
    UpdateNGOLocationRequest,
    NGOLoginRequest,
    NGOLoginResponse

)
from service.auth_service import register_ngo_owner
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
import traceback
from schemas.otp import  VerifyOTPRequest, VerifyOTPResponse , VerifyNGOOTPRequest , VerifyNGOOTPResponse
from service.ngo_service import (
    update_ngo_location,
    get_current_ngo,
    login_ngo,
    authenticate_ngo,
    verify_and_create_ngo,
    get_volunteer_requests
)
from passlib.context import CryptContext

from models.volunteer_request import VolunteerRequest
import traceback

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.ngo import NGOInfo
from schemas.volunteer_request import VolunteerRequestActionRequest
from service.ngo_service import (
    get_current_ngo,
    manage_volunteer_request_service,
)





router = APIRouter(
    prefix="/ngo",
    tags=["NGO"]
)







@router.post("/register")
async def register(
    user: NGOOwnerRegisterRequest,
    db: Session = Depends(get_db)
):
    try:
        return await register_ngo_owner(db, user)

    except HTTPException as exc:
        raise exc

    except Exception as e:
        traceback.print_exc()   # Print full traceback in terminal
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
@router.post("/verify-otp", response_model=VerifyNGOOTPResponse)
def verify_ngo_otp(
    data: VerifyNGOOTPRequest,
    db: Session = Depends(get_db)
):
    try:
        return verify_and_create_ngo(db, data)

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

@router.patch(
    "/location",
    response_model=UpdateNGOLocationResponse
)
def update_location(
    data: UpdateNGOLocationRequest,
    current_ngo: NGOInfo = Depends(get_current_ngo),
    db: Session = Depends(get_db)
):
    return update_ngo_location(
        session=db,
        current_ngo=current_ngo,
        data=data
    )


@router.post("/login", response_model=NGOLoginResponse)
def login(
    data: NGOLoginRequest,
    db: Session = Depends(get_db)
):
    try:
        return authenticate_ngo(db, data)

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
    raise

@router.get("/volunteer-requests")
def volunteer_requests(
    current_ngo: NGOInfo = Depends(get_current_ngo),
    db: Session = Depends(get_db)
):
    try:
        return get_volunteer_requests(
            db,
            current_ngo
        )

    except HTTPException as exc:
        raise exc

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.patch("/volunteer-request/{request_id}")
def manage_volunteer_request(
    request_id: str,
    body: VolunteerRequestActionRequest,
    current_ngo: NGOInfo = Depends(get_current_ngo),
    db: Session = Depends(get_db),
):
    try:
        return manage_volunteer_request_service(
            session=db,
            current_ngo=current_ngo,
            request_id=request_id,
            body=body,
        )

    except HTTPException as exc:
        raise exc

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
 