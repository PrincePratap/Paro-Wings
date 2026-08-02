from typing import Optional, Any
from uuid import UUID
import logging
import traceback


from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.dependency import get_db
from models.ngo import NGOInfo
from schemas.ngo import(
     UpdateNGOLocationRequest,
     NGOLoginRequest)
from utils.jwt import SECRET_KEY, ALGORITHM, create_access_token
from utils.security import hash_password, verify_password
from service.auth_service import (
    generate_account_token,
    generate_testing_otp,
    store_otp,
    success_response,
    error_response,
)
from passlib.context import CryptContext
from service.email_service import send_otp_email
from utils.jwt import ALGORITHM, SECRET_KEY, create_access_token
from utils.security import hash_password, verify_password
import logging
from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.dependency import get_db
from models.otp import OTPVerification
from models.user import User
from schemas.otp import LoginRequest, VerifyOTPRequest
from schemas.userschemas import GoogleLoginRequest, UserCreate
from service.email_service import send_otp_email
from utils.jwt import ALGORITHM, SECRET_KEY, create_access_token
from utils.security import hash_password, verify_password
from service.auth_service import verify_otp ,delete_otp


from models.volunteer_request import VolunteerRequest
from schemas.volunteer_request import (
    VolunteerRequestActionRequest,
    VolunteerRequestAction,
)
from service.auth_service import success_response
from models.ngo import NGOInfo
from models.volunteer import Volunteer
from models.volunteer_request import VolunteerRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



logger = logging.getLogger(__name__)


def find_ngo_by_email(
    session: Session,
    email: str
) -> Optional[NGOInfo]:

    statement = select(NGOInfo).where(
        NGOInfo.email == email
    )

    result = session.execute(statement)

    return result.scalar_one_or_none()

def serialize_ngo(ngo: NGOInfo) -> dict:
    return {
        "ngo_id": ngo.id,
        "ngo_name": ngo.name,
        "owner_name": ngo.owner_name,
        "owner_email": ngo.owner_email,
        "owner_phone": ngo.owner_phone,
        "total_volunteers": ngo.total_volunteers,
        "is_verified": ngo.is_verified,
        "is_active": ngo.is_active
    }



def generate_ngo_jwt(ngo: NGOInfo) -> str:
    return generate_account_token(
        subject=str(ngo.id),
        email=ngo.email or "",
        role="ngo_admin",
        account_type="ngo",
    )


def find_ngo_by_id(
    session: Session,
    ngo_id: str
) -> Optional[NGOInfo]:

    return session.query(NGOInfo).filter(
        NGOInfo.id == ngo_id
    ).first()


def update_ngo_info(
    session: Session,
    current_ngo: NGOInfo,
    data: dict
):
    ngo = session.query(NGOInfo).filter(
        NGOInfo.id == current_ngo.id
    ).first()

    if ngo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NGO not found."
        )

    for key, value in data.items():
        if hasattr(ngo, key):
            setattr(ngo, key, value)

    session.commit()
    session.refresh(ngo)

    return {
        "success": True,
        "message": "NGO information updated successfully.",
        "data": serialize_ngo(ngo)
    }




def get_current_ngo(
    request: Request,
    session: Session = Depends(get_db)
) -> NGOInfo:
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

    ngo_id = payload.get("sub")

    if not ngo_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token."
        )

    ngo = find_ngo_by_id(session, str(ngo_id))
    # If your NGO id column is PostgreSQL UUID, use:
    # ngo = find_ngo_by_id(session, UUID(str(ngo_id)))

    if not ngo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NGO not found."
        )

    return ngo

def login_ngo(
    session: Session,
    data: NGOLoginRequest
):
    ngo = session.query(NGOInfo).filter(
        NGOInfo.email == data.email.lower().strip()
    ).first()

    if not ngo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NGO not found."
        )

    if not ngo.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please verify your email first."
        )

    if not pwd_context.verify(data.password, ngo.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    token = generate_ngo_jwt(ngo)

    return {
        "success": True,
        "message": "Login successful.",
        "data": {
            "ngo_id": ngo.id,
            "ngo_name": ngo.name,
            "owner_name": ngo.owner_name,
            "owner_email": ngo.owner_email,
            "owner_phone": ngo.owner_phone,
            "total_volunteers": ngo.total_volunteers,
            "access_token": token,
            "token_type": "bearer"
        }
    }

def authenticate_ngo(
    session: Session,
    data: NGOLoginRequest
) -> dict[str, Any]:

    email = str(data.email).strip().lower()

    ngo = find_ngo_by_email(session, email)

    if not ngo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not verify_password(data.password, ngo.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not ngo.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email first."
        )

    token = generate_ngo_jwt(ngo)

    return success_response(
    "Login successful",
    {
        "ngo_id": str(ngo.id),
        "ngo_name": ngo.name,
        "owner_name": ngo.owner_name,
        "owner_email": ngo.owner_email,
        "owner_phone": ngo.owner_phone,
        "total_volunteers": ngo.total_volunteers,
        "access_token": token,
        "token_type": "bearer"
    }
)

def verify_and_create_ngo(
    session: Session,
    data: VerifyOTPRequest
) -> dict[str, Any]:

    otp = data.otp.strip()

    ngo = find_ngo_by_id(session, str(data.ngo_id))

    if not ngo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending NGO not found"
        )

    verify_otp(session, ngo.email, otp)

    try:
        ngo.is_verified = True

        delete_otp(
            session,
            ngo.email,
            commit=False
        )

        session.commit()
        session.refresh(ngo)

    except Exception:
        session.rollback()
        raise

    logger.info("NGO verified")

    token = generate_ngo_jwt(ngo)

    return success_response(
    "Login successful",
    {
        "ngo_id": ngo.id,
        "ngo_name": ngo.name,
        "owner_name": ngo.owner_name,
        "owner_email": ngo.owner_email,
        "owner_phone": ngo.owner_phone,
        "total_volunteers": ngo.total_volunteers,
        "is_verified": ngo.is_verified,
        "is_active": ngo.is_active,
        "access_token": token
    }
)

def get_volunteer_requests(
    session: Session,
    current_ngo: NGOInfo
) -> dict[str, Any]:

    requests = (
        session.query(VolunteerRequest)
        .filter(
            VolunteerRequest.ngo_id == current_ngo.id,
            VolunteerRequest.status == "pending"
        )
        .order_by(VolunteerRequest.created_at.desc())
        .all()
    )

    data = []

    for request in requests:
        data.append({
            "request_id": request.id,
            "volunteer_id": request.volunteer_id,
            "volunteer_name": request.volunteer_name,
            "volunteer_email": request.volunteer_email,
            "volunteer_phone": request.volunteer_phone,
            "ngo_id": request.ngo_id,
            "ngo_name": request.ngo_name,
            "message": request.message,
            "experience": request.experience,
            "available_days": request.available_days,
            "preferred_role": request.preferred_role,
            "status": request.status,
            "created_at": request.created_at
        })

    return success_response(
        "Volunteer requests fetched successfully.",
        data
    )

def manage_volunteer_request_service(
    session: Session,
    current_ngo: NGOInfo,
    request_id: str,
    body: VolunteerRequestActionRequest,
):
    # Find request
    volunteer_request = (
        session.query(VolunteerRequest)
        .filter(VolunteerRequest.id == request_id)
        .first()
    )

    if not volunteer_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer request not found."
        )

    # Verify request belongs to current NGO
    if volunteer_request.ngo_id != current_ngo.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to perform this action."
        )

    # Request already processed
    if volunteer_request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request is already {volunteer_request.status}."
        )

    # Find volunteer
    volunteer = (
        session.query(Volunteer)
        .filter(Volunteer.id == volunteer_request.volunteer_id)
        .first()
    )

    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found."
        )

    # Approve
    if body.action == VolunteerRequestAction.APPROVE:

        volunteer_request.status = "approved"

        volunteer.ngo_id = current_ngo.id

        current_ngo.total_volunteers += 1

        message = "Volunteer request approved successfully."

    # Reject
    else:

        volunteer_request.status = "rejected"
        volunteer_request.rejection_reason = body.rejection_reason

        message = "Volunteer request rejected successfully."

    volunteer_request.reviewed_by = current_ngo.id
    volunteer_request.reviewed_at = datetime.utcnow()

    session.commit()
    session.refresh(volunteer_request)

    return success_response(
        message,
        {
            "request_id": str(volunteer_request.id),
            "status": volunteer_request.status
        }
    )






