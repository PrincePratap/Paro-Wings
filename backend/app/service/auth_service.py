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





from models.ngo import NGOInfo
from schemas.ngo import  NGOOwnerRegisterRequest


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
    role: str,
    commit: bool = True,
) -> User:
    user = User(
        full_name=full_name,
        email=email,
        phone=phone,
        role = role,
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


def generate_account_token(*, subject: str, email: str, role: str, account_type: str) -> str:
    return create_access_token(
        {
            "sub": subject,
            "email": email,
            "role": role,
            "account_type": account_type,
        }
    )


def generate_jwt(user: User) -> str:
    role = user.role.value if getattr(user, "role", None) else "citizen"
    return generate_account_token(
        subject=str(user.id),
        email=user.email,
        role=role,
        account_type="user",
    )


def build_login_payload(
    *,
    account_id: str,
    email: str,
    name: str,
    phone: str,
    role: str,
    account_type: str,
) -> dict[str, Any]:
    return {
        "id": account_id,
        "name": name,
        "email": email,
        "phone": phone,
        "role": role,
        "account_type": account_type,
        "access_token": "",
        "token_type": "bearer",
    }


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


def serialize_user_login(user: User) -> dict[str, Any]:
    return build_login_payload(
        account_id=str(user.id),
        email=user.email,
        name=user.full_name,
        phone=user.phone,
        role=user.role.value if getattr(user, "role", None) else "citizen",
        account_type="user",
    )


def serialize_ngo_login(ngo: NGOInfo) -> dict[str, Any]:
    return build_login_payload(
        account_id=str(ngo.id),
        email=ngo.email or "",
        name=ngo.name,
        phone=ngo.phone or "",
        role="ngo_admin",
        account_type="ngo",
    )


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
    role_name = str(user_data.role.value if getattr(user_data.role, "value", None) is not None else user_data.role)

    if find_user_by_email(session, email) or find_ngo_by_email(session, email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    if find_user_by_phone(session, phone):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone already registered")

    otp = generate_testing_otp()
    store_otp(session, email, otp)
    logger.info("OTP generated")

    if role_name == "ngo_admin":
        ngo = create_ngo_account(
            session,
            full_name=full_name,
            email=email,
            phone=phone,
            password=user_data.password,
            ngo_name=user_data.ngo_name.strip() if user_data.ngo_name else full_name,
            commit=False,
        )
        session.commit()
        session.refresh(ngo)
        return success_response("OTP sent successfully.", {"id": str(ngo.id), "role": role_name})

    try:
        user = create_user(
            session,
            full_name=full_name,
            email=email,
            phone=phone,
            password=user_data.password,
            role=role_name,
            commit=False,
        )
        session.commit()
        session.refresh(user)
    except Exception:
        session.rollback()
        raise

    return success_response("OTP sent successfully.", {"id": str(user.id), "role": role_name})





def verify_and_create_user(session: Session, data: VerifyOTPRequest) -> dict[str, Any]:
    otp = data.otp.strip()
    role_name = (data.role or "").strip().lower()

    if role_name == "ngo_admin" or data.ngo_id is not None:
        ngo = find_ngo_by_id(session, data.ngo_id) if data.ngo_id is not None else None
        if ngo is None and data.user_id is not None:
            ngo = find_ngo_by_id(session, data.user_id)
        if ngo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pending NGO not found")

        verify_otp(session, ngo.email, otp)

        try:
            ngo.is_verified = True
            delete_otp(session, ngo.email, commit=False)
            session.commit()
            session.refresh(ngo)
        except Exception:
            session.rollback()
            raise

        logger.info("NGO verified")
        token = generate_account_token(
            subject=str(ngo.id),
            email=ngo.email or "",
            role="ngo_admin",
            account_type="ngo",
        )
        return success_response(
            "OTP verified successfully.",
            {
                "id": str(ngo.id),
                "name": ngo.name,
                "email": ngo.email,
                "phone": ngo.phone,
                "role": "ngo_admin",
                "account_type": "ngo",
                "access_token": token,
                "token_type": "bearer",
            },
        )

    user = find_user_by_id(session, data.user_id) if data.user_id is not None else None
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
            "id": str(user.id),
            "name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role.value if user.role else None,
            "account_type": "user",
            "access_token": token,
            "token_type": "bearer",
        },
    )


def authenticate_user(session: Session, data: LoginRequest) -> dict[str, Any]:
    email = str(data.email).strip().lower()
    user = find_user_by_email(session, email)

    if user is not None:
        if not verify_password(data.password, user.password_hash):
            logger.warning("Login failed: invalid password for user")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        if not user.is_verified:
            logger.warning("Login failed: user account is not verified")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not verified")

        token = generate_jwt(user)
        login_payload = serialize_user_login(user)
        login_payload["access_token"] = token
        login_payload["token_type"] = "bearer"
        logger.info("User login success")
        return success_response("Login successful", login_payload)

    ngo = find_ngo_by_email(session, email)
    if ngo is not None:
        if not verify_password(data.password, ngo.password_hash):
            logger.warning("Login failed: invalid password for NGO")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        if not ngo.is_verified:
            logger.warning("Login failed: NGO account is not verified")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="NGO not verified")

        token = generate_account_token(
            subject=str(ngo.id),
            email=ngo.email or email,
            role="ngo_admin",
            account_type="ngo",
        )
        login_payload = serialize_ngo_login(ngo)
        login_payload["access_token"] = token
        login_payload["token_type"] = "bearer"
        logger.info("NGO login success")
        return success_response("Login successful", login_payload)

    logger.warning("Login failed: neither user nor NGO found")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


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


# NGO  




def serialize_ngo(
    ngo: NGOInfo
) -> dict[str, Any]:

    return {
        "id": str(ngo.id),
        "name": ngo.name,
        "email": ngo.email,
        "phone": ngo.phone,
        "city": ngo.city,
        "state": ngo.state,
        "status": ngo.status,
        "is_verified": ngo.is_verified,
        "is_active": ngo.is_active,
        "accepts_rescue_requests": ngo.accepts_rescue_requests,
        "created_at": ngo.created_at.isoformat()
    }





def find_ngo_by_email(
    session: Session,
    email: str
) -> Optional[NGOInfo]:

    statement = select(NGOInfo).where(
        NGOInfo.email == email
    )

    result = session.execute(statement)

    return result.scalar_one_or_none()


def find_ngo_by_id(session: Session, ngo_id: str | UUID) -> Optional[NGOInfo]:
    return session.get(NGOInfo, str(ngo_id))


def create_ngo_account(
    session: Session,
    *,
    full_name: str,
    email: str,
    phone: str,
    password: str,
    ngo_name: str,
    commit: bool = True,
) -> NGOInfo:
    ngo = NGOInfo(
        name=ngo_name,
        email=email,
        phone=phone,
        owner_name=full_name,
        owner_email=email,
        owner_phone=phone,
        password_hash=hash_password(password),
        status="pending",
        is_verified=False,
        is_active=True,
        accepts_rescue_requests=True,
    )
    session.add(ngo)

    if commit:
        try:
            session.commit()
            session.refresh(ngo)
        except Exception:
            session.rollback()
            raise

    return ngo


async def register_ngo_owner(
    session: Session,
    ngo_data: NGOOwnerRegisterRequest
) -> dict[str, Any]:

    logger.info("NGO Owner registration started")

    full_name = ngo_data.full_name.strip()
    email = str(ngo_data.email).strip().lower()
    phone = ngo_data.phone.strip()
    ngo_name = ngo_data.ngo_name.strip()

    if find_user_by_email(session, email) or find_ngo_by_email(session, email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    otp = generate_testing_otp()
    store_otp(session, email, otp)
    logger.info("OTP generated")

    try:
        ngo = create_ngo_account(
            session,
            full_name=full_name,
            email=email,
            phone=phone,
            password=ngo_data.password,
            ngo_name=ngo_name,
            commit=False,
        )
        session.commit()
        session.refresh(ngo)
    except Exception:
        session.rollback()
        raise

    return success_response(
        "OTP sent successfully",
        {
            "id": str(ngo.id),
            "role": "ngo_admin",
        },
    )

