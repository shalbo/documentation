from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.marketing_services import (
    create_user_referral,
    get_user_referral,
    list_active_banners,
    list_active_campaigns,
    list_active_partners,
    subscribe_newsletter,
    track_attribution,
    validate_referral_code,
)
from app.models import MarketingCampaign, User
from app.rate_limit import check_rate_limit
from app.schemas import AttributionTrackIn, NewsletterSubscribeIn

router = APIRouter(prefix="/marketing", tags=["marketing"])
me_router = APIRouter(tags=["marketing"])


class ReferralOut(BaseModel):
    code: str
    reward_points: int
    uses_count: int
    max_uses: int | None


@router.get("/banners")
def marketing_banners(
    placement: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    data = list_active_banners(db, placement=placement)
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/partners")
def marketing_partners(db: Session = Depends(get_db)):
    data = list_active_partners(db)
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/campaigns")
def marketing_campaigns(db: Session = Depends(get_db)):
    data = list_active_campaigns(db)
    return {"data": data, "meta": {"total": len(data)}}


@router.post("/newsletter/subscribe")
def newsletter_subscribe(
    body: NewsletterSubscribeIn, request: Request, db: Session = Depends(get_db)
):
    check_rate_limit(request, suffix="newsletter")
    campaign_id = None
    if body.campaign_slug:
        campaign = db.scalar(
            select(MarketingCampaign).where(MarketingCampaign.slug == body.campaign_slug)
        )
        if campaign:
            campaign_id = campaign.id
    try:
        entry = subscribe_newsletter(
            db,
            body.email,
            phone=body.phone,
            source=body.source,
            campaign_id=campaign_id,
        )
        db.commit()
        return {
            "data": {
                "email": entry.email,
                "subscribed": True,
                "message": "تم الاشتراك بنجاح",
            }
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "NEWSLETTER_FAILED", "message": str(exc)},
        ) from exc


@router.post("/attribution/track")
def attribution_track(body: AttributionTrackIn, db: Session = Depends(get_db)):
    event = track_attribution(
        db,
        event_type=body.event_type,
        utm_source=body.utm_source,
        utm_medium=body.utm_medium,
        utm_campaign=body.utm_campaign,
        campaign_slug=body.campaign_slug,
        session_id=body.session_id,
    )
    db.commit()
    return {"data": {"tracked": True, "event_id": str(event.id)}}


@router.get("/referrals/validate")
def referrals_validate(code: str = Query(min_length=3, max_length=20), db: Session = Depends(get_db)):
    return {"data": validate_referral_code(db, code)}


@me_router.get("/me/referral")
def my_referral(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    referral = get_user_referral(db, user.id)
    if not referral:
        return {"data": None, "meta": {"has_referral": False}}
    return {
        "data": ReferralOut(
            code=referral.code,
            reward_points=referral.reward_points,
            uses_count=referral.uses_count,
            max_uses=referral.max_uses,
        ).model_dump(),
        "meta": {"has_referral": True},
    }


@me_router.post("/me/referral")
def create_referral(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        referral = create_user_referral(db, user)
        db.commit()
        return {
            "data": ReferralOut(
                code=referral.code,
                reward_points=referral.reward_points,
                uses_count=referral.uses_count,
                max_uses=referral.max_uses,
            ).model_dump()
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "REFERRAL_FAILED", "message": str(exc)},
        ) from exc
