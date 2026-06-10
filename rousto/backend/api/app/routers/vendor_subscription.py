from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_vendor
from app.models import Vendor
from app.subscription_services import (
    request_tier_upgrade,
    subscription_out,
    vendor_subscription_dashboard,
)
from app.tier_services import get_tier_or_none

router = APIRouter(prefix="/vendor/subscription", tags=["vendor-subscription"])


class UpgradeRequestIn(BaseModel):
    tier_id: UUID


@router.get("")
def vendor_subscription_info(
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db),
):
    try:
        data = vendor_subscription_dashboard(db, vendor)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "SUBSCRIPTION_ERROR", "message": str(exc)},
        ) from exc
    return {"data": data}


@router.post("/upgrade-request", status_code=201)
def vendor_request_upgrade(
    body: UpgradeRequestIn,
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db),
):
    tier = get_tier_or_none(db, body.tier_id)
    if not tier or not tier.is_active:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_TIER", "message": "الباقة المطلوبة غير متاحة"},
        )
    try:
        pending = request_tier_upgrade(db, vendor, tier)
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "UPGRADE_ERROR", "message": str(exc)},
        ) from exc
    return {
        "data": subscription_out(pending),
        "meta": {
            "message": f"تم إرسال طلب الترقية إلى باقة {tier.name_ar}. سيتواصل معك فريق الإدارة.",
        },
    }

