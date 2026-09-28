from fastapi import APIRouter
from sqlalchemy import text
from app.database.connection import engine

router = APIRouter()

@router.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception:
        return {"status": "degraded", "database": "unavailable"}
