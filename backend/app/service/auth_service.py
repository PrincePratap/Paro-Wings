import logging
from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
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

logger = logging.getLogger(__name__)

OTP_TTL_MINUTES = 5


def success_response(message: str, data: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    return {"success": True, "message": message, "data": data or {}}


def error_response(message: str) -> dict[str, Any]:
    return {"success": False, "message": message}


def find_user_by_email(session: Session, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    result = session.execute(statement)
    return result.scalar_one_or_none()


def find_user_by_phone(session: Session, phone: str) -> Optional[User]:
    statement = select(User).where(User.phone == phone)
    result = session.execute(statement)
    return result.scalar_one_or_none()


def find_user_by_id(session: Session, user_id: UUID) -> Optional[User]:
    return session.get(User, user_id)


def generate_testing_otp() -> str:
    """Testing only. Remove before production."""
    return "123456"


def generate_pending_user_id() -> str:
    return str(uuid4())


def store_otp(session: Session, email: str, otp: str) -> OTPVerification:
    statement = select(OTPVerification).where(OTPVerification.email == email)
    result = session.execute(statement)
    otp_record = result.scalar_one_or_none()

    expires_at = datetime.utcnow() + timedelta(minutes=OTP_TTL_MINUTES)

    if otp_record is None:
        otp_record = OTPVerification(
            email=email,
            otp=otp,
            expires_at=expires_at,
        )
        session.add(otp_record)
    else:
        otp_record.otp = otp
        otp_record.created_at = datetime.utcnow()
        otp_record.expires_at = expires_at

    try:
        session.commit()
        session.refresh(otp_record)
    except Exception:
        session.rollback()
        raise

    return otp_record


def verify_otp(session: Session, email: str, otp: str) -> OTPVerification:
    statement = select(OTPVerification).where(OTPVerification.email == email)
    result = session.execute(statement)
    otp_record = result.scalar_one_or_none()

    if otp_record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OTP not found")

    if otp_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP expired")

    if otp_record.otp != otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")

    return otp_record


def delete_otp(session: Session, email: str, *, commit: bool = True) -> None:
    statement = select(OTPVerification).where(OTPVerification.email == email)
    result = session.execute(statement)
    otp_record = result.scalar_one_or_none()

    if otp_record is None:
        return

    session.delete(otp_record)
    if commit:
        try:
            session.commit()
        except Exception:
            session.rollback()
            raise


def create_user(
    session: Session,
    *,
    full_name: str,
    email: str,
    phone: str,
    password: str,
    commit: bool = True,
) -> User:
    user = User(
        full_name=full_name,
        email=email,
        phone=phone,
        password_hash=hash_password(password),
    )
    session.add(user)

    if commit:
        try:
            session.commit()
            session.refresh(user)
        except Exception:
            session.rollback()
            raise

    return user


def generate_jwt(user: User) -> str:
    return create_access_token({"sub": str(user.id), "email": user.email})


def serialize_user(user: User) -> dict[str, Any]:
    return {
        "id": str(user.id),
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role.value if user.role else None,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


def get_current_user(request: Request, session: Session = Depends(get_db)) -> User:
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")

    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.") from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")

    user = find_user_by_id(session, UUID(str(user_id)))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return user


async def register_user(session: Session, user_data: UserCreate) -> dict[str, Any]:
    logger.info("Registration started")

    full_name = user_data.full_name.strip()
    email = str(user_data.email).strip().lower()
    phone = user_data.phone.strip()

    if find_user_by_email(session, email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    if find_user_by_phone(session, phone):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone already registered")

    otp = generate_testing_otp()
    store_otp(session, email, otp)
    logger.info("OTP generated")

    # try:
    #     await send_otp_email(email, otp)
    # except Exception:
    #     logger.warning("OTP email delivery failed; continuing in testing mode")

    try:
        user = create_user(
            session,
            full_name=full_name,
            email=email,
            phone=phone,
            password=user_data.password,
            commit=False,
        )
        session.commit()
        session.refresh(user)
    except Exception:
        session.rollback()
        raise

    return success_response("OTP sent successfully", {"user_id": str(user.id)})


def verify_and_create_user(session: Session, data: VerifyOTPRequest) -> dict[str, Any]:
    otp = data.otp.strip()
    user = find_user_by_id(session, data.user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pending user not found")

    verify_otp(session, user.email, otp)

    try:
        user.is_verified = True
        delete_otp(session, user.email, commit=False)
        session.commit()
        session.refresh(user)
    except Exception:
        session.rollback()
        raise

    logger.info("User verified")
    token = generate_jwt(user)
    return success_response(
        "OTP verified successfully.",
        {
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "token": token,
        },
    )


def authenticate_user(session: Session, data: LoginRequest) -> dict[str, Any]:
    email = str(data.email).strip().lower()
    user = find_user_by_email(session, email)

    if not user:
        logger.warning("Login failed: user not found")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not verify_password(data.password, user.password_hash):
        logger.warning("Login failed: invalid password")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = generate_jwt(user)
    logger.info("Login success")
    response = success_response("Login successful", {"token": token, "user": serialize_user(user)})
    # response["access_token"] = token
    # response["token_type"] = "bearer"
    # response["user"] = serialize_user(user)
    return response


def google_login_user(session: Session, data: GoogleLoginRequest) -> dict[str, Any]:
    email = str(data.email).strip().lower()
    user = find_user_by_email(session, email)

    if not user:
        logger.info("Creating user from Google login")
        try:
            user = create_user(
                session,
                full_name=data.full_name.strip(),
                email=email,
                phone="",
                password="GOOGLE_AUTH",
                commit=False,
            )
            session.commit()
            session.refresh(user)
        except Exception:
            session.rollback()
            raise

    token = generate_jwt(user)
    logger.info("Google login success")
    response = success_response("Google login successful", {"token": token, "user": serialize_user(user)})
    response["access_token"] = token
    response["token_type"] = "bearer"
    response["user"] = serialize_user(user)
    return response
