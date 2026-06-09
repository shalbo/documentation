from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_vendor, require_admin_key
from app.models import Vendor
from app.schemas import (
    VendorAvailabilityIn,
    VendorBaseLocationIn,
    VendorLiveLocationIn,
)
from app.vendor_map_services import (
    active_job_out,
    build_vendor_map,
    get_active_job_for_vendor,
    list_approved_vendors_map,
    set_vendor_availability,
    update_vendor_base_location,
    update_vendor_live_location,
)

router = APIRouter(tags=["vendor-map"])


@router.get("/vendor/me/map")
def get_vendor_map(
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db),
):
    try:
        data = build_vendor_map(db, vendor)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "MAP_ERROR", "message": str(exc)},
        ) from exc
    return {"data": data}


@router.put("/vendor/me/location/base")
def put_vendor_base_location(
    body: VendorBaseLocationIn,
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db),
):
    try:
        update_vendor_base_location(
            db,
            vendor,
            lat=body.lat,
            lng=body.lng,
            service_radius_km=body.service_radius_km,
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "LOCATION_ERROR", "message": str(exc)},
        ) from exc
    return {"data": build_vendor_map(db, vendor)}


@router.patch("/vendor/me/location/live")
def patch_vendor_live_location(
    body: VendorLiveLocationIn,
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db),
):
    try:
        update_vendor_live_location(
            db,
            vendor,
            lat=body.lat,
            lng=body.lng,
            booking_id=body.booking_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "LOCATION_ERROR", "message": str(exc)},
        ) from exc
    return {"data": build_vendor_map(db, vendor)}


@router.get("/vendor/me/jobs/active")
def get_vendor_active_job(
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db),
):
    try:
        booking = get_active_job_for_vendor(db, vendor)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "JOB_ERROR", "message": str(exc)},
        ) from exc

    data = active_job_out(db, booking)
    return {"data": data, "meta": {"has_active_job": data is not None}}


@router.patch("/vendor/me/availability")
def patch_vendor_availability(
    body: VendorAvailabilityIn,
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db),
):
    try:
        set_vendor_availability(db, vendor, is_available=body.is_available)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "AVAILABILITY_ERROR", "message": str(exc)},
        ) from exc
    return {"data": build_vendor_map(db, vendor)}


@router.get("/admin/vendors/map")
def admin_vendors_map(
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    data = list_approved_vendors_map(db)
    available = sum(1 for item in data if item.get("is_available"))
    return {
        "data": data,
        "meta": {"total": len(data), "available_count": available},
    }
