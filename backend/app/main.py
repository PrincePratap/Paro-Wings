from fastapi import FastAPI
from routers.auth import router as auth_routher 
from routers.reports import router as reports_routher

from database.base import Base
from database.database import engine
from models.user import User
from routers.ngo import router as ngo_routher
from routers.adoption import router as adoption_router
from routers.my_animal import router as my_animal_router
from routers.training import router as training_animals_router


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



@app.get("/")
def root():
    return {
        "message": "Welcome to Paro Wings"
    }

Base.metadata.create_all(bind=engine)