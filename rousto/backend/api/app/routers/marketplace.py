from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.i18n import resolve_locale
from app.marketplace_services import (
    find_vendors_nearby_for_part,
    get_marketplace_home,
)
from app.parts_services import get_part_detail

router = APIRouter(tags=["marketplace"])


@router.get("/marketplace/home")
def marketplace_home(
    car_year_id: UUID | None = Query(default=None),
    locale: str = Depends(resolve_locale),
    db: Session = Depends(get_db),
):
    """Default bootstrap payload — spare parts marketplace first."""
    data = get_marketplace_home(db, locale, car_year_id=car_year_id)
    return {
        "data": data,
        "meta": {"locale": locale, "car_year_id": str(car_year_id) if car_year_id else None},
    }


@router.get("/parts/{part_id}/vendors-nearby")
def part_vendors_nearby(
    part_id: UUID,
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    limit: int = Query(default=20, ge=1, le=50),
    locale: str = Depends(resolve_locale),
    db: Session = Depends(get_db),
):
    if not get_part_detail(db, part_id, locale):
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "القطعة غير موجودة"},
        )
    data = find_vendors_nearby_for_part(
        db, part_id, lat=lat, lng=lng, locale=locale, limit=limit
    )
    return {
        "data": data,
        "meta": {"total": len(data), "part_id": str(part_id), "lat": lat, "lng": lng},
    }
