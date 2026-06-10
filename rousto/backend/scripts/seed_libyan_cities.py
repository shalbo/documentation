#!/usr/bin/env python3
"""Equivalent to: php artisan db:seed --class=CitySeeder

Usage: cd rousto/backend/api && python3 ../scripts/seed_libyan_cities.py
"""

import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

API_DIR = Path(__file__).resolve().parents[1] / "api"
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from app.city_seed_data import LIBYAN_CITIES  # noqa: E402
from app.config import settings  # noqa: E402
from app.models import City  # noqa: E402

SCHEMA = Path(__file__).resolve().parents[1] / "database" / "047_cities_schema.sql"
SEED_SQL = Path(__file__).resolve().parents[1] / "database" / "047_libyan_cities_seed.sql"


def seed_cities(db: Session) -> int:
    now = datetime.now(timezone.utc)
    count = 0
    for cid_str, name_ar, name_en, region in LIBYAN_CITIES:
        cid = uuid.UUID(cid_str)
        row = db.scalar(select(City).where(City.name_en == name_en))
        if row:
            row.name_ar = name_ar
            row.region = region
            row.is_active = True
            row.updated_at = now
        else:
            db.add(
                City(
                    id=cid,
                    name_ar=name_ar,
                    name_en=name_en,
                    region=region,
                    is_active=True,
                    created_at=now,
                    updated_at=now,
                )
            )
        count += 1
    return count


def main() -> None:
    engine = create_engine(settings.database_url)
    schema_sql = SCHEMA.read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.exec_driver_sql(schema_sql)
    with Session(engine) as db:
        n = seed_cities(db)
        db.commit()
    print(f"Seeded {n} Libyan cities (CitySeeder)")


if __name__ == "__main__":
    main()
