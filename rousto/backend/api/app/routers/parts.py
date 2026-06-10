from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.i18n import resolve_locale
from app.models import User
from app.vin_compat_services import normalize_vin_prefix
from app.vin_decoder_services import decode_vin
from app.parts_services import (
    create_warranty_claim,
    get_part_detail,
    list_booking_parts,
    list_part_categories,
    search_parts,
)
from app.rate_limit import check_rate_limit
from app.services import load_booking

router = APIRouter(tags=["parts"])


class WarrantyClaimIn(BaseModel):
    booking_part_id: UUID
    description: str = Field(min_length=5, max_length=2000)


@router.get("/parts/categories")
def get_part_categories(
    locale: str = Depends(resolve_locale),
    db: Session = Depends(get_db),
):
    data = list_part_categories(db, locale)
    return {"data": data, "meta": {"total": len(data), "locale": locale}}


@router.get("/parts/search")
def search_parts_catalog(
    request: Request,
    q: str | None = Query(default=None, max_length=80),
    category: str | None = Query(default=None),
    category_id: UUID | None = Query(default=None),
    make: str | None = Query(default=None, max_length=40),
    model: str | None = Query(default=None, max_length=40),
    car_year_id: UUID | None = Query(default=None),
    oem: str | None = Query(default=None, max_length=60),
    vin: str | None = Query(default=None, max_length=17),
    oem_only: bool = Query(default=False),
    in_stock_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=100),
    locale: str = Depends(resolve_locale),
    db: Session = Depends(get_db),
):
    if not any([q, category, category_id, make, model, car_year_id, oem, vin]):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "QUERY_REQUIRED",
                "message": "أدخل نص بحث أو فئة أو مركبة أو رقم OEM أو VIN",
            },
        )
    if vin:
        try:
            normalize_vin_prefix(vin)
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail={"code": "INVALID_VIN", "message": str(exc)},
            ) from exc
    check_rate_limit(request, suffix="parts_search", limit=60)
    data = search_parts(
        db,
        query=q,
        category=category,
        category_id=category_id,
        make=make,
        model=model,
        car_year_id=car_year_id,
        oem=oem,
        vin=vin,
        oem_only=oem_only,
        in_stock_only=in_stock_only,
        locale=locale,
        limit=limit,
    )
    vehicle = None
    if vin:
        try:
            vehicle = decode_vin(db, vin)
        except ValueError:
            vehicle = None

    return {
        "data": data,
        "meta": {
            "total": len(data),
            "locale": locale,
            "query": q,
            "car_year_id": str(car_year_id) if car_year_id else None,
            "in_stock_only": in_stock_only,
            "vin_prefix": normalize_vin_prefix(vin) if vin else None,
            "strict_vin_match": bool(vin),
            "decoded_vehicle": vehicle,
        },
    }


@router.get("/parts/{part_id}")
def get_part(
    part_id: UUID,
    locale: str = Depends(resolve_locale),
    db: Session = Depends(get_db),
):
    data = get_part_detail(db, part_id, locale)
    if not data:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "القطعة غير موجودة"},
        )
    return {"data": data}


@router.get("/bookings/{booking_id}/parts")
def get_booking_parts(
    booking_id: UUID,
    locale: str = Depends(resolve_locale),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = load_booking(db, booking_id, user.id)
    if not booking:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "الحجز غير موجود"},
        )
    data = list_booking_parts(db, booking_id, locale)
    return {"data": data, "meta": {"total": len(data)}}


@router.post("/parts/warranty-claims", status_code=201)
def post_warranty_claim(
    body: WarrantyClaimIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        claim = create_warranty_claim(
            db,
            user_id=user.id,
            booking_part_id=body.booking_part_id,
            description=body.description,
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "CLAIM_ERROR", "message": str(exc)},
        ) from exc
    return {
        "data": {
            "id": claim.id,
            "status": claim.status,
            "booking_part_id": claim.booking_part_id,
        }
    }
