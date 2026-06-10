"""Libyan cities lookup for registration, shipping, and filters."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import City


def city_out(c: City) -> dict:
    return {
        "id": str(c.id),
        "name_ar": c.name_ar,
        "name_en": c.name_en,
        "region": c.region,
        "is_active": c.is_active,
    }


def list_cities(
    db: Session,
    *,
    region: str | None = None,
    active_only: bool = True,
) -> list[dict]:
    stmt = select(City).order_by(City.region, City.name_ar)
    if active_only:
        stmt = stmt.where(City.is_active.is_(True))
    if region:
        stmt = stmt.where(City.region == region)
    rows = db.scalars(stmt).all()
    return [city_out(r) for r in rows]


def resolve_city(
    db: Session,
    *,
    city_id: uuid.UUID | None = None,
    name_ar: str | None = None,
) -> City | None:
    if city_id:
        return db.get(City, city_id)
    if name_ar:
        return db.scalar(
            select(City).where(City.name_ar == name_ar.strip(), City.is_active.is_(True))
        )
    return None


def validate_city_name(db: Session, name_ar: str) -> City:
    city = resolve_city(db, name_ar=name_ar)
    if not city:
        raise ValueError("اختر مدينة من القائمة المعتمدة")
    return city
