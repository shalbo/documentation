"""Centralized Notification Engine — dispatch logging, broadcasts, templates, analytics."""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import (
    Notification,
    NotificationBroadcast,
    NotificationDispatchLog,
    NotificationTemplate,
    Role,
    User,
    UserRole,
)
from app.notification_inbox_services import (
    NOTIFICATION_CATEGORIES,
    dispatch_user_notification,
    get_category_prefs,
    get_template,
    render_template,
)

BROADCAST_SEGMENTS = frozenset(
    {"all_users", "customers", "technicians", "admins"}
)

EVENT_SOURCES = frozenset(
    {
        "booking_hook",
        "support_hook",
        "towing_hook",
        "admin_send",
        "admin_broadcast",
        "vendor_hook",
        "driver_hook",
        "system",
    }
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def next_broadcast_reference(db: Session) -> str:
    count = db.scalar(select(func.count()).select_from(NotificationBroadcast)) or 0
    return f"BCAST-2026-{count + 1:03d}"


def record_dispatch_log(
    db: Session,
    *,
    event_source: str,
    user_id: uuid.UUID,
    category: str,
    title: str,
    notification_id: uuid.UUID | None = None,
    broadcast_id: uuid.UUID | None = None,
    template_slug: str | None = None,
    push_sent: bool = False,
    in_app_created: bool = False,
    status: str = "delivered",
    metadata: dict | None = None,
) -> NotificationDispatchLog:
    channel = "both"
    if push_sent and not in_app_created:
        channel = "push"
    elif in_app_created and not push_sent:
        channel = "in_app"

    entry = NotificationDispatchLog(
        id=uuid.uuid4(),
        event_source=event_source,
        notification_id=notification_id,
        broadcast_id=broadcast_id,
        user_id=user_id,
        category=category,
        template_slug=template_slug,
        title=title[:200],
        channel=channel,
        push_sent=push_sent,
        in_app_created=in_app_created,
        status=status,
        metadata_json=metadata or {},
        created_at=_now(),
    )
    db.add(entry)
    return entry


def engine_dispatch(
    db: Session,
    user_id: uuid.UUID,
    *,
    event_source: str,
    category: str,
    title: str,
    body: str,
    data: dict | None = None,
    action_url: str | None = None,
    template_slug: str | None = None,
    send_push: bool = True,
    broadcast_id: uuid.UUID | None = None,
) -> Notification | None:
    if event_source not in EVENT_SOURCES:
        raise ValueError(f"مصدر الحدث غير مدعوم: {event_source}")

    push_enabled, in_app_enabled = get_category_prefs(db, user_id, category)

    if not in_app_enabled and not (send_push and push_enabled):
        record_dispatch_log(
            db,
            event_source=event_source,
            user_id=user_id,
            category=category,
            title=title,
            template_slug=template_slug,
            status="skipped_prefs",
            broadcast_id=broadcast_id,
        )
        return None

    notification = dispatch_user_notification(
        db,
        user_id,
        category=category,
        title=title,
        body=body,
        data=data,
        action_url=action_url,
        template_slug=template_slug,
        send_push=send_push,
    )

    if notification:
        record_dispatch_log(
            db,
            event_source=event_source,
            user_id=user_id,
            category=category,
            title=title,
            notification_id=notification.id,
            template_slug=template_slug,
            push_sent=notification.push_sent,
            in_app_created=True,
            status="delivered",
            broadcast_id=broadcast_id,
        )
    return notification


def dispatch_log_out(row: NotificationDispatchLog, user: User | None = None) -> dict:
    return {
        "id": row.id,
        "event_source": row.event_source,
        "notification_id": row.notification_id,
        "broadcast_id": row.broadcast_id,
        "user_id": row.user_id,
        "user_name": user.full_name if user else None,
        "user_phone": user.phone if user else None,
        "category": row.category,
        "template_slug": row.template_slug,
        "title": row.title,
        "channel": row.channel,
        "push_sent": row.push_sent,
        "in_app_created": row.in_app_created,
        "status": row.status,
        "metadata": row.metadata_json or {},
        "created_at": row.created_at,
    }


def broadcast_out(row: NotificationBroadcast) -> dict:
    return {
        "id": row.id,
        "reference": row.reference,
        "category": row.category,
        "title": row.title,
        "body": row.body,
        "target_segment": row.target_segment,
        "template_slug": row.template_slug,
        "recipients_count": row.recipients_count,
        "push_sent_count": row.push_sent_count,
        "in_app_count": row.in_app_count,
        "skipped_count": row.skipped_count,
        "created_by": row.created_by,
        "created_at": row.created_at,
    }


def template_out(row: NotificationTemplate) -> dict:
    return {
        "id": row.id,
        "slug": row.slug,
        "category": row.category,
        "title_template": row.title_template,
        "title_template_en": row.title_template_en,
        "body_template": row.body_template,
        "body_template_en": row.body_template_en,
        "action_url_template": row.action_url_template,
        "is_active": row.is_active,
        "created_at": row.created_at,
    }


def list_dispatch_log(
    db: Session,
    *,
    event_source: str | None = None,
    category: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[dict], int]:
    query = select(NotificationDispatchLog)
    count_q = select(func.count()).select_from(NotificationDispatchLog)
    if event_source:
        query = query.where(NotificationDispatchLog.event_source == event_source)
        count_q = count_q.where(NotificationDispatchLog.event_source == event_source)
    if category:
        query = query.where(NotificationDispatchLog.category == category)
        count_q = count_q.where(NotificationDispatchLog.category == category)

    total = db.scalar(count_q) or 0
    rows = db.scalars(
        query.order_by(NotificationDispatchLog.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()

    user_ids = {r.user_id for r in rows}
    users = {
        u.id: u
        for u in db.scalars(select(User).where(User.id.in_(user_ids))).all()
    } if user_ids else {}

    return [dispatch_log_out(r, users.get(r.user_id)) for r in rows], total


def get_engine_analytics(db: Session) -> dict:
    now = _now()
    day_ago = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)

    total_inbox = db.scalar(select(func.count()).select_from(Notification)) or 0
    unread = (
        db.scalar(
            select(func.count()).select_from(Notification).where(
                Notification.is_read.is_(False)
            )
        )
        or 0
    )
    push_sent_total = (
        db.scalar(
            select(func.count()).select_from(Notification).where(
                Notification.push_sent.is_(True)
            )
        )
        or 0
    )
    dispatches_24h = (
        db.scalar(
            select(func.count())
            .select_from(NotificationDispatchLog)
            .where(NotificationDispatchLog.created_at >= day_ago)
        )
        or 0
    )
    dispatches_7d = (
        db.scalar(
            select(func.count())
            .select_from(NotificationDispatchLog)
            .where(NotificationDispatchLog.created_at >= week_ago)
        )
        or 0
    )
    broadcasts_total = (
        db.scalar(select(func.count()).select_from(NotificationBroadcast)) or 0
    )
    templates_active = (
        db.scalar(
            select(func.count())
            .select_from(NotificationTemplate)
            .where(NotificationTemplate.is_active.is_(True))
        )
        or 0
    )
    skipped_prefs = (
        db.scalar(
            select(func.count())
            .select_from(NotificationDispatchLog)
            .where(NotificationDispatchLog.status == "skipped_prefs")
        )
        or 0
    )

    by_category = db.execute(
        select(Notification.category, func.count())
        .group_by(Notification.category)
        .order_by(func.count().desc())
    ).all()

    by_source = db.execute(
        select(NotificationDispatchLog.event_source, func.count())
        .group_by(NotificationDispatchLog.event_source)
        .order_by(func.count().desc())
    ).all()

    return {
        "inbox_total": total_inbox,
        "inbox_unread": unread,
        "push_sent_total": push_sent_total,
        "dispatches_24h": dispatches_24h,
        "dispatches_7d": dispatches_7d,
        "broadcasts_total": broadcasts_total,
        "templates_active": templates_active,
        "skipped_by_preferences": skipped_prefs,
        "by_category": [{"category": c, "count": n} for c, n in by_category],
        "by_event_source": [{"source": s, "count": n} for s, n in by_source],
    }


def list_templates(db: Session) -> list[dict]:
    rows = db.scalars(
        select(NotificationTemplate).order_by(NotificationTemplate.slug)
    ).all()
    return [template_out(t) for t in rows]


def create_template(
    db: Session,
    *,
    slug: str,
    category: str,
    title_template: str,
    body_template: str,
    title_template_en: str | None = None,
    body_template_en: str | None = None,
    action_url_template: str | None = None,
) -> NotificationTemplate:
    if category not in NOTIFICATION_CATEGORIES:
        raise ValueError("فئة غير مدعومة")
    row = NotificationTemplate(
        id=uuid.uuid4(),
        slug=slug.strip(),
        category=category,
        title_template=title_template,
        title_template_en=title_template_en,
        body_template=body_template,
        body_template_en=body_template_en,
        action_url_template=action_url_template,
        is_active=True,
        created_at=_now(),
    )
    db.add(row)
    db.flush()
    return row


def update_template(
    db: Session,
    template: NotificationTemplate,
    *,
    title_template: str | None = None,
    body_template: str | None = None,
    title_template_en: str | None = None,
    body_template_en: str | None = None,
    action_url_template: str | None = None,
    is_active: bool | None = None,
) -> NotificationTemplate:
    if title_template is not None:
        template.title_template = title_template
    if body_template is not None:
        template.body_template = body_template
    if title_template_en is not None:
        template.title_template_en = title_template_en
    if body_template_en is not None:
        template.body_template_en = body_template_en
    if action_url_template is not None:
        template.action_url_template = action_url_template
    if is_active is not None:
        template.is_active = is_active
    return template


def resolve_broadcast_recipients(db: Session, segment: str) -> list[User]:
    if segment not in BROADCAST_SEGMENTS:
        raise ValueError("شريحة غير مدعومة")

    if segment == "all_users":
        return list(db.scalars(select(User).where(User.is_active.is_(True))).all())

    role_slug = {
        "customers": "customer",
        "technicians": "technician",
        "admins": "admin",
    }[segment]

    role = db.scalar(select(Role).where(Role.slug == role_slug))
    if not role:
        return []

    user_ids = db.scalars(
        select(UserRole.user_id).where(UserRole.role_id == role.id)
    ).all()
    if not user_ids:
        return []

    return list(
        db.scalars(
            select(User).where(User.id.in_(user_ids), User.is_active.is_(True))
        ).all()
    )


def run_broadcast(
    db: Session,
    *,
    category: str,
    title: str,
    body: str,
    target_segment: str,
    template_slug: str | None = None,
    context: dict[str, str] | None = None,
    send_push: bool = True,
    created_by: str | None = None,
) -> NotificationBroadcast:
    if category not in NOTIFICATION_CATEGORIES:
        raise ValueError("فئة غير مدعومة")

    recipients = resolve_broadcast_recipients(db, target_segment)
    broadcast = NotificationBroadcast(
        id=uuid.uuid4(),
        reference=next_broadcast_reference(db),
        category=category,
        title=title[:200],
        body=body,
        target_segment=target_segment,
        template_slug=template_slug,
        created_by=created_by,
        created_at=_now(),
    )
    db.add(broadcast)
    db.flush()

    push_count = 0
    in_app_count = 0
    skipped = 0

    template = get_template(db, template_slug) if template_slug else None

    for user in recipients:
        try:
            send_title = title
            send_body = body
            if template:
                locale = user.locale if user.locale in {"ar", "en"} else "ar"
                if locale == "en" and template.title_template_en:
                    send_title = render_template(template.title_template_en, context or {})
                    send_body = render_template(
                        template.body_template_en or template.body_template,
                        context or {},
                    )
                else:
                    send_title = render_template(template.title_template, context or {})
                    send_body = render_template(template.body_template, context or {})

            notification = engine_dispatch(
                db,
                user.id,
                event_source="admin_broadcast",
                category=category,
                title=send_title,
                body=send_body,
                template_slug=template_slug,
                send_push=send_push,
                broadcast_id=broadcast.id,
            )
            if notification is None:
                skipped += 1
            else:
                in_app_count += 1
                if notification.push_sent:
                    push_count += 1
        except Exception:
            skipped += 1

    broadcast.recipients_count = len(recipients)
    broadcast.push_sent_count = push_count
    broadcast.in_app_count = in_app_count
    broadcast.skipped_count = skipped
    return broadcast


def search_users(db: Session, query: str, *, limit: int = 20) -> list[dict]:
    needle = f"%{query.strip()}%"
    users = db.scalars(
        select(User)
        .where(
            User.is_active.is_(True),
            or_(
                User.full_name.ilike(needle),
                User.phone.ilike(needle),
                User.email.ilike(needle),
            ),
        )
        .limit(limit)
    ).all()
    return [
        {
            "id": u.id,
            "full_name": u.full_name,
            "phone": u.phone,
            "email": u.email,
        }
        for u in users
    ]
