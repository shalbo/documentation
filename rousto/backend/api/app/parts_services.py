"""Spare parts catalog — search, booking parts, warranty claims."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.category_services import collect_filter_category_ids, is_leaf_category
from app.fitment_services import part_ids_for_car_year
from app.vin_compat_services import (
    apply_where_compatible_with_vin,
    list_vin_prefixes_for_part,
)
from app.i18n import pick_localized
from app.models import (
    Booking,
    BookingPart,
    Part,
    PartCategory,
    PartInventory,
    PartSupplier,
    PartWarrantyClaim,
    Vendor,
)

WARRANTY_STATUSES = frozenset({"open", "in_review", "resolved", "rejected"})


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _vendor_store_visible() -> tuple:
    return (
        Vendor.status == "approved",
        Vendor.is_active.is_(True),
    )


def _part_has_only_inactive_vendor_stock(db: Session, part_id: uuid.UUID) -> bool:
    rows = db.execute(
        select(PartInventory.qty_available, Vendor.is_active, Vendor.status)
        .join(Vendor, Vendor.id == PartInventory.vendor_id)
        .where(PartInventory.part_id == part_id, PartInventory.qty_available > 0)
    ).all()
    if not rows:
        return False
    return not any(
        qty > 0 and status == "approved" and is_active for qty, is_active, status in rows
    )


def _vendors_in_stock(db: Session, part_id: uuid.UUID) -> list[dict]:
    rows = db.execute(
        select(PartInventory, Vendor)
        .join(Vendor, Vendor.id == PartInventory.vendor_id)
        .where(
            PartInventory.part_id == part_id,
            PartInventory.qty_available > 0,
            *_vendor_store_visible(),
        )
    ).all()
    return [
        {
            "vendor_id": v.id,
            "business_name": v.business_name,
            "city": v.city,
            "qty_available": inv.qty_available,
        }
        for inv, v in rows
    ]


def part_out(
    part: Part,
    locale: str,
    *,
    db: Session | None = None,
    vendors: list[dict] | None = None,
) -> dict:
    data = {
        "id": part.id,
        "part_number": part.part_number,
        "oem_number": part.oem_number or part.part_number,
        "vin_prefix": part.vin_prefix,
        "vin_prefixes": list_vin_prefixes_for_part(db, part.id)
        if db
        else [],
        "slug": part.slug,
        "name": pick_localized(part, "name", locale),
        "name_ar": part.name_ar,
        "description_ar": part.description_ar,
        "is_oem": part.is_oem,
        "part_condition": part.part_condition,
        "condition": part.part_condition,
        "price_sar": float(part.price_sar),
        "warranty_months": part.warranty_months,
        "vehicle_compatibility": part.vehicle_compatibility or [],
        "image_url": part.image_url,
        "category": {
            "slug": part.category.slug,
            "name": pick_localized(part.category, "name", locale),
        }
        if part.category
        else None,
        "supplier": {
            "slug": part.supplier.slug,
            "name": pick_localized(part.supplier, "name", locale),
            "is_oem": part.supplier.is_oem,
        }
        if part.supplier
        else None,
    }
    if vendors is not None:
        data["vendors_in_stock"] = vendors
        data["stock_total"] = sum(v["qty_available"] for v in vendors)
    return data


def list_part_categories(db: Session, locale: str) -> list[dict]:
    rows = db.scalars(
        select(PartCategory)
        .where(PartCategory.is_active.is_(True))
        .order_by(PartCategory.sort_order)
    ).all()
    return [
        {
            "id": c.id,
            "slug": c.slug,
            "name": pick_localized(c, "name", locale),
            "name_ar": c.name_ar,
        }
        for c in rows
    ]


def search_parts(
    db: Session,
    *,
    query: str | None = None,
    category: str | None = None,
    category_id: uuid.UUID | None = None,
    make: str | None = None,
    model: str | None = None,
    car_year_id: uuid.UUID | None = None,
    oem: str | None = None,
    vin: str | None = None,
    oem_only: bool = False,
    in_stock_only: bool = False,
    condition: str | None = None,
    locale: str = "ar",
    limit: int = 50,
) -> list[dict]:
    stmt = (
        select(Part)
        .options(joinedload(Part.category), joinedload(Part.supplier))
        .where(Part.is_active.is_(True))
    )

    if category_id:
        filter_ids = collect_filter_category_ids(db, category_id)
        if not filter_ids:
            return []
        stmt = stmt.where(Part.category_id.in_(filter_ids))
    elif category:
        stmt = stmt.join(PartCategory).where(PartCategory.slug == category)

    if oem_only:
        stmt = stmt.where(Part.is_oem.is_(True))

    if condition:
        stmt = stmt.where(Part.part_condition == condition)

    if oem:
        oem_clean = oem.strip().upper()
        stmt = stmt.where(
            or_(
                func.upper(Part.oem_number) == oem_clean,
                func.upper(Part.part_number) == oem_clean,
            )
        )

    if vin:
        stmt = apply_where_compatible_with_vin(stmt, db, vin)

    if query and not vin:
        needle = f"%{query.strip()}%"
        stmt = stmt.where(
            or_(
                Part.name_ar.ilike(needle),
                Part.name_en.ilike(needle),
                Part.part_number.ilike(needle),
                Part.oem_number.ilike(needle),
                Part.slug.ilike(needle),
            )
        )

    if in_stock_only:
        stmt = (
            stmt.join(PartInventory, PartInventory.part_id == Part.id)
            .join(Vendor, Vendor.id == PartInventory.vendor_id)
            .where(
                PartInventory.qty_available > 0,
                *_vendor_store_visible(),
            )
            .distinct()
        )

    fitment_ids: set[uuid.UUID] | None = None
    if car_year_id:
        fitment_ids = part_ids_for_car_year(db, car_year_id)
        if not fitment_ids:
            return []
        stmt = stmt.where(Part.id.in_(fitment_ids))

    parts = db.scalars(stmt.order_by(Part.name_ar).limit(limit)).unique().all()

    results = []
    for part in parts:
        if make or model:
            compat = part.vehicle_compatibility or []
            if not _matches_vehicle(compat, make, model):
                continue
        if _part_has_only_inactive_vendor_stock(db, part.id):
            continue
        vendors = _vendors_in_stock(db, part.id)
        if in_stock_only and not vendors:
            continue
        results.append(part_out(part, locale, db=db, vendors=vendors))
    return results


def _matches_vehicle(
    compat: list[dict[str, Any]],
    make: str | None,
    model: str | None,
) -> bool:
    if not compat:
        return True
    for entry in compat:
        entry_make = str(entry.get("make", "*"))
        entry_model = str(entry.get("model", "*"))
        if make and entry_make not in {"*", make}:
            continue
        if model and entry_model not in {"*", model}:
            continue
        return True
    return False


def get_part_detail(db: Session, part_id: uuid.UUID, locale: str) -> dict | None:
    part = db.scalar(
        select(Part)
        .options(joinedload(Part.category), joinedload(Part.supplier))
        .where(Part.id == part_id, Part.is_active.is_(True))
    )
    if not part:
        return None

    if _part_has_only_inactive_vendor_stock(db, part_id):
        return None

    vendors = _vendors_in_stock(db, part_id)
    return part_out(part, locale, db=db, vendors=vendors)


def list_booking_parts(db: Session, booking_id: uuid.UUID, locale: str) -> list[dict]:
    rows = db.scalars(
        select(BookingPart)
        .options(joinedload(BookingPart.part).joinedload(Part.category))
        .where(BookingPart.booking_id == booking_id)
        .order_by(BookingPart.installed_at.desc())
    ).unique().all()

    return [
        {
            "id": row.id,
            "part_id": row.part_id,
            "part_number": row.part.part_number,
            "name": pick_localized(row.part, "name", locale),
            "qty": row.qty,
            "unit_price_sar": float(row.unit_price_sar),
            "warranty_expires_at": row.warranty_expires_at,
            "is_oem": row.part.is_oem,
        }
        for row in rows
    ]


def attach_part_to_booking(
    db: Session,
    booking: Booking,
    *,
    part_id: uuid.UUID,
    vendor_id: uuid.UUID | None,
    qty: int = 1,
) -> BookingPart:
    part = db.get(Part, part_id)
    if not part or not part.is_active:
        raise ValueError("القطعة غير موجودة")

    warranty_end = _now() + timedelta(days=30 * part.warranty_months)
    row = BookingPart(
        id=uuid.uuid4(),
        booking_id=booking.id,
        part_id=part_id,
        vendor_id=vendor_id,
        qty=qty,
        unit_price_sar=float(part.price_sar),
        warranty_expires_at=warranty_end,
        installed_at=_now(),
    )
    db.add(row)

    if vendor_id:
        inv = db.scalar(
            select(PartInventory).where(
                PartInventory.vendor_id == vendor_id,
                PartInventory.part_id == part_id,
            )
        )
        if inv and inv.qty_available >= qty:
            inv.qty_available -= qty
            inv.updated_at = _now()

    return row


def create_warranty_claim(
    db: Session,
    *,
    user_id: uuid.UUID,
    booking_part_id: uuid.UUID,
    description: str,
) -> PartWarrantyClaim:
    booking_part = db.scalar(
        select(BookingPart)
        .options(joinedload(BookingPart.part))
        .where(BookingPart.id == booking_part_id)
    )
    if not booking_part:
        raise ValueError("سجل القطعة غير موجود")

    booking = db.get(Booking, booking_part.booking_id)
    if not booking or booking.user_id != user_id:
        raise ValueError("لا تملك صلاحية على هذا الحجز")

    existing = db.scalar(
        select(PartWarrantyClaim).where(
            PartWarrantyClaim.booking_part_id == booking_part_id,
            PartWarrantyClaim.status.in_(("open", "in_review")),
        )
    )
    if existing:
        raise ValueError("توجد مطالبة ضمان مفتوحة لهذه القطعة")

    claim = PartWarrantyClaim(
        id=uuid.uuid4(),
        booking_part_id=booking_part_id,
        user_id=user_id,
        description=description.strip(),
        status="open",
        created_at=_now(),
    )
    db.add(claim)
    return claim


def list_warranty_claims_admin(
    db: Session,
    *,
    status: str | None = None,
    limit: int = 50,
) -> list[dict]:
    query = (
        select(PartWarrantyClaim)
        .order_by(PartWarrantyClaim.created_at.desc())
        .limit(limit)
    )
    if status:
        query = query.where(PartWarrantyClaim.status == status)

    rows = db.scalars(query).all()
    return [
        {
            "id": c.id,
            "booking_part_id": c.booking_part_id,
            "user_id": c.user_id,
            "description": c.description,
            "status": c.status,
            "created_at": c.created_at,
        }
        for c in rows
    ]


def list_parts_admin(db: Session, locale: str = "ar") -> list[dict]:
    parts = db.scalars(
        select(Part)
        .options(joinedload(Part.category), joinedload(Part.supplier))
        .order_by(Part.name_ar)
    ).unique().all()
    return [part_out(p, locale, db=db) for p in parts]


def create_part(
    db: Session,
    *,
    part_number: str,
    slug: str,
    name_ar: str,
    category_id: uuid.UUID,
    price_sar: float,
    name_en: str | None = None,
    supplier_id: uuid.UUID | None = None,
    is_oem: bool = False,
    warranty_months: int = 6,
    vehicle_compatibility: list | None = None,
    oem_number: str | None = None,
    vin_prefix: str | None = None,
    description_ar: str | None = None,
    part_condition: str = "new",
    require_leaf_category: bool = False,
) -> Part:
    if require_leaf_category and not is_leaf_category(db, category_id):
        raise ValueError("يجب اختيار قسم فرعي قبل حفظ القطعة")
    part = Part(
        id=uuid.uuid4(),
        part_number=part_number.strip(),
        oem_number=(oem_number or part_number).strip(),
        vin_prefix=vin_prefix.strip() if vin_prefix else None,
        slug=slug.strip(),
        name_ar=name_ar,
        name_en=name_en,
        description_ar=description_ar,
        category_id=category_id,
        supplier_id=supplier_id,
        is_oem=is_oem,
        part_condition=part_condition,
        price_sar=price_sar,
        warranty_months=warranty_months,
        vehicle_compatibility=vehicle_compatibility or [],
        is_active=True,
        created_at=_now(),
    )
    db.add(part)
    db.flush()
    return part
