import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import UserDeviceToken


def register_device_token(
    db: Session,
    *,
    user_id: uuid.UUID,
    fcm_token: str,
    platform: str = "unknown",
) -> UserDeviceToken:
    token = fcm_token.strip()
    if len(token) < 20:
        raise ValueError("رمز الجهاز غير صالح")

    now = datetime.now(timezone.utc)
    existing = db.scalar(
        select(UserDeviceToken).where(
            UserDeviceToken.user_id == user_id,
            UserDeviceToken.fcm_token == token,
        )
    )
    if existing:
        existing.is_active = True
        existing.platform = platform
        existing.updated_at = now
        return existing

    entry = UserDeviceToken(
        id=uuid.uuid4(),
        user_id=user_id,
        fcm_token=token,
        platform=platform,
        created_at=now,
        updated_at=now,
    )
    db.add(entry)
    db.flush()
    return entry


def deactivate_device_token(db: Session, user_id: uuid.UUID, fcm_token: str) -> bool:
    entry = db.scalar(
        select(UserDeviceToken).where(
            UserDeviceToken.user_id == user_id,
            UserDeviceToken.fcm_token == fcm_token.strip(),
        )
    )
    if not entry:
        return False
    entry.is_active = False
    entry.updated_at = datetime.now(timezone.utc)
    return True


def list_active_tokens(db: Session, user_id: uuid.UUID) -> list[str]:
    rows = db.scalars(
        select(UserDeviceToken.fcm_token).where(
            UserDeviceToken.user_id == user_id,
            UserDeviceToken.is_active.is_(True),
        )
    ).all()
    return list(rows)
