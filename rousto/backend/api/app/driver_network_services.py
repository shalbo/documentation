"""Logistics & Driver Network — driver pool, fares, cancellation, ratings."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.logistics_services import haversine_km
from app.models import Technician, TowingDispatch, Vendor
from app.towing_dispatch_services import (
    DISPATCH_ORDER,
    STATUS_LABELS,
    assign_tow_driver,
    build_towing_dispatch_map,
    compute_total_route_km,
    load_dispatch,
)

DRIVER_TYPES = frozenset({"service", "tow", "courier"})
DEFAULT_BASE_FARE_SAR = 75.0
DEFAULT_PER_KM_RATE_SAR = 8.0
JOB_POOL_RADIUS_KM = 25.0
CANCELLABLE_STATUSES = frozenset({"pending", "dispatched"})
DRIVER_ACTIVE_STATUSES = frozenset(
    {"dispatched", "en_route_pickup", "at_pickup", "en_route_dropoff"}
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def compute_towing_fare(
    total_route_km: float | None,
    *,
    base_fare: float = DEFAULT_BASE_FARE_SAR,
    per_km: float = DEFAULT_PER_KM_RATE_SAR,
) -> dict:
    km = float(total_route_km or 0)
    total = round(base_fare + km * per_km, 2)
    return {
        "base_fare_sar": base_fare,
        "per_km_rate_sar": per_km,
        "total_fare_sar": total,
    }


def apply_dispatch_fare(dispatch: TowingDispatch) -> None:
    fare = compute_towing_fare(
        float(dispatch.total_route_km) if dispatch.total_route_km else 0
    )
    dispatch.base_fare_sar = fare["base_fare_sar"]
    dispatch.per_km_rate_sar = fare["per_km_rate_sar"]
    dispatch.total_fare_sar = fare["total_fare_sar"]


def technician_for_vendor(db: Session, vendor: Vendor) -> Technician | None:
    if not vendor.technician_id:
        return None
    return db.get(Technician, vendor.technician_id)


def driver_out(tech: Technician, *, completed_jobs: int = 0, active_jobs: int = 0) -> dict:
    return {
        "id": tech.id,
        "full_name": tech.full_name,
        "phone": tech.phone,
        "driver_type": tech.driver_type,
        "rating": float(tech.rating),
        "is_available": tech.is_available,
        "location": (
            {"lat": float(tech.current_lat), "lng": float(tech.current_lng)}
            if tech.current_lat is not None
            else None
        ),
        "completed_jobs": completed_jobs,
        "active_jobs": active_jobs,
    }


def dispatch_job_summary(dispatch: TowingDispatch, *, distance_km: float | None = None) -> dict:
    return {
        "id": dispatch.id,
        "reference": dispatch.reference,
        "status": dispatch.status,
        "pickup_label": dispatch.pickup_label,
        "pickup_lat": float(dispatch.pickup_lat),
        "pickup_lng": float(dispatch.pickup_lng),
        "dropoff_label": dispatch.dropoff_label,
        "dropoff_lat": float(dispatch.dropoff_lat),
        "dropoff_lng": float(dispatch.dropoff_lng),
        "total_route_km": float(dispatch.total_route_km) if dispatch.total_route_km else None,
        "total_fare_sar": float(dispatch.total_fare_sar) if dispatch.total_fare_sar else None,
        "distance_km": distance_km,
        "created_at": dispatch.created_at,
    }


def list_available_tow_jobs(
    db: Session,
    technician: Technician,
    *,
    radius_km: float = JOB_POOL_RADIUS_KM,
) -> list[dict]:
    if technician.driver_type != "tow":
        raise ValueError("السائق ليس من نوع سطحة")
    if technician.current_lat is None or technician.current_lng is None:
        return []

    dispatches = db.scalars(
        select(TowingDispatch)
        .where(TowingDispatch.status == "pending")
        .order_by(TowingDispatch.created_at.desc())
    ).all()

    jobs = []
    for dispatch in dispatches:
        dist = haversine_km(
            float(technician.current_lat),
            float(technician.current_lng),
            float(dispatch.pickup_lat),
            float(dispatch.pickup_lng),
        )
        if dist <= radius_km:
            jobs.append(dispatch_job_summary(dispatch, distance_km=round(dist, 2)))
    return jobs


def accept_tow_job(
    db: Session,
    technician: Technician,
    dispatch_id: uuid.UUID,
) -> TowingDispatch:
    if not technician.is_available:
        raise ValueError("السائق غير متاح حالياً")

    active = db.scalar(
        select(TowingDispatch).where(
            TowingDispatch.technician_id == technician.id,
            TowingDispatch.status.in_(DRIVER_ACTIVE_STATUSES),
        )
    )
    if active:
        raise ValueError("لديك مهمة نشطة بالفعل")

    dispatch = load_dispatch(db, dispatch_id)
    if not dispatch:
        raise ValueError("طلب السحب غير موجود")
    if dispatch.status != "pending":
        raise ValueError("الطلب لم يعد متاحاً للقبول")

    assign_tow_driver(db, dispatch, technician.id)
    dispatch.total_route_km = compute_total_route_km(dispatch)
    apply_dispatch_fare(dispatch)
    return dispatch


def get_driver_active_job(db: Session, technician_id: uuid.UUID) -> dict | None:
    dispatch = db.scalar(
        select(TowingDispatch)
        .options(
            joinedload(TowingDispatch.technician),
            joinedload(TowingDispatch.events),
            joinedload(TowingDispatch.booking),
        )
        .where(
            TowingDispatch.technician_id == technician_id,
            TowingDispatch.status.in_(DRIVER_ACTIVE_STATUSES),
        )
        .order_by(TowingDispatch.updated_at.desc())
        .limit(1)
    )
    if not dispatch:
        return None
    return build_towing_dispatch_map(db, dispatch)


def list_customer_dispatches(
    db: Session,
    user_id: uuid.UUID,
    *,
    status: str | None = None,
    limit: int = 50,
) -> list[dict]:
    query = (
        select(TowingDispatch)
        .where(TowingDispatch.user_id == user_id)
        .order_by(TowingDispatch.created_at.desc())
        .limit(limit)
    )
    if status:
        query = query.where(TowingDispatch.status == status)

    rows = db.scalars(query).all()
    return [
        {
            **dispatch_job_summary(d),
            "technician_name": d.technician.full_name if d.technician else None,
            "customer_rating": d.customer_rating,
        }
        for d in rows
    ]


def cancel_towing_dispatch(
    db: Session,
    dispatch: TowingDispatch,
    *,
    reason: str | None = None,
) -> TowingDispatch:
    if dispatch.status not in CANCELLABLE_STATUSES:
        raise ValueError("لا يمكن إلغاء الطلب في هذه المرحلة")

    now = _now()
    dispatch.status = "cancelled"
    dispatch.cancelled_at = now
    dispatch.cancel_reason = (reason or "إلغاء")[:200]
    dispatch.updated_at = now

    from app.models import TowingDispatchEvent

    db.add(
        TowingDispatchEvent(
            id=uuid.uuid4(),
            dispatch_id=dispatch.id,
            status="cancelled",
            label_ar=STATUS_LABELS["cancelled"],
            occurred_at=now,
            metadata_={"reason": dispatch.cancel_reason},
        )
    )
    return dispatch


def rate_dispatch_driver(
    db: Session,
    dispatch: TowingDispatch,
    rating: int,
) -> TowingDispatch:
    if dispatch.status != "completed":
        raise ValueError("يمكن التقييم بعد اكتمال الطلب فقط")
    if dispatch.customer_rating is not None:
        raise ValueError("تم التقييم مسبقاً")
    if not dispatch.technician:
        raise ValueError("لا يوجد سائق للتقييم")

    dispatch.customer_rating = rating
    tech = dispatch.technician
    current = float(tech.rating)
    tech.rating = round((current + rating) / 2, 1)
    dispatch.updated_at = _now()
    return dispatch


def list_drivers_admin(
    db: Session,
    *,
    driver_type: str | None = None,
) -> list[dict]:
    query = select(Technician).order_by(Technician.full_name)
    if driver_type:
        query = query.where(Technician.driver_type == driver_type)

    technicians = db.scalars(query).all()
    result = []
    for tech in technicians:
        completed = (
            db.scalar(
                select(func.count())
                .select_from(TowingDispatch)
                .where(
                    TowingDispatch.technician_id == tech.id,
                    TowingDispatch.status == "completed",
                )
            )
            or 0
        )
        active = (
            db.scalar(
                select(func.count())
                .select_from(TowingDispatch)
                .where(
                    TowingDispatch.technician_id == tech.id,
                    TowingDispatch.status.in_(DRIVER_ACTIVE_STATUSES),
                )
            )
            or 0
        )
        result.append(driver_out(tech, completed_jobs=completed, active_jobs=active))
    return result


def get_driver_network_analytics(db: Session) -> dict:
    total = db.scalar(select(func.count()).select_from(Technician)) or 0
    available = (
        db.scalar(
            select(func.count())
            .select_from(Technician)
            .where(Technician.is_available.is_(True))
        )
        or 0
    )
    by_type = db.execute(
        select(Technician.driver_type, func.count())
        .group_by(Technician.driver_type)
        .order_by(func.count().desc())
    ).all()
    pending_jobs = (
        db.scalar(
            select(func.count())
            .select_from(TowingDispatch)
            .where(TowingDispatch.status == "pending")
        )
        or 0
    )
    active_dispatches = (
        db.scalar(
            select(func.count())
            .select_from(TowingDispatch)
            .where(TowingDispatch.status.in_(DRIVER_ACTIVE_STATUSES))
        )
        or 0
    )
    return {
        "drivers_total": total,
        "drivers_available": available,
        "pending_tow_jobs": pending_jobs,
        "active_dispatches": active_dispatches,
        "by_driver_type": [{"type": t, "count": n} for t, n in by_type],
    }
