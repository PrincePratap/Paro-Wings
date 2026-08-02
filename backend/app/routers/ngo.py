
from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session

from database.dependency  import get_db
from models.ngo import NGOInfo



from schemas.ngo import (
    NGOOwnerRegisterRequest,
    UpdateContactInfo,
    NGOLoginRequest,
    NGOLoginResponse,
    UpdateNGOResponse,
    UpdateNGOBasicInfo,
    updateNGOOwnerInfo,
    UpdateNGOLocationData,
    UpdateNGOMapInfo
    )
from service.ngo_update_service import update_map_info, update_ngo_basic_info, update_ngo_contact_info , update_ngo_owner_info , update_ngo_location_info

from service.auth_service import register_ngo_owner
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import traceback
from schemas.otp import  VerifyOTPRequest, VerifyOTPResponse , VerifyNGOOTPRequest , VerifyNGOOTPResponse
from service.ngo_service import (
    get_current_ngo,
    authenticate_ngo,
    verify_and_create_ngo,
    get_volunteer_requests
)




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
    "/basic-info",
    response_model=UpdateNGOResponse
)
def update_basic_info(
    data: UpdateNGOBasicInfo,
    current_ngo: NGOInfo = Depends(get_current_ngo),
    db: Session = Depends(get_db),
):
    try:
        return update_ngo_basic_info(
            session=db,
            current_ngo=current_ngo,
            data=data,
        )
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

@router.patch(
    "/contact-info",
    response_model=UpdateNGOResponse
)
def update_contact_info(
    data: UpdateContactInfo,
    current_ngo: NGOInfo = Depends(get_current_ngo),
    db: Session = Depends(get_db),
):
    try:
        return update_ngo_contact_info(
            session=db,
            current_ngo=current_ngo,
            data=data,
        )
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

@router.patch(
    "/owner-info",
    response_model=UpdateNGOResponse
)
def update_owner_info(
    data: updateNGOOwnerInfo,
    current_ngo: NGOInfo = Depends(get_current_ngo),
    db: Session = Depends(get_db),
):
    try:
        return update_ngo_owner_info(
            session=db,
            current_ngo=current_ngo,
            data=data,
        )
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
@router.patch(
    "/location-info",
    response_model=UpdateNGOResponse
)
def update_location(
    data: UpdateNGOLocationData,
    current_ngo: NGOInfo = Depends(get_current_ngo),
    db: Session = Depends(get_db),
):
    try:
        return update_ngo_location_info(
            session=db,
            current_ngo=current_ngo,
            data=data,
        )
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

@router.patch("/map-info", response_model=UpdateNGOResponse)
def update_map(
    data: UpdateNGOMapInfo,
    current_ngo: NGOInfo = Depends(get_current_ngo),
    db: Session = Depends(get_db),
):
    try:
        return update_map_info(
            session=db,
            current_ngo=current_ngo,
            data=data,
        )
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e),
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

