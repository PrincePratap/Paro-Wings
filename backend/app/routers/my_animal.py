from fastapi import APIRouter, Depends,HTTPException, status
from sqlalchemy.orm import Session

from database.dependency import get_db
from models.my_animal import MyAnimal
from schemas.my_animal import MyAnimalCreate, MyAnimalResponse , MyAnimalUpdate
from typing import List
from uuid import UUID




router = APIRouter(
    prefix="/animals",
    tags=["My Animals"],
)


@router.post("/create", response_model=MyAnimalResponse)
def create_my_animal(
    data: MyAnimalCreate,
    db: Session = Depends(get_db),
):
    animal = MyAnimal(**data.model_dump())

    db.add(animal)
    db.commit()
    db.refresh(animal)

    return animal

@router.get(
    "/my",
    response_model=List[MyAnimalResponse],
    summary="Get My Animals",
    description="Get all animals belonging to a user."
)
def get_my_animals(
    owner_id: str,
    db: Session = Depends(get_db),
):
    animals = (
        db.query(MyAnimal)
        .filter(MyAnimal.owner_id == owner_id)
        .order_by(MyAnimal.created_at.desc())
        .all()
    )

    return animals

@router.get(
    "/{animal_id}",
    response_model=MyAnimalResponse,
    summary="Get Animal Details"
)
def get_animal(
    animal_id: UUID,
    db: Session = Depends(get_db),
):
    animal = (
        db.query(MyAnimal)
        .filter(MyAnimal.id == animal_id)
        .first()
    )

    if not animal:
        raise HTTPException(
            status_code=404,
            detail="Animal not found."
        )

    return animal

@router.put(
    "/{animal_id}",
    response_model=MyAnimalResponse,
    summary="Update Animal"
)
def update_animal(
    animal_id: UUID,
    data: MyAnimalUpdate,
    db: Session = Depends(get_db),
):
    animal = (
        db.query(MyAnimal)
        .filter(MyAnimal.id == animal_id)
        .first()
    )

    if not animal:
        raise HTTPException(
            status_code=404,
            detail="Animal not found."
        )

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(animal, key, value)

    db.commit()
    db.refresh(animal)

    return animal

@router.delete(
    "/{animal_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Animal",
    description="Delete an animal by its ID."
)
def delete_animal(
    animal_id: UUID,
    db: Session = Depends(get_db),
):
    animal = (
        db.query(MyAnimal)
        .filter(MyAnimal.id == animal_id)
        .first()
    )

    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Animal not found."
        )

    db.delete(animal)
    db.commit()

    return {
        "message": "Animal deleted successfully."
    }