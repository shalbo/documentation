from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.models import Promotion, User
from app.schemas import PromotionOut, PromotionValidateIn
from app.services import calculate_discount, find_active_promotion

router = APIRouter(prefix="/promotions", tags=["promotions"])


@router.get("")
def list_promotions(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    promotions = db.scalars(
        select(Promotion)
        .where(
            Promotion.is_active.is_(True),
            Promotion.starts_at <= now,
            (Promotion.ends_at.is_(None)) | (Promotion.ends_at >= now),
        )
        .order_by(Promotion.title_ar)
    ).all()
    data = [PromotionOut.model_validate(p).model_dump() for p in promotions]
    return {"data": data, "meta": {"total": len(data)}}


@router.post("/validate")
def validate_promotion(
    body: PromotionValidateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    promotion = find_active_promotion(db, body.code, body.service_price_sar)
    if not promotion:
        return {
            "data": {
                "valid": False,
                "discount_sar": 0,
                "total_sar": body.service_price_sar,
                "promotion": None,
                "message": "كود الخصم غير صالح أو منتهي",
            }
        }

    discount = calculate_discount(promotion, body.service_price_sar)
    return {
        "data": {
            "valid": True,
            "discount_sar": discount,
            "total_sar": body.service_price_sar - discount,
            "promotion": PromotionOut.model_validate(promotion).model_dump(),
            "message": None,
        }
    }
