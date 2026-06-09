from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.deps import require_admin_key
from app.models import Service, ServiceCategory
from app.schemas import (
    AdminCategoryCreate,
    AdminCategoryOut,
    AdminCategoryReorderIn,
    AdminCategoryUpdate,
    AdminServiceCreate,
    AdminServiceOut,
    AdminServiceUpdate,
)

router = APIRouter(prefix="/admin", tags=["admin-catalog"])

PROTECTED_CATEGORY_SLUG = "all"


def _category_out(category: ServiceCategory) -> dict:
    return AdminCategoryOut.model_validate(category).model_dump()


def _service_out(service: Service) -> dict:
    return AdminServiceOut(
        id=service.id,
        slug=service.slug,
        name_ar=service.name_ar,
        subtitle_ar=service.subtitle_ar,
        icon_key=service.icon_key,
        price_sar=float(service.price_sar),
        duration_minutes=service.duration_minutes,
        category_id=service.category_id,
        category_slug=service.category.slug,
        category_name_ar=service.category.name_ar,
        is_active=service.is_active,
        created_at=service.created_at,
    ).model_dump()


def _get_category_or_404(db: Session, category_id: UUID) -> ServiceCategory:
    category = db.get(ServiceCategory, category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "التصنيف غير موجود"},
        )
    return category


def _guard_protected_category(category: ServiceCategory, *, deactivate: bool = False) -> None:
    if category.slug != PROTECTED_CATEGORY_SLUG:
        return
    if deactivate:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "PROTECTED_CATEGORY",
                "message": "لا يمكن تعطيل تصنيف الكل",
            },
        )


def _validate_assignable_category(db: Session, category_id: UUID) -> ServiceCategory:
    category = _get_category_or_404(db, category_id)
    if category.slug == PROTECTED_CATEGORY_SLUG:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_CATEGORY",
                "message": "لا يمكن ربط خدمة بتصنيف الكل",
            },
        )
    if not category.is_active:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INACTIVE_CATEGORY",
                "message": "التصنيف غير نشط",
            },
        )
    return category


def _get_service_or_404(db: Session, service_id: UUID) -> Service:
    service = db.scalar(
        select(Service)
        .options(joinedload(Service.category))
        .where(Service.id == service_id)
    )
    if not service:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "الخدمة غير موجودة"},
        )
    return service


@router.get("/categories")
def admin_list_categories(
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    categories = db.scalars(
        select(ServiceCategory).order_by(ServiceCategory.sort_order)
    ).all()
    data = [_category_out(c) for c in categories]
    return {"data": data, "meta": {"total": len(data)}}


@router.post("/categories", status_code=201)
def admin_create_category(
    body: AdminCategoryCreate,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    if body.slug == PROTECTED_CATEGORY_SLUG:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "RESERVED_SLUG",
                "message": "المعرّف all محجوز للنظام",
            },
        )

    category = ServiceCategory(
        id=uuid4(),
        slug=body.slug,
        name_ar=body.name_ar,
        sort_order=body.sort_order,
        is_active=body.is_active,
    )
    db.add(category)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail={"code": "DUPLICATE_SLUG", "message": "المعرّف مستخدم مسبقاً"},
        ) from exc
    db.refresh(category)
    return {"data": _category_out(category)}


@router.get("/categories/{category_id}")
def admin_get_category(
    category_id: UUID,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    category = _get_category_or_404(db, category_id)
    return {"data": _category_out(category)}


@router.patch("/categories/{category_id}")
def admin_update_category(
    category_id: UUID,
    body: AdminCategoryUpdate,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    category = _get_category_or_404(db, category_id)
    if body.is_active is False:
        _guard_protected_category(category, deactivate=True)

    updates = body.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return {"data": _category_out(category)}


@router.post("/categories/reorder")
def admin_reorder_categories(
    body: AdminCategoryReorderIn,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    for item in body.items:
        category = _get_category_or_404(db, item.id)
        category.sort_order = item.sort_order
    db.commit()
    categories = db.scalars(
        select(ServiceCategory).order_by(ServiceCategory.sort_order)
    ).all()
    data = [_category_out(c) for c in categories]
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/services")
def admin_list_services(
    category: str | None = Query(default=None),
    active: bool | None = Query(default=None),
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    stmt = (
        select(Service)
        .options(joinedload(Service.category))
        .order_by(Service.name_ar)
    )
    if category:
        stmt = stmt.join(ServiceCategory).where(ServiceCategory.slug == category)
    if active is not None:
        stmt = stmt.where(Service.is_active.is_(active))

    services = db.scalars(stmt).unique().all()
    data = [_service_out(s) for s in services]
    return {"data": data, "meta": {"total": len(data)}}


@router.post("/services", status_code=201)
def admin_create_service(
    body: AdminServiceCreate,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    _validate_assignable_category(db, body.category_id)

    service = Service(
        id=uuid4(),
        category_id=body.category_id,
        slug=body.slug,
        name_ar=body.name_ar,
        subtitle_ar=body.subtitle_ar,
        icon_key=body.icon_key,
        price_sar=body.price_sar,
        duration_minutes=body.duration_minutes,
        is_active=body.is_active,
        created_at=datetime.now(timezone.utc),
    )
    db.add(service)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail={"code": "DUPLICATE_SLUG", "message": "المعرّف مستخدم مسبقاً"},
        ) from exc
    service = _get_service_or_404(db, service.id)
    return {"data": _service_out(service)}


@router.get("/services/{service_id}")
def admin_get_service(
    service_id: UUID,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    service = _get_service_or_404(db, service_id)
    return {"data": _service_out(service)}


@router.patch("/services/{service_id}")
def admin_update_service(
    service_id: UUID,
    body: AdminServiceUpdate,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    service = _get_service_or_404(db, service_id)
    updates = body.model_dump(exclude_unset=True)

    if "category_id" in updates:
        _validate_assignable_category(db, updates["category_id"])

    for field, value in updates.items():
        setattr(service, field, value)

    db.commit()
    service = _get_service_or_404(db, service_id)
    return {"data": _service_out(service)}
