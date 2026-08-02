
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.dependency import get_db
from schemas.otp import LoginRequest, LoginResponse, VerifyOTPRequest, VerifyOTPResponse
from schemas.userschemas import GoogleLoginRequest, UserCreate, UserProfileResponse
from service.auth_service import (
    authenticate_user,
    get_current_user,
    google_login_user,
    register_user,
    verify_and_create_user,
)
import traceback


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.get("/")
def test_auth() -> dict[str, str]:
    return {"message": "Auth Router Working"}



@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)) -> dict:
    try:
        return await register_user(db, user)

    except HTTPException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.detail,
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


@router.post("/verify-otp", response_model=VerifyOTPResponse)
def verify_otp(data: VerifyOTPRequest, db: Session = Depends(get_db)) -> dict:
    try:
        return verify_and_create_user(db, data)
    except HTTPException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "message": exc.detail},
        )
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Internal server error"},
        )


@router.get("/me", response_model=UserProfileResponse)
def get_me(current_user=Depends(get_current_user)) -> dict:
    try:
        return {
            "success": True,
            "message": "User profile fetched successfully.",
            "data": {
                "id": current_user.id,
                "full_name": current_user.full_name,
                "email": current_user.email,
                "phone": current_user.phone,
                "role": current_user.role,
                "is_verified": current_user.is_verified,
                "created_at": current_user.created_at,
            },
        }
    except HTTPException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "message": exc.detail},
        )
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Internal server error"},
        )


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> dict:
    try:
        return authenticate_user(db, data)
    except HTTPException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "message": exc.detail},
        )
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Internal server error"},
        )


@router.post("/google-login")
def google_login(data: GoogleLoginRequest, db: Session = Depends(get_db)) -> dict:
    try:
        return google_login_user(db, data)
    except HTTPException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "message": exc.detail},
        )
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Internal server error"},
        )