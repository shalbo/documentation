import re
import secrets
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    MarketingAttributionEvent,
    MarketingBanner,
    MarketingCampaign,
    MarketingNewsletterSubscriber,
    MarketingPartner,
    MarketingReferral,
    Promotion,
    Testimonial,
    User,
)

REFERRAL_CODE_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _is_active_window(starts_at: datetime, ends_at: datetime | None, now: datetime) -> bool:
    if starts_at > now:
        return False
    if ends_at and ends_at < now:
        return False
    return True


def serialize_banner(banner: MarketingBanner) -> dict:
    return {
        "id": str(banner.id),
        "slug": banner.slug,
        "title_ar": banner.title_ar,
        "subtitle_ar": banner.subtitle_ar,
        "placement": banner.placement,
        "image_url": banner.image_url,
        "cta_text_ar": banner.cta_text_ar,
        "cta_url": banner.cta_url,
        "campaign_id": str(banner.campaign_id) if banner.campaign_id else None,
        "promotion_id": str(banner.promotion_id) if banner.promotion_id else None,
        "sort_order": banner.sort_order,
        "is_active": banner.is_active,
    }


def serialize_partner(partner: MarketingPartner) -> dict:
    return {
        "id": str(partner.id),
        "slug": partner.slug,
        "name_ar": partner.name_ar,
        "logo_url": partner.logo_url,
        "website_url": partner.website_url,
        "sort_order": partner.sort_order,
    }


def serialize_campaign(campaign: MarketingCampaign) -> dict:
    return {
        "id": str(campaign.id),
        "slug": campaign.slug,
        "name_ar": campaign.name_ar,
        "description_ar": campaign.description_ar,
        "channel": campaign.channel,
        "utm_source": campaign.utm_source,
        "utm_medium": campaign.utm_medium,
        "utm_campaign": campaign.utm_campaign,
        "utm_content": campaign.utm_content,
        "starts_at": campaign.starts_at.isoformat(),
        "ends_at": campaign.ends_at.isoformat() if campaign.ends_at else None,
        "is_active": campaign.is_active,
    }


def list_active_banners(db: Session, placement: str | None = None) -> list[dict]:
    now = _now()
    stmt = select(MarketingBanner).where(MarketingBanner.is_active.is_(True))
    if placement:
        stmt = stmt.where(MarketingBanner.placement == placement)
    banners = db.scalars(stmt.order_by(MarketingBanner.sort_order)).all()
    return [
        serialize_banner(b)
        for b in banners
        if _is_active_window(b.starts_at, b.ends_at, now)
    ]


def list_active_partners(db: Session) -> list[dict]:
    partners = db.scalars(
        select(MarketingPartner)
        .where(MarketingPartner.is_active.is_(True))
        .order_by(MarketingPartner.sort_order)
    ).all()
    return [serialize_partner(p) for p in partners]


def list_active_campaigns(db: Session) -> list[dict]:
    now = _now()
    campaigns = db.scalars(
        select(MarketingCampaign)
        .where(MarketingCampaign.is_active.is_(True))
        .order_by(MarketingCampaign.starts_at.desc())
    ).all()
    return [
        serialize_campaign(c)
        for c in campaigns
        if _is_active_window(c.starts_at, c.ends_at, now)
    ]


def subscribe_newsletter(
    db: Session,
    email: str,
    phone: str | None = None,
    source: str = "landing",
    campaign_id: uuid.UUID | None = None,
) -> MarketingNewsletterSubscriber:
    normalized = email.strip().lower()
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", normalized):
        raise ValueError("البريد الإلكتروني غير صالح")

    existing = db.scalar(
        select(MarketingNewsletterSubscriber).where(
            MarketingNewsletterSubscriber.email == normalized
        )
    )
    if existing:
        if existing.is_active:
            raise ValueError("البريد مسجّل مسبقاً")
        existing.is_active = True
        existing.unsubscribed_at = None
        existing.subscribed_at = _now()
        existing.source = source
        existing.campaign_id = campaign_id
        if phone:
            existing.phone = phone.strip()
        return existing

    entry = MarketingNewsletterSubscriber(
        id=uuid.uuid4(),
        email=normalized,
        phone=phone.strip() if phone else None,
        source=source,
        campaign_id=campaign_id,
        subscribed_at=_now(),
    )
    db.add(entry)
    db.flush()
    return entry


def track_attribution(
    db: Session,
    event_type: str,
    utm_source: str | None = None,
    utm_medium: str | None = None,
    utm_campaign: str | None = None,
    campaign_slug: str | None = None,
    user_id: uuid.UUID | None = None,
    session_id: str | None = None,
    metadata: dict | None = None,
) -> MarketingAttributionEvent:
    campaign_id = None
    if campaign_slug:
        campaign = db.scalar(
            select(MarketingCampaign).where(MarketingCampaign.slug == campaign_slug)
        )
        if campaign:
            campaign_id = campaign.id

    event = MarketingAttributionEvent(
        id=uuid.uuid4(),
        campaign_id=campaign_id,
        event_type=event_type,
        utm_source=utm_source,
        utm_medium=utm_medium,
        utm_campaign=utm_campaign,
        user_id=user_id,
        session_id=session_id,
        metadata_json=metadata or {},
        created_at=_now(),
    )
    db.add(event)
    db.flush()
    return event


def validate_referral_code(db: Session, code: str) -> dict:
    normalized = code.strip().upper()
    referral = db.scalar(
        select(MarketingReferral).where(
            MarketingReferral.code == normalized,
            MarketingReferral.is_active.is_(True),
        )
    )
    if not referral:
        return {"valid": False, "code": normalized, "reward_points": 0, "message": "كود غير صالح"}

    if referral.max_uses and referral.uses_count >= referral.max_uses:
        return {
            "valid": False,
            "code": normalized,
            "reward_points": referral.reward_points,
            "message": "انتهت صلاحية الكود",
        }

    return {
        "valid": True,
        "code": normalized,
        "reward_points": referral.reward_points,
        "message": None,
    }


def get_user_referral(db: Session, user_id: uuid.UUID) -> MarketingReferral | None:
    return db.scalar(
        select(MarketingReferral).where(
            MarketingReferral.referrer_user_id == user_id,
            MarketingReferral.is_active.is_(True),
        )
    )


def _generate_referral_code() -> str:
    return "".join(secrets.choice(REFERRAL_CODE_CHARS) for _ in range(8))


def create_user_referral(db: Session, user: User, reward_points: int = 100) -> MarketingReferral:
    existing = get_user_referral(db, user.id)
    if existing:
        return existing

    for _ in range(10):
        code = _generate_referral_code()
        collision = db.scalar(
            select(MarketingReferral.id).where(MarketingReferral.code == code)
        )
        if collision:
            continue
        referral = MarketingReferral(
            id=uuid.uuid4(),
            referrer_user_id=user.id,
            code=code,
            reward_points=reward_points,
            max_uses=50,
            created_at=_now(),
        )
        db.add(referral)
        db.flush()
        return referral

    raise ValueError("تعذّر إنشاء كود إحالة")


def get_landing_marketing(db: Session) -> dict:
    return {
        "banners": list_active_banners(db, placement="home_hero"),
        "partners": list_active_partners(db),
    }


def get_marketing_analytics(db: Session) -> dict:
    return {
        "campaigns_total": db.scalar(select(func.count()).select_from(MarketingCampaign)) or 0,
        "banners_active": db.scalar(
            select(func.count())
            .select_from(MarketingBanner)
            .where(MarketingBanner.is_active.is_(True))
        )
        or 0,
        "partners_active": db.scalar(
            select(func.count())
            .select_from(MarketingPartner)
            .where(MarketingPartner.is_active.is_(True))
        )
        or 0,
        "newsletter_subscribers": db.scalar(
            select(func.count())
            .select_from(MarketingNewsletterSubscriber)
            .where(MarketingNewsletterSubscriber.is_active.is_(True))
        )
        or 0,
        "referrals_active": db.scalar(
            select(func.count())
            .select_from(MarketingReferral)
            .where(MarketingReferral.is_active.is_(True))
        )
        or 0,
        "attribution_events": db.scalar(
            select(func.count()).select_from(MarketingAttributionEvent)
        )
        or 0,
        "promotions_active": db.scalar(
            select(func.count()).select_from(Promotion).where(Promotion.is_active.is_(True))
        )
        or 0,
        "testimonials_published": db.scalar(
            select(func.count())
            .select_from(Testimonial)
            .where(Testimonial.is_published.is_(True))
        )
        or 0,
    }
