from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user, require_admin_key
from app.models import User
from app.notification_inbox_services import (
    NOTIFICATION_CATEGORIES,
    admin_list_notifications,
    dispatch_user_notification,
    list_notifications,
    list_user_preferences,
    mark_all_read,
    mark_read,
    notify_from_template,
    unread_count,
    update_user_preferences,
)

router = APIRouter(tags=["notifications"])


class PreferenceItemIn(BaseModel):
    category: str
    push_enabled: bool = True
    in_app_enabled: bool = True


class PreferencesUpdateIn(BaseModel):
    preferences: list[PreferenceItemIn]


class AdminSendIn(BaseModel):
    user_id: UUID
    category: str = Field(default="system")
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=2000)
    action_url: str | None = Field(default=None, max_length=300)
    template_slug: str | None = Field(default=None, max_length=60)
    context: dict[str, str] = Field(default_factory=dict)
    send_push: bool = True


@router.get("/me/notifications")
def get_my_notifications(
    unread_only: bool = Query(default=False),
    category: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if category and category not in NOTIFICATION_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_CATEGORY", "message": "فئة الإشعار غير مدعومة"},
        )
    data, total = list_notifications(
        db,
        user.id,
        unread_only=unread_only,
        category=category,
        limit=limit,
        offset=offset,
    )
    return {"data": data, "meta": {"total": total, "unread": unread_count(db, user.id)}}


@router.get("/me/notifications/unread-count")
def get_unread_count(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {"data": {"count": unread_count(db, user.id)}}


@router.patch("/me/notifications/{notification_id}/read")
def patch_notification_read(
    notification_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = mark_read(db, user.id, notification_id)
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "الإشعار غير موجود"},
        )
    db.commit()
    return {"data": row}


@router.post("/me/notifications/read-all")
def post_read_all(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    count = mark_all_read(db, user.id)
    db.commit()
    return {"data": {"marked_read": count}}


@router.get("/me/notification-preferences")
def get_preferences(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = list_user_preferences(db, user.id)
    return {"data": data, "meta": {"total": len(data)}}


@router.put("/me/notification-preferences")
def put_preferences(
    body: PreferencesUpdateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        data = update_user_preferences(
            db,
            user.id,
            [p.model_dump() for p in body.preferences],
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "PREFERENCES_ERROR", "message": str(exc)},
        ) from exc
    return {"data": data}


@router.get("/admin/notifications")
def admin_notifications(
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


@router.post("/admin/notifications/send", status_code=201)
def admin_send_notification(
    body: AdminSendIn,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    try:
        if body.template_slug:
            notification = notify_from_template(
                db,
                body.user_id,
                body.template_slug,
                body.context,
                send_push=body.send_push,
            )
        else:
            if body.category not in NOTIFICATION_CATEGORIES:
                raise ValueError("فئة الإشعار غير مدعومة")
            notification = dispatch_user_notification(
                db,
                body.user_id,
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
        return {
            "data": {
                "sent": False,
                "reason": "disabled_by_preferences",
            }
        }

    from app.notification_inbox_services import notification_out

    return {"data": {"sent": True, "notification": notification_out(notification)}}
