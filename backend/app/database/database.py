from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os


DATABASE_URL = "postgresql://postgres:cody2002@localhost:5432/paro_wings"
DATABASE_URL = os.getenv("DATABASE_URL")


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)