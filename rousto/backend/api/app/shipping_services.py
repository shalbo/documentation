"""Hybrid shipping — local GPS courier vs intercity flat-rate carriers."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.logistics_services import haversine_km
from app.models import (
    IntercityShippingRate,
    Part,
    PartInventory,
    PartOrder,
    PartOrderSettlement,
    Technician,
    Vendor,
)
from app.technician_domain import SERVICE_DRIVER_TYPE

LOCAL_BASE_FEE_SAR = 25.0
LOCAL_PER_KM_SAR = 2.5
PLATFORM_PARTS_RATE = Decimal("0.12")
VENDOR_PARTS_RATE = Decimal("0.88")
COURIER_SHARE_OF_SHIPPING = Decimal("0.70")
CARRIER_SHARE_OF_SHIPPING = Decimal("0.85")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _gen_reference() -> str:
    return f"PO{uuid.uuid4().hex[:8].upper()}"


def classify_shipping(origin_city: str, destination_city: str) -> str:
    if origin_city.strip().lower() == destination_city.strip().lower():
        return "local_delivery"
    return "intercity_shipping"


def quote_shipping(
    db: Session,
    *,
    origin_city: str,
    destination_city: str,
    dest_lat: float | None = None,
    dest_lng: float | None = None,
    vendor_lat: float | None = None,
    vendor_lng: float | None = None,
) -> dict:
    shipping_type = classify_shipping(origin_city, destination_city)

    if shipping_type == "intercity_shipping":
        rate = db.scalar(
            select(IntercityShippingRate).where(
                IntercityShippingRate.origin_city == origin_city,
                IntercityShippingRate.destination_city == destination_city,
                IntercityShippingRate.is_active.is_(True),
            )
        )
        if not rate:
            raise ValueError(f"لا يوجد شحن بين المدن: {origin_city} → {destination_city}")
        return {
            "shipping_type": shipping_type,
            "shipping_fee_sar": float(rate.flat_fee_sar),
            "carrier_name": rate.carrier_name,
            "carrier_slug": rate.carrier_slug,
            "eta_days": rate.eta_days,
            "eta_label_ar": f"{rate.eta_days} أيام عمل",
        }

    distance_km = 5.0
    if all(v is not None for v in (dest_lat, dest_lng, vendor_lat, vendor_lng)):
        distance_km = haversine_km(
            float(vendor_lat), float(vendor_lng), dest_lat, dest_lng
        )
    fee = LOCAL_BASE_FEE_SAR + round(distance_km * LOCAL_PER_KM_SAR, 2)
    return {
        "shipping_type": shipping_type,
        "shipping_fee_sar": round(fee, 2),
        "distance_km": round(distance_km, 2),
        "eta_label_ar": "توصيل فوري اليوم",
    }


def find_nearest_courier(
    db: Session,
    *,
    dest_lat: float,
    dest_lng: float,
) -> Technician | None:
    technicians = db.scalars(
        select(Technician).where(
            Technician.is_available.is_(True),
            Technician.driver_type == SERVICE_DRIVER_TYPE,
            Technician.current_lat.isnot(None),
            Technician.current_lng.isnot(None),
        )
    ).all()
    if not technicians:
        return None
    return min(
        technicians,
        key=lambda t: haversine_km(
            float(t.current_lat), float(t.current_lng), dest_lat, dest_lng
        ),
    )


def calculate_settlements(
    *,
    subtotal_sar: float,
    shipping_fee_sar: float,
    shipping_type: str,
    vendor_id: uuid.UUID,
    courier_id: uuid.UUID | None = None,
) -> list[dict]:
    subtotal = Decimal(str(subtotal_sar))
    shipping = Decimal(str(shipping_fee_sar))
    legs: list[dict] = []

    platform_part = (subtotal * PLATFORM_PARTS_RATE).quantize(Decimal("0.01"))
    vendor_part = (subtotal * VENDOR_PARTS_RATE).quantize(Decimal("0.01"))
    legs.append(
        {
            "recipient_type": "platform",
            "recipient_id": None,
            "amount_sar": float(platform_part),
            "label_ar": "عمولة المنصة (قطع)",
        }
    )
    legs.append(
        {
            "recipient_type": "vendor",
            "recipient_id": vendor_id,
            "amount_sar": float(vendor_part),
            "label_ar": "حصة المحل",
        }
    )

    if shipping > 0:
        if shipping_type == "local_delivery" and courier_id:
            courier_amt = (shipping * COURIER_SHARE_OF_SHIPPING).quantize(
                Decimal("0.01")
            )
            platform_ship = shipping - courier_amt
            legs.append(
                {
                    "recipient_type": "courier",
                    "recipient_id": courier_id,
                    "amount_sar": float(courier_amt),
                    "label_ar": "أجر المندوب",
                }
            )
            legs.append(
                {
                    "recipient_type": "platform",
                    "recipient_id": None,
                    "amount_sar": float(platform_ship),
                    "label_ar": "عمولة توصيل محلي",
                }
            )
        elif shipping_type == "intercity_shipping":
            carrier_amt = (shipping * CARRIER_SHARE_OF_SHIPPING).quantize(
                Decimal("0.01")
            )
            platform_ship = shipping - carrier_amt
            legs.append(
                {
                    "recipient_type": "carrier",
                    "recipient_id": None,
                    "amount_sar": float(carrier_amt),
                    "label_ar": "أجر شركة الشحن",
                }
            )
            legs.append(
                {
                    "recipient_type": "platform",
                    "recipient_id": None,
                    "amount_sar": float(platform_ship),
                    "label_ar": "عمولة شحن بين المدن",
                }
            )

    return legs


def create_part_order(
    db: Session,
    *,
    user_id: uuid.UUID,
    part_id: uuid.UUID,
    vendor_id: uuid.UUID,
    qty: int,
    origin_city: str,
    destination_city: str,
    dest_lat: float | None = None,
    dest_lng: float | None = None,
) -> PartOrder:
    part = db.get(Part, part_id)
    if not part or not part.is_active:
        raise ValueError("القطعة غير متوفرة")

    inv = db.scalar(
        select(PartInventory).where(
            PartInventory.part_id == part_id,
            PartInventory.vendor_id == vendor_id,
            PartInventory.qty_available >= qty,
        )
    )
    if not inv:
        raise ValueError("المحل لا يملك الكمية المطلوبة في المخزون")

    vendor = db.get(Vendor, vendor_id)
    if not vendor or vendor.status != "approved":
        raise ValueError("المحل غير معتمد")

    quote = quote_shipping(
        db,
        origin_city=origin_city or vendor.city,
        destination_city=destination_city,
        dest_lat=dest_lat,
        dest_lng=dest_lng,
        vendor_lat=float(vendor.base_lat) if vendor.base_lat else None,
        vendor_lng=float(vendor.base_lng) if vendor.base_lng else None,
    )

    subtotal = float(part.price_sar) * qty
    shipping_fee = quote["shipping_fee_sar"]
    total = round(subtotal + shipping_fee, 2)
    now = _now()

    courier_id = None
    carrier_name = None
    if quote["shipping_type"] == "local_delivery" and dest_lat and dest_lng:
        courier = find_nearest_courier(db, dest_lat=dest_lat, dest_lng=dest_lng)
        if courier:
            courier_id = courier.id
    elif quote["shipping_type"] == "intercity_shipping":
        carrier_name = quote.get("carrier_name")

    order = PartOrder(
        id=uuid.uuid4(),
        reference=_gen_reference(),
        user_id=user_id,
        part_id=part_id,
        vendor_id=vendor_id,
        qty=qty,
        subtotal_sar=subtotal,
        shipping_type=quote["shipping_type"],
        shipping_fee_sar=shipping_fee,
        total_sar=total,
        origin_city=origin_city or vendor.city,
        destination_city=destination_city,
        dest_lat=dest_lat,
        dest_lng=dest_lng,
        courier_technician_id=courier_id,
        intercity_carrier=carrier_name,
        status="confirmed",
        created_at=now,
        updated_at=now,
    )
    db.add(order)

    inv.qty_available -= qty
    inv.updated_at = now

    for leg in calculate_settlements(
        subtotal_sar=subtotal,
        shipping_fee_sar=shipping_fee,
        shipping_type=quote["shipping_type"],
        vendor_id=vendor_id,
        courier_id=courier_id,
    ):
        db.add(
            PartOrderSettlement(
                id=uuid.uuid4(),
                part_order_id=order.id,
                recipient_type=leg["recipient_type"],
                recipient_id=leg.get("recipient_id"),
                amount_sar=leg["amount_sar"],
                label_ar=leg["label_ar"],
                status="held",
                created_at=now,
            )
        )

    db.flush()
    return order


def list_intercity_rates_admin(db: Session) -> list[dict]:
    rows = db.scalars(
        select(IntercityShippingRate).order_by(
            IntercityShippingRate.origin_city, IntercityShippingRate.destination_city
        )
    ).all()
    return [
        {
            "id": r.id,
            "origin_city": r.origin_city,
            "destination_city": r.destination_city,
            "flat_fee_sar": float(r.flat_fee_sar),
            "carrier_name": r.carrier_name,
            "carrier_slug": r.carrier_slug,
            "eta_days": r.eta_days,
            "is_active": r.is_active,
        }
        for r in rows
    ]


def order_out(order: PartOrder) -> dict:
    return {
        "id": order.id,
        "reference": order.reference,
        "part_id": order.part_id,
        "vendor_id": order.vendor_id,
        "qty": order.qty,
        "subtotal_sar": float(order.subtotal_sar),
        "shipping_type": order.shipping_type,
        "shipping_fee_sar": float(order.shipping_fee_sar),
        "total_sar": float(order.total_sar),
        "origin_city": order.origin_city,
        "destination_city": order.destination_city,
        "courier_technician_id": order.courier_technician_id,
        "intercity_carrier": order.intercity_carrier,
        "status": order.status,
        "created_at": order.created_at,
    }
