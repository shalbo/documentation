from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.city_services import list_cities
from app.db import get_db

router = APIRouter(prefix="/cities", tags=["cities"])


@router.get("")
def get_cities(
    region: str | None = Query(
        default=None,
        pattern=r"^(West|East|South)$",
        description="Filter by region: West, East, or South",
    ),
    db: Session = Depends(get_db),
):
    data = list_cities(db, region=region)
    return {
        "data": data,
        "meta": {
            "total": len(data),
            "region": region,
        },
    }
