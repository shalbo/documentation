#!/usr/bin/env python3
"""Equivalent to: php artisan db:seed --class=CategorySeeder

Upserts main & sub part_categories with parent_id tree.
Usage: cd rousto/backend/api && python3 ../scripts/seed_categories_tree.py
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

from app.category_seed_data import (  # noqa: E402
    MAIN_CATEGORIES,
    MAIN_CATEGORY_IDS,
    SUB_CATEGORIES,
    SUB_CATEGORY_IDS,
)
from app.config import settings  # noqa: E402
from app.models import PartCategory  # noqa: E402

SEED_SQL = Path(__file__).resolve().parents[1] / "database" / "045_part_categories_comprehensive_seed.sql"


def _upsert(
    db: Session,
    *,
    cat_id: uuid.UUID,
    slug: str,
    name_ar: str,
    name_en: str,
    parent_id: uuid.UUID | None,
    sort_order: int,
    icon_key: str | None,
) -> None:
    now = datetime.now(timezone.utc)
    row = db.scalar(select(PartCategory).where(PartCategory.slug == slug))
    if row:
        row.name_ar = name_ar
        row.name_en = name_en
        row.parent_id = parent_id
        row.sort_order = sort_order
        row.icon_key = icon_key
        row.is_active = True
        return
    db.add(
        PartCategory(
            id=cat_id,
            slug=slug,
            name_ar=name_ar,
            name_en=name_en,
            parent_id=parent_id,
            sort_order=sort_order,
            icon_key=icon_key,
            is_active=True,
        )
    )


def seed_tree(db: Session) -> tuple[int, int]:
    main_ids: dict[str, uuid.UUID] = {}
    for order, (slug, (name_ar, name_en, icon_key)) in enumerate(
        MAIN_CATEGORIES.items(), start=1
    ):
        cat_id = uuid.UUID(MAIN_CATEGORY_IDS[slug])
        _upsert(
            db,
            cat_id=cat_id,
            slug=slug,
            name_ar=name_ar,
            name_en=name_en,
            parent_id=None,
            sort_order=order,
            icon_key=icon_key,
        )
        main_ids[slug] = cat_id
    db.flush()

    parent_order: dict[str, int] = {}
    for slug, name_ar, name_en, parent_slug, icon_key in SUB_CATEGORIES:
        parent_order[parent_slug] = parent_order.get(parent_slug, 0) + 1
        cat_id = uuid.UUID(SUB_CATEGORY_IDS[slug])
        _upsert(
            db,
            cat_id=cat_id,
            slug=slug,
            name_ar=name_ar,
            name_en=name_en,
            parent_id=main_ids[parent_slug],
            sort_order=parent_order[parent_slug],
            icon_key=icon_key,
        )
    return len(MAIN_CATEGORIES), len(SUB_CATEGORIES)


def main() -> None:
    engine = create_engine(settings.database_url)
    with Session(engine) as db:
        mains, subs = seed_tree(db)
        db.commit()
    print(f"Seeded {mains} main + {subs} sub categories (CategorySeeder)")


if __name__ == "__main__":
    main()
