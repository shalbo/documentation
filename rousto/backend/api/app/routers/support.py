from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user, require_admin_key
from app.models import SecurityAuditLog, SupportFaq, SupportTicket, User
from app.schemas import (
    SecurityReportIn,
    SupportTicketCreateIn,
    SupportTicketMessageIn,
    SupportTicketReplyIn,
    SupportTicketUpdateIn,
)
from app.support_services import (
    add_ticket_message,
    create_support_ticket,
    faq_out,
    get_user_security_summary,
    load_ticket,
    log_security_event,
    report_suspicious_activity,
    ticket_detail,
    ticket_summary,
    update_ticket_admin,
)

router = APIRouter(tags=["support"])


def _client_meta(request: Request) -> tuple[str | None, str | None]:
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    return ip, ua


@router.get("/support/faq")
def list_faq(
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = (
        select(SupportFaq)
        .where(SupportFaq.is_active.is_(True))
        .order_by(SupportFaq.sort_order, SupportFaq.slug)
    )
    if category:
        query = query.where(SupportFaq.category == category)

    items = db.scalars(query).all()
    data = [faq_out(item) for item in items]
    return {"data": data, "meta": {"total": len(data)}}


@router.post("/support/tickets", status_code=201)
def post_support_ticket(
    body: SupportTicketCreateIn,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ip, ua = _client_meta(request)
    try:
        ticket = create_support_ticket(
            db,
            user=user,
            category=body.category,
            subject=body.subject,
            message=body.message,
            priority=body.priority,
            booking_id=body.booking_id,
            ip_address=ip,
            user_agent=ua,
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "TICKET_ERROR", "message": str(exc)},
        ) from exc

    ticket = load_ticket(db, ticket.id, user_id=user.id)
    return {"data": ticket_detail(ticket)}


@router.get("/support/tickets")
def list_my_tickets(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tickets = db.scalars(
        select(SupportTicket)
        .where(SupportTicket.user_id == user.id)
        .order_by(SupportTicket.created_at.desc())
    ).all()
    data = [ticket_summary(t) for t in tickets]
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/support/tickets/{ticket_id}")
def get_support_ticket(
    ticket_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = load_ticket(db, ticket_id, user_id=user.id)
    if not ticket:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "التذكرة غير موجودة"},
        )
    return {"data": ticket_detail(ticket)}


@router.post("/support/tickets/{ticket_id}/messages")
def post_ticket_message(
    ticket_id: UUID,
    body: SupportTicketMessageIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = load_ticket(db, ticket_id, user_id=user.id)
    if not ticket:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "التذكرة غير موجودة"},
        )
    if ticket.status in {"resolved", "closed"}:
        raise HTTPException(
            status_code=400,
            detail={"code": "TICKET_CLOSED", "message": "التذكرة مغلقة"},
        )

    add_ticket_message(
        db,
        ticket,
        author_type="customer",
        author_label=user.full_name,
        message=body.message,
        new_status="open" if ticket.status == "waiting_customer" else None,
    )
    db.commit()
    ticket = load_ticket(db, ticket_id, user_id=user.id)
    return {"data": ticket_detail(ticket)}


@router.get("/me/security")
def get_my_security(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {"data": get_user_security_summary(db, user.id)}


@router.post("/me/security/report")
def post_security_report(
    body: SecurityReportIn,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ip, ua = _client_meta(request)
    data = report_suspicious_activity(
        db,
        user,
        description=body.description,
        ip_address=ip,
        user_agent=ua,
    )
    db.commit()
    return {"data": data}


@router.get("/admin/support/tickets")
def admin_list_tickets(
    status: str | None = Query(default=None),
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    query = select(SupportTicket).order_by(SupportTicket.created_at.desc())
    if status:
        query = query.where(SupportTicket.status == status)

    tickets = db.scalars(query).all()
    data = [ticket_summary(t) for t in tickets]
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/admin/support/tickets/{ticket_id}")
def admin_get_ticket(
    ticket_id: UUID,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    ticket = load_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "التذكرة غير موجودة"},
        )
    return {"data": ticket_detail(ticket)}


@router.patch("/admin/support/tickets/{ticket_id}")
def admin_update_ticket(
    ticket_id: UUID,
    body: SupportTicketUpdateIn,
    request: Request,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    ticket = db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "التذكرة غير موجودة"},
        )

    update_ticket_admin(db, ticket, status=body.status, priority=body.priority)
    ip, ua = _client_meta(request)
    log_security_event(
        db,
        event_type="ticket_updated",
        severity="info",
        ip_address=ip,
        user_agent=ua,
        metadata={"reference": ticket.reference, "status": ticket.status},
    )
    db.commit()
    ticket = load_ticket(db, ticket_id)
    return {"data": ticket_detail(ticket)}


@router.post("/admin/support/tickets/{ticket_id}/reply")
def admin_reply_ticket(
    ticket_id: UUID,
    body: SupportTicketReplyIn,
    request: Request,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    ticket = load_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "التذكرة غير موجودة"},
        )

    add_ticket_message(
        db,
        ticket,
        author_type="admin",
        author_label="فريق الدعم",
        message=body.message,
        new_status=body.status or "waiting_customer",
    )
    ip, ua = _client_meta(request)
    log_security_event(
        db,
        event_type="ticket_replied",
        user_id=ticket.user_id,
        ip_address=ip,
        user_agent=ua,
        metadata={"reference": ticket.reference},
    )
    db.commit()
    ticket = load_ticket(db, ticket_id)
    return {"data": ticket_detail(ticket)}


@router.get("/admin/security/events")
def admin_security_events(
    severity: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    query = select(SecurityAuditLog).order_by(SecurityAuditLog.created_at.desc()).limit(limit)
    if severity:
        query = query.where(SecurityAuditLog.severity == severity)

    events = db.scalars(query).all()
    data = [
        {
            "id": e.id,
            "user_id": e.user_id,
            "event_type": e.event_type,
            "severity": e.severity,
            "ip_address": e.ip_address,
            "metadata": e.metadata_,
            "created_at": e.created_at,
        }
        for e in events
    ]
    return {"data": data, "meta": {"total": len(data)}}
