from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user, get_current_vendor, require_admin_key
from app.driver_network_services import (
    DRIVER_TYPES,
    accept_tow_job,
    cancel_towing_dispatch,
    get_driver_active_job,
    get_driver_network_analytics,
    list_available_tow_jobs,
    list_customer_dispatches,
    list_drivers_admin,
    rate_dispatch_driver,
    technician_for_vendor,
)
from app.models import User, Vendor
from app.towing_dispatch_services import build_towing_dispatch_map, load_dispatch

router = APIRouter(tags=["driver-network"])


class TowingCancelIn(BaseModel):
    reason: str | None = Field(default=None, max_length=200)


class TowingRateIn(BaseModel):
    rating: int = Field(ge=1, le=5)


class DriverAvailabilityIn(BaseModel):
    is_available: bool


@router.get("/driver/me/jobs/available")
def driver_available_jobs(
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db),
):
    tech = technician_for_vendor(db, vendor)
    if not tech:
        raise HTTPException(
            status_code=400,
            detail={"code": "NO_TECHNICIAN", "message": "لا يوجد فني مرتبط بالحساب"},
        )
    try:
        jobs = list_available_tow_jobs(db, tech)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "JOB_POOL_ERROR", "message": str(exc)},
        ) from exc
    return {"data": jobs, "meta": {"total": len(jobs)}}


@router.post("/driver/me/jobs/{dispatch_id}/accept", status_code=201)
def driver_accept_job(
    dispatch_id: UUID,
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db),
):
    tech = technician_for_vendor(db, vendor)
    if not tech:
        raise HTTPException(
            status_code=400,
            detail={"code": "NO_TECHNICIAN", "message": "لا يوجد فني مرتبط بالحساب"},
        )
    try:
        dispatch = accept_tow_job(db, tech, dispatch_id)
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "ACCEPT_ERROR", "message": str(exc)},
        ) from exc

    try:
        from app.notifications import notify_towing_status_change
        from app.towing_dispatch_services import STATUS_LABELS

        notify_towing_status_change(
            db,
            user_id=dispatch.user_id,
            dispatch_ref=dispatch.reference,
            status=dispatch.status,
            label_ar=STATUS_LABELS.get(dispatch.status, dispatch.status),
        )
    except Exception:
        pass

    return {"data": build_towing_dispatch_map(db, dispatch)}


@router.get("/driver/me/jobs/active")
def driver_active_job(
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db),
):
    tech = technician_for_vendor(db, vendor)
    if not tech:
        return {"data": None}
    data = get_driver_active_job(db, tech.id)
    return {"data": data}


@router.get("/towing/dispatches")
def customer_towing_history(
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = list_customer_dispatches(db, user.id, status=status, limit=limit)
    return {"data": data, "meta": {"total": len(data)}}


@router.post("/towing/dispatches/{dispatch_id}/cancel")
def customer_cancel_dispatch(
    dispatch_id: UUID,
    body: TowingCancelIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dispatch = load_dispatch(db, dispatch_id, user_id=user.id)
    if not dispatch:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "طلب السحب غير موجود"},
        )
    try:
        cancel_towing_dispatch(db, dispatch, reason=body.reason)
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "CANCEL_ERROR", "message": str(exc)},
        ) from exc
    return {"data": build_towing_dispatch_map(db, dispatch)}


@router.post("/towing/dispatches/{dispatch_id}/rate")
def customer_rate_dispatch(
    dispatch_id: UUID,
    body: TowingRateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dispatch = load_dispatch(db, dispatch_id, user_id=user.id)
    if not dispatch:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "طلب السحب غير موجود"},
        )
    try:
        rate_dispatch_driver(db, dispatch, body.rating)
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "RATE_ERROR", "message": str(exc)},
        ) from exc
    return {
        "data": {
            "dispatch_id": dispatch.id,
            "rating": dispatch.customer_rating,
            "driver_rating": float(dispatch.technician.rating) if dispatch.technician else None,
        }
    }


@router.get("/admin/drivers")
def admin_list_drivers(
    driver_type: str | None = Query(default=None),
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    if driver_type and driver_type not in DRIVER_TYPES:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_TYPE", "message": "نوع سائق غير مدعوم"},
        )
    data = list_drivers_admin(db, driver_type=driver_type)
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/admin/drivers/analytics")
def admin_driver_analytics(
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    return {"data": get_driver_network_analytics(db)}


@router.patch("/admin/drivers/{technician_id}/availability")
def admin_toggle_driver_availability(
    technician_id: UUID,
    body: DriverAvailabilityIn,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    from app.models import Technician

    tech = db.get(Technician, technician_id)
    if not tech:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "السائق غير موجود"},
        )
    tech.is_available = body.is_available
    db.commit()
    return {"data": {"id": tech.id, "is_available": tech.is_available}}
