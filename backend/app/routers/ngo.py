from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.dependency  import get_db
from models.ngo import NGOInFo 
from schemas.ngo import NGO as NgoRequest 

router = APIRouter(
    prefix="/ngo",
    tags=["NGO"]
)

@router.post("/register")
async def register_ngo(
    data: NgoRequest,
    db: Session = Depends(get_db)
):

    existing_email = (
        db.query(NGOInFo)
        .filter(NGOInFo.email == data.email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="NGO email already exists"
        )

    ngo = NGOInFo(
        id=str(uuid4()),

        name=data.name,
        email=data.email,
        phone=data.phone,

        owner_name=data.owner_name,
        owner_email=data.owner_email,
        owner_phone=data.owner_phone,

        address_line_1=data.address_line_1,
        address_line_2=data.address_line_2,
        landmark=data.landmark,

        city=data.city,
        district=data.district,
        state=data.state,
        country=data.country,
        postal_code=data.postal_code,

        latitude=data.latitude,
        longitude=data.longitude,

        website=str(data.website) if data.website else None,
        description=data.description,

        emergency_contact=data.emergency_contact,
        accepts_rescue_requests=data.accepts_rescue_requests
    )

    db.add(ngo)
    db.commit()
    db.refresh(ngo)

    return {
        "message": "NGO registered successfully",
        "ngo_id": ngo.id
    }


@router.get("/")
async def get_all_ngos(
    db: Session = Depends(get_db)
):
    ngos = db.query(NGOInFo).all()

    return [
        {
            "id": ngo.id,
            "name": ngo.name,
            "email": ngo.email,
            "phone": ngo.phone,
            "city": ngo.city,
            "state": ngo.state,
            "country": ngo.country,
            "latitude": ngo.latitude,
            "longitude": ngo.longitude,
            "accepts_rescue_requests": ngo.accepts_rescue_requests
        }
        for ngo in ngos
    ]  
   

@router.get("/{ngo_id}")
async def get_ngo(
    ngo_id: str,
    db: Session = Depends(get_db)
):
    ngo = db.query(NGOInFo).filter(
        NGOInFo.id == ngo_id
    ).first()

    if not ngo:
        raise HTTPException(
            status_code=404,
            detail="NGO not found"
        )

    return ngo