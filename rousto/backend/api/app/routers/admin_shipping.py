from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_admin_key
from app.models import IntercityShippingRate
from app.shipping_services import list_intercity_rates_admin

router = APIRouter(prefix="/admin", tags=["admin-shipping"])


class IntercityRateIn(BaseModel):
    origin_city: str = Field(min_length=2, max_length=60)
    destination_city: str = Field(min_length=2, max_length=60)
    flat_fee_sar: float = Field(gt=0)
    carrier_name: str = Field(min_length=2, max_length=80)
    carrier_slug: str = Field(min_length=2, max_length=40)
    eta_days: int = Field(default=2, ge=1, le=14)


@router.get("/shipping/intercity-rates")
def admin_list_intercity_rates(
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    data = list_intercity_rates_admin(db)
    return {"data": data, "meta": {"total": len(data)}}


@router.post("/shipping/intercity-rates", status_code=201)
def admin_create_intercity_rate(
    body: IntercityRateIn,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    from datetime import datetime, timezone

    row = IntercityShippingRate(
        id=uuid4(),
        origin_city=body.origin_city.strip(),
        destination_city=body.destination_city.strip(),
        flat_fee_sar=body.flat_fee_sar,
        carrier_name=body.carrier_name.strip(),
        carrier_slug=body.carrier_slug.strip(),
        eta_days=body.eta_days,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db.add(row)
    try:
        db.commit()
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "RATE_ERROR", "message": str(exc)},
        ) from exc
    return {"data": {"id": row.id}}


@router.patch("/shipping/intercity-rates/{rate_id}")
def admin_patch_intercity_rate(
    rate_id: UUID,
    flat_fee_sar: float | None = None,
    is_active: bool | None = None,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    row = db.get(IntercityShippingRate, rate_id)
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "التعرفة غير موجودة"},
        )
    if flat_fee_sar is not None:
        row.flat_fee_sar = flat_fee_sar
    if is_active is not None:
        row.is_active = is_active
    db.commit()
    return {"data": {"id": row.id, "is_active": row.is_active}}
