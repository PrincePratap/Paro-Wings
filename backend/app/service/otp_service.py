import random
from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy.orm import Session

from models.otp import OTPVerification
from schemas.otp import SendOTPRequest
from service.email_service import send_otp_email


def generate_otp():
    return str(random.randint(100000, 999999))


def generate_pending_user_id() -> str:
    return str(uuid4())


async def send_otp(
        data: SendOTPRequest,
        db: Session

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
        "message": "OTP sent successfully",
        "data": {
            "user_id": generate_pending_user_id()
        }
    }





