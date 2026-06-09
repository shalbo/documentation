import math
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Booking, BookingStatusEvent, Technician, TechnicianLocationUpdate

TRACKING_ORDER = [
    "confirmed",
    "technician_assigned",
    "en_route",
    "in_progress",
    "completed",
]

STATUS_EVENT_LABELS = {
    "confirmed": "تم تأكيد الحجز",
    "technician_assigned": "تم تعيين الفني",
    "en_route": "الفني في الطريق إليك",
    "in_progress": "جاري تنفيذ الخدمة",
    "completed": "اكتملت الخدمة",
}

ACTIVE_LOGISTICS_STATUSES = {
    "confirmed",
    "technician_assigned",
    "en_route",
    "in_progress",
}

AVG_SPEED_KMH = 30.0


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def estimate_eta_minutes(distance_km: float, avg_speed_kmh: float = AVG_SPEED_KMH) -> int:
    if distance_km <= 0:
        return 1
    minutes = (distance_km / avg_speed_kmh) * 60
    return max(1, round(minutes))


def compute_logistics_metrics(booking: Booking) -> dict:
    destination = None
    distance_km = None
    eta_minutes = None

    if booking.address and booking.address.latitude is not None:
        destination = {
            "label": f"{booking.address.label} · {booking.address.district}",
            "lat": float(booking.address.latitude),
            "lng": float(booking.address.longitude),
        }

    tech = booking.technician
    if (
        destination
        and tech
        and tech.current_lat is not None
        and tech.current_lng is not None
        and booking.status in {"technician_assigned", "en_route"}
    ):
        distance_km = round(
            haversine_km(
                float(tech.current_lat),
                float(tech.current_lng),
                destination["lat"],
                destination["lng"],
            ),
            2,
        )
        eta_minutes = estimate_eta_minutes(distance_km)

    if eta_minutes is None and booking.status == "en_route":
        for event in reversed(booking.status_events):
            if event.status == "en_route" and event.metadata_:
                eta_minutes = event.metadata_.get("eta_minutes")
                break

    return {
        "destination": destination,
        "distance_km": distance_km,
        "eta_minutes": eta_minutes,
    }


def build_full_tracking_steps(booking: Booking) -> list[dict]:
    events_by_status = {event.status: event for event in booking.status_events}
    current_idx = (
        TRACKING_ORDER.index(booking.status)
        if booking.status in TRACKING_ORDER
        else -1
    )
    steps = []

    for i, status in enumerate(TRACKING_ORDER):
        event = events_by_status.get(status)
        if i <= current_idx:
            label = event.label_ar if event else STATUS_EVENT_LABELS[status]
            occurred_at = event.occurred_at if event else booking.created_at
            steps.append(
                {
                    "status": status,
                    "label_ar": label,
                    "occurred_at": occurred_at,
                    "is_current": status == booking.status,
                    "is_done": i < current_idx,
                }
            )
        else:
            steps.append(
                {
                    "status": status,
                    "label_ar": STATUS_EVENT_LABELS[status],
                    "occurred_at": None,
                    "is_current": False,
                    "is_done": False,
                }
            )
    return steps


def load_booking_for_logistics(
    db: Session, booking_id: UUID, user_id: UUID | None = None
) -> Booking | None:
    stmt = (
        select(Booking)
        .options(
            joinedload(Booking.service),
            joinedload(Booking.vehicle),
            joinedload(Booking.address),
            joinedload(Booking.technician),
            joinedload(Booking.status_events),
        )
        .where(Booking.id == booking_id)
    )
    if user_id:
        stmt = stmt.where(Booking.user_id == user_id)
    return db.scalar(stmt)


def transition_booking_status(
    db: Session,
    booking: Booking,
    new_status: str,
    *,
    metadata: dict | None = None,
) -> Booking:
    if new_status not in TRACKING_ORDER:
        raise ValueError("حالة غير مدعومة")

    current_idx = (
        TRACKING_ORDER.index(booking.status)
        if booking.status in TRACKING_ORDER
        else -1
    )
    new_idx = TRACKING_ORDER.index(new_status)
    if new_idx <= current_idx:
        raise ValueError("لا يمكن الرجوع لحالة سابقة")

    now = datetime.now(timezone.utc)
    event_metadata = metadata or {}

    if new_status == "en_route" and booking.address and booking.technician:
        metrics = compute_logistics_metrics(booking)
        if metrics["eta_minutes"] is not None:
            event_metadata["eta_minutes"] = metrics["eta_minutes"]
        if metrics["distance_km"] is not None:
            event_metadata["distance_km"] = metrics["distance_km"]

    booking.status = new_status
    booking.updated_at = now
    db.add(
        BookingStatusEvent(
            id=uuid4(),
            booking_id=booking.id,
            status=new_status,
            label_ar=STATUS_EVENT_LABELS[new_status],
            occurred_at=now,
            metadata_=event_metadata,
        )
    )
    if new_status == "completed":
        from app.split_payments import release_technician_splits

        release_technician_splits(db, booking.id)

    db.commit()

    try:
        from app.notifications import notify_booking_status_change

        notify_booking_status_change(
            db,
            user_id=booking.user_id,
            booking_ref=booking.reference,
            status=new_status,
            label_ar=STATUS_EVENT_LABELS[new_status],
        )
    except Exception:
        pass

    return booking


def advance_booking_status(db: Session, booking: Booking) -> Booking:
    if booking.status not in TRACKING_ORDER:
        raise ValueError("حالة الحجز غير قابلة للتقدم")
    current_idx = TRACKING_ORDER.index(booking.status)
    if current_idx >= len(TRACKING_ORDER) - 1:
        raise ValueError("الحجز مكتمل بالفعل")
    next_status = TRACKING_ORDER[current_idx + 1]
    return transition_booking_status(db, booking, next_status)


def update_technician_location(
    db: Session,
    technician: Technician,
    lat: float,
    lng: float,
    *,
    booking_id: UUID | None = None,
) -> Technician:
    now = datetime.now(timezone.utc)
    technician.current_lat = lat
    technician.current_lng = lng
    db.add(
        TechnicianLocationUpdate(
            id=uuid4(),
            technician_id=technician.id,
            booking_id=booking_id,
            lat=lat,
            lng=lng,
            recorded_at=now,
        )
    )
    db.commit()
    db.refresh(technician)
    return technician


def simulate_technician_move(db: Session, booking: Booking, *, step_ratio: float = 0.15) -> Booking:
    if not booking.technician or not booking.address:
        raise ValueError("الحجز يفتقد فني أو عنوان")
    if booking.address.latitude is None or booking.technician.current_lat is None:
        raise ValueError("إحداثيات غير متوفرة")

    tech_lat = float(booking.technician.current_lat)
    tech_lng = float(booking.technician.current_lng)
    dest_lat = float(booking.address.latitude)
    dest_lng = float(booking.address.longitude)

    new_lat = tech_lat + (dest_lat - tech_lat) * step_ratio
    new_lng = tech_lng + (dest_lng - tech_lng) * step_ratio

    update_technician_location(
        db,
        booking.technician,
        new_lat,
        new_lng,
        booking_id=booking.id,
    )

    db.refresh(booking.technician)

    if booking.status == "en_route":
        for event in reversed(booking.status_events):
            if event.status == "en_route":
                metrics = compute_logistics_metrics(booking)
                event.metadata_ = {
                    **(event.metadata_ or {}),
                    **{
                        k: v
                        for k, v in metrics.items()
                        if k in {"eta_minutes", "distance_km"} and v is not None
                    },
                }
                db.commit()
                break

    db.refresh(booking)
    return booking
