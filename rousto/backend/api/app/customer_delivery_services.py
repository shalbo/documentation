from app.logistics_services import (
    build_full_tracking_steps,
    compute_logistics_metrics,
    haversine_km,
)
from app.models import Booking
from app.services import status_label_ar, to_float
from app.vendor_map_services import get_location_trail

REFRESH_INTERVAL_SECONDS = 20
TRAIL_LIMIT = 20

DELIVERY_PHASES = {
    "pending": ("waiting", "بانتظار التأكيد"),
    "confirmed": ("waiting", "بانتظار تعيين الفني"),
    "technician_assigned": ("assigned", "تم تعيين الفني"),
    "en_route": ("en_route", "الفني في الطريق إليك"),
    "in_progress": ("arrived", "جاري تنفيذ الخدمة"),
    "completed": ("completed", "اكتملت الخدمة"),
    "cancelled": ("cancelled", "ملغى"),
}

LIVE_STATUSES = frozenset({"technician_assigned", "en_route", "in_progress"})


def _delivery_phase(booking: Booking) -> tuple[str, str]:
    return DELIVERY_PHASES.get(booking.status, ("waiting", "غير معروف"))


def _initial_distance_km(
    booking: Booking,
    trail: list[dict],
    destination: dict | None,
) -> float | None:
    if not destination:
        return None

    dest_lat = destination["lat"]
    dest_lng = destination["lng"]

    if trail:
        first = trail[0]
        return round(
            haversine_km(first["lat"], first["lng"], dest_lat, dest_lng),
            2,
        )

    for event in booking.status_events:
        if event.status == "en_route" and event.metadata_:
            stored = event.metadata_.get("distance_km")
            if stored is not None:
                return round(float(stored), 2)

    tech = booking.technician
    if tech and tech.current_lat is not None:
        return round(
            haversine_km(
                float(tech.current_lat),
                float(tech.current_lng),
                dest_lat,
                dest_lng,
            ),
            2,
        )

    return None


def _progress_percent(
    current_distance_km: float | None,
    initial_distance_km: float | None,
    status: str,
) -> float | None:
    if status == "completed":
        return 100.0
    if status == "in_progress":
        return 95.0
    if current_distance_km is None or initial_distance_km is None:
        return None
    if initial_distance_km <= 0:
        return None

    progress = (1 - current_distance_km / initial_distance_km) * 100
    return round(max(0.0, min(100.0, progress)), 1)


def _map_bounds(points: list[tuple[float, float]]) -> dict | None:
    if not points:
        return None

    lats = [p[0] for p in points]
    lngs = [p[1] for p in points]
    padding = 0.0005

    return {
        "min_lat": round(min(lats) - padding, 7),
        "max_lat": round(max(lats) + padding, 7),
        "min_lng": round(min(lngs) - padding, 7),
        "max_lng": round(max(lngs) + padding, 7),
    }


def build_customer_delivery_map(db, booking: Booking) -> dict:
    metrics = compute_logistics_metrics(booking)
    destination = metrics.get("destination")
    phase_key, phase_label = _delivery_phase(booking)

    trail: list[dict] = []
    if booking.technician_id:
        trail = get_location_trail(
            db,
            booking.technician_id,
            booking_id=booking.id,
            limit=TRAIL_LIMIT,
        )

    initial_distance = _initial_distance_km(booking, trail, destination)
    progress = _progress_percent(
        metrics.get("distance_km"),
        initial_distance,
        booking.status,
    )

    technician_out = None
    if booking.technician:
        technician_out = {
            "id": str(booking.technician.id),
            "full_name": booking.technician.full_name,
            "phone": booking.technician.phone,
            "rating": to_float(booking.technician.rating),
            "avatar_initials": booking.technician.avatar_initials,
            "eta_minutes": metrics.get("eta_minutes"),
            "location": (
                {
                    "lat": to_float(booking.technician.current_lat),
                    "lng": to_float(booking.technician.current_lng),
                }
                if booking.technician.current_lat is not None
                else None
            ),
        }

    map_points: list[tuple[float, float]] = []
    if destination:
        map_points.append((destination["lat"], destination["lng"]))
    if technician_out and technician_out.get("location"):
        loc = technician_out["location"]
        map_points.append((loc["lat"], loc["lng"]))
    for point in trail:
        map_points.append((point["lat"], point["lng"]))

    is_live = booking.status in LIVE_STATUSES and technician_out is not None

    return {
        "booking": {
            "id": booking.id,
            "reference": booking.reference,
            "status": booking.status,
            "status_label_ar": status_label_ar(booking.status),
        },
        "delivery_phase": phase_key,
        "delivery_phase_label_ar": phase_label,
        "is_live": is_live,
        "refresh_interval_seconds": REFRESH_INTERVAL_SECONDS if is_live else None,
        "technician": technician_out,
        "customer_location": destination,
        "distance_km": metrics.get("distance_km"),
        "eta_minutes": metrics.get("eta_minutes"),
        "initial_distance_km": initial_distance,
        "progress_percent": progress,
        "trail": trail,
        "map_bounds": _map_bounds(map_points),
        "steps": build_full_tracking_steps(booking),
    }
