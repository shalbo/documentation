from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import HealthOut

router = APIRouter(tags=["health"])


@router.get("/health", response_model=dict)
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
        status = "ok"
    except Exception:
        db_status = "disconnected"
        status = "degraded"

    payload = HealthOut(status=status, database=db_status)
    return {"data": payload.model_dump()}
