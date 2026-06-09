import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.logistics_services import estimate_eta_minutes, haversine_km, update_technician_location
from app.models import Booking, Technician, TowingDispatch, TowingDispatchEvent
from app.vendor_map_services import get_location_trail

REFRESH_INTERVAL_SECONDS = 20
TRAIL_LIMIT = 20

DISPATCH_ORDER = [
    "pending",
    "dispatched",
    "en_route_pickup",
    "at_pickup",
    "en_route_dropoff",
    "completed",
]

DISPATCH_PHASES = {
    "pending": ("waiting", "بانتظار الإرسال"),
    "dispatched": ("assigned", "تم تعيين السطحة"),
    "en_route_pickup": ("to_pickup", "السطحة متجهة لموقع العطل"),
    "at_pickup": ("at_pickup", "السطحة عند السيارة"),
    "en_route_dropoff": ("to_dropoff", "نقل السيارة إلى الورشة"),
    "completed": ("completed", "تم التسليم"),
    "cancelled": ("cancelled", "ملغى"),
}

PICKUP_LEG_STATUSES = frozenset({"dispatched", "en_route_pickup"})
DROPOFF_LEG_STATUSES = frozenset({"at_pickup", "en_route_dropoff"})
LIVE_STATUSES = frozenset(
    {"dispatched", "en_route_pickup", "at_pickup", "en_route_dropoff"}
)

STATUS_LABELS = {
    "pending": "طلب سحب جديد",
    "dispatched": "تم تعيين السطحة",
    "en_route_pickup": "متجه لموقع العطل",
    "at_pickup": "عند السيارة",
    "en_route_dropoff": "متجه للورشة",
    "completed": "تم التسليم",
    "cancelled": "ملغى",
}


def _location(label: str, lat: float, lng: float) -> dict:
    return {"label": label, "lat": float(lat), "lng": float(lng)}


def _active_leg(status: str) -> str | None:
    if status in PICKUP_LEG_STATUSES:
        return "to_pickup"
    if status in DROPOFF_LEG_STATUSES:
        return "to_dropoff"
    return None


def _current_target(dispatch: TowingDispatch) -> dict | None:
    leg = _active_leg(dispatch.status)
    if leg == "to_pickup":
        return _location(dispatch.pickup_label, dispatch.pickup_lat, dispatch.pickup_lng)
    if leg == "to_dropoff":
        return _location(dispatch.dropoff_label, dispatch.dropoff_lat, dispatch.dropoff_lng)
    return None


def _map_bounds(points: list[tuple[float, float]]) -> dict | None:
    if not points:
        return None
    lats = [p[0] for p in points]
    lngs = [p[1] for p in points]
    pad = 0.0008
    return {
        "min_lat": round(min(lats) - pad, 7),
        "max_lat": round(max(lats) + pad, 7),
        "min_lng": round(min(lngs) - pad, 7),
        "max_lng": round(max(lngs) + pad, 7),
    }


def _progress_percent(dispatch: TowingDispatch, current_km: float | None) -> float | None:
    if dispatch.status == "completed":
        return 100.0
    if dispatch.status == "at_pickup":
        return 50.0
    total = float(dispatch.total_route_km) if dispatch.total_route_km else None
    if total and current_km is not None and total > 0:
        leg = _active_leg(dispatch.status)
        if leg == "to_pickup":
            pickup_to_dropoff = haversine_km(
                float(dispatch.pickup_lat),
                float(dispatch.pickup_lng),
                float(dispatch.dropoff_lat),
                float(dispatch.dropoff_lng),
            )
            pickup_leg = max(total - pickup_to_dropoff, total * 0.4)
            return round(max(0, min(50, (1 - current_km / pickup_leg) * 50)), 1)
        if leg == "to_dropoff":
            pickup_to_dropoff = haversine_km(
                float(dispatch.pickup_lat),
                float(dispatch.pickup_lng),
                float(dispatch.dropoff_lat),
                float(dispatch.dropoff_lng),
            )
            dropoff_progress = (1 - current_km / pickup_to_dropoff) * 50 if pickup_to_dropoff else 0
            return round(max(50, min(100, 50 + dropoff_progress)), 1)
    return None


def load_dispatch(
    db: Session,
    dispatch_id: uuid.UUID,
    *,
    user_id: uuid.UUID | None = None,
) -> TowingDispatch | None:
    stmt = (
        select(TowingDispatch)
        .options(
            joinedload(TowingDispatch.booking),
            joinedload(TowingDispatch.technician),
            joinedload(TowingDispatch.events),
        )
        .where(TowingDispatch.id == dispatch_id)
    )
    if user_id:
        stmt = stmt.where(TowingDispatch.user_id == user_id)
    return db.scalar(stmt)


def next_dispatch_reference(db: Session) -> str:
    count = db.scalar(select(func.count()).select_from(TowingDispatch)) or 0
    return f"TOW-2026-{count + 1:03d}"


def compute_total_route_km(dispatch: TowingDispatch) -> float:
    pickup_to_dropoff = haversine_km(
        float(dispatch.pickup_lat),
        float(dispatch.pickup_lng),
        float(dispatch.dropoff_lat),
        float(dispatch.dropoff_lng),
    )
    if dispatch.technician and dispatch.technician.current_lat is not None:
        to_pickup = haversine_km(
            float(dispatch.technician.current_lat),
            float(dispatch.technician.current_lng),
            float(dispatch.pickup_lat),
            float(dispatch.pickup_lng),
        )
        return round(to_pickup + pickup_to_dropoff, 2)
    return round(pickup_to_dropoff * 1.2, 2)


def build_dispatch_steps(dispatch: TowingDispatch) -> list[dict]:
    events_by_status = {e.status: e for e in dispatch.events}
    current_idx = (
        DISPATCH_ORDER.index(dispatch.status)
        if dispatch.status in DISPATCH_ORDER
        else -1
    )
    steps = []
    for i, status in enumerate(DISPATCH_ORDER):
        event = events_by_status.get(status)
        if i <= current_idx:
            steps.append(
                {
                    "status": status,
                    "label_ar": event.label_ar if event else STATUS_LABELS[status],
                    "occurred_at": event.occurred_at if event else dispatch.created_at,
                    "is_current": status == dispatch.status,
                    "is_done": i < current_idx,
                }
            )
        else:
            steps.append(
                {
                    "status": status,
                    "label_ar": STATUS_LABELS[status],
                    "occurred_at": None,
                    "is_current": False,
                    "is_done": False,
                }
            )
    return steps


def build_towing_dispatch_map(db: Session, dispatch: TowingDispatch) -> dict:
    phase_key, phase_label = DISPATCH_PHASES.get(
        dispatch.status, ("waiting", "غير معروف")
    )
    pickup = _location(dispatch.pickup_label, dispatch.pickup_lat, dispatch.pickup_lng)
    dropoff = _location(dispatch.dropoff_label, dispatch.dropoff_lat, dispatch.dropoff_lng)
    active_leg = _active_leg(dispatch.status)

    trail: list[dict] = []
    distance_km = None
    eta_minutes = None
    tow_truck = None

    if dispatch.technician_id and dispatch.technician:
        tech = dispatch.technician
        trail = get_location_trail(
            db,
            dispatch.technician_id,
            booking_id=dispatch.booking_id,
            limit=TRAIL_LIMIT,
        )
        target = _current_target(dispatch)
        if target and tech.current_lat is not None:
            distance_km = round(
                haversine_km(
                    float(tech.current_lat),
                    float(tech.current_lng),
                    target["lat"],
                    target["lng"],
                ),
                2,
            )
            eta_minutes = estimate_eta_minutes(distance_km)
        tow_truck = {
            "id": str(tech.id),
            "full_name": tech.full_name,
            "phone": tech.phone,
            "rating": float(tech.rating),
            "avatar_initials": tech.avatar_initials,
            "location": (
                {"lat": float(tech.current_lat), "lng": float(tech.current_lng)}
                if tech.current_lat is not None
                else None
            ),
            "eta_minutes": eta_minutes,
        }

    map_points: list[tuple[float, float]] = [
        (pickup["lat"], pickup["lng"]),
        (dropoff["lat"], dropoff["lng"]),
    ]
    if tow_truck and tow_truck.get("location"):
        loc = tow_truck["location"]
        map_points.append((loc["lat"], loc["lng"]))
    for point in trail:
        map_points.append((point["lat"], point["lng"]))

    total_route = float(dispatch.total_route_km) if dispatch.total_route_km else None
    is_live = dispatch.status in LIVE_STATUSES

    return {
        "dispatch": {
            "id": dispatch.id,
            "reference": dispatch.reference,
            "booking_id": dispatch.booking_id,
            "status": dispatch.status,
            "dispatch_phase": phase_key,
            "dispatch_phase_label_ar": phase_label,
            "notes": dispatch.notes,
        },
        "pickup": pickup,
        "dropoff": dropoff,
        "active_leg": active_leg,
        "tow_truck": tow_truck,
        "distance_km": distance_km,
        "total_route_km": total_route,
        "eta_minutes": eta_minutes,
        "progress_percent": _progress_percent(dispatch, distance_km),
        "trail": trail,
        "map_bounds": _map_bounds(map_points),
        "steps": build_dispatch_steps(dispatch),
        "is_live": is_live,
        "refresh_interval_seconds": REFRESH_INTERVAL_SECONDS if is_live else None,
    }


def create_towing_dispatch(
    db: Session,
    *,
    user_id: uuid.UUID,
    booking_id: uuid.UUID,
    pickup_label: str,
    pickup_lat: float,
    pickup_lng: float,
    dropoff_label: str,
    dropoff_lat: float,
    dropoff_lng: float,
    notes: str | None = None,
) -> TowingDispatch:
    booking = db.get(Booking, booking_id)
    if not booking or booking.user_id != user_id:
        raise ValueError("الحجز غير موجود أو لا يخصك")

    existing = db.scalar(
        select(TowingDispatch).where(TowingDispatch.booking_id == booking_id)
    )
    if existing:
        raise ValueError("يوجد طلب سحب مرتبط بهذا الحجز")

    now = datetime.now(timezone.utc)
    dispatch = TowingDispatch(
        id=uuid.uuid4(),
        reference=next_dispatch_reference(db),
        booking_id=booking_id,
        user_id=user_id,
        pickup_label=pickup_label,
        pickup_lat=pickup_lat,
        pickup_lng=pickup_lng,
        dropoff_label=dropoff_label,
        dropoff_lat=dropoff_lat,
        dropoff_lng=dropoff_lng,
        status="pending",
        notes=notes,
        created_at=now,
        updated_at=now,
    )
    db.add(dispatch)
    db.flush()
    dispatch.total_route_km = compute_total_route_km(dispatch)

    db.add(
        TowingDispatchEvent(
            id=uuid.uuid4(),
            dispatch_id=dispatch.id,
            status="pending",
            label_ar=STATUS_LABELS["pending"],
            occurred_at=now,
            metadata_={},
        )
    )
    return dispatch


def assign_tow_driver(
    db: Session, dispatch: TowingDispatch, technician_id: uuid.UUID
) -> TowingDispatch:
    if dispatch.status != "pending":
        raise ValueError("يمكن التعيين فقط للطلبات المعلّقة")

    technician = db.get(Technician, technician_id)
    if not technician:
        raise ValueError("سائق السطحة غير موجود")

    now = datetime.now(timezone.utc)
    dispatch.technician_id = technician_id
    dispatch.status = "dispatched"
    dispatch.dispatched_at = now
    dispatch.updated_at = now
    dispatch.total_route_km = compute_total_route_km(dispatch)

    db.add(
        TowingDispatchEvent(
            id=uuid.uuid4(),
            dispatch_id=dispatch.id,
            status="dispatched",
            label_ar=f"تم تعيين {technician.full_name}",
            occurred_at=now,
            metadata_={},
        )
    )
    return dispatch


def advance_dispatch_status(db: Session, dispatch: TowingDispatch) -> TowingDispatch:
    if dispatch.status not in DISPATCH_ORDER:
        raise ValueError("حالة غير مدعومة")
    idx = DISPATCH_ORDER.index(dispatch.status)
    if idx >= len(DISPATCH_ORDER) - 1:
        raise ValueError("الطلب مكتمل بالفعل")

    new_status = DISPATCH_ORDER[idx + 1]
    now = datetime.now(timezone.utc)
    metadata: dict = {}

    if dispatch.technician and new_status in {"en_route_pickup", "en_route_dropoff"}:
        target = _current_target_for_status(new_status, dispatch)
        if target and dispatch.technician.current_lat is not None:
            dist = haversine_km(
                float(dispatch.technician.current_lat),
                float(dispatch.technician.current_lng),
                target["lat"],
                target["lng"],
            )
            metadata["distance_km"] = round(dist, 2)
            metadata["eta_minutes"] = estimate_eta_minutes(dist)

    dispatch.status = new_status
    dispatch.updated_at = now
    if new_status == "completed":
        dispatch.completed_at = now

    db.add(
        TowingDispatchEvent(
            id=uuid.uuid4(),
            dispatch_id=dispatch.id,
            status=new_status,
            label_ar=STATUS_LABELS[new_status],
            occurred_at=now,
            metadata_=metadata,
        )
    )
    return dispatch


def _current_target_for_status(status: str, dispatch: TowingDispatch) -> dict | None:
    if status == "en_route_pickup":
        return _location(dispatch.pickup_label, dispatch.pickup_lat, dispatch.pickup_lng)
    if status == "en_route_dropoff":
        return _location(dispatch.dropoff_label, dispatch.dropoff_lat, dispatch.dropoff_lng)
    return None


def update_tow_location(
    db: Session,
    dispatch: TowingDispatch,
    lat: float,
    lng: float,
) -> TowingDispatch:
    if not dispatch.technician:
        raise ValueError("لا يوجد سائق معيّن")
    update_technician_location(
        db,
        dispatch.technician,
        lat,
        lng,
        booking_id=dispatch.booking_id,
    )
    db.refresh(dispatch)
    return dispatch
