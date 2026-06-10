"""Spare parts marketplace — home feed, vendor geo search, admin analytics."""

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.logistics_services import haversine_km
from app.models import (
    BookingPart,
    Part,
    PartInventory,
    PartWarrantyClaim,
    Promotion,
    Vendor,
)
from app.category_services import get_category_tree, list_root_categories
from app.fitment_services import part_ids_for_car_year
from app.parts_services import part_out

DEFAULT_LAT = 24.7136
DEFAULT_LNG = 46.6753


def _vendor_out(vendor: Vendor, locale: str, *, distance_km: float | None = None) -> dict:
    data: dict[str, Any] = {
        "id": vendor.id,
        "business_name": vendor.business_name,
        "city": vendor.city,
        "status": vendor.status,
    }
    if vendor.base_lat is not None and vendor.base_lng is not None:
        data["location"] = {
            "lat": float(vendor.base_lat),
            "lng": float(vendor.base_lng),
        }
    if distance_km is not None:
        data["distance_km"] = round(distance_km, 2)
    return data


def list_featured_vendors(db: Session, locale: str, *, limit: int = 6) -> list[dict]:
    stmt = (
        select(Vendor, func.count(PartInventory.id).label("sku_count"))
        .join(PartInventory, PartInventory.vendor_id == Vendor.id)
        .where(Vendor.status == "approved", PartInventory.qty_available > 0)
        .group_by(Vendor.id)
        .order_by(func.count(PartInventory.id).desc())
        .limit(limit)
    )
    rows = db.execute(stmt).all()
    return [_vendor_out(v, locale) for v, _ in rows]


def list_featured_parts(
    db: Session,
    locale: str,
    *,
    car_year_id: uuid.UUID | None = None,
    limit: int = 8,
) -> list[dict]:
    stmt = (
        select(Part)
        .options(joinedload(Part.category), joinedload(Part.supplier))
        .where(Part.is_active.is_(True))
    )
    if car_year_id:
        fit_ids = part_ids_for_car_year(db, car_year_id)
        if not fit_ids:
            return []
        stmt = stmt.where(Part.id.in_(fit_ids))
    parts = db.scalars(
        stmt.order_by(Part.is_oem.desc(), Part.name_ar).limit(limit)
    ).unique().all()
    return [part_out(p, locale) for p in parts]


def get_marketplace_home(
    db: Session,
    locale: str,
    *,
    car_year_id: uuid.UUID | None = None,
) -> dict:
    promotions = db.scalars(
        select(Promotion)
        .where(Promotion.is_active.is_(True))
        .order_by(Promotion.starts_at.desc())
        .limit(3)
    ).all()

    return {
        "categories": list_root_categories(db, locale),
        "category_tree": get_category_tree(db, locale),
        "featured_parts": list_featured_parts(db, locale, car_year_id=car_year_id),
        "featured_vendors": list_featured_vendors(db, locale),
        "promotions": [
            {
                "id": p.id,
                "code": p.code,
                "title": p.title_ar,
                "title_ar": p.title_ar,
                "discount_value": float(p.discount_value),
                "discount_type": p.discount_type,
            }
            for p in promotions
        ],
        "default_location": {"lat": DEFAULT_LAT, "lng": DEFAULT_LNG},
    }


def find_vendors_nearby_for_part(
    db: Session,
    part_id: uuid.UUID,
    *,
    lat: float,
    lng: float,
    locale: str = "ar",
    limit: int = 20,
    max_radius_km: float = 50.0,
) -> list[dict]:
    part = db.scalar(
        select(Part).where(Part.id == part_id, Part.is_active.is_(True))
    )
    if not part:
        return []

    stmt = (
        select(PartInventory, Vendor)
        .join(Vendor, Vendor.id == PartInventory.vendor_id)
        .where(
            PartInventory.part_id == part_id,
            PartInventory.qty_available > 0,
            Vendor.status == "approved",
            Vendor.base_lat.isnot(None),
            Vendor.base_lng.isnot(None),
        )
    )
    inventory_rows = db.execute(stmt).all()

    results: list[dict] = []
    for inv, vendor in inventory_rows:
        v_lat = float(vendor.base_lat)  # type: ignore[arg-type]
        v_lng = float(vendor.base_lng)  # type: ignore[arg-type]
        dist = haversine_km(lat, lng, v_lat, v_lng)
        radius = float(vendor.service_radius_km or max_radius_km)
        if dist > max(radius, max_radius_km):
            continue
        entry = _vendor_out(vendor, locale, distance_km=dist)
        entry["qty_available"] = inv.qty_available
        entry["part_price_sar"] = float(part.price_sar)
        results.append(entry)

    results.sort(key=lambda x: x.get("distance_km", 999))
    return results[:limit]


def get_marketplace_analytics(db: Session) -> dict:
    parts_count = db.scalar(
        select(func.count()).select_from(Part).where(Part.is_active.is_(True))
    ) or 0
    vendors_with_stock = db.scalar(
        select(func.count(func.distinct(PartInventory.vendor_id))).where(
            PartInventory.qty_available > 0
        )
    ) or 0
    low_stock = db.scalar(
        select(func.count()).select_from(PartInventory).where(
            PartInventory.qty_available > 0,
            PartInventory.qty_available <= 5,
        )
    ) or 0
    open_warranty = db.scalar(
        select(func.count())
        .select_from(PartWarrantyClaim)
        .where(PartWarrantyClaim.status.in_(("open", "in_review")))
    ) or 0
    parts_sold = db.scalar(select(func.count()).select_from(BookingPart)) or 0
    inventory_units = db.scalar(
        select(func.coalesce(func.sum(PartInventory.qty_available), 0))
    ) or 0

    return {
        "active_parts": parts_count,
        "vendors_with_stock": vendors_with_stock,
        "inventory_units": int(inventory_units),
        "low_stock_skus": low_stock,
        "parts_sold_total": parts_sold,
        "open_warranty_claims": open_warranty,
    }
