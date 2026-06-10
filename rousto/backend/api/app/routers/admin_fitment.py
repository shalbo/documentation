from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_admin_key
from app.fitment_services import add_part_compatibility, list_part_compatibilities
from app.i18n import resolve_locale

router = APIRouter(prefix="/admin", tags=["admin-fitment"])


class CompatibilityIn(BaseModel):
    car_year_id: UUID
    fitment_note_ar: str | None = Field(default=None, max_length=200)


class PartOemPatchIn(BaseModel):
    oem_number: str | None = Field(default=None, max_length=60)
    vin_prefix: str | None = Field(default=None, max_length=11)


@router.get("/parts/{part_id}/compatibilities")
def admin_list_compatibilities(
    part_id: UUID,
    locale: str = Depends(resolve_locale),
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    data = list_part_compatibilities(db, part_id, locale)
    return {"data": data, "meta": {"total": len(data)}}


@router.post("/parts/{part_id}/compatibilities", status_code=201)
def admin_add_compatibility(
    part_id: UUID,
    body: CompatibilityIn,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    try:
        row = add_part_compatibility(
            db,
            part_id=part_id,
            car_year_id=body.car_year_id,
            fitment_note_ar=body.fitment_note_ar,
        )
        db.commit()
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "COMPAT_ERROR", "message": str(exc)},
        ) from exc
    return {"data": {"id": row.id, "part_id": part_id, "car_year_id": body.car_year_id}}


@router.patch("/parts/{part_id}/oem")
def admin_patch_part_oem(
    part_id: UUID,
    body: PartOemPatchIn,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    from app.models import Part

    part = db.get(Part, part_id)
    if not part:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "القطعة غير موجودة"},
        )
    if body.oem_number is not None:
        part.oem_number = body.oem_number.strip()
    if body.vin_prefix is not None:
        part.vin_prefix = body.vin_prefix.strip().upper()[:11] or None
    db.commit()
    return {
        "data": {
            "id": part.id,
            "oem_number": part.oem_number,
            "vin_prefix": part.vin_prefix,
        }
    }
