from fastapi import APIRouter, Depends , HTTPException
from uuid import UUID

from sqlalchemy.orm import Session

from database.dependency import get_db

from models.adoption import Adoption , AdoptionRequest

from schemas.adoption import AdoptionCreate,AdoptionRequestCreate,UpdateAdoptionRequestStatus

from typing import Optional
from fastapi import Query






router = APIRouter(
    tags=["Adoptions"]
)


@router.post("/adoptions")
def create_adoption(
    request: AdoptionCreate,
    db: Session = Depends(get_db)
):

    adoption = Adoption(**request.model_dump())

    db.add(adoption)
    db.commit()
    db.refresh(adoption)

    return adoption




@router.get("/adoptions")
def get_all_adoptions(
    city: Optional[str] = Query(None),
    animal_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):

    query = (
        db.query(Adoption)
        .filter(Adoption.adoption_status == "available")
    )

    if city:
        query = query.filter(
            Adoption.city.ilike(f"%{city}%")
        )

    if animal_type:
        query = query.filter(
            Adoption.animal_type.ilike(f"%{animal_type}%")
        )

    adoptions = (
        query.order_by(
            Adoption.created_at.desc()
        ).all()
    )

    return {
        "success": True,
        "message": "Adoptions fetched successfully",
        "total": len(adoptions),
        "data": adoptions
    }





@router.post("/adoption-requests")
def create_request(
    request: AdoptionRequestCreate,
    db: Session = Depends(get_db)
):
    adoption_request = AdoptionRequest(**request.model_dump())

    db.add(adoption_request)
    db.commit()
    db.refresh(adoption_request)

    return adoption_request


@router.get("/{adoption_id}")
def get_adoption_details(
    adoption_id: UUID,
    db: Session = Depends(get_db)
):

    adoption = (
        db.query(Adoption)
        .filter(Adoption.id == adoption_id)
        .first()
    )

    if not adoption:
        raise HTTPException(
            status_code=404,
            detail="Adoption not found"
        )

    return adoption





@router.get("/adoption-requests/{adoption_id}")
def get_adoption_requests(
    adoption_id: UUID,
    db: Session = Depends(get_db)
):

    adoption = (
        db.query(Adoption)
        .filter(Adoption.id == adoption_id)
        .first()
    )

    if not adoption:
        raise HTTPException(
            status_code=404,
            detail="Adoption not found"
        )

    requests = (
        db.query(AdoptionRequest)
        .filter(
            AdoptionRequest.animal_id == adoption_id
        )
        .order_by(
            AdoptionRequest.created_at.desc()
        )
        .all()
    )

    return {
        "adoption_id": adoption.id,
        "animal_name": adoption.animal_name,
        "owner_name": adoption.owner_name,
        "total_requests": len(requests),
        "requests": requests
    }

@router.put("/adoption-requests/{request_id}")
def update_request_status(
    request_id: UUID,
    data: UpdateAdoptionRequestStatus,
    db: Session = Depends(get_db)
):

    request = (
        db.query(AdoptionRequest)
        .filter(AdoptionRequest.id == request_id)
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    request.status = data.status

    if data.status == "approved":
        adoption = (
            db.query(Adoption)
            .filter(Adoption.id == request.animal_id)
            .first()
        )

        if adoption:
            adoption.adoption_status = "adopted"

    db.commit()

    return {
        "success": True,
        "message": f"Request {data.status} successfully",
        "status": request.status
    }


@router.delete("/adoptions/{adoption_id}")
def delete_adoption(
    adoption_id: UUID,
    db: Session = Depends(get_db)
):

    adoption = (
        db.query(Adoption)
        .filter(Adoption.id == adoption_id)
        .first()
    )

    if not adoption:
        raise HTTPException(
            status_code=404,
            detail="Adoption not found"
        )

    # Delete all adoption requests related to this adoption
    (
        db.query(AdoptionRequest)
        .filter(AdoptionRequest.animal_id == adoption_id)
        .delete()
    )

    db.delete(adoption)
    db.commit()

    return {
        "success": True,
        "message": "Adoption deleted successfully"
    }

@router.get("/adoptions/my/{owner_id}")
def get_my_adoptions(
    owner_id: UUID,
    db: Session = Depends(get_db)
):

    adoptions = (
        db.query(Adoption)
        .filter(Adoption.owner_id == owner_id)
        .order_by(Adoption.created_at.desc())
        .all()
    )

    return {
        "owner_id": owner_id,
        "total_posts": len(adoptions),
        "adoptions": adoptions
    }

