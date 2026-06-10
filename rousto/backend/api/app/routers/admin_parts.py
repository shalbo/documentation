from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.deps import require_admin_key
from app.i18n import resolve_locale
from app.models import Part, PartCategory
from app.parts_services import (
    attach_part_to_booking,
    create_part,
    list_parts_admin,
    list_warranty_claims_admin,
    part_out,
)
from app.logistics_services import load_booking_for_logistics

router = APIRouter(prefix="/admin", tags=["admin-parts"])


class PartCreateIn(BaseModel):
    part_number: str = Field(min_length=2, max_length=60)
    slug: str = Field(min_length=2, max_length=80)
    name_ar: str = Field(min_length=2, max_length=200)
    name_en: str | None = Field(default=None, max_length=200)
    category_id: UUID
    price_sar: float = Field(gt=0)
    supplier_id: UUID | None = None
    is_oem: bool = False
    warranty_months: int = Field(default=6, ge=1, le=36)
    vehicle_compatibility: list[dict] = Field(default_factory=list)
    oem_number: str | None = Field(default=None, max_length=60)
    vin_prefix: str | None = Field(default=None, max_length=11)


class PartPatchIn(BaseModel):
    name_ar: str | None = Field(default=None, max_length=200)
    price_sar: float | None = Field(default=None, gt=0)
    is_active: bool | None = None
    warranty_months: int | None = Field(default=None, ge=1, le=36)


class AttachPartIn(BaseModel):
    part_id: UUID
    vendor_id: UUID | None = None
    qty: int = Field(default=1, ge=1, le=20)


@router.get("/parts")
def admin_list_parts(
    locale: str = Depends(resolve_locale),
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    data = list_parts_admin(db, locale)
    return {"data": data, "meta": {"total": len(data)}}


@router.post("/parts", status_code=201)
def admin_create_part(
    body: PartCreateIn,
    locale: str = Depends(resolve_locale),
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    if not db.get(PartCategory, body.category_id):
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_CATEGORY", "message": "فئة غير موجودة"},
        )
    try:
        created = create_part(db, **body.model_dump())
        db.commit()
        part = db.scalar(
            select(Part)
            .options(joinedload(Part.category), joinedload(Part.supplier))
            .where(Part.id == created.id)
        )
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail={"code": "CREATE_ERROR", "message": str(exc)},
        ) from exc
    return {"data": part_out(part, locale, db=db)}


@router.patch("/parts/{part_id}")
def admin_patch_part(
    part_id: UUID,
    body: PartPatchIn,
    locale: str = Depends(resolve_locale),
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    part = db.get(Part, part_id)
    if not part:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "القطعة غير موجودة"},
        )
    if body.name_ar is not None:
        part.name_ar = body.name_ar
    if body.price_sar is not None:
        part.price_sar = body.price_sar
    if body.is_active is not None:
        part.is_active = body.is_active
    if body.warranty_months is not None:
        part.warranty_months = body.warranty_months
    db.commit()
    return {"data": part_out(part, locale, db=db)}


@router.get("/part-warranty-claims")
def admin_warranty_claims(
    status: str | None = Query(default=None),
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    data = list_warranty_claims_admin(db, status=status)
    return {"data": data, "meta": {"total": len(data)}}


@router.post("/bookings/{booking_id}/parts", status_code=201)
def admin_attach_booking_part(
    booking_id: UUID,
    body: AttachPartIn,
    locale: str = Depends(resolve_locale),
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    booking = load_booking_for_logistics(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "الحجز غير موجود"},
        )
    try:
        row = attach_part_to_booking(
            db,
            booking,
            part_id=body.part_id,
            vendor_id=body.vendor_id,
            qty=body.qty,
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "ATTACH_ERROR", "message": str(exc)},
        ) from exc
    return {
        "data": {
            "id": row.id,
            "part_id": row.part_id,
            "qty": row.qty,
            "unit_price_sar": float(row.unit_price_sar),
        }
    }
