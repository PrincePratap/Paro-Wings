from fastapi import FastAPI
from app.routers.auth import router as auth_routher 

from app.database.base import Base
from app.database.database import engine
from app.models.user import User

app = FastAPI(
    title="Paro Wings API",
    version="1.0.0"
)

app.include_router(auth_routher)

@app.get("/")
def root():
    return {
        "message": "Welcome to Paro Wings"
    }

Base.metadata.create_all(bind=engine)