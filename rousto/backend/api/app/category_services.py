"""Hierarchical spare parts category tree."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.i18n import pick_localized
from app.models import PartCategory


def category_out(cat: PartCategory, locale: str, *, include_children: bool = False) -> dict:
    data = {
        "id": cat.id,
        "slug": cat.slug,
        "name": pick_localized(cat, "name", locale),
        "name_ar": cat.name_ar,
        "sort_order": cat.sort_order,
        "parent_id": cat.parent_id,
        "icon_key": cat.icon_key,
        "is_root": cat.parent_id is None,
        "is_leaf": cat.parent_id is not None,
    }
    if include_children and cat.children:
        active = [c for c in cat.children if c.is_active]
        data["children"] = [
            category_out(c, locale) for c in sorted(active, key=lambda x: x.sort_order)
        ]
    return data


def list_root_categories(db: Session, locale: str) -> list[dict]:
    roots = db.scalars(
        select(PartCategory)
        .where(PartCategory.parent_id.is_(None), PartCategory.is_active.is_(True))
        .order_by(PartCategory.sort_order)
    ).all()
    return [category_out(r, locale) for r in roots]


def list_child_categories(
    db: Session, parent_id: uuid.UUID, locale: str
) -> list[dict]:
    children = db.scalars(
        select(PartCategory)
        .where(
            PartCategory.parent_id == parent_id,
            PartCategory.is_active.is_(True),
        )
        .order_by(PartCategory.sort_order)
    ).all()
    return [category_out(c, locale) for c in children]


def get_category_tree(db: Session, locale: str) -> list[dict]:
    roots = db.scalars(
        select(PartCategory)
        .options(joinedload(PartCategory.children))
        .where(PartCategory.parent_id.is_(None), PartCategory.is_active.is_(True))
        .order_by(PartCategory.sort_order)
    ).unique().all()
    return [category_out(r, locale, include_children=True) for r in roots]


def get_category(db: Session, category_id: uuid.UUID) -> PartCategory | None:
    return db.get(PartCategory, category_id)


def is_leaf_category(db: Session, category_id: uuid.UUID) -> bool:
    cat = db.get(PartCategory, category_id)
    if not cat or not cat.is_active:
        return False
    return cat.parent_id is not None


def collect_filter_category_ids(
    db: Session, category_id: uuid.UUID
) -> set[uuid.UUID]:
    """Leaf → single id; root → all active descendant leaf ids."""
    cat = db.get(PartCategory, category_id)
    if not cat or not cat.is_active:
        return set()

    if cat.parent_id is not None:
        return {cat.id}

    descendants = db.scalars(
        select(PartCategory.id).where(
            PartCategory.parent_id == category_id,
            PartCategory.is_active.is_(True),
        )
    ).all()
    return set(descendants)


def create_category(
    db: Session,
    *,
    slug: str,
    name_ar: str,
    name_en: str | None = None,
    parent_id: uuid.UUID | None = None,
    sort_order: int = 0,
    icon_key: str | None = None,
) -> PartCategory:
    if parent_id is not None:
        parent = db.get(PartCategory, parent_id)
        if not parent or parent.parent_id is not None:
            raise ValueError("القسم الرئيسي غير صالح — اختر قسماً رئيسياً فقط كأب")
    cat = PartCategory(
        id=uuid.uuid4(),
        slug=slug.strip(),
        name_ar=name_ar,
        name_en=name_en,
        parent_id=parent_id,
        sort_order=sort_order,
        icon_key=icon_key,
        is_active=True,
    )
    db.add(cat)
    db.flush()
    return cat
