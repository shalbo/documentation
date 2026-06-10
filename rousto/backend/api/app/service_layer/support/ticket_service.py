"""Support ticket facade."""

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

__all__ = [
    "add_ticket_message",
    "create_support_ticket",
    "faq_out",
    "get_user_security_summary",
    "load_ticket",
    "log_security_event",
    "report_suspicious_activity",
    "ticket_detail",
    "ticket_summary",
    "update_ticket_admin",
]
