from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.deps import get_current_user
from app.models import Booking, User
from app.schemas import BookingCreateIn
from app.customer_delivery_services import build_customer_delivery_map
from app.services import (
    ACTIVE_STATUSES,
    build_tracking,
    create_booking,
    load_booking,
    serialize_booking,
)
from app.rate_limit import check_rate_limit
from app.split_payments import get_booking_split

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("")
def list_bookings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bookings = db.scalars(
        select(Booking)
        .options(
            joinedload(Booking.service),
            joinedload(Booking.vehicle),
            joinedload(Booking.address),
        )
        .where(Booking.user_id == user.id)
        .order_by(Booking.created_at.desc())
    ).unique().all()
    data = [serialize_booking(b) for b in bookings]
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/active")
def get_active_booking(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    booking = db.scalar(
        select(Booking)
        .where(Booking.user_id == user.id, Booking.status.in_(ACTIVE_STATUSES))
        .order_by(Booking.created_at.desc())
        .limit(1)
    )
    if not booking:
        return {"data": None}
    full = load_booking(db, booking.id, user.id)
    return {"data": serialize_booking(full) if full else None}


@router.get("/active/delivery-map")
def get_active_delivery_map(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    booking = db.scalar(
        select(Booking)
        .where(Booking.user_id == user.id, Booking.status.in_(ACTIVE_STATUSES))
        .order_by(Booking.created_at.desc())
        .limit(1)
    )
    if not booking:
        return {"data": None}
    full = load_booking(db, booking.id, user.id)
    if not full:
        return {"data": None}
    return {"data": build_customer_delivery_map(db, full)}


@router.get("/{booking_id}")
def get_booking(
    booking_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = load_booking(db, booking_id, user.id)
    if not booking:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "الحجز غير موجود"},
        )
    return {"data": serialize_booking(booking)}


@router.get("/{booking_id}/payment-split")
def get_booking_payment_split(
    booking_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = load_booking(db, booking_id, user.id)
    if not booking:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "الحجز غير موجود"},
        )
    data = get_booking_split(db, booking_id)
    if not data:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "لا يوجد تقسيم لهذا الحجز"},
        )
    return {"data": data}


@router.get("/{booking_id}/tracking")
def get_booking_tracking(
    booking_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = load_booking(db, booking_id, user.id)
    if not booking:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "الحجز غير موجود"},
        )
    return {"data": build_tracking(booking)}


@router.get("/{booking_id}/delivery-map")
def get_booking_delivery_map(
    booking_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = load_booking(db, booking_id, user.id)
    if not booking:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "الحجز غير موجود"},
        )
    return {"data": build_customer_delivery_map(db, booking)}


@router.post("", status_code=201)
def post_booking(
    body: BookingCreateIn,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_rate_limit(request, suffix="booking_create", limit=20)
    try:
        booking = create_booking(
            db,
            user,
            service_id=body.service_id,
            vehicle_id=body.vehicle_id,
            address_id=body.address_id,
            payment_method_id=body.payment_method_id,
            promotion_code=body.promotion_code,
            reward_slug=body.reward_slug,
            scheduled_at=body.scheduled_at,
            notes=body.notes,
            scan_id=body.scan_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_BOOKING", "message": str(exc)},
        ) from exc
    return {"data": serialize_booking(booking)}
