from fastapi import FastAPI
from routers.auth import router as auth_routher 
from routers.reports import router as reports_routher

from database.base import Base
from database.database import engine
from models.user import User
from routers.ngo import router as ngo_routher

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