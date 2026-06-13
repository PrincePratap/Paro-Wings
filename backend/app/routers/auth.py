
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependency  import get_db
from app.schemas.userschemas import UserCreate
from app.models.user import User 
from app.models.otp import OTPVerification

from app.schemas.otp import SendOTPRequest , VerifyOTPRequest
from app.service.email_service import send_otp_email  
from fastapi import HTTPException
from datetime import datetime, timedelta

from app.models.otp import OTPVerification
from app.utils.otp_generator import generate_otp
from datetime import datetime
from fastapi import HTTPException

from app.models.otp import OTPVerification
from app.utils.jwt import create_access_token
from app.schemas.otp import LoginRequest




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
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        password_hash=user.password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User Created"
    }

@router.post("/send-otp")
async def send_otp(
    data: SendOTPRequest,
    db: Session = Depends(get_db)
):

    email = data.email

    otp = generate_otp()

    existing_otp = (
        db.query(OTPVerification)
        .filter(OTPVerification.email == email)
        .first()
    )

    if existing_otp:

        existing_otp.otp = otp
        existing_otp.created_at = datetime.utcnow()
        existing_otp.expires_at = datetime.utcnow() + timedelta(minutes=5)

    else:

        otp_record = OTPVerification(
            email=email,
            otp=otp,
            expires_at=datetime.utcnow() + timedelta(minutes=5)
        )

        db.add(otp_record)

    db.commit()

    await send_otp_email(email, otp)

    return {
        "success": True,
        "message": "OTP sent successfully"
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

    return {
        "success": True,
        "message": "OTP verified successfully"
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