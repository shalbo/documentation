from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.models import Service, ServiceCategory
from app.schemas import (
    CategoryBrief,
    CategoryOut,
    CategoryTreeMeta,
    CategoryTreeOut,
    ServiceInTreeOut,
    ServiceOut,
)

router = APIRouter(tags=["catalog"])


@router.get("/categories/tree")
def categories_tree(db: Session = Depends(get_db)):
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

        node = CategoryTreeOut(
            id=category.id,
            slug=category.slug,
            name_ar=category.name_ar,
            sort_order=category.sort_order,
            services_count=len(category_services),
            services=[
                ServiceInTreeOut(
                    id=s.id,
                    slug=s.slug,
                    name_ar=s.name_ar,
                    subtitle_ar=s.subtitle_ar,
                    icon_key=s.icon_key,
                    price_sar=float(s.price_sar),
                    duration_minutes=s.duration_minutes,
                )
                for s in category_services
            ],
        )
        tree.append(node.model_dump())

    meta = CategoryTreeMeta(
        total_categories=len(tree),
        total_services=len(all_services),
    )
    return {"data": tree, "meta": meta.model_dump()}


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    categories = db.scalars(
        select(ServiceCategory)
        .where(ServiceCategory.is_active.is_(True))
        .order_by(ServiceCategory.sort_order)
    ).all()
    data = [CategoryOut.model_validate(c).model_dump() for c in categories]
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/services")
def list_services(
    category: str | None = Query(default=None),
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
    data = []
    for service in services:
        item = ServiceOut(
            id=service.id,
            slug=service.slug,
            name_ar=service.name_ar,
            subtitle_ar=service.subtitle_ar,
            icon_key=service.icon_key,
            price_sar=float(service.price_sar),
            duration_minutes=service.duration_minutes,
            category=CategoryBrief(
                slug=service.category.slug,
                name_ar=service.category.name_ar,
            ),
        )
        data.append(item.model_dump())
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/services/{service_id}")
def get_service(service_id: UUID, db: Session = Depends(get_db)):
    service = db.scalar(
        select(Service)
        .options(joinedload(Service.category))
        .where(Service.id == service_id, Service.is_active.is_(True))
    )
    if not service:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "الخدمة غير موجودة"},
        )
    item = ServiceOut(
        id=service.id,
        slug=service.slug,
        name_ar=service.name_ar,
        subtitle_ar=service.subtitle_ar,
        icon_key=service.icon_key,
        price_sar=float(service.price_sar),
        duration_minutes=service.duration_minutes,
        category=CategoryBrief(
            slug=service.category.slug,
            name_ar=service.category.name_ar,
        ),
    )
    return {"data": item.model_dump()}
