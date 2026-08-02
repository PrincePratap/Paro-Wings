from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database.base import Base
from database.database import engine
from models.user import User
from routers.adoption import router as adoption_router
from routers.auth import router as auth_routher
from routers.my_animal import router as my_animal_router
from routers.ngo import router as ngo_routher
from routers.reports import router as reports_routher
from routers.training import router as training_animals_router
from routers.upload import router as upload_router
from routers.volunteer import router as volunteer
from routers.volunteer_request import router as volunteer_request_router


app = FastAPI(
    title="Paro Wings API",
    version="1.0.0"
)

app.include_router(auth_routher)
app.include_router(reports_routher)
app.include_router(ngo_routher)
app.include_router(adoption_router)
app.include_router(my_animal_router)
app.include_router(training_animals_router)
app.include_router(upload_router)
app.include_router(volunteer)
app.include_router(volunteer_request_router)




@app.get("/")
def root():
    return {
        "message": "Welcome to Paro Wings"
    }

Base.metadata.create_all(bind=engine)
