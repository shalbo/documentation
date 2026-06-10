"""Libyan cities lookup for registration, shipping, and filters."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import City

VALID_REGIONS = frozenset({"West", "East", "South"})


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


def list_cities_admin(
    db: Session,
    *,
    region: str | None = None,
    active_only: bool | None = None,
) -> list[dict]:
    stmt = select(City).order_by(City.region, City.name_ar)
    if active_only is not None:
        stmt = stmt.where(City.is_active.is_(active_only))
    if region:
        stmt = stmt.where(City.region == region)
    rows = db.scalars(stmt).all()
    return [city_out(r) for r in rows]


def get_city_or_none(db: Session, city_id: uuid.UUID) -> City | None:
    return db.get(City, city_id)


def create_city(
    db: Session,
    *,
    name_ar: str,
    name_en: str,
    region: str,
    is_active: bool = True,
) -> City:
    if region not in VALID_REGIONS:
        raise ValueError("الإقليم يجب أن يكون West أو East أو South")
    now = datetime.now(timezone.utc)
    city = City(
        id=uuid.uuid4(),
        name_ar=name_ar.strip(),
        name_en=name_en.strip(),
        region=region,
        is_active=is_active,
        created_at=now,
        updated_at=now,
    )
    db.add(city)
    db.flush()
    return city


def update_city(
    db: Session,
    city: City,
    *,
    name_ar: str | None = None,
    name_en: str | None = None,
    region: str | None = None,
    is_active: bool | None = None,
) -> City:
    if name_ar is not None:
        city.name_ar = name_ar.strip()
    if name_en is not None:
        city.name_en = name_en.strip()
    if region is not None:
        if region not in VALID_REGIONS:
            raise ValueError("الإقليم يجب أن يكون West أو East أو South")
        city.region = region
    if is_active is not None:
        city.is_active = is_active
    city.updated_at = datetime.now(timezone.utc)
    db.flush()
    return city
