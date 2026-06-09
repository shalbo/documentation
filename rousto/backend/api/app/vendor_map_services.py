import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.logistics_services import (
    ACTIVE_LOGISTICS_STATUSES,
    compute_logistics_metrics,
    update_technician_location,
)
from app.models import Booking, Technician, TechnicianLocationUpdate, Vendor

ACTIVE_JOB_STATUSES = frozenset(ACTIVE_LOGISTICS_STATUSES)
TRAIL_LIMIT = 20


def require_approved_vendor(vendor: Vendor) -> None:
    if vendor.status != "approved":
        raise ValueError("الموقع متاح للفنيين المُوافَق عليهم فقط")
    if not vendor.technician_id:
        raise ValueError("الفني غير مرتبط بحساب تقني")


def _location_point(lat: float | None, lng: float | None) -> dict | None:
    if lat is None or lng is None:
        return None
    return {"lat": float(lat), "lng": float(lng)}


def get_technician_for_vendor(db: Session, vendor: Vendor) -> Technician:
    require_approved_vendor(vendor)
    technician = db.get(Technician, vendor.technician_id)
    if not technician:
        raise ValueError("سجل الفني غير موجود")
    return technician


def get_active_job_for_vendor(db: Session, vendor: Vendor) -> Booking | None:
    require_approved_vendor(vendor)
    return db.scalar(
        select(Booking)
        .options(
            joinedload(Booking.address),
            joinedload(Booking.service),
            joinedload(Booking.technician),
            joinedload(Booking.status_events),
        )
        .where(
            Booking.technician_id == vendor.technician_id,
            Booking.status.in_(ACTIVE_JOB_STATUSES),
        )
        .order_by(Booking.updated_at.desc())
        .limit(1)
    )


def get_location_trail(
    db: Session,
    technician_id: uuid.UUID,
    *,
    booking_id: uuid.UUID | None = None,
    limit: int = TRAIL_LIMIT,
) -> list[dict]:
    query = (
        select(TechnicianLocationUpdate)
        .where(TechnicianLocationUpdate.technician_id == technician_id)
        .order_by(TechnicianLocationUpdate.recorded_at.desc())
        .limit(limit)
    )
    if booking_id:
        query = query.where(TechnicianLocationUpdate.booking_id == booking_id)

    updates = db.scalars(query).all()
    return [
        {
            "lat": float(item.lat),
            "lng": float(item.lng),
            "recorded_at": item.recorded_at,
            "booking_id": item.booking_id,
        }
        for item in reversed(updates)
    ]


def active_job_out(db: Session, booking: Booking | None) -> dict | None:
    if not booking:
        return None

    metrics = compute_logistics_metrics(booking)
    destination = metrics.get("destination")

    return {
        "booking_id": booking.id,
        "reference": booking.reference,
        "status": booking.status,
        "service_name_ar": booking.service.name_ar if booking.service else None,
        "destination": destination,
        "distance_km": metrics.get("distance_km"),
        "eta_minutes": metrics.get("eta_minutes"),
    }


def build_vendor_map(db: Session, vendor: Vendor) -> dict:
    technician = get_technician_for_vendor(db, vendor)
    active_job = get_active_job_for_vendor(db, vendor)

    last_update = db.scalar(
        select(TechnicianLocationUpdate)
        .where(TechnicianLocationUpdate.technician_id == technician.id)
        .order_by(TechnicianLocationUpdate.recorded_at.desc())
        .limit(1)
    )

    live_location = _location_point(technician.current_lat, technician.current_lng)
    if live_location and last_update:
        live_location["recorded_at"] = last_update.recorded_at

    base_location = _location_point(vendor.base_lat, vendor.base_lng)
    if base_location:
        base_location["service_radius_km"] = float(vendor.service_radius_km)

    trail_booking_id = active_job.id if active_job else None
    trail = get_location_trail(
        db, technician.id, booking_id=trail_booking_id, limit=TRAIL_LIMIT
    )
    if not trail and technician.current_lat is not None:
        trail = [
            {
                "lat": float(technician.current_lat),
                "lng": float(technician.current_lng),
                "recorded_at": last_update.recorded_at if last_update else None,
                "booking_id": None,
            }
        ]

    return {
        "vendor_id": vendor.id,
        "business_name": vendor.business_name,
        "contact_name": vendor.contact_name,
        "city": vendor.city,
        "technician_id": vendor.technician_id,
        "is_available": technician.is_available,
        "base_location": base_location,
        "live_location": live_location,
        "active_job": active_job_out(db, active_job),
        "trail": trail,
    }


def update_vendor_base_location(
    db: Session,
    vendor: Vendor,
    *,
    lat: float,
    lng: float,
    service_radius_km: float | None = None,
) -> Vendor:
    require_approved_vendor(vendor)
    now = datetime.now(timezone.utc)

    vendor.base_lat = lat
    vendor.base_lng = lng
    if service_radius_km is not None:
        if service_radius_km <= 0 or service_radius_km > 100:
            raise ValueError("نطاق التغطية يجب أن يكون بين 1 و 100 كم")
        vendor.service_radius_km = service_radius_km
    vendor.updated_at = now
    return vendor


def update_vendor_live_location(
    db: Session,
    vendor: Vendor,
    *,
    lat: float,
    lng: float,
    booking_id: uuid.UUID | None = None,
) -> Technician:
    if booking_id is not None:
        booking = db.get(Booking, booking_id)
        if not booking or booking.technician_id != vendor.technician_id:
            raise ValueError("الحجز غير مرتبط بهذا الفني")
    technician = get_technician_for_vendor(db, vendor)
    update_technician_location(
        db,
        technician,
        lat,
        lng,
        booking_id=booking_id,
    )
    return technician


def set_vendor_availability(
    db: Session, vendor: Vendor, *, is_available: bool
) -> Technician:
    technician = get_technician_for_vendor(db, vendor)
    technician.is_available = is_available
    db.commit()
    db.refresh(technician)
    return technician


def list_approved_vendors_map(db: Session) -> list[dict]:
    vendors = db.scalars(
        select(Vendor)
        .where(Vendor.status == "approved", Vendor.technician_id.isnot(None))
        .order_by(Vendor.business_name)
    ).all()

    return [build_vendor_map(db, vendor) for vendor in vendors]
