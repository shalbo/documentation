from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Address,
    Booking,
    BookingStatusEvent,
    Payment,
    PaymentMethod,
    Promotion,
    Service,
    ServiceCategory,
    Technician,
    User,
    Vehicle,
    VehicleScan,
)
from app.monetization import (
    calculate_membership_discount,
    get_membership_plan_for_user,
    record_booking_revenue,
    record_promo_redemption,
    redeem_loyalty_reward,
)

ACTIVE_STATUSES = {
    "pending",
    "confirmed",
    "technician_assigned",
    "en_route",
    "in_progress",
}

STATUS_LABELS_AR = {
    "pending": "بانتظار التأكيد",
    "confirmed": "مؤكد",
    "technician_assigned": "تم تعيين الفني",
    "en_route": "جارية",
    "in_progress": "قيد التنفيذ",
    "completed": "مكتمل",
    "cancelled": "ملغى",
}

STATUS_EVENT_LABELS = {
    "confirmed": "تم تأكيد الحجز",
    "technician_assigned": "تم تعيين الفني",
    "en_route": "الفني في الطريق إليك",
    "in_progress": "تنفيذ الخدمة",
    "completed": "اكتمال الخدمة",
}


def status_label_ar(status: str) -> str:
    return STATUS_LABELS_AR.get(status, status)


def to_float(value) -> float:
    if value is None:
        return 0.0
    return float(value)


def vehicle_display_name(vehicle: Vehicle) -> str:
    parts = [vehicle.make, vehicle.model, str(vehicle.year)]
    if vehicle.color:
        parts.append(vehicle.color)
    parts.append(vehicle.plate_number)
    return " · ".join(parts)


def calculate_discount(promotion: Promotion, service_price: float) -> float:
    price = Decimal(str(service_price))
    if promotion.discount_type == "percentage":
        discount = price * Decimal(str(promotion.discount_value)) / Decimal("100")
    else:
        discount = Decimal(str(promotion.discount_value))
    return float(min(discount, price))


def find_active_promotion(db: Session, code: str, service_price: float) -> Promotion | None:
    now = datetime.now(timezone.utc)
    promotion = db.scalar(
        select(Promotion).where(
            func.upper(Promotion.code) == code.upper(),
            Promotion.is_active.is_(True),
            Promotion.starts_at <= now,
            (Promotion.ends_at.is_(None)) | (Promotion.ends_at >= now),
            Promotion.min_order_sar <= service_price,
        )
    )
    return promotion


def next_booking_reference(db: Session) -> str:
    count = db.scalar(select(func.count()).select_from(Booking)) or 0
    return f"RST-2026-{count + 1:03d}"


def assign_available_technician(db: Session) -> Technician | None:
    return db.scalar(
        select(Technician)
        .where(Technician.is_available.is_(True))
        .order_by(Technician.rating.desc())
        .limit(1)
    )


def get_user_stats(db: Session, user_id: UUID) -> dict:
    services_count = db.scalar(
        select(func.count())
        .select_from(Booking)
        .where(Booking.user_id == user_id, Booking.status == "completed")
    ) or 0
    vehicles_count = db.scalar(
        select(func.count()).select_from(Vehicle).where(Vehicle.user_id == user_id)
    ) or 0
    return {"services_count": services_count, "vehicles_count": vehicles_count}


def serialize_booking(booking: Booking) -> dict:
    service_brief = None
    if booking.service:
        service_brief = {
            "name_ar": booking.service.name_ar,
            "icon_key": booking.service.icon_key,
            "duration_minutes": booking.service.duration_minutes,
        }

    vehicle_out = None
    if booking.vehicle:
        vehicle_out = {
            "id": booking.vehicle.id,
            "make": booking.vehicle.make,
            "model": booking.vehicle.model,
            "year": booking.vehicle.year,
            "color": booking.vehicle.color,
            "plate_number": booking.vehicle.plate_number,
            "is_default": booking.vehicle.is_default,
            "display_name": vehicle_display_name(booking.vehicle),
        }

    address_out = None
    if booking.address:
        address_out = {
            "id": booking.address.id,
            "label": booking.address.label,
            "district": booking.address.district,
            "city": booking.address.city,
            "latitude": to_float(booking.address.latitude),
            "longitude": to_float(booking.address.longitude),
            "is_default": booking.address.is_default,
        }

    return {
        "id": booking.id,
        "reference": booking.reference,
        "status": booking.status,
        "status_label_ar": status_label_ar(booking.status),
        "scheduled_at": booking.scheduled_at,
        "service_price_sar": to_float(booking.service_price_sar),
        "discount_sar": to_float(booking.discount_sar),
        "total_sar": to_float(booking.total_sar),
        "notes": booking.notes,
        "created_at": booking.created_at,
        "service": service_brief,
        "vehicle": vehicle_out,
        "address": address_out,
    }


def load_booking(db: Session, booking_id: UUID, user_id: UUID) -> Booking | None:
    return db.scalar(
        select(Booking)
        .options(
            joinedload(Booking.service),
            joinedload(Booking.vehicle),
            joinedload(Booking.address),
            joinedload(Booking.technician),
            joinedload(Booking.status_events),
        )
        .where(Booking.id == booking_id, Booking.user_id == user_id)
    )


def create_booking(
    db: Session,
    user: User,
    *,
    service_id: UUID,
    vehicle_id: UUID,
    address_id: UUID,
    payment_method_id: UUID | None,
    promotion_code: str | None,
    reward_slug: str | None,
    scheduled_at: datetime,
    notes: str | None,
    scan_id: UUID | None = None,
) -> Booking:
    service = db.get(Service, service_id)
    if not service or not service.is_active:
        raise ValueError("الخدمة غير موجودة")

    vehicle = db.scalar(
        select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.user_id == user.id)
    )
    if not vehicle:
        raise ValueError("المركبة غير موجودة")

    address = db.scalar(
        select(Address).where(Address.id == address_id, Address.user_id == user.id)
    )
    if not address:
        raise ValueError("العنوان غير موجود")

    if scan_id:
        scan = db.scalar(
            select(VehicleScan).where(
                VehicleScan.id == scan_id,
                VehicleScan.user_id == user.id,
                VehicleScan.status == "completed",
            )
        )
        if not scan:
            raise ValueError("الفحص غير موجود أو غير مكتمل")

    if payment_method_id:
        payment_method = db.scalar(
            select(PaymentMethod).where(
                PaymentMethod.id == payment_method_id,
                PaymentMethod.user_id == user.id,
            )
        )
        if not payment_method:
            raise ValueError("طريقة الدفع غير موجودة")

    service_price = to_float(service.price_sar)
    plan = get_membership_plan_for_user(db, user.id)
    membership_discount = calculate_membership_discount(plan, service_price)
    price_after_membership = service_price - membership_discount

    promo_discount = 0.0
    promotion = None
    if promotion_code:
        promotion = find_active_promotion(db, promotion_code, price_after_membership)
        if not promotion:
            raise ValueError("كود الخصم غير صالح")
        promo_discount = calculate_discount(promotion, price_after_membership)

    points_discount = 0.0
    if reward_slug:
        points_discount, _ = redeem_loyalty_reward(db, user, reward_slug)

    total_sar = max(
        0.0, service_price - membership_discount - promo_discount - points_discount
    )
    technician = assign_available_technician(db)

    booking = Booking(
        id=uuid4(),
        reference=next_booking_reference(db),
        user_id=user.id,
        service_id=service.id,
        vehicle_id=vehicle.id,
        address_id=address.id,
        payment_method_id=payment_method_id,
        technician_id=technician.id if technician else None,
        promotion_id=promotion.id if promotion else None,
        scan_id=scan_id,
        scheduled_at=scheduled_at,
        service_price_sar=service_price,
        discount_sar=promo_discount,
        membership_discount_sar=membership_discount,
        points_discount_sar=points_discount,
        total_sar=total_sar,
        status="confirmed" if technician else "pending",
        notes=notes,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(booking)
    db.flush()

    events = [
        BookingStatusEvent(
            id=uuid4(),
            booking_id=booking.id,
            status="confirmed",
            label_ar=STATUS_EVENT_LABELS["confirmed"],
            occurred_at=datetime.now(timezone.utc),
            metadata_={},
        )
    ]
    if technician:
        booking.status = "technician_assigned"
        events.append(
            BookingStatusEvent(
                id=uuid4(),
                booking_id=booking.id,
                status="technician_assigned",
                label_ar=STATUS_EVENT_LABELS["technician_assigned"],
                occurred_at=datetime.now(timezone.utc),
                metadata_={},
            )
        )

    db.add_all(events)
    db.add(
        Payment(
            id=uuid4(),
            booking_id=booking.id,
            amount_sar=total_sar,
            status="captured",
            gateway_ref=f"PAY-{booking.reference}",
            paid_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
        )
    )
    record_booking_revenue(
        db,
        booking.id,
        gross_sar=service_price,
        membership_discount_sar=membership_discount,
        promo_discount_sar=promo_discount,
        points_discount_sar=points_discount,
        net_sar=total_sar,
    )
    if promotion:
        record_promo_redemption(
            db, user.id, promotion.id, booking.id, promo_discount
        )
    db.commit()
    db.refresh(booking)
    return load_booking(db, booking.id, user.id)


TRACKING_ORDER = [
    "confirmed",
    "technician_assigned",
    "en_route",
    "in_progress",
    "completed",
]


def build_tracking(booking: Booking) -> dict:
    current_status = booking.status
    current_idx = (
        TRACKING_ORDER.index(current_status)
        if current_status in TRACKING_ORDER
        else -1
    )
    steps = []
    for event in booking.status_events:
        event_idx = (
            TRACKING_ORDER.index(event.status)
            if event.status in TRACKING_ORDER
            else -1
        )
        is_current = event.status == current_status
        is_done = event_idx >= 0 and current_idx >= 0 and event_idx < current_idx
        steps.append(
            {
                "status": event.status,
                "label_ar": event.label_ar,
                "occurred_at": event.occurred_at,
                "is_current": is_current,
                "is_done": is_done,
            }
        )

    technician_out = None
    if booking.technician:
        eta = None
        for event in reversed(booking.status_events):
            if event.status == "en_route" and event.metadata_:
                eta = event.metadata_.get("eta_minutes")
                break
        technician_out = {
            "full_name": booking.technician.full_name,
            "rating": to_float(booking.technician.rating),
            "avatar_initials": booking.technician.avatar_initials,
            "eta_minutes": eta,
            "location": (
                {
                    "lat": to_float(booking.technician.current_lat),
                    "lng": to_float(booking.technician.current_lng),
                }
                if booking.technician.current_lat is not None
                else None
            ),
        }

    return {
        "booking": {
            "id": booking.id,
            "reference": booking.reference,
            "status": booking.status,
            "status_label_ar": status_label_ar(booking.status),
        },
        "technician": technician_out,
        "steps": steps,
    }
