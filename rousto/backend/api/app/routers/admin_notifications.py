from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_admin_key
from app.models import NotificationTemplate
from app.notification_engine_services import (
    BROADCAST_SEGMENTS,
    broadcast_out,
    create_template,
    engine_dispatch,
    get_engine_analytics,
    list_dispatch_log,
    list_templates,
    run_broadcast,
    search_users,
    template_out,
    update_template,
)
from app.notification_inbox_services import (
    NOTIFICATION_CATEGORIES,
    admin_list_notifications,
    notification_out,
    notify_from_template,
)
from app.notification_engine_services import engine_dispatch as _engine_dispatch

router = APIRouter(prefix="/admin/notifications", tags=["admin-notifications"])


class TemplateCreateIn(BaseModel):
    slug: str = Field(min_length=2, max_length=60)
    category: str
    title_template: str = Field(min_length=1, max_length=200)
    body_template: str = Field(min_length=1, max_length=2000)
    title_template_en: str | None = Field(default=None, max_length=200)
    body_template_en: str | None = Field(default=None, max_length=2000)
    action_url_template: str | None = Field(default=None, max_length=300)


class TemplateUpdateIn(BaseModel):
    title_template: str | None = Field(default=None, max_length=200)
    body_template: str | None = Field(default=None, max_length=2000)
    title_template_en: str | None = Field(default=None, max_length=200)
    body_template_en: str | None = Field(default=None, max_length=2000)
    action_url_template: str | None = Field(default=None, max_length=300)
    is_active: bool | None = None


class AdminSendIn(BaseModel):
    user_id: UUID
    category: str = Field(default="system")
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=2000)
    action_url: str | None = Field(default=None, max_length=300)
    template_slug: str | None = Field(default=None, max_length=60)
    context: dict[str, str] = Field(default_factory=dict)
    send_push: bool = True


class BroadcastIn(BaseModel):
    category: str = Field(default="system")
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=2000)
    target_segment: str = Field(default="all_users")
    template_slug: str | None = Field(default=None, max_length=60)
    context: dict[str, str] = Field(default_factory=dict)
    send_push: bool = True
    created_by: str | None = Field(default="admin", max_length=120)


@router.get("")
def admin_inbox_list(
    user_id: UUID | None = Query(default=None),
    category: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    data, total = admin_list_notifications(
        db,
        user_id=user_id,
        category=category,
        limit=limit,
        offset=offset,
    )
    return {"data": data, "meta": {"total": total}}


@router.get("/analytics")
def admin_notification_analytics(
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    return {"data": get_engine_analytics(db)}


@router.get("/dispatch-log")
def admin_dispatch_log(
    event_source: str | None = Query(default=None),
    category: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    data, total = list_dispatch_log(
        db,
        event_source=event_source,
        category=category,
        limit=limit,
        offset=offset,
    )
    return {"data": data, "meta": {"total": total}}


@router.get("/templates")
def admin_list_templates(
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    data = list_templates(db)
    return {"data": data, "meta": {"total": len(data)}}


@router.post("/templates", status_code=201)
def admin_create_template(
    body: TemplateCreateIn,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    try:
        row = create_template(db, **body.model_dump())
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "TEMPLATE_ERROR", "message": str(exc)},
        ) from exc
    return {"data": template_out(row)}


@router.patch("/templates/{template_id}")
def admin_patch_template(
    template_id: UUID,
    body: TemplateUpdateIn,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    row = db.get(NotificationTemplate, template_id)
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "القالب غير موجود"},
        )
    update_template(db, row, **body.model_dump(exclude_unset=True))
    db.commit()
    return {"data": template_out(row)}


@router.get("/users/search")
def admin_search_users(
    q: str = Query(min_length=1, max_length=80),
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    data = search_users(db, q)
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/broadcasts")
def admin_list_broadcasts(
    limit: int = Query(default=50, ge=1, le=100),
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    from app.models import NotificationBroadcast
    from sqlalchemy import select

    rows = db.scalars(
        select(NotificationBroadcast)
        .order_by(NotificationBroadcast.created_at.desc())
        .limit(limit)
    ).all()
    data = [broadcast_out(r) for r in rows]
    return {"data": data, "meta": {"total": len(data)}}


@router.post("/broadcast", status_code=201)
def admin_broadcast(
    body: BroadcastIn,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    if body.target_segment not in BROADCAST_SEGMENTS:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_SEGMENT", "message": "شريحة غير مدعومة"},
        )
    if body.category not in NOTIFICATION_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_CATEGORY", "message": "فئة غير مدعومة"},
        )
    try:
        broadcast = run_broadcast(db, **body.model_dump())
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "BROADCAST_ERROR", "message": str(exc)},
        ) from exc
    return {"data": broadcast_out(broadcast)}


@router.post("/send", status_code=201)
def admin_send_single(
    body: AdminSendIn,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    if body.category not in NOTIFICATION_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_CATEGORY", "message": "فئة غير مدعومة"},
        )
    try:
        if body.template_slug:
            notification = notify_from_template(
                db,
                body.user_id,
                body.template_slug,
                body.context,
                send_push=body.send_push,
            )
            if notification:
                from app.notification_engine_services import record_dispatch_log

                record_dispatch_log(
                    db,
                    event_source="admin_send",
                    user_id=body.user_id,
                    category=body.category,
                    title=notification.title,
                    notification_id=notification.id,
                    template_slug=body.template_slug,
                    push_sent=notification.push_sent,
                    in_app_created=True,
                )
        else:
            notification = _engine_dispatch(
                db,
                body.user_id,
                event_source="admin_send",
                category=body.category,
                title=body.title,
                body=body.body,
                action_url=body.action_url,
                send_push=body.send_push,
            )
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "SEND_ERROR", "message": str(exc)},
        ) from exc
    if notification is None:
        return {"data": {"sent": False, "reason": "disabled_by_preferences"}}
    return {"data": {"sent": True, "notification": notification_out(notification)}}
