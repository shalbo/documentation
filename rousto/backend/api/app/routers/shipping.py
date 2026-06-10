from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.models import User
from app.shipping_services import create_part_order, order_out, quote_shipping

router = APIRouter(prefix="/shipping", tags=["shipping"])


class ShippingQuoteIn(BaseModel):
    origin_city: str = Field(min_length=2, max_length=60)
    destination_city: str = Field(min_length=2, max_length=60)
    dest_lat: float | None = Field(default=None, ge=-90, le=90)
    dest_lng: float | None = Field(default=None, ge=-180, le=180)
    vendor_lat: float | None = None
    vendor_lng: float | None = None


class PartOrderIn(BaseModel):
    part_id: UUID
    vendor_id: UUID
    qty: int = Field(default=1, ge=1, le=20)
    origin_city: str = Field(min_length=2, max_length=60)
    destination_city: str = Field(min_length=2, max_length=60)
    dest_lat: float | None = Field(default=None, ge=-90, le=90)
    dest_lng: float | None = Field(default=None, ge=-180, le=180)


@router.post("/quote")
def post_shipping_quote(
    body: ShippingQuoteIn,
    db: Session = Depends(get_db),
):
    try:
        data = quote_shipping(
            db,
            origin_city=body.origin_city,
            destination_city=body.destination_city,
            dest_lat=body.dest_lat,
            dest_lng=body.dest_lng,
            vendor_lat=body.vendor_lat,
            vendor_lng=body.vendor_lng,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "SHIPPING_ERROR", "message": str(exc)},
        ) from exc
    return {"data": data}


@router.post("/part-orders", status_code=201)
def post_part_order(
    body: PartOrderIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        order = create_part_order(
            db,
            user_id=user.id,
            part_id=body.part_id,
            vendor_id=body.vendor_id,
            qty=body.qty,
            origin_city=body.origin_city,
            destination_city=body.destination_city,
            dest_lat=body.dest_lat,
            dest_lng=body.dest_lng,
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "ORDER_ERROR", "message": str(exc)},
        ) from exc
    return {"data": order_out(order)}


@router.get("/part-orders/{order_id}")
def get_part_order(
    order_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models import PartOrder

    order = db.get(PartOrder, order_id)
    if not order or order.user_id != user.id:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "الطلب غير موجود"},
        )
    return {"data": order_out(order)}
