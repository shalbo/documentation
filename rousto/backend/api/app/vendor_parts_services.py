"""Vendor product listing — create parts with inventory under leaf categories."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import PartInventory, Vendor
from app.parts_services import create_part, part_out


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
    is_oem: bool = False,
    warranty_months: int = 6,
    locale: str = "ar",
) -> dict:
    if vendor.status != "approved":
        raise ValueError("المحل غير معتمد بعد")

    part = create_part(
        db,
        part_number=part_number,
        slug=slug,
        name_ar=name_ar,
        name_en=name_en,
        category_id=category_id,
        price_sar=price_sar,
        oem_number=oem_number,
        vin_prefix=vin_prefix,
        is_oem=is_oem,
        warranty_months=warranty_months,
        require_leaf_category=True,
    )

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

    data = part_out(part, locale)
    data["inventory"] = {
        "vendor_id": vendor.id,
        "qty_available": qty_available,
    }
    return data
