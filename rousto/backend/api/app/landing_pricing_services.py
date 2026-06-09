from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    LandingHeroStat,
    LandingPageFeature,
    LandingPricingPlan,
    MembershipPlan,
    Service,
    ServicePackage,
)

ICON_EMOJI = {
    "oil_barrel": "🛢️",
    "tire_repair": "🛞",
    "disc_full": "🛑",
    "ac_unit": "❄️",
    "battery_charging": "🔋",
    "laptop_mac": "💻",
}

FEATURE_ICONS = {
    "price_check": "✓",
    "verified": "✓",
    "shield": "✓",
    "location": "✓",
}

CURRENCY_AR = "دينار"


def _service_icon(icon_key: str | None) -> str:
    if not icon_key:
        return "🔧"
    return ICON_EMOJI.get(icon_key, "🔧")


def _serialize_service(service: Service) -> dict:
    price = float(service.price_sar)
    return {
        "id": str(service.id),
        "slug": service.slug,
        "name_ar": service.name_ar,
        "subtitle_ar": service.subtitle_ar,
        "icon_key": service.icon_key,
        "icon_emoji": _service_icon(service.icon_key),
        "price_sar": price,
        "price_label_ar": f"يبدأ من {int(price) if price == int(price) else price} {CURRENCY_AR}",
        "duration_minutes": service.duration_minutes,
    }


def _serialize_marketing_plan(plan: LandingPricingPlan) -> dict:
    price = float(plan.price_sar)
    return {
        "id": str(plan.id),
        "slug": plan.slug,
        "name_ar": plan.name_ar,
        "description_ar": plan.description_ar,
        "price_sar": price,
        "price_label_ar": plan.price_label_ar,
        "billing_period": plan.billing_period,
        "price_display_ar": (
            "مجاني" if price == 0 else f"{int(price) if price == int(price) else price} {CURRENCY_AR}"
        ),
        "features": plan.features if isinstance(plan.features, list) else [],
        "cta_text_ar": plan.cta_text_ar,
        "cta_url": plan.cta_url,
        "badge_ar": plan.badge_ar,
        "is_featured": plan.is_featured,
    }


def _serialize_membership(plan: MembershipPlan) -> dict:
    price = float(plan.price_sar)
    return {
        "id": str(plan.id),
        "slug": plan.slug,
        "name_ar": plan.name_ar,
        "description_ar": plan.description_ar,
        "price_sar": price,
        "billing_period": plan.billing_period,
        "discount_percent": plan.discount_percent,
        "priority_booking": plan.priority_booking,
        "free_inspection": plan.free_inspection,
    }


def _serialize_package(pkg: ServicePackage) -> dict:
    return {
        "id": str(pkg.id),
        "slug": pkg.slug,
        "name_ar": pkg.name_ar,
        "description_ar": pkg.description_ar,
        "price_sar": float(pkg.price_sar),
        "visits_count": pkg.visits_count,
        "validity_days": pkg.validity_days,
        "savings_sar": float(pkg.savings_sar),
    }


def get_landing_pricing(db: Session) -> dict:
    services = db.scalars(
        select(Service).where(Service.is_active.is_(True)).order_by(Service.price_sar)
    ).all()
    marketing = db.scalars(
        select(LandingPricingPlan)
        .where(LandingPricingPlan.is_active.is_(True))
        .order_by(LandingPricingPlan.sort_order)
    ).all()
    memberships = db.scalars(
        select(MembershipPlan)
        .where(MembershipPlan.is_active.is_(True))
        .order_by(MembershipPlan.sort_order)
    ).all()
    packages = db.scalars(
        select(ServicePackage)
        .where(ServicePackage.is_active.is_(True))
        .order_by(ServicePackage.price_sar)
    ).all()

    return {
        "services": [_serialize_service(s) for s in services],
        "marketing_plans": [_serialize_marketing_plan(p) for p in marketing],
        "membership_plans": [_serialize_membership(m) for m in memberships],
        "packages": [_serialize_package(p) for p in packages],
    }


def get_landing_page(db: Session) -> dict:
    hero_stats = db.scalars(
        select(LandingHeroStat)
        .where(LandingHeroStat.is_active.is_(True))
        .order_by(LandingHeroStat.sort_order)
    ).all()
    features = db.scalars(
        select(LandingPageFeature)
        .where(LandingPageFeature.is_active.is_(True))
        .order_by(LandingPageFeature.sort_order)
    ).all()
    pricing = get_landing_pricing(db)

    return {
        "hero": {
            "stats": [
                {
                    "slug": s.slug,
                    "value_ar": s.value_ar,
                    "label_ar": s.label_ar,
                }
                for s in hero_stats
            ]
        },
        "pricing": pricing,
        "features": [
            {
                "slug": f.slug,
                "title_ar": f.title_ar,
                "description_ar": f.description_ar,
                "icon": FEATURE_ICONS.get(f.icon_key or "", "✓"),
            }
            for f in features
        ],
    }
