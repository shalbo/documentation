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
) -> None:
    from app.notification_inbox_services import notify_from_template

    try:
        notification = notify_from_template(
            db,
            user_id,
            "booking_status",
            {"reference": booking_ref, "label": label_ar},
            extra_data={
                "booking_ref": booking_ref,
                "status": status,
                "type": "booking_status",
            },
        )
        if notification:
            from app.notification_engine_services import record_dispatch_log

            record_dispatch_log(
                db,
                event_source="booking_hook",
                user_id=user_id,
                category="booking",
                title=notification.title,
                notification_id=notification.id,
                template_slug="booking_status",
                push_sent=notification.push_sent,
                in_app_created=True,
            )
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.warning("Booking notification failed: %s", exc)


def notify_support_reply(
    db: Session,
    *,
    user_id,
    ticket_ref: str,
    preview: str,
) -> None:
    from app.notification_inbox_services import notify_from_template

    try:
        notification = notify_from_template(
            db,
            user_id,
            "support_reply",
            {"reference": ticket_ref, "preview": preview[:200]},
            extra_data={
                "ticket_ref": ticket_ref,
                "type": "support_reply",
            },
        )
        if notification:
            from app.notification_engine_services import record_dispatch_log

            record_dispatch_log(
                db,
                event_source="support_hook",
                user_id=user_id,
                category="support",
                title=notification.title,
                notification_id=notification.id,
                template_slug="support_reply",
                push_sent=notification.push_sent,
                in_app_created=True,
            )
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.warning("Support notification failed: %s", exc)


def notify_customer_booking_created(db: Session, *, booking) -> None:
    from app.i18n import BOOKING_EVENT_LABELS, label_from_map
    from app.models import User

    user = db.get(User, booking.user_id)
    locale = user.locale if user and user.locale in {"ar", "en"} else "ar"
    label = label_from_map(BOOKING_EVENT_LABELS, "confirmed", locale)
    notify_booking_status_change(
        db,
        user_id=booking.user_id,
        booking_ref=booking.reference,
        status=booking.status,
        label_ar=label,
    )


def notify_vendor_new_booking(db: Session, *, booking) -> None:
    from app.models import UserVendorLink
    from app.notification_inbox_services import dispatch_user_notification
    from sqlalchemy import select

    vendor_user_id = None
    if booking.technician_id:
        link = db.scalar(
            select(UserVendorLink).where(UserVendorLink.vendor_id.isnot(None)).limit(1)
        )
        if link:
            vendor_user_id = link.user_id

    if not vendor_user_id:
        return

    try:
        dispatch_user_notification(
            db,
            vendor_user_id,
            category="booking",
            title=f"New booking {booking.reference}",
            body="A customer placed a new service booking.",
            data={
                "type": "vendor_new_booking",
                "booking_ref": booking.reference,
                "booking_id": str(booking.id),
            },
            send_push=True,
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.warning("Vendor booking notification failed: %s", exc)


def notify_nearby_drivers_towing(
    db: Session,
    *,
    dispatch,
    pickup_lat: float,
    pickup_lng: float,
    radius_km: float = 15.0,
) -> int:
    from app.logistics_services import haversine_km
    from app.models import Technician, UserVendorLink, Vendor
    from app.notification_inbox_services import dispatch_user_notification
    from sqlalchemy import select

    technicians = db.scalars(
        select(Technician).where(
            Technician.is_available.is_(True),
            Technician.driver_type == "tow",
            Technician.current_lat.isnot(None),
            Technician.current_lng.isnot(None),
        )
    ).all()

    sent = 0
    for tech in technicians:
        dist = haversine_km(
            float(tech.current_lat),
            float(tech.current_lng),
            pickup_lat,
            pickup_lng,
        )
        if dist > radius_km:
            continue

        vendor = db.scalar(
            select(Vendor).where(
                Vendor.technician_id == tech.id,
                Vendor.status == "approved",
            )
        )
        if not vendor:
            continue
        link = db.scalar(
            select(UserVendorLink).where(UserVendorLink.vendor_id == vendor.id)
        )
        if not link:
            continue
        user_id = link.user_id

        try:
            dispatch_user_notification(
                db,
                user_id,
                category="towing",
                title=f"Urgent towing request {dispatch.reference}",
                body=f"Pickup within {round(dist, 1)} km — respond immediately.",
                data={
                    "type": "driver_towing_alert",
                    "dispatch_ref": dispatch.reference,
                    "dispatch_id": str(dispatch.id),
                    "distance_km": str(round(dist, 1)),
                    "priority": "high",
                },
                send_push=True,
            )
            sent += 1
        except Exception as exc:
            logger.warning("Driver towing alert failed: %s", exc)

    if sent:
        db.commit()
    return sent


def notify_towing_status_change(
    db: Session,
    *,
    user_id,
    dispatch_ref: str,
    status: str,
    label_ar: str,
) -> None:
    from app.notification_inbox_services import notify_from_template

    try:
        notification = notify_from_template(
            db,
            user_id,
            "towing_status",
            {"reference": dispatch_ref, "label": label_ar},
            extra_data={
                "dispatch_ref": dispatch_ref,
                "status": status,
                "type": "towing_status",
            },
        )
        if notification:
            from app.notification_engine_services import record_dispatch_log

            record_dispatch_log(
                db,
                event_source="towing_hook",
                user_id=user_id,
                category="towing",
                title=notification.title,
                notification_id=notification.id,
                template_slug="towing_status",
                push_sent=notification.push_sent,
                in_app_created=True,
            )
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.warning("Towing notification failed: %s", exc)
