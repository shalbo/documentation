from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_admin_key
from app.logistics_services import (
    advance_booking_status,
    load_booking_for_logistics,
    simulate_technician_move,
    transition_booking_status,
    update_technician_location,
)
from app.models import Technician
from app.schemas import BookingStatusUpdateIn, TechnicianLocationUpdateIn
from app.services import build_tracking

router = APIRouter(prefix="/logistics", tags=["logistics"])


@router.post("/bookings/{booking_id}/advance")
def advance_booking(
    booking_id: UUID,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    booking = load_booking_for_logistics(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "الحجز غير موجود"},
        )
    try:
        advance_booking_status(db, booking)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_TRANSITION", "message": str(exc)},
        ) from exc
    booking = load_booking_for_logistics(db, booking_id)
    return {"data": build_tracking(booking)}


@router.post("/bookings/{booking_id}/status")
def set_booking_status(
    booking_id: UUID,
    body: BookingStatusUpdateIn,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    booking = load_booking_for_logistics(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "الحجز غير موجود"},
        )
    try:
        transition_booking_status(db, booking, body.status, metadata=body.metadata)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_TRANSITION", "message": str(exc)},
        ) from exc
    booking = load_booking_for_logistics(db, booking_id)
    return {"data": build_tracking(booking)}


@router.patch("/technicians/{technician_id}/location")
def patch_technician_location(
    technician_id: UUID,
    body: TechnicianLocationUpdateIn,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    technician = db.get(Technician, technician_id)
    if not technician:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "الفني غير موجود"},
        )
    update_technician_location(
        db,
        technician,
        body.lat,
        body.lng,
        booking_id=body.booking_id,
    )
    return {
        "data": {
            "id": str(technician.id),
            "lat": float(technician.current_lat),
            "lng": float(technician.current_lng),
        }
    }


@router.post("/bookings/{booking_id}/simulate-move")
def simulate_move(
    booking_id: UUID,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    booking = load_booking_for_logistics(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "الحجز غير موجود"},
        )
    try:
        simulate_technician_move(db, booking)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "SIMULATION_FAILED", "message": str(exc)},
        ) from exc
    booking = load_booking_for_logistics(db, booking_id)
    return {"data": build_tracking(booking)}
