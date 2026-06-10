"""Vendor subscription tiers — dynamic limits read from database."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import PartInventory, Tier, Vendor

DEFAULT_STARTER_SLUG = "starter"
UNLIMITED_PRODUCTS = -1


def _now() -> datetime:
    return datetime.now(timezone.utc)


def is_unlimited_products(products_limit: int) -> bool:
    return products_limit == UNLIMITED_PRODUCTS


def products_limit_label(products_limit: int) -> str:
    if is_unlimited_products(products_limit):
        return "غير محدود"
    return str(products_limit)


def tier_out(tier: Tier, *, vendor_count: int | None = None) -> dict:
    data = {
        "id": tier.id,
        "slug": tier.slug,
        "name_ar": tier.name_ar,
        "name_en": tier.name_en,
        "price": float(tier.price),
        "products_limit": tier.products_limit,
        "products_limit_label": products_limit_label(tier.products_limit),
        "is_unlimited_products": is_unlimited_products(tier.products_limit),
        "allow_excel_upload": tier.allow_excel_upload,
        "allow_vin_decoder": tier.allow_vin_decoder,
        "allow_unlimited_chat": tier.allow_unlimited_chat,
        "has_gold_badge": tier.has_gold_badge,
        "sort_order": tier.sort_order,
        "is_active": tier.is_active,
        "updated_at": tier.updated_at.isoformat() if tier.updated_at else None,
    }
    if vendor_count is not None:
        data["vendor_count"] = vendor_count
    return data


def get_default_tier(db: Session) -> Tier | None:
    return db.scalar(
        select(Tier)
        .where(Tier.slug == DEFAULT_STARTER_SLUG, Tier.is_active.is_(True))
        .limit(1)
    )


def resolve_vendor_tier(db: Session, vendor: Vendor) -> Tier:
    if vendor.tier_id:
        tier = db.get(Tier, vendor.tier_id)
        if tier and tier.is_active:
            return tier
    if vendor.tier and vendor.tier.is_active:
        return vendor.tier
    tier = get_default_tier(db)
    if tier:
        return tier
    raise ValueError("لا توجد باقة افتراضية مفعّلة للتجار")


def count_vendor_products(db: Session, vendor_id: uuid.UUID) -> int:
    return db.scalar(
        select(func.count(PartInventory.id)).where(
            PartInventory.vendor_id == vendor_id
        )
    ) or 0


def ensure_products_capacity(
    db: Session,
    vendor: Vendor,
    *,
    additional: int = 1,
) -> Tier:
    tier = resolve_vendor_tier(db, vendor)
    if is_unlimited_products(tier.products_limit):
        return tier
    current = count_vendor_products(db, vendor.id)
    if current + additional > tier.products_limit:
        raise ValueError(
            f"وصلت لسقف الباقة ({tier.products_limit} قطعة). "
            f"الحالي: {current}. ترقِّ باقتك لإضافة المزيد."
        )
    return tier


def require_excel_upload(db: Session, vendor: Vendor) -> Tier:
    tier = resolve_vendor_tier(db, vendor)
    if not tier.allow_excel_upload:
        raise ValueError(
            f"باقة «{tier.name_ar}» لا تتضمن رفع Excel. رقِّ باقتك لتفعيل الرفع الجماعي."
        )
    return tier


def require_vin_decoder(db: Session, vendor: Vendor) -> Tier:
    tier = resolve_vendor_tier(db, vendor)
    if not tier.allow_vin_decoder:
        raise ValueError(
            f"باقة «{tier.name_ar}» لا تتضمن فك ترميز VIN. رقِّ باقتك لتفعيل الميزة."
        )
    return tier


def require_unlimited_chat(db: Session, vendor: Vendor) -> Tier:
    tier = resolve_vendor_tier(db, vendor)
    if not tier.allow_unlimited_chat:
        raise ValueError(
            f"باقة «{tier.name_ar}» لا تتضمن محادثة غير محدودة مع العملاء."
        )
    return tier


def vendor_has_gold_badge(db: Session, vendor: Vendor) -> bool:
    try:
        tier = resolve_vendor_tier(db, vendor)
        return tier.has_gold_badge
    except ValueError:
        return False


def vendor_tier_summary(db: Session, vendor: Vendor) -> dict:
    tier = resolve_vendor_tier(db, vendor)
    current = count_vendor_products(db, vendor.id)
    unlimited = is_unlimited_products(tier.products_limit)
    return {
        "tier": tier_out(tier),
        "usage": {
            "products_count": current,
            "products_limit": tier.products_limit,
            "products_remaining": None if unlimited else max(0, tier.products_limit - current),
            "is_unlimited_products": unlimited,
        },
    }


def list_tiers_admin(db: Session) -> list[dict]:
    rows = db.execute(
        select(Tier, func.count(Vendor.id).label("vendor_count"))
        .outerjoin(Vendor, Vendor.tier_id == Tier.id)
        .group_by(Tier.id)
        .order_by(Tier.sort_order, Tier.name_ar)
    ).all()
    return [tier_out(tier, vendor_count=count) for tier, count in rows]


def get_tier_or_none(db: Session, tier_id: uuid.UUID) -> Tier | None:
    return db.get(Tier, tier_id)


def update_tier(
    db: Session,
    tier: Tier,
    *,
    name_ar: str | None = None,
    name_en: str | None = None,
    price: float | None = None,
    products_limit: int | None = None,
    allow_excel_upload: bool | None = None,
    allow_vin_decoder: bool | None = None,
    allow_unlimited_chat: bool | None = None,
    has_gold_badge: bool | None = None,
    sort_order: int | None = None,
    is_active: bool | None = None,
) -> Tier:
    if name_ar is not None:
        tier.name_ar = name_ar.strip()
    if name_en is not None:
        tier.name_en = name_en.strip()
    if price is not None:
        if price < 0:
            raise ValueError("السعر لا يمكن أن يكون سالباً")
        tier.price = round(price, 2)
    if products_limit is not None:
        if products_limit != UNLIMITED_PRODUCTS and products_limit < 0:
            raise ValueError(
                "سقف القطع يجب أن يكون -1 (غير محدود) أو عدداً موجباً"
            )
        tier.products_limit = products_limit
    if allow_excel_upload is not None:
        tier.allow_excel_upload = allow_excel_upload
    if allow_vin_decoder is not None:
        tier.allow_vin_decoder = allow_vin_decoder
    if allow_unlimited_chat is not None:
        tier.allow_unlimited_chat = allow_unlimited_chat
    if has_gold_badge is not None:
        tier.has_gold_badge = has_gold_badge
    if sort_order is not None:
        tier.sort_order = sort_order
    if is_active is not None:
        tier.is_active = is_active
    tier.updated_at = _now()
    db.flush()
    return tier


def load_vendor_with_tier(db: Session, vendor_id: uuid.UUID) -> Vendor | None:
    return db.scalar(
        select(Vendor)
        .options(joinedload(Vendor.tier))
        .where(Vendor.id == vendor_id)
    )
