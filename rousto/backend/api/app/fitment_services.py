"""Guaranteed fitment — car makes/models/years and part compatibility."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.i18n import pick_localized
from app.models import CarMake, CarModel, CarYear, PartVehicleCompatibility


def _now() -> datetime:
    return datetime.now(timezone.utc)


def list_makes(db: Session, locale: str) -> list[dict]:
    rows = db.scalars(
        select(CarMake)
        .where(CarMake.is_active.is_(True))
        .order_by(CarMake.sort_order, CarMake.name_ar)
    ).all()
    return [
        {
            "id": m.id,
            "slug": m.slug,
            "name": pick_localized(m, "name", locale),
            "name_ar": m.name_ar,
        }
        for m in rows
    ]


def list_models(db: Session, make_id: uuid.UUID, locale: str) -> list[dict]:
    rows = db.scalars(
        select(CarModel)
        .where(CarModel.make_id == make_id, CarModel.is_active.is_(True))
        .order_by(CarModel.name_ar)
    ).all()
    return [
        {
            "id": m.id,
            "slug": m.slug,
            "make_id": m.make_id,
            "name": pick_localized(m, "name", locale),
            "name_ar": m.name_ar,
        }
        for m in rows
    ]


def list_years(db: Session, model_id: uuid.UUID) -> list[dict]:
    rows = db.scalars(
        select(CarYear)
        .where(CarYear.model_id == model_id, CarYear.is_active.is_(True))
        .order_by(CarYear.year.desc())
    ).all()
    return [{"id": y.id, "model_id": y.model_id, "year": y.year} for y in rows]


def resolve_car_year(
    db: Session,
    *,
    make_slug: str | None = None,
    model_slug: str | None = None,
    year: int | None = None,
    car_year_id: uuid.UUID | None = None,
) -> CarYear | None:
    if car_year_id:
        return db.scalar(
            select(CarYear)
            .options(joinedload(CarYear.model).joinedload(CarModel.make))
            .where(CarYear.id == car_year_id, CarYear.is_active.is_(True))
        )
    if not (make_slug and model_slug and year):
        return None
    return db.scalar(
        select(CarYear)
        .join(CarModel, CarModel.id == CarYear.model_id)
        .join(CarMake, CarMake.id == CarModel.make_id)
        .where(
            CarMake.slug == make_slug,
            CarModel.slug == model_slug,
            CarYear.year == year,
            CarYear.is_active.is_(True),
        )
        .options(joinedload(CarYear.model).joinedload(CarModel.make))
    )


def car_year_out(car_year: CarYear, locale: str) -> dict:
    model = car_year.model
    make = model.make if model else None
    return {
        "car_year_id": car_year.id,
        "year": car_year.year,
        "model": {
            "id": model.id,
            "slug": model.slug,
            "name": pick_localized(model, "name", locale),
        }
        if model
        else None,
        "make": {
            "id": make.id,
            "slug": make.slug,
            "name": pick_localized(make, "name", locale),
        }
        if make
        else None,
    }


def part_ids_for_car_year(db: Session, car_year_id: uuid.UUID) -> set[uuid.UUID]:
    rows = db.scalars(
        select(PartVehicleCompatibility.part_id).where(
            PartVehicleCompatibility.car_year_id == car_year_id
        )
    ).all()
    return set(rows)


def add_part_compatibility(
    db: Session,
    *,
    part_id: uuid.UUID,
    car_year_id: uuid.UUID,
    fitment_note_ar: str | None = None,
) -> PartVehicleCompatibility:
    existing = db.scalar(
        select(PartVehicleCompatibility).where(
            PartVehicleCompatibility.part_id == part_id,
            PartVehicleCompatibility.car_year_id == car_year_id,
        )
    )
    if existing:
        return existing
    row = PartVehicleCompatibility(
        id=uuid.uuid4(),
        part_id=part_id,
        car_year_id=car_year_id,
        fitment_note_ar=fitment_note_ar,
        created_at=_now(),
    )
    db.add(row)
    db.flush()
    return row


def list_part_compatibilities(db: Session, part_id: uuid.UUID, locale: str) -> list[dict]:
    links = db.scalars(
        select(PartVehicleCompatibility).where(
            PartVehicleCompatibility.part_id == part_id
        )
    ).all()

    result = []
    for link in links:
        cy = db.scalar(
            select(CarYear)
            .options(joinedload(CarYear.model).joinedload(CarModel.make))
            .where(CarYear.id == link.car_year_id)
        )
        if cy:
            result.append(
                {
                    "id": link.id,
                    "fitment": car_year_out(cy, locale),
                    "fitment_note_ar": link.fitment_note_ar,
                }
            )
    return result
