"""Firebase Cloud Messaging — optional push notifications."""

import logging

from sqlalchemy.orm import Session

from app.config import settings
from app.device_services import list_active_tokens

logger = logging.getLogger("rousto.notifications")

_fcm_ready = False


def _init_fcm() -> bool:
    global _fcm_ready
    if _fcm_ready:
        return True
    if not settings.fcm_enabled or not settings.fcm_credentials_path:
        return False
    try:
        import firebase_admin
        from firebase_admin import credentials

        if not firebase_admin._apps:
            cred = credentials.Certificate(settings.fcm_credentials_path)
            firebase_admin.initialize_app(cred)
        _fcm_ready = True
        logger.info("Firebase Admin SDK initialized")
        return True
    except ImportError:
        logger.warning("firebase-admin not installed; FCM disabled")
        return False
    except Exception as exc:
        logger.exception("FCM init failed: %s", exc)
        return False


def send_push(
    *,
    token: str,
    title: str,
    body: str,
    data: dict[str, str] | None = None,
) -> bool:
    if not _init_fcm():
        return False

    try:
        from firebase_admin import messaging

        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data={k: str(v) for k, v in (data or {}).items()},
            token=token,
            android=messaging.AndroidConfig(priority="high"),
        )
        messaging.send(message)
        return True
    except Exception as exc:
        logger.warning("FCM send failed: %s", exc)
        return False


def send_push_to_user(
    db: Session,
    user_id,
    *,
    title: str,
    body: str,
    data: dict[str, str] | None = None,
) -> int:
    tokens = list_active_tokens(db, user_id)
    sent = 0
    for token in tokens:
        if send_push(token=token, title=title, body=body, data=data):
            sent += 1
    return sent


def notify_booking_status_change(
    db: Session,
    *,
    user_id,
    booking_ref: str,
    status: str,
    label_ar: str,
) -> int:
    return send_push_to_user(
        db,
        user_id,
        title=f"تحديث حجز {booking_ref}",
        body=label_ar,
        data={
            "type": "booking_status",
            "booking_ref": booking_ref,
            "status": status,
        },
    )
