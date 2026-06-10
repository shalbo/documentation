from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_admin_key
from app.models import Vendor
from app.subscription_services import (
    admin_assign_vendor_subscription,
    list_vendor_subscriptions_admin,
    subscription_out,
)
from app.tier_services import get_tier_or_none

router = APIRouter(prefix="/admin", tags=["admin-subscriptions"])


class AdminVendorSubscriptionUpdate(BaseModel):
    tier_id: UUID
    expires_at: datetime | None = None
    payment_method: str | None = Field(default=None, max_length=40)
    payment_note: str | None = Field(default=None, max_length=500)


@router.get("/vendor-subscriptions")
def admin_list_vendor_subscriptions(
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    data = list_vendor_subscriptions_admin(db)
    return {"data": data, "meta": {"total": len(data)}}


@router.patch("/vendors/{vendor_id}/subscription")
def admin_update_vendor_subscription(
    vendor_id: UUID,
    body: AdminVendorSubscriptionUpdate,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    vendor = db.get(Vendor, vendor_id)
    if not vendor:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "التاجر غير موجود"},
        )
    tier = get_tier_or_none(db, body.tier_id)
    if not tier or not tier.is_active:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_TIER", "message": "الباقة غير صالحة"},
        )
    try:
        sub = admin_assign_vendor_subscription(
            db,
            vendor,
            tier,
            expires_at=body.expires_at,
            payment_method=body.payment_method or "manual",
            payment_note=body.payment_note,
            upgraded_by="admin",
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "SUBSCRIPTION_ERROR", "message": str(exc)},
        ) from exc
    return {
        "data": {
            "vendor_id": vendor.id,
            "subscription": subscription_out(sub),
        },
        "meta": {
            "message": f"تم تحديث باقة {vendor.business_name} إلى {tier.name_ar}",
        },
    }
