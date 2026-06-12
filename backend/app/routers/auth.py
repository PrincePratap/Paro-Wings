
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependency  import get_db
from app.schemas.userschemas import UserCreate
from app.models.user import User


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