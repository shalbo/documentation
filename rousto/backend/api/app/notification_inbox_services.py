"""NOTIV — in-app inbox, preferences, and unified dispatch."""

import re
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Notification, NotificationTemplate, UserNotificationPreference

NOTIFICATION_CATEGORIES = (
    "booking",
    "support",
    "towing",
    "promo",
    "security",
    "system",
)

CATEGORY_LABELS_AR = {
    "booking": "الحجوزات",
    "support": "الدعم",
    "towing": "السطحات",
    "promo": "العروض",
    "security": "الأمان",
    "system": "النظام",
}

_TEMPLATE_RE = re.compile(r"\{\{(\w+)\}\}")


def render_template(template: str, context: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        return context.get(key, match.group(0))

    return _TEMPLATE_RE.sub(repl, template)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def get_category_prefs(
    db: Session, user_id: uuid.UUID, category: str
) -> tuple[bool, bool]:
    pref = db.scalar(
        select(UserNotificationPreference).where(
            UserNotificationPreference.user_id == user_id,
            UserNotificationPreference.category == category,
        )
    )
    if pref:
        return pref.push_enabled, pref.in_app_enabled
    return True, True


def list_user_preferences(db: Session, user_id: uuid.UUID) -> list[dict]:
    rows = db.scalars(
        select(UserNotificationPreference).where(
            UserNotificationPreference.user_id == user_id
        )
    ).all()
    by_cat = {r.category: r for r in rows}
    data = []
    for cat in NOTIFICATION_CATEGORIES:
        row = by_cat.get(cat)
        data.append(
            {
                "category": cat,
                "category_label_ar": CATEGORY_LABELS_AR.get(cat, cat),
                "push_enabled": row.push_enabled if row else True,
                "in_app_enabled": row.in_app_enabled if row else True,
            }
        )
    return data


def update_user_preferences(
    db: Session,
    user_id: uuid.UUID,
    items: list[dict],
) -> list[dict]:
    now = _now()
    for item in items:
        cat = item["category"]
        if cat not in NOTIFICATION_CATEGORIES:
            raise ValueError(f"فئة غير مدعومة: {cat}")

        pref = db.scalar(
            select(UserNotificationPreference).where(
                UserNotificationPreference.user_id == user_id,
                UserNotificationPreference.category == cat,
            )
        )
        if pref:
            pref.push_enabled = item.get("push_enabled", pref.push_enabled)
            pref.in_app_enabled = item.get("in_app_enabled", pref.in_app_enabled)
            pref.updated_at = now
        else:
            db.add(
                UserNotificationPreference(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    category=cat,
                    push_enabled=item.get("push_enabled", True),
                    in_app_enabled=item.get("in_app_enabled", True),
                    updated_at=now,
                )
            )
    db.flush()
    return list_user_preferences(db, user_id)


def notification_out(row: Notification) -> dict:
    return {
        "id": row.id,
        "category": row.category,
        "category_label_ar": CATEGORY_LABELS_AR.get(row.category, row.category),
        "template_slug": row.template_slug,
        "title": row.title,
        "body": row.body,
        "data": row.data_json or {},
        "action_url": row.action_url,
        "is_read": row.is_read,
        "read_at": row.read_at,
        "push_sent": row.push_sent,
        "created_at": row.created_at,
    }


def list_notifications(
    db: Session,
    user_id: uuid.UUID,
    *,
    unread_only: bool = False,
    category: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict], int]:
    query = select(Notification).where(Notification.user_id == user_id)
    count_query = select(func.count()).select_from(Notification).where(
        Notification.user_id == user_id
    )

    if unread_only:
        query = query.where(Notification.is_read.is_(False))
        count_query = count_query.where(Notification.is_read.is_(False))
    if category:
        query = query.where(Notification.category == category)
        count_query = count_query.where(Notification.category == category)

    total = db.scalar(count_query) or 0
    rows = db.scalars(
        query.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
    ).all()
    return [notification_out(r) for r in rows], total


def unread_count(db: Session, user_id: uuid.UUID) -> int:
    return (
        db.scalar(
            select(func.count())
            .select_from(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
        )
        or 0
    )


def mark_read(db: Session, user_id: uuid.UUID, notification_id: uuid.UUID) -> dict | None:
    row = db.get(Notification, notification_id)
    if not row or row.user_id != user_id:
        return None
    if not row.is_read:
        row.is_read = True
        row.read_at = _now()
    return notification_out(row)


def mark_all_read(db: Session, user_id: uuid.UUID) -> int:
    now = _now()
    rows = db.scalars(
        select(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
    ).all()
    for row in rows:
        row.is_read = True
        row.read_at = now
    return len(rows)


def get_template(db: Session, slug: str) -> NotificationTemplate | None:
    return db.scalar(
        select(NotificationTemplate).where(
            NotificationTemplate.slug == slug,
            NotificationTemplate.is_active.is_(True),
        )
    )


def dispatch_user_notification(
    db: Session,
    user_id: uuid.UUID,
    *,
    category: str,
    title: str,
    body: str,
    data: dict | None = None,
    action_url: str | None = None,
    template_slug: str | None = None,
    send_push: bool = True,
) -> Notification | None:
    if category not in NOTIFICATION_CATEGORIES:
        raise ValueError(f"فئة غير مدعومة: {category}")

    push_enabled, in_app_enabled = get_category_prefs(db, user_id, category)
    if not in_app_enabled and not (send_push and push_enabled):
        return None

    now = _now()
    notification = None
    if in_app_enabled:
        notification = Notification(
            id=uuid.uuid4(),
            user_id=user_id,
            category=category,
            template_slug=template_slug,
            title=title[:200],
            body=body,
            data_json=data or {},
            action_url=action_url,
            is_read=False,
            push_sent=False,
            created_at=now,
        )
        db.add(notification)
        db.flush()

    if send_push and push_enabled:
        from app.notifications import send_push_to_user

        push_data = {k: str(v) for k, v in (data or {}).items()}
        push_data["category"] = category
        if notification:
            push_data["notification_id"] = str(notification.id)
        sent = send_push_to_user(
            db,
            user_id,
            title=title[:200],
            body=body[:500],
            data=push_data,
        )
        if notification and sent > 0:
            notification.push_sent = True

    return notification


def notify_from_template(
    db: Session,
    user_id: uuid.UUID,
    template_slug: str,
    context: dict[str, str],
    *,
    extra_data: dict | None = None,
    send_push: bool = True,
) -> Notification | None:
    template = get_template(db, template_slug)
    if not template:
        raise ValueError(f"قالب غير موجود: {template_slug}")

    title = render_template(template.title_template, context)
    body = render_template(template.body_template, context)
    action_url = None
    if template.action_url_template:
        action_url = render_template(template.action_url_template, context)

    data = dict(extra_data or {})
    data["template_slug"] = template_slug

    return dispatch_user_notification(
        db,
        user_id,
        category=template.category,
        title=title,
        body=body,
        data=data,
        action_url=action_url,
        template_slug=template_slug,
        send_push=send_push,
    )


def admin_list_notifications(
    db: Session,
    *,
    user_id: uuid.UUID | None = None,
    category: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[dict], int]:
    query = select(Notification)
    count_query = select(func.count()).select_from(Notification)

    if user_id:
        query = query.where(Notification.user_id == user_id)
        count_query = count_query.where(Notification.user_id == user_id)
    if category:
        query = query.where(Notification.category == category)
        count_query = count_query.where(Notification.category == category)

    total = db.scalar(count_query) or 0
    rows = db.scalars(
        query.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
    ).all()
    return [notification_out(r) for r in rows], total
