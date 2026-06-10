#!/usr/bin/env python3
"""Equivalent to: php artisan db:seed --class=VinDecoderSeeder

Re-runs Libyan market VIN decoder upserts against PostgreSQL.
Usage: cd rousto/backend/api && python3 ../scripts/seed_vin_decoders_libya.py
"""

import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

API_DIR = Path(__file__).resolve().parents[1] / "api"
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from app.config import settings  # noqa: E402

SEED_FILE = Path(__file__).resolve().parents[1] / "database" / "044_vin_decoders_libya_seed.sql"
SCHEMA_FILE = Path(__file__).resolve().parents[1] / "database" / "044_vin_decoders_schema.sql"


def main() -> None:
    engine = create_engine(settings.database_url)
    schema_sql = SCHEMA_FILE.read_text(encoding="utf-8")
    seed_sql = SEED_FILE.read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.execute(text(schema_sql))
        conn.execute(text(seed_sql))
    print(f"Seeded vin_decoders from {SEED_FILE.name}")


if __name__ == "__main__":
    main()
