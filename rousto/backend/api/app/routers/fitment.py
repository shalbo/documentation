from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.fitment_services import (
    car_year_out,
    list_makes,
    list_models,
    list_years,
    resolve_car_year,
)
from app.i18n import resolve_locale

router = APIRouter(prefix="/fitment", tags=["fitment"])


@router.get("/makes")
def get_makes(
    locale: str = Depends(resolve_locale),
    db: Session = Depends(get_db),
):
    data = list_makes(db, locale)
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/models")
def get_models(
    make_id: UUID = Query(...),
    locale: str = Depends(resolve_locale),
    db: Session = Depends(get_db),
):
    data = list_models(db, make_id, locale)
    return {"data": data, "meta": {"total": len(data), "make_id": str(make_id)}}


@router.get("/years")
def get_years(
    model_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    data = list_years(db, model_id)
    return {"data": data, "meta": {"total": len(data), "model_id": str(model_id)}}


@router.get("/resolve")
def resolve_fitment(
    car_year_id: UUID | None = Query(default=None),
    make: str | None = Query(default=None),
    model: str | None = Query(default=None),
    year: int | None = Query(default=None, ge=1980, le=2035),
    locale: str = Depends(resolve_locale),
    db: Session = Depends(get_db),
):
    cy = resolve_car_year(
        db,
        car_year_id=car_year_id,
        make_slug=make,
        model_slug=model,
        year=year,
    )
    if not cy:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "المركبة غير موجودة في الكتالوج"},
        )
    return {"data": car_year_out(cy, locale)}
