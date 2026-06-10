"""Vendor subscriptions — lifecycle, admin assignment, upgrade requests."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Subscription, Tier, Vendor, VendorProfile
from app.tier_services import (
    count_vendor_products,
    is_unlimited_products,
    resolve_vendor_tier,
    tier_out,
)

DEFAULT_SUBSCRIPTION_DAYS = 365


def _now() -> datetime:
    return datetime.now(timezone.utc)


def subscription_out(sub: Subscription) -> dict:
    return {
        "id": sub.id,
        "vendor_id": sub.vendor_id,
        "tier_id": sub.tier_id,
        "status": sub.status,
        "started_at": sub.started_at.isoformat() if sub.started_at else None,
        "expires_at": sub.expires_at.isoformat() if sub.expires_at else None,
        "payment_method": sub.payment_method,
        "payment_note": sub.payment_note,
        "upgraded_by": sub.upgraded_by,
        "tier": tier_out(sub.tier) if sub.tier else None,
    }


def get_active_subscription(db: Session, vendor_id: uuid.UUID) -> Subscription | None:
    return db.scalar(
        select(Subscription)
        .options(joinedload(Subscription.tier))
        .where(
            Subscription.vendor_id == vendor_id,
            Subscription.status == "active",
        )
        .order_by(Subscription.started_at.desc())
        .limit(1)
    )


def _sync_vendor_tier(
    db: Session,
    vendor: Vendor,
    tier: Tier,
    *,
    profile: VendorProfile | None = None,
) -> None:
    vendor.tier_id = tier.id
    vendor.updated_at = _now()
    if profile is None and vendor.id:
        profile = db.scalar(
            select(VendorProfile).where(VendorProfile.vendor_id == vendor.id)
        )
    if profile:
        profile.tier_id = tier.id
        profile.updated_at = _now()


def admin_assign_vendor_subscription(
    db: Session,
    vendor: Vendor,
    tier: Tier,
    *,
    expires_at: datetime | None = None,
    payment_method: str | None = None,
    payment_note: str | None = None,
    upgraded_by: str = "admin",
) -> Subscription:
    now = _now()
    expiry = expires_at or (now + timedelta(days=DEFAULT_SUBSCRIPTION_DAYS))

    for sub in db.scalars(
        select(Subscription).where(
            Subscription.vendor_id == vendor.id,
            Subscription.status == "active",
        )
    ).all():
        sub.status = "cancelled"
        sub.updated_at = now

    subscription = Subscription(
        id=uuid.uuid4(),
        vendor_id=vendor.id,
        tier_id=tier.id,
        status="active",
        started_at=now,
        expires_at=expiry,
        payment_method=payment_method,
        payment_note=payment_note,
        upgraded_by=upgraded_by,
        created_at=now,
        updated_at=now,
    )
    db.add(subscription)
    _sync_vendor_tier(db, vendor, tier)
    db.flush()
    subscription.tier = tier
    return subscription


def request_tier_upgrade(
    db: Session,
    vendor: Vendor,
    target_tier: Tier,
) -> Subscription:
    current = resolve_vendor_tier(db, vendor)
    if current.id == target_tier.id:
        raise ValueError("أنت مشترك بالفعل في هذه الباقة")
    if target_tier.sort_order <= current.sort_order:
        raise ValueError("يمكن طلب الترقية إلى باقة أعلى فقط")

    now = _now()
    pending = Subscription(
        id=uuid.uuid4(),
        vendor_id=vendor.id,
        tier_id=target_tier.id,
        status="pending",
        started_at=now,
        expires_at=None,
        payment_method="upgrade_request",
        payment_note=f"طلب ترقية من {current.slug} إلى {target_tier.slug}",
        upgraded_by=None,
        created_at=now,
        updated_at=now,
    )
    db.add(pending)
    db.flush()
    pending.tier = target_tier
    return pending


def vendor_subscription_dashboard(db: Session, vendor: Vendor) -> dict:
    tier = resolve_vendor_tier(db, vendor)
    active = get_active_subscription(db, vendor.id)
    current = count_vendor_products(db, vendor.id)
    unlimited = is_unlimited_products(tier.products_limit)
    all_tiers = db.scalars(
        select(Tier)
        .where(Tier.is_active.is_(True), Tier.slug.in_(("standard", "professional", "enterprise")))
        .order_by(Tier.sort_order)
    ).all()

    return {
        "current_tier": tier_out(tier),
        "subscription": subscription_out(active) if active else None,
        "usage": {
            "products_count": current,
            "products_limit": tier.products_limit,
            "products_remaining": None if unlimited else max(0, tier.products_limit - current),
            "is_unlimited_products": unlimited,
        },
        "available_tiers": [tier_out(t) for t in all_tiers],
    }


def list_vendor_subscriptions_admin(db: Session) -> list[dict]:
    vendors = db.scalars(
        select(Vendor)
        .options(joinedload(Vendor.tier))
        .order_by(Vendor.business_name)
    ).unique().all()

    out: list[dict] = []
    for vendor in vendors:
        active = get_active_subscription(db, vendor.id)
        tier = None
        try:
            tier = resolve_vendor_tier(db, vendor)
        except ValueError:
            pass
        out.append(
            {
                "vendor_id": vendor.id,
                "business_name": vendor.business_name,
                "email": vendor.email,
                "status": vendor.status,
                "tier": tier_out(tier) if tier else None,
                "subscription": subscription_out(active) if active else None,
                "products_count": count_vendor_products(db, vendor.id),
            }
        )
    return out
