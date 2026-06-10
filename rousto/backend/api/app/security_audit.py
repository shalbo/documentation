"""Security audit helpers — log auth failures and rate limits."""

from fastapi import Request
from sqlalchemy.orm import Session

from app.support_services import log_security_event


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def audit_security_event(
    db: Session,
    request: Request,
    *,
    event_type: str,
    user_id=None,
    severity: str = "warn",
    metadata: dict | None = None,
) -> None:
    try:
        log_security_event(
            db,
            event_type=event_type,
            user_id=user_id,
            severity=severity,
            ip_address=client_ip(request),
            user_agent=request.headers.get("User-Agent"),
            metadata=metadata or {},
        )
        db.commit()
    except Exception:
        db.rollback()
