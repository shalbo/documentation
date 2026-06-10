"""Financial audit logging."""

from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import PaymentAuditLog

logger = logging.getLogger("rousto.payments")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def log_payment_event(
    db: Session,
    *,
    event_type: str,
    gateway: str | None = None,
    reference_id: uuid.UUID | None = None,
    ip_address: str | None = None,
    payload: bytes | dict | None = None,
    details: dict | None = None,
) -> PaymentAuditLog:
    payload_hash = None
    if isinstance(payload, bytes):
        payload_hash = hashlib.sha256(payload).hexdigest()
    entry = PaymentAuditLog(
        id=uuid.uuid4(),
        event_type=event_type,
        gateway=gateway,
        reference_id=reference_id,
        ip_address=ip_address,
        payload_hash=payload_hash,
        details_json=details or {},
        created_at=_now(),
    )
    db.add(entry)
    logger.info(
        "payment_audit event=%s gateway=%s ref=%s",
        event_type,
        gateway,
        reference_id,
    )
    return entry
