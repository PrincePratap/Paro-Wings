from fastapi import FastAPI
from app.routers.auth import router as auth_routher 
from app.routers.reports import router as reports_routher

from app.database.base import Base
from app.database.database import engine
from app.models.user import User
from app.routers.ngo import router as ngo_routher

app = FastAPI(
    title="Paro Wings API",
    version="1.0.0"
)

app.include_router(auth_routher)
app.include_router(reports_routher)
app.include_router(ngo_routher)


@app.get("/")
def root():
    return {
        "message": "Welcome to Paro Wings"
    }

Base.metadata.create_all(bind=engine)