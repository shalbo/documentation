from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.category_services import (
    get_category_tree,
    list_child_categories,
    list_root_categories,
)
from app.db import get_db
from app.i18n import resolve_locale

router = APIRouter(prefix="/parts/categories", tags=["part-categories"])


@router.get("/tree")
def categories_tree(
    locale: str = Depends(resolve_locale),
    db: Session = Depends(get_db),
):
    data = get_category_tree(db, locale)
    return {"data": data, "meta": {"total_roots": len(data), "locale": locale}}


@router.get("/roots")
def categories_roots(
    locale: str = Depends(resolve_locale),
    db: Session = Depends(get_db),
):
    data = list_root_categories(db, locale)
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/{parent_id}/children")
def categories_children(
    parent_id: UUID,
    locale: str = Depends(resolve_locale),
    db: Session = Depends(get_db),
):
    data = list_child_categories(db, parent_id, locale)
    return {"data": data, "meta": {"total": len(data), "parent_id": str(parent_id)}}
