from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.i18n import resolve_locale
from app.deps import get_current_user, require_admin_key
from app.models import User
from app.notification_inbox_services import (
    NOTIFICATION_CATEGORIES,
    list_notifications,
    list_user_preferences,
    mark_all_read,
    mark_read,
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


@router.get("/me/notifications")
def get_my_notifications(
    unread_only: bool = Query(default=False),
    category: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    locale: str = Depends(resolve_locale),
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
        locale=locale,
    )
    return {
        "data": data,
        "meta": {"total": total, "unread": unread_count(db, user.id), "locale": locale},
    }


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
    locale: str = Depends(resolve_locale),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = list_user_preferences(db, user.id, locale)
    return {"data": data, "meta": {"total": len(data)}}


@router.put("/me/notification-preferences")
def put_preferences(
    body: PreferencesUpdateIn,
    locale: str = Depends(resolve_locale),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        data = update_user_preferences(
            db,
            user.id,
            [p.model_dump() for p in body.preferences],
            locale=locale,
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "PREFERENCES_ERROR", "message": str(exc)},
        ) from exc
    return {"data": data}


