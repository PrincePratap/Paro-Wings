
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.dependency  import get_db
from schemas.userschemas import UserCreate
from models.user import User 
from models.otp import OTPVerification

from schemas.otp import   VerifyOTPRequest
from fastapi import HTTPException
from datetime import datetime

from utils.jwt import create_access_token
from schemas.otp import LoginRequest
from schemas.otp import   SendOTPRequest
from service.otp_service import send_otp




router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.get("/")
def test_auth():
    return {
        "message": "Auth Router Working"
    }


@router.post("/register")
async def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )


    new_user = User(
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        password_hash=user.password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

  
    otp_response = await send_otp(
        SendOTPRequest(email=new_user.email),
        db
    )

    return {
        "message": "User Created",
        "otp": otp_response,
        "user": {
            "id": str(new_user.id),
            "email": new_user.email
        }
    }


@router.post("/verify-otp")
async def verify_otp(
    data: VerifyOTPRequest,
    db: Session = Depends(get_db)
):

    email = data.email
    otp = data.otp

    otp_record = (
        db.query(OTPVerification)
        .filter(OTPVerification.email == email)
        .first()
    )

    if not otp_record:
        raise HTTPException(
            status_code=404,
            detail="OTP not found"
        )

    if otp_record.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="OTP expired"
        )

    if otp_record.otp != otp:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    db.delete(otp_record)
    db.commit()


    token = create_access_token(
        {
            "sub": data.user_id,
            "email": data.email
        }
    )


    return {
        "success": True,
        "message": "OTP verified successfully",
        "bearer_token": token 
    }

@router.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if user.password_hash != data.password:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }