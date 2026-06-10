"""Libyan market VIN decoder — WMI+VDS prefix lookup."""

import re
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import VinDecoder

VIN_CLEAN = re.compile(r"^[A-HJ-NPR-Z0-9]{8,17}$", re.IGNORECASE)


def _clean_vin(full_vin: str) -> str:
    cleaned = full_vin.strip().upper().replace(" ", "").replace("-", "")
    if len(cleaned) < 8:
        raise ValueError("رقم الهيكل قصير جداً — أدخل 8 رموز على الأقل")
    if not VIN_CLEAN.match(cleaned[:17]):
        raise ValueError("رقم الهيكل يحتوي رموزاً غير صالحة")
    return cleaned[:17]


def decode_vin(db: Session, full_vin: str) -> dict | None:
    """Longest-prefix match against vin_decoders (Libyan market catalog)."""
    vin = _clean_vin(full_vin)
    rows = db.scalars(
        select(VinDecoder)
        .where(VinDecoder.market == "libya")
        .order_by(func.length(VinDecoder.vin_prefix).desc())
    ).all()
    for row in rows:
        if vin.startswith(row.vin_prefix.upper()):
            return _decoder_out(row, matched_prefix=row.vin_prefix, input_vin=vin)
    return None


def _decoder_out(row: VinDecoder, *, matched_prefix: str, input_vin: str) -> dict:
    return {
        "vin_prefix": matched_prefix,
        "input_vin": input_vin,
        "make": row.make,
        "model": row.model,
        "year_range": row.year_range,
        "engine": row.engine,
        "market": row.market,
        "label_ar": f"{row.make} {row.model} ({row.year_range})",
    }


def list_decoders_admin(db: Session, *, limit: int = 100) -> list[dict]:
    rows = db.scalars(
        select(VinDecoder).order_by(VinDecoder.make, VinDecoder.model).limit(limit)
    ).all()
    return [
        {
            "id": r.id,
            "vin_prefix": r.vin_prefix,
            "make": r.make,
            "model": r.model,
            "year_range": r.year_range,
            "engine": r.engine,
            "market": r.market,
        }
        for r in rows
    ]


def upsert_decoder(
    db: Session,
    *,
    vin_prefix: str,
    make: str,
    model: str,
    year_range: str | None = None,
    engine: str | None = None,
    market: str = "libya",
) -> VinDecoder:
    prefix = vin_prefix.strip().upper()[:11]
    existing = db.scalar(
        select(VinDecoder).where(VinDecoder.vin_prefix == prefix)
    )
    now = datetime.now(timezone.utc)
    if existing:
        existing.make = make
        existing.model = model
        existing.year_range = year_range
        existing.engine = engine
        existing.market = market
        existing.updated_at = now
        return existing
    row = VinDecoder(
        id=uuid.uuid4(),
        vin_prefix=prefix,
        make=make,
        model=model,
        year_range=year_range,
        engine=engine,
        market=market,
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    db.flush()
    return row
