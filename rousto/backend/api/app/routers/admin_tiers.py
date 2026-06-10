from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_admin_key
from app.tier_services import get_tier_or_none, list_tiers_admin, tier_out, update_tier

router = APIRouter(prefix="/admin", tags=["admin-tiers"])


class AdminTierUpdate(BaseModel):
    name_ar: str | None = Field(default=None, min_length=2, max_length=80)
    name_en: str | None = Field(default=None, min_length=2, max_length=80)
    price: float | None = Field(default=None, ge=0)
    products_limit: int | None = Field(default=None, ge=-1)
    allow_excel_upload: bool | None = None
    allow_vin_decoder: bool | None = None
    allow_unlimited_chat: bool | None = None
    has_gold_badge: bool | None = None
    sort_order: int | None = Field(default=None, ge=0, le=999)
    is_active: bool | None = None


def _get_tier_or_404(db: Session, tier_id: UUID):
    tier = get_tier_or_none(db, tier_id)
    if not tier:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "الباقة غير موجودة"},
        )
    return tier


@router.get("/tiers")
def admin_list_tiers(
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    data = list_tiers_admin(db)
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/tiers/{tier_id}")
def admin_get_tier(
    tier_id: UUID,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    tier = _get_tier_or_404(db, tier_id)
    return {"data": tier_out(tier)}


@router.put("/tiers/{tier_id}")
def admin_update_tier(
    tier_id: UUID,
    body: AdminTierUpdate,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    tier = _get_tier_or_404(db, tier_id)
    if not body.model_fields_set:
        raise HTTPException(
            status_code=400,
            detail={"code": "EMPTY_BODY", "message": "أرسل حقلاً واحداً على الأقل للتحديث"},
        )
    try:
        updated = update_tier(
            db,
            tier,
            name_ar=body.name_ar,
            name_en=body.name_en,
            price=body.price,
            products_limit=body.products_limit,
            allow_excel_upload=body.allow_excel_upload,
            allow_vin_decoder=body.allow_vin_decoder,
            allow_unlimited_chat=body.allow_unlimited_chat,
            has_gold_badge=body.has_gold_badge,
            sort_order=body.sort_order,
            is_active=body.is_active,
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "VALIDATION_ERROR", "message": str(exc)},
        ) from exc
    return {
        "data": tier_out(updated),
        "meta": {
            "message": "تم تحديث قيود الباقة عالمياً في المنصة",
            "tier_id": str(tier_id),
        },
    }
