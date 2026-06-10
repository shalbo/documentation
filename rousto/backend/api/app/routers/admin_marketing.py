from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_admin_key
from app.marketing_services import (
    get_marketing_analytics,
    serialize_banner,
    serialize_campaign,
    serialize_partner,
)
from app.models import (
    MarketingBanner,
    MarketingCampaign,
    MarketingNewsletterSubscriber,
    MarketingPartner,
    Promotion,
    Testimonial,
)
from app.schemas import (
    AdminBannerCreate,
    AdminBannerUpdate,
    AdminCampaignCreate,
    AdminCampaignUpdate,
    AdminPartnerCreate,
    AdminPartnerUpdate,
    AdminPromotionCreate,
    AdminPromotionOut,
    AdminPromotionUpdate,
    AdminTestimonialUpdate,
    TestimonialOut,
)

router = APIRouter(prefix="/admin", tags=["admin-marketing"])


def _now() -> datetime:
    return datetime.now(timezone.utc)


@router.get("/promotions")
def admin_list_promotions(
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    promos = db.scalars(select(Promotion).order_by(Promotion.code)).all()
    data = [AdminPromotionOut.model_validate(p).model_dump() for p in promos]
    return {"data": data, "meta": {"total": len(data)}}


@router.post("/promotions", status_code=201)
def admin_create_promotion(
    body: AdminPromotionCreate,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    promo = Promotion(
        id=uuid4(),
        code=body.code.strip().upper(),
        title_ar=body.title_ar,
        description_ar=body.description_ar,
        discount_type=body.discount_type,
        discount_value=body.discount_value,
        min_order_sar=body.min_order_sar,
        max_uses_per_user=body.max_uses_per_user,
        starts_at=body.starts_at or _now(),
        ends_at=body.ends_at,
        is_active=body.is_active,
    )
    db.add(promo)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail={"code": "DUPLICATE_CODE", "message": "كود العرض موجود مسبقاً"},
        ) from exc
    db.refresh(promo)
    return {"data": AdminPromotionOut.model_validate(promo).model_dump()}


@router.patch("/promotions/{promotion_id}")
def admin_update_promotion(
    promotion_id: UUID,
    body: AdminPromotionUpdate,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    promo = db.get(Promotion, promotion_id)
    if not promo:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "العرض غير موجود"},
        )
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(promo, field, value)
    db.commit()
    db.refresh(promo)
    return {"data": AdminPromotionOut.model_validate(promo).model_dump()}


@router.get("/marketing/campaigns")
def admin_list_campaigns(
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    campaigns = db.scalars(
        select(MarketingCampaign).order_by(MarketingCampaign.created_at.desc())
    ).all()
    data = [serialize_campaign(c) for c in campaigns]
    return {"data": data, "meta": {"total": len(data)}}


@router.post("/marketing/campaigns", status_code=201)
def admin_create_campaign(
    body: AdminCampaignCreate,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    campaign = MarketingCampaign(
        id=uuid4(),
        slug=body.slug,
        name_ar=body.name_ar,
        description_ar=body.description_ar,
        channel=body.channel,
        utm_source=body.utm_source,
        utm_medium=body.utm_medium,
        utm_campaign=body.utm_campaign,
        utm_content=body.utm_content,
        starts_at=body.starts_at or _now(),
        ends_at=body.ends_at,
        is_active=body.is_active,
        created_at=_now(),
    )
    db.add(campaign)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail={"code": "DUPLICATE_SLUG", "message": "المعرّف موجود مسبقاً"},
        ) from exc
    db.refresh(campaign)
    return {"data": serialize_campaign(campaign)}


@router.patch("/marketing/campaigns/{campaign_id}")
def admin_update_campaign(
    campaign_id: UUID,
    body: AdminCampaignUpdate,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    campaign = db.get(MarketingCampaign, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "الحملة غير موجودة"},
        )
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(campaign, field, value)
    db.commit()
    db.refresh(campaign)
    return {"data": serialize_campaign(campaign)}


@router.get("/marketing/banners")
def admin_list_banners(
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    banners = db.scalars(
        select(MarketingBanner).order_by(MarketingBanner.placement, MarketingBanner.sort_order)
    ).all()
    data = [serialize_banner(b) for b in banners]
    return {"data": data, "meta": {"total": len(data)}}


@router.post("/marketing/banners", status_code=201)
def admin_create_banner(
    body: AdminBannerCreate,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    banner = MarketingBanner(
        id=uuid4(),
        slug=body.slug,
        title_ar=body.title_ar,
        subtitle_ar=body.subtitle_ar,
        placement=body.placement,
        image_url=body.image_url,
        cta_text_ar=body.cta_text_ar,
        cta_url=body.cta_url,
        campaign_id=body.campaign_id,
        promotion_id=body.promotion_id,
        sort_order=body.sort_order,
        starts_at=body.starts_at or _now(),
        ends_at=body.ends_at,
        is_active=body.is_active,
    )
    db.add(banner)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail={"code": "DUPLICATE_SLUG", "message": "المعرّف موجود مسبقاً"},
        ) from exc
    db.refresh(banner)
    return {"data": serialize_banner(banner)}


@router.patch("/marketing/banners/{banner_id}")
def admin_update_banner(
    banner_id: UUID,
    body: AdminBannerUpdate,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    banner = db.get(MarketingBanner, banner_id)
    if not banner:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "البانر غير موجود"},
        )
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(banner, field, value)
    db.commit()
    db.refresh(banner)
    return {"data": serialize_banner(banner)}


@router.get("/marketing/partners")
def admin_list_partners(
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    partners = db.scalars(
        select(MarketingPartner).order_by(MarketingPartner.sort_order)
    ).all()
    data = [serialize_partner(p) for p in partners]
    return {"data": data, "meta": {"total": len(data)}}


@router.post("/marketing/partners", status_code=201)
def admin_create_partner(
    body: AdminPartnerCreate,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    partner = MarketingPartner(
        id=uuid4(),
        slug=body.slug,
        name_ar=body.name_ar,
        logo_url=body.logo_url,
        website_url=body.website_url,
        sort_order=body.sort_order,
        is_active=body.is_active,
    )
    db.add(partner)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail={"code": "DUPLICATE_SLUG", "message": "المعرّف موجود مسبقاً"},
        ) from exc
    db.refresh(partner)
    return {"data": serialize_partner(partner)}


@router.patch("/marketing/partners/{partner_id}")
def admin_update_partner(
    partner_id: UUID,
    body: AdminPartnerUpdate,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    partner = db.get(MarketingPartner, partner_id)
    if not partner:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "الشريك غير موجود"},
        )
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(partner, field, value)
    db.commit()
    db.refresh(partner)
    return {"data": serialize_partner(partner)}


@router.get("/marketing/newsletter")
def admin_list_newsletter(
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    subs = db.scalars(
        select(MarketingNewsletterSubscriber)
        .where(MarketingNewsletterSubscriber.is_active.is_(True))
        .order_by(MarketingNewsletterSubscriber.subscribed_at.desc())
    ).all()
    data = [
        {
            "id": str(s.id),
            "email": s.email,
            "phone": s.phone,
            "source": s.source,
            "subscribed_at": s.subscribed_at.isoformat(),
        }
        for s in subs
    ]
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/testimonials")
def admin_list_testimonials(
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    items = db.scalars(select(Testimonial).order_by(Testimonial.created_at.desc())).all()
    data = [
        {
            **TestimonialOut.model_validate(t).model_dump(),
            "is_published": t.is_published,
        }
        for t in items
    ]
    return {"data": data, "meta": {"total": len(data)}}


@router.patch("/testimonials/{testimonial_id}")
def admin_update_testimonial(
    testimonial_id: UUID,
    body: AdminTestimonialUpdate,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    item = db.get(Testimonial, testimonial_id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "الرأي غير موجود"},
        )
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return {
        "data": {
            **TestimonialOut.model_validate(item).model_dump(),
            "is_published": item.is_published,
        }
    }


@router.get("/marketing/analytics")
def admin_marketing_analytics(
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    return {"data": get_marketing_analytics(db)}
