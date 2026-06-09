from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.cache import cached
from app.config import settings
from app.db import get_db
from app.i18n import error_message, pick_localized, resolve_locale
from app.models import Service, ServiceCategory
from app.rate_limit import check_rate_limit

router = APIRouter(tags=["catalog"])


def _service_node(service: Service, locale: str) -> dict:
    return {
        "id": service.id,
        "slug": service.slug,
        "name": pick_localized(service, "name", locale),
        "subtitle": pick_localized(service, "subtitle", locale) or None,
        "name_ar": service.name_ar,
        "subtitle_ar": service.subtitle_ar,
        "icon_key": service.icon_key,
        "price_sar": float(service.price_sar),
        "duration_minutes": service.duration_minutes,
    }


def _category_brief(category: ServiceCategory, locale: str) -> dict:
    return {
        "slug": category.slug,
        "name": pick_localized(category, "name", locale),
        "name_ar": category.name_ar,
    }


def _build_categories_tree(db: Session, locale: str) -> dict:
    categories = db.scalars(
        select(ServiceCategory)
        .where(ServiceCategory.is_active.is_(True))
        .order_by(ServiceCategory.sort_order)
    ).all()
    services = db.scalars(
        select(Service)
        .options(joinedload(Service.category))
        .where(Service.is_active.is_(True))
        .order_by(Service.name_ar)
    ).unique().all()

    services_by_category: dict[str, list[Service]] = {}
    for service in services:
        services_by_category.setdefault(str(service.category_id), []).append(service)

    all_services = list(services)
    tree = []
    for category in categories:
        if category.slug == "all":
            category_services = all_services
        else:
            category_services = services_by_category.get(str(category.id), [])

        tree.append(
            {
                "id": category.id,
                "slug": category.slug,
                "name": pick_localized(category, "name", locale),
                "name_ar": category.name_ar,
                "sort_order": category.sort_order,
                "services_count": len(category_services),
                "services": [_service_node(s, locale) for s in category_services],
            }
        )

    return {
        "data": tree,
        "meta": {
            "total_categories": len(tree),
            "total_services": len(all_services),
            "locale": locale,
        },
    }


@router.get("/categories/tree")
def categories_tree(
    locale: str = Depends(resolve_locale),
    db: Session = Depends(get_db),
):
    return cached(
        settings.cache_categories_ttl,
        f"categories_tree:{locale}",
        lambda: _build_categories_tree(db, locale),
    )


@router.get("/categories")
def list_categories(
    locale: str = Depends(resolve_locale),
    db: Session = Depends(get_db),
):
    categories = db.scalars(
        select(ServiceCategory)
        .where(ServiceCategory.is_active.is_(True))
        .order_by(ServiceCategory.sort_order)
    ).all()
    data = [
        {
            "id": c.id,
            "slug": c.slug,
            "name": pick_localized(c, "name", locale),
            "name_ar": c.name_ar,
            "sort_order": c.sort_order,
        }
        for c in categories
    ]
    return {"data": data, "meta": {"total": len(data), "locale": locale}}


@router.get("/services")
def list_services(
    category: str | None = Query(default=None),
    locale: str = Depends(resolve_locale),
    db: Session = Depends(get_db),
):
    stmt = (
        select(Service)
        .options(joinedload(Service.category))
        .where(Service.is_active.is_(True))
        .order_by(Service.name_ar)
    )
    if category and category != "all":
        stmt = stmt.join(ServiceCategory).where(ServiceCategory.slug == category)

    services = db.scalars(stmt).unique().all()
    data = [
        {
            **_service_node(service, locale),
            "category": _category_brief(service.category, locale),
        }
        for service in services
    ]
    return {"data": data, "meta": {"total": len(data), "locale": locale}}


@router.get("/services/search")
def search_services(
    request: Request,
    q: str = Query(min_length=1, max_length=80),
    locale: str = Depends(resolve_locale),
    db: Session = Depends(get_db),
):
    check_rate_limit(request, suffix="catalog_search", limit=60)
    needle = f"%{q.strip()}%"
    services = db.scalars(
        select(Service)
        .options(joinedload(Service.category))
        .where(
            Service.is_active.is_(True),
            or_(
                Service.name_ar.ilike(needle),
                Service.name_en.ilike(needle),
                Service.slug.ilike(needle),
                Service.subtitle_ar.ilike(needle),
                Service.subtitle_en.ilike(needle),
            ),
        )
        .order_by(Service.name_ar)
        .limit(50)
    ).unique().all()
    data = [
        {
            **_service_node(service, locale),
            "category": _category_brief(service.category, locale),
        }
        for service in services
    ]
    return {"data": data, "meta": {"total": len(data), "locale": locale, "query": q}}


@router.get("/services/{service_id}")
def get_service(
    service_id: UUID,
    locale: str = Depends(resolve_locale),
    db: Session = Depends(get_db),
):
    service = db.scalar(
        select(Service)
        .options(joinedload(Service.category))
        .where(Service.id == service_id, Service.is_active.is_(True))
    )
    if not service:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NOT_FOUND",
                "message": error_message("NOT_FOUND", locale, override_ar="الخدمة غير موجودة"),
            },
        )
    return {
        "data": {
            **_service_node(service, locale),
            "category": _category_brief(service.category, locale),
        },
        "meta": {"locale": locale},
    }
