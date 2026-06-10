from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.deps import get_current_user, require_admin_key
from app.models import TowingDispatch, User
from app.schemas import TowingDispatchAssignIn, TowingDispatchCreateIn, TowingLocationUpdateIn
from app.towing_dispatch_services import (
    advance_dispatch_status,
    assign_tow_driver,
    build_towing_dispatch_map,
    create_towing_dispatch,
    load_dispatch,
    update_tow_location,
)

router = APIRouter(tags=["towing-dispatch"])

ACTIVE_CUSTOMER_STATUSES = (
    "pending",
    "dispatched",
    "en_route_pickup",
    "at_pickup",
    "en_route_dropoff",
)


def _dispatch_summary(dispatch: TowingDispatch) -> dict:
    return {
        "id": dispatch.id,
        "reference": dispatch.reference,
        "booking_id": dispatch.booking_id,
        "status": dispatch.status,
        "pickup_label": dispatch.pickup_label,
        "dropoff_label": dispatch.dropoff_label,
        "technician_id": dispatch.technician_id,
        "total_route_km": float(dispatch.total_route_km) if dispatch.total_route_km else None,
        "created_at": dispatch.created_at,
    }


@router.post("/towing/dispatches", status_code=201)
def post_towing_dispatch(
    body: TowingDispatchCreateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        dispatch = create_towing_dispatch(
            db,
            user_id=user.id,
            booking_id=body.booking_id,
            pickup_label=body.pickup_label,
            pickup_lat=body.pickup_lat,
            pickup_lng=body.pickup_lng,
            dropoff_label=body.dropoff_label,
            dropoff_lat=body.dropoff_lat,
            dropoff_lng=body.dropoff_lng,
            notes=body.notes,
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "DISPATCH_ERROR", "message": str(exc)},
        ) from exc

    try:
        from app.notifications import notify_nearby_drivers_towing

        notify_nearby_drivers_towing(
            db,
            dispatch=dispatch,
            pickup_lat=body.pickup_lat,
            pickup_lng=body.pickup_lng,
        )
    except Exception:
        pass

    return {"data": build_towing_dispatch_map(db, dispatch)}


@router.get("/towing/dispatches/active/map")
def get_active_towing_map(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dispatch = db.scalar(
        select(TowingDispatch)
        .options(
            joinedload(TowingDispatch.technician),
            joinedload(TowingDispatch.events),
            joinedload(TowingDispatch.booking),
        )
        .where(
            TowingDispatch.user_id == user.id,
            TowingDispatch.status.in_(ACTIVE_CUSTOMER_STATUSES),
        )
        .order_by(TowingDispatch.created_at.desc())
        .limit(1)
    )
    if not dispatch:
        return {"data": None}
    return {"data": build_towing_dispatch_map(db, dispatch)}


@router.get("/towing/dispatches/{dispatch_id}/map")
def get_towing_dispatch_map(
    dispatch_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dispatch = load_dispatch(db, dispatch_id, user_id=user.id)
    if not dispatch:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "طلب السحب غير موجود"},
        )
    return {"data": build_towing_dispatch_map(db, dispatch)}


@router.get("/admin/towing/dispatches")
def admin_list_dispatches(
    status: str | None = Query(default=None),
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    query = select(TowingDispatch).order_by(TowingDispatch.created_at.desc())
    if status:
        query = query.where(TowingDispatch.status == status)

    dispatches = db.scalars(query).all()
    data = [_dispatch_summary(d) for d in dispatches]
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/admin/towing/dispatches/map")
def admin_towing_dispatches_map(
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    dispatches = db.scalars(
        select(TowingDispatch)
        .options(
            joinedload(TowingDispatch.technician),
            joinedload(TowingDispatch.events),
            joinedload(TowingDispatch.booking),
        )
        .where(TowingDispatch.status != "cancelled")
        .order_by(TowingDispatch.created_at.desc())
    ).unique().all()

    data = [build_towing_dispatch_map(db, d) for d in dispatches]
    active = sum(1 for item in data if item.get("is_live"))
    return {"data": data, "meta": {"total": len(data), "live_count": active}}


@router.post("/admin/towing/dispatches/{dispatch_id}/dispatch")
def admin_assign_dispatch(
    dispatch_id: UUID,
    body: TowingDispatchAssignIn,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    dispatch = load_dispatch(db, dispatch_id)
    if not dispatch:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "طلب السحب غير موجود"},
        )
    try:
        assign_tow_driver(db, dispatch, body.technician_id)
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "ASSIGN_ERROR", "message": str(exc)},
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

    dispatch = load_dispatch(db, dispatch_id)
    return {"data": build_towing_dispatch_map(db, dispatch)}


@router.post("/admin/towing/dispatches/{dispatch_id}/advance")
def admin_advance_dispatch(
    dispatch_id: UUID,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    dispatch = load_dispatch(db, dispatch_id)
    if not dispatch:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "طلب السحب غير موجود"},
        )
    try:
        advance_dispatch_status(db, dispatch)
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "ADVANCE_ERROR", "message": str(exc)},
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

    dispatch = load_dispatch(db, dispatch_id)
    return {"data": build_towing_dispatch_map(db, dispatch)}


@router.patch("/admin/towing/dispatches/{dispatch_id}/location")
def admin_update_tow_location(
    dispatch_id: UUID,
    body: TowingLocationUpdateIn,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    dispatch = load_dispatch(db, dispatch_id)
    if not dispatch:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "طلب السحب غير موجود"},
        )
    try:
        update_tow_location(db, dispatch, body.lat, body.lng)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "LOCATION_ERROR", "message": str(exc)},
        ) from exc

    dispatch = load_dispatch(db, dispatch_id)
    return {"data": build_towing_dispatch_map(db, dispatch)}
