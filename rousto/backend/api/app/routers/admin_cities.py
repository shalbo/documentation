from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.city_services import (
    VALID_REGIONS,
    city_out,
    create_city,
    get_city_or_none,
    list_cities_admin,
    update_city,
)
from app.db import get_db
from app.deps import require_admin_key

router = APIRouter(prefix="/admin", tags=["admin-cities"])


class AdminCityCreate(BaseModel):
    name_ar: str = Field(min_length=2, max_length=80)
    name_en: str = Field(min_length=2, max_length=80)
    region: str = Field(pattern=r"^(West|East|South)$")
    is_active: bool = True


class AdminCityUpdate(BaseModel):
    name_ar: str | None = Field(default=None, min_length=2, max_length=80)
    name_en: str | None = Field(default=None, min_length=2, max_length=80)
    region: str | None = Field(default=None, pattern=r"^(West|East|South)$")
    is_active: bool | None = None


def _get_city_or_404(db: Session, city_id: UUID):
    city = get_city_or_none(db, city_id)
    if not city:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "المدينة غير موجودة"},
        )
    return city


@router.get("/cities")
def admin_list_cities(
    region: str | None = Query(default=None, pattern=r"^(West|East|South)$"),
    active: bool | None = Query(default=None),
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    if region and region not in VALID_REGIONS:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_REGION", "message": "إقليم غير صالح"},
        )
    data = list_cities_admin(db, region=region, active_only=active)
    return {"data": data, "meta": {"total": len(data), "region": region}}


@router.post("/cities", status_code=201)
def admin_create_city(
    body: AdminCityCreate,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    try:
        city = create_city(
            db,
            name_ar=body.name_ar,
            name_en=body.name_en,
            region=body.region,
            is_active=body.is_active,
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "VALIDATION_ERROR", "message": str(exc)},
        ) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail={"code": "DUPLICATE", "message": "اسم المدينة بالإنجليزية مستخدم مسبقاً"},
        ) from exc
    db.refresh(city)
    return {"data": city_out(city)}


@router.get("/cities/{city_id}")
def admin_get_city(
    city_id: UUID,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    city = _get_city_or_404(db, city_id)
    return {"data": city_out(city)}


@router.patch("/cities/{city_id}")
def admin_update_city(
    city_id: UUID,
    body: AdminCityUpdate,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    city = _get_city_or_404(db, city_id)
    updates = body.model_dump(exclude_unset=True)
    if not updates:
        return {"data": city_out(city)}
    try:
        update_city(db, city, **updates)
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "VALIDATION_ERROR", "message": str(exc)},
        ) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail={"code": "DUPLICATE", "message": "اسم المدينة بالإنجليزية مستخدم مسبقاً"},
        ) from exc
    db.refresh(city)
    return {"data": city_out(city)}
