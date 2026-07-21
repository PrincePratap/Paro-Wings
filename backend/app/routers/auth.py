
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.dependency import get_db
from schemas.otp import LoginRequest, VerifyOTPRequest
from schemas.userschemas import GoogleLoginRequest, UserCreate
from service.auth_service import authenticate_user, google_login_user, register_user, verify_and_create_user

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
            content={"success": False, "message": exc.detail},
        )
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Internal server error"},
        )


@router.post("/verify-otp")
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


@router.post("/login")
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