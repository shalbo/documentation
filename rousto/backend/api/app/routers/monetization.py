from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.models import LoyaltyReward, MembershipPlan, ServicePackage, User
from app.monetization import (
    get_monetization_summary,
    redeem_loyalty_reward,
    subscribe_membership,
)

router = APIRouter(tags=["monetization"])


class SubscribeIn(BaseModel):
    plan_slug: str = Field(min_length=1, max_length=40)


class RedeemIn(BaseModel):
    reward_slug: str = Field(min_length=1, max_length=40)


@router.get("/monetization/plans")
def list_plans(db: Session = Depends(get_db)):
    plans = db.scalars(
        select(MembershipPlan)
        .where(MembershipPlan.is_active.is_(True))
        .order_by(MembershipPlan.sort_order)
    ).all()
    data = [
        {
            "id": str(p.id),
            "slug": p.slug,
            "name_ar": p.name_ar,
            "description_ar": p.description_ar,
            "price_sar": float(p.price_sar),
            "billing_period": p.billing_period,
            "discount_percent": p.discount_percent,
            "priority_booking": p.priority_booking,
            "free_inspection": p.free_inspection,
        }
        for p in plans
    ]
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/monetization/packages")
def list_packages(db: Session = Depends(get_db)):
    packages = db.scalars(
        select(ServicePackage)
        .where(ServicePackage.is_active.is_(True))
        .order_by(ServicePackage.price_sar)
    ).all()
    data = [
        {
            "id": str(p.id),
            "slug": p.slug,
            "name_ar": p.name_ar,
            "description_ar": p.description_ar,
            "price_sar": float(p.price_sar),
            "visits_count": p.visits_count,
            "validity_days": p.validity_days,
            "savings_sar": float(p.savings_sar),
        }
        for p in packages
    ]
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/monetization/rewards")
def list_rewards(db: Session = Depends(get_db)):
    rewards = db.scalars(
        select(LoyaltyReward)
        .where(LoyaltyReward.is_active.is_(True))
        .order_by(LoyaltyReward.points_cost)
    ).all()
    data = [
        {
            "id": str(r.id),
            "slug": r.slug,
            "title_ar": r.title_ar,
            "description_ar": r.description_ar,
            "points_cost": r.points_cost,
            "discount_sar": float(r.discount_sar),
        }
        for r in rewards
    ]
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/me/monetization")
def my_monetization(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return {"data": get_monetization_summary(db, user)}


@router.post("/me/membership/subscribe", status_code=201)
def subscribe(
    body: SubscribeIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        membership = subscribe_membership(db, user, body.plan_slug)
        db.commit()
        plan = db.get(MembershipPlan, membership.plan_id)
        return {
            "data": {
                "plan_slug": plan.slug,
                "plan_name_ar": plan.name_ar,
                "discount_percent": plan.discount_percent,
                "expires_at": membership.expires_at,
            }
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "SUBSCRIBE_FAILED", "message": str(exc)},
        ) from exc


@router.post("/me/loyalty/redeem")
def redeem_points(
    body: RedeemIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        discount_sar, points_spent = redeem_loyalty_reward(db, user, body.reward_slug)
        db.commit()
        db.refresh(user)
        return {
            "data": {
                "discount_sar": discount_sar,
                "points_spent": points_spent,
                "balance_remaining": user.loyalty_points,
            }
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "REDEEM_FAILED", "message": str(exc)},
        ) from exc
