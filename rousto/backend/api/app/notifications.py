"""Firebase Cloud Messaging integration (optional).

Set FCM_ENABLED=true and provide FCM_CREDENTIALS_PATH to activate.
"""

import logging
from typing import Any

from app.config import settings

logger = logging.getLogger("rousto.notifications")


def send_push(
    *,
    token: str,
    title: str,
    body: str,
    data: dict[str, str] | None = None,
) -> bool:
    if not settings.fcm_enabled:
        logger.debug("FCM disabled; skipped push to %s", token[:8])
        return False
    if not settings.fcm_credentials_path:
        logger.warning("FCM enabled but FCM_CREDENTIALS_PATH is empty")
        return False

    try:
        # Production: use firebase_admin.messaging.send()
        logger.info("FCM stub send title=%s token=%s...", title, token[:8])
        return True
    except Exception as exc:
        logger.exception("FCM send failed: %s", exc)
        return False


def notify_booking_update(user_id: str, booking_ref: str, status: str) -> None:
    """Queue a booking status push — wire to device tokens table in production."""
    _ = (user_id, booking_ref, status)
    logger.debug("notify_booking_update stub called")
