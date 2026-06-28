# routers/training_animals.py

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.dependency import get_db
from app.models.training import TrainingAnimal
from app.schemas.training import (
    TrainingAnimalCreate,
    TrainingAnimalUpdate,
    TrainingAnimalResponse,
)

router = APIRouter(
    prefix="/training/animals",
    tags=["Training Animals"],
)

@router.post("", response_model=TrainingAnimalResponse)
def create_training_animal(
    request: TrainingAnimalCreate,
    db: Session = Depends(get_db)
):
    animal = db.query(TrainingAnimal).filter(
        TrainingAnimal.name == request.name
    ).first()

    if animal:
        raise HTTPException(
            status_code=400,
            detail="Animal already exists."
        )

    animal = TrainingAnimal(
        name=request.name,
        icon=request.icon
    )

    db.add(animal)
    db.commit()
    db.refresh(animal)

    return animal

@router.get("", response_model=list[TrainingAnimalResponse])
def get_training_animals(
    db: Session = Depends(get_db)
):
   return (
    db.query(TrainingAnimal)
    .filter(TrainingAnimal.is_active.is_(True))
    .order_by(TrainingAnimal.name)
    .all()
)

@router.get("/{animal_id}", response_model=TrainingAnimalResponse)
def get_training_animal(
    animal_id: UUID,
    db: Session = Depends(get_db)
):
    animal = db.query(TrainingAnimal).filter(
        TrainingAnimal.id == animal_id
    ).first()

    if not animal:
        raise HTTPException(404, "Animal not found.")

    return animal

@router.put("/{animal_id}", response_model=TrainingAnimalResponse)
def update_training_animal(
    animal_id: UUID,
    request: TrainingAnimalUpdate,
    db: Session = Depends(get_db)
):
    animal = db.query(TrainingAnimal).filter(
        TrainingAnimal.id == animal_id
    ).first()

    if not animal:
        raise HTTPException(404, "Animal not found.")

    animal.name = request.name
    animal.icon = request.icon
    animal.is_active = request.is_active

    db.commit()
    db.refresh(animal)

    return animal


@router.delete("/{animal_id}")
def delete_training_animal(
    animal_id: UUID,
    db: Session = Depends(get_db)
):
    animal = db.query(TrainingAnimal).filter(
        TrainingAnimal.id == animal_id
    ).first()

    if not animal:
        raise HTTPException(404, "Animal not found.")

    animal.is_active = False

    db.commit()

    return {
        "message": "Training animal deleted successfully."
    }