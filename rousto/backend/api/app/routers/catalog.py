from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.models import Service, ServiceCategory
from app.schemas import CategoryBrief, CategoryOut, ServiceOut

router = APIRouter(tags=["catalog"])


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
