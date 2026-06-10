"""VIN prefix ↔ spare part compatibility (Guaranteed Fitment by VIN)."""

import re
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Part, PartVinCompatibility

VIN_PATTERN = re.compile(r"^[A-HJ-NPR-Z0-9]{11,17}$", re.IGNORECASE)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_vin_prefix(full_vin: str) -> str:
    """Extract the fixed 11-character WMI+VDS prefix from a full VIN."""
    cleaned = full_vin.strip().upper().replace(" ", "").replace("-", "")
    if len(cleaned) < 11:
        raise ValueError("رقم الهيكل يجب أن يحتوي 11 رمزاً على الأقل")
    if not VIN_PATTERN.match(cleaned[:17]):
        raise ValueError("رقم الهيكل يحتوي رموزاً غير صالحة")
    return cleaned[:11]


def parse_vin_prefixes(raw: str | list[str] | None) -> list[str]:
    if not raw:
        return []
    if isinstance(raw, list):
        items = raw
    else:
        items = re.split(r"[\s,;]+", raw.strip())
    prefixes: list[str] = []
    for item in items:
        item = item.strip()
        if not item:
            continue
        prefixes.append(normalize_vin_prefix(item))
    return list(dict.fromkeys(prefixes))


def part_ids_compatible_with_vin(db: Session, full_vin: str) -> set[uuid.UUID]:
    prefix = normalize_vin_prefix(full_vin)
    rows = db.scalars(
        select(PartVinCompatibility.part_id).where(
            PartVinCompatibility.vin_prefix == prefix
        )
    ).all()
    return set(rows)


def apply_where_compatible_with_vin(stmt, db: Session, full_vin: str):
    """Strict scope: only parts explicitly linked to the VIN prefix."""
    part_ids = part_ids_compatible_with_vin(db, full_vin)
    if not part_ids:
        return stmt.where(Part.id.in_([]))
    return stmt.where(Part.id.in_(part_ids))


def list_vin_prefixes_for_part(db: Session, part_id: uuid.UUID) -> list[str]:
    rows = db.scalars(
        select(PartVinCompatibility.vin_prefix)
        .where(PartVinCompatibility.part_id == part_id)
        .order_by(PartVinCompatibility.vin_prefix)
    ).all()
    return list(rows)


def add_part_vin_compatibilities(
    db: Session,
    part_id: uuid.UUID,
    prefixes: list[str],
) -> list[PartVinCompatibility]:
    created: list[PartVinCompatibility] = []
    for prefix in prefixes:
        existing = db.scalar(
            select(PartVinCompatibility).where(
                PartVinCompatibility.part_id == part_id,
                PartVinCompatibility.vin_prefix == prefix,
            )
        )
        if existing:
            created.append(existing)
            continue
        row = PartVinCompatibility(
            id=uuid.uuid4(),
            part_id=part_id,
            vin_prefix=prefix,
            created_at=_now(),
        )
        db.add(row)
        created.append(row)
    if prefixes:
        part = db.get(Part, part_id)
        if part and not part.vin_prefix:
            part.vin_prefix = prefixes[0]
    db.flush()
    return created


def replace_part_vin_compatibilities(
    db: Session,
    part_id: uuid.UUID,
    prefixes: list[str],
) -> list[PartVinCompatibility]:
    existing = db.scalars(
        select(PartVinCompatibility).where(PartVinCompatibility.part_id == part_id)
    ).all()
    for row in existing:
        db.delete(row)
    db.flush()
    return add_part_vin_compatibilities(db, part_id, prefixes)
