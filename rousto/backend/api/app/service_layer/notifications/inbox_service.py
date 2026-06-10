"""Notification inbox facade."""

from app.notification_inbox_services import (
    NOTIFICATION_CATEGORIES,
    list_notifications,
    list_user_preferences,
    mark_all_read,
    mark_read,
    unread_count,
    update_user_preferences,
)

__all__ = [
    "NOTIFICATION_CATEGORIES",
    "list_notifications",
    "list_user_preferences",
    "mark_all_read",
    "mark_read",
    "unread_count",
    "update_user_preferences",
]
