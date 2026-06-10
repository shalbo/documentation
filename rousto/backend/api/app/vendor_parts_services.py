"""Vendor product listing — create parts with inventory under leaf categories."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import PartInventory, Vendor
from app.parts_services import create_part, part_out
from app.tier_services import ensure_products_capacity, require_vin_decoder
from app.vin_compat_services import add_part_vin_compatibilities, parse_vin_prefixes


def _now() -> datetime:
    return datetime.now(timezone.utc)


def vendor_create_product(
    db: Session,
    vendor: Vendor,
    *,
    category_id: uuid.UUID,
    part_number: str,
    slug: str,
    name_ar: str,
    price_sar: float,
    qty_available: int,
    name_en: str | None = None,
    oem_number: str | None = None,
    vin_prefix: str | None = None,
    vin_prefixes: list[str] | None = None,
    is_oem: bool = False,
    part_condition: str = "new",
    warranty_months: int = 6,
    locale: str = "ar",
) -> dict:
    if vendor.status != "approved":
        raise ValueError("المحل غير معتمد بعد")

    ensure_products_capacity(db, vendor)
    prefixes = parse_vin_prefixes(vin_prefixes or vin_prefix)
    if prefixes:
        require_vin_decoder(db, vendor)
    part = create_part(
        db,
        part_number=part_number,
        slug=slug,
        name_ar=name_ar,
        name_en=name_en,
        category_id=category_id,
        price_sar=price_sar,
        oem_number=oem_number,
        vin_prefix=prefixes[0] if prefixes else vin_prefix,
        is_oem=is_oem,
        part_condition=part_condition,
        warranty_months=warranty_months,
        require_leaf_category=True,
    )
    if prefixes:
        add_part_vin_compatibilities(db, part.id, prefixes)

    inv = PartInventory(
        id=uuid.uuid4(),
        vendor_id=vendor.id,
        part_id=part.id,
        qty_available=qty_available,
        cost_sar=round(price_sar * 0.75, 2),
        updated_at=_now(),
    )
    db.add(inv)
    db.flush()

    data = part_out(part, locale, db=db)
    data["vin_prefixes"] = prefixes
    data["inventory"] = {
        "vendor_id": vendor.id,
        "qty_available": qty_available,
    }
    return data
