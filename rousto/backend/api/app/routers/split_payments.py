from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user, require_admin_key
from app.models import Booking, SplitRule
from app.split_payments import get_booking_split, preview_split, release_splits_for_booking

router = APIRouter(prefix="/payments", tags=["split-payments"])


class SplitPreviewIn(BaseModel):
    amount_sar: float = Field(gt=0)


class SplitReleaseIn(BaseModel):
    booking_id: UUID
    recipient_type: str | None = Field(
        default="technician",
        pattern=r"^(platform|technician|reserve)$",
    )


@router.get("/split-rules")
def list_split_rules(db: Session = Depends(get_db)):
    rules = db.scalars(
        select(SplitRule).where(SplitRule.is_active.is_(True)).order_by(SplitRule.slug)
    ).all()
    data = [
        {
            "slug": r.slug,
            "name_ar": r.name_ar,
            "platform_rate": float(r.platform_rate),
            "technician_rate": float(r.technician_rate),
            "reserve_rate": float(r.reserve_rate),
            "is_default": r.is_default,
        }
        for r in rules
    ]
    return {"data": data, "meta": {"total": len(data)}}


@router.post("/split/preview")
def split_preview(body: SplitPreviewIn, db: Session = Depends(get_db)):
    try:
        data = preview_split(db, body.amount_sar)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "SPLIT_ERROR", "message": str(exc)},
        ) from exc
    return {"data": data}


@router.post("/splits/release")
def release_split_legs(
    body: SplitReleaseIn,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    booking = db.get(Booking, body.booking_id)
    if not booking:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "الحجز غير موجود"},
        )

    count = release_splits_for_booking(
        db, body.booking_id, recipient_type=body.recipient_type
    )
    if count == 0:
        raise HTTPException(
            status_code=400,
            detail={"code": "NO_HELD_SPLITS", "message": "لا توجد حصص معلّقة للإطلاق"},
        )
    db.commit()

    data = get_booking_split(db, body.booking_id)
    return {"data": data, "meta": {"released_count": count}}
