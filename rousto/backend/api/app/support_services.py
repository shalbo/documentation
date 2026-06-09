import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import (
    SecurityAuditLog,
    SupportFaq,
    SupportTicket,
    SupportTicketMessage,
    User,
    UserSecurityProfile,
)

TICKET_STATUSES = frozenset(
    {"open", "in_progress", "waiting_customer", "resolved", "closed"}
)

CATEGORY_LABELS = {
    "booking": "الحجوزات",
    "payment": "المدفوعات",
    "account": "الحساب",
    "technical": "تقني",
    "other": "أخرى",
}

PRIORITY_LABELS = {
    "low": "منخفضة",
    "normal": "عادية",
    "high": "عالية",
    "urgent": "عاجلة",
}

STATUS_LABELS = {
    "open": "مفتوحة",
    "in_progress": "قيد المعالجة",
    "waiting_customer": "بانتظار العميل",
    "resolved": "محلولة",
    "closed": "مغلقة",
}


def next_ticket_reference(db: Session) -> str:
    count = db.scalar(select(func.count()).select_from(SupportTicket)) or 0
    return f"SUP-2026-{count + 1:03d}"


def log_security_event(
    db: Session,
    *,
    event_type: str,
    user_id: uuid.UUID | None = None,
    severity: str = "info",
    ip_address: str | None = None,
    user_agent: str | None = None,
    metadata: dict | None = None,
) -> SecurityAuditLog:
    entry = SecurityAuditLog(
        id=uuid.uuid4(),
        user_id=user_id,
        event_type=event_type,
        severity=severity,
        ip_address=ip_address,
        user_agent=(user_agent[:300] if user_agent else None),
        metadata_=metadata or {},
        created_at=datetime.now(timezone.utc),
    )
    db.add(entry)
    return entry


def _get_or_create_security_profile(db: Session, user_id: uuid.UUID) -> UserSecurityProfile:
    profile = db.get(UserSecurityProfile, user_id)
    if profile:
        return profile
    now = datetime.now(timezone.utc)
    profile = UserSecurityProfile(
        user_id=user_id,
        login_alerts_enabled=True,
        updated_at=now,
    )
    db.add(profile)
    db.flush()
    return profile


def faq_out(item: SupportFaq) -> dict:
    return {
        "id": item.id,
        "slug": item.slug,
        "category": item.category,
        "question_ar": item.question_ar,
        "answer_ar": item.answer_ar,
        "sort_order": item.sort_order,
    }


def message_out(msg: SupportTicketMessage) -> dict:
    return {
        "id": msg.id,
        "author_type": msg.author_type,
        "author_label": msg.author_label,
        "message": msg.message,
        "created_at": msg.created_at,
    }


def ticket_summary(ticket: SupportTicket) -> dict:
    return {
        "id": ticket.id,
        "reference": ticket.reference,
        "category": ticket.category,
        "category_label_ar": CATEGORY_LABELS.get(ticket.category, ticket.category),
        "priority": ticket.priority,
        "priority_label_ar": PRIORITY_LABELS.get(ticket.priority, ticket.priority),
        "status": ticket.status,
        "status_label_ar": STATUS_LABELS.get(ticket.status, ticket.status),
        "subject": ticket.subject,
        "booking_id": ticket.booking_id,
        "user_id": ticket.user_id,
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at,
        "resolved_at": ticket.resolved_at,
    }


def ticket_detail(ticket: SupportTicket) -> dict:
    data = ticket_summary(ticket)
    data["messages"] = [message_out(m) for m in ticket.messages]
    return data


def create_support_ticket(
    db: Session,
    *,
    user: User,
    category: str,
    subject: str,
    message: str,
    priority: str = "normal",
    booking_id: uuid.UUID | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> SupportTicket:
    if booking_id is not None:
        from app.models import Booking

        booking = db.get(Booking, booking_id)
        if not booking or booking.user_id != user.id:
            raise ValueError("الحجز غير موجود أو لا يخصك")

    now = datetime.now(timezone.utc)
    ticket = SupportTicket(
        id=uuid.uuid4(),
        reference=next_ticket_reference(db),
        user_id=user.id,
        booking_id=booking_id,
        category=category,
        priority=priority,
        status="open",
        subject=subject.strip(),
        created_at=now,
        updated_at=now,
    )
    db.add(ticket)
    db.flush()

    db.add(
        SupportTicketMessage(
            id=uuid.uuid4(),
            ticket_id=ticket.id,
            author_type="customer",
            author_label=user.full_name,
            message=message.strip(),
            created_at=now,
        )
    )

    log_security_event(
        db,
        event_type="ticket_created",
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
        metadata={"reference": ticket.reference, "category": category},
    )
    return ticket


def add_ticket_message(
    db: Session,
    ticket: SupportTicket,
    *,
    author_type: str,
    author_label: str,
    message: str,
    new_status: str | None = None,
) -> SupportTicketMessage:
    now = datetime.now(timezone.utc)
    msg = SupportTicketMessage(
        id=uuid.uuid4(),
        ticket_id=ticket.id,
        author_type=author_type,
        author_label=author_label,
        message=message.strip(),
        created_at=now,
    )
    db.add(msg)
    ticket.updated_at = now
    if new_status and new_status in TICKET_STATUSES:
        ticket.status = new_status
        if new_status in {"resolved", "closed"}:
            ticket.resolved_at = now
    return msg


def update_ticket_admin(
    db: Session,
    ticket: SupportTicket,
    *,
    status: str | None = None,
    priority: str | None = None,
) -> SupportTicket:
    now = datetime.now(timezone.utc)
    if status and status in TICKET_STATUSES:
        ticket.status = status
        if status in {"resolved", "closed"}:
            ticket.resolved_at = now
    if priority:
        ticket.priority = priority
    ticket.updated_at = now
    return ticket


def get_user_security_summary(db: Session, user_id: uuid.UUID) -> dict:
    profile = _get_or_create_security_profile(db, user_id)
    recent = db.scalars(
        select(SecurityAuditLog)
        .where(SecurityAuditLog.user_id == user_id)
        .order_by(SecurityAuditLog.created_at.desc())
        .limit(10)
    ).all()
    open_count = db.scalar(
        select(func.count())
        .select_from(SupportTicket)
        .where(
            SupportTicket.user_id == user_id,
            SupportTicket.status.in_(("open", "in_progress", "waiting_customer")),
        )
    ) or 0

    return {
        "login_alerts_enabled": profile.login_alerts_enabled,
        "suspicious_activity_reported_at": profile.suspicious_activity_reported_at,
        "last_security_review_at": profile.last_security_review_at,
        "open_tickets_count": open_count,
        "recent_events": [
            {
                "id": e.id,
                "event_type": e.event_type,
                "severity": e.severity,
                "created_at": e.created_at,
                "metadata": e.metadata_,
            }
            for e in recent
        ],
    }


def report_suspicious_activity(
    db: Session,
    user: User,
    *,
    description: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> dict:
    profile = _get_or_create_security_profile(db, user.id)
    now = datetime.now(timezone.utc)
    profile.suspicious_activity_reported_at = now
    profile.updated_at = now

    log_security_event(
        db,
        event_type="suspicious_activity_reported",
        user_id=user.id,
        severity="warn",
        ip_address=ip_address,
        user_agent=user_agent,
        metadata={"description": description[:500]},
    )
    return get_user_security_summary(db, user.id)


def load_ticket(
    db: Session, ticket_id: uuid.UUID, *, user_id: uuid.UUID | None = None
) -> SupportTicket | None:
    stmt = (
        select(SupportTicket)
        .options(joinedload(SupportTicket.messages))
        .where(SupportTicket.id == ticket_id)
    )
    if user_id:
        stmt = stmt.where(SupportTicket.user_id == user_id)
    return db.scalar(stmt)
