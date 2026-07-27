from typing import Optional , Any
from sqlalchemy import select
from sqlalchemy.orm import Session
from database.dependency import get_db
from models.ngo import NGOInfo
from utils.jwt import SECRET_KEY, ALGORITHM, create_access_token
from utils.security import hash_password, verify_password

from models.volunteer import Volunteer
from utils.jwt import SECRET_KEY, ALGORITHM, create_access_token
from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from database.dependency import get_db
from models.volunteer import Volunteer
from service.auth_service import generate_testing_otp, store_otp, success_response, error_response
from schemas.volunteer import (
     VolunteerLoginRequest,
     VolunteerRegisterRequest
     )
import logging
from schemas.otp import LoginRequest, VerifyOTPRequest
from service.auth_service import verify_otp ,delete_otp




logger = logging.getLogger(__name__)




def find_volunteer_by_email(
    session: Session,
    email: str
) -> Optional[Volunteer]:

    statement = select(Volunteer).where(
        Volunteer.email == email
    )

    result = session.execute(statement)

    return result.scalar_one_or_none()

def generate_volunteer_jwt(volunteer: Volunteer) -> str:
    return create_access_token(
        {
            "sub": str(volunteer.id),
            "email": volunteer.email,
            "type": "volunteer"
        }
    )
def find_volunteer_by_id(
    session: Session,
    volunteer_id: str
) -> Optional[Volunteer]:

    return session.query(Volunteer).filter(
        Volunteer.id == volunteer_id
    ).first()

def get_current_volunteer(
    request: Request,
    session: Session = Depends(get_db)
) -> Volunteer:

    authorization = request.headers.get("Authorization")

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token."
        )

    token = authorization.split(" ", 1)[1].strip()

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token."
        ) from exc

    volunteer_id = payload.get("sub")

    if not volunteer_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token."
        )

    volunteer = find_volunteer_by_id(session, str(volunteer_id))
    # If your Volunteer.id column is PostgreSQL UUID, use:
    # volunteer = find_volunteer_by_id(session, UUID(str(volunteer_id)))

    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found."
        )

    return volunteer

def authenticate_volunteer(
    session: Session,
    data: VolunteerLoginRequest
) -> dict[str, Any]:

    email = str(data.email).strip().lower()

    volunteer = find_volunteer_by_email(session, email)

    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not verify_password(data.password, volunteer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not volunteer.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email first."
        )

    token = generate_volunteer_jwt(volunteer)

    return success_response(
        "Login successful",
        {
            "volunteer_id": str(volunteer.id),
            "full_name": volunteer.full_name,
            "email": volunteer.email,
            "phone": volunteer.phone,
            "ngo_id": volunteer.ngo_id,
            "is_verified": volunteer.is_verified,
            "is_active": volunteer.is_active,
            "access_token": token,
            "token_type": "bearer"
        }
    )

def verify_and_create_volunteer(
    session: Session,
    data: VerifyOTPRequest
) -> dict[str, Any]:

    otp = data.otp.strip()

    volunteer = find_volunteer_by_id(session, str(data.volunteer_id))

    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending volunteer not found"
        )

    verify_otp(session, volunteer.email, otp)

    try:
        volunteer.is_verified = True

        delete_otp(
            session,
            volunteer.email,
            commit=False
        )

        session.commit()
        session.refresh(volunteer)

    except Exception:
        session.rollback()
        raise

    logger.info("Volunteer verified")

    token = generate_volunteer_jwt(volunteer)

    return success_response(
        "Volunteer verified successfully",
        {
            "volunteer_id": volunteer.id,
            "full_name": volunteer.full_name,
            "email": volunteer.email,
            "phone": volunteer.phone,
            "ngo_id": volunteer.ngo_id,
            "is_verified": volunteer.is_verified,
            "is_active": volunteer.is_active,
            "access_token": token,
            "token_type": "bearer"
        }
    )

async def register_volunteer(
    session: Session,
    volunteer_data: VolunteerRegisterRequest
) -> dict[str, Any]:

    logger.info("Volunteer registration started")

    full_name = volunteer_data.full_name.strip()
    email = str(volunteer_data.email).strip().lower()
    phone = volunteer_data.phone.strip()

    # Check if Volunteer email already exists
    if find_volunteer_by_email(session, email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Generate OTP
    otp = generate_testing_otp()

    store_otp(session, email, otp)

    logger.info("OTP generated")

    # Send Email (Production)
    # try:
    #     await send_otp_email(email, otp)
    # except Exception:
    #     logger.warning("OTP email delivery failed")

    try:

        volunteer = Volunteer(

            full_name=full_name,

            email=email,
            phone=phone,

            password_hash=hash_password(volunteer_data.password),

            is_verified=False,
            is_active=True

        )

        session.add(volunteer)
        session.commit()
        session.refresh(volunteer)

    except Exception:
        session.rollback()
        raise

    return success_response(
        "OTP sent successfully",
        {
            "volunteer_id": str(volunteer.id)
        }
    )