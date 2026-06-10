from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Booking, Payment, PaymentSplitLeg, SplitRule

RECIPIENT_LABELS = {
    "platform": "عمولة المنصة",
    "technician": "حصة الفني",
    "reserve": "احتياطي المنصة",
}

INITIAL_LEG_STATUS = {
    "platform": "released",
    "technician": "held",
    "reserve": "held",
}


def get_default_rule(db: Session) -> SplitRule:
    rule = db.scalar(
        select(SplitRule).where(SplitRule.is_default.is_(True), SplitRule.is_active.is_(True))
    )
    if not rule:
        raise ValueError("لا توجد قاعدة تقسيم افتراضية")
    return rule


def calculate_split_legs(amount_sar: float, rule: SplitRule) -> list[dict]:
    net = Decimal(str(amount_sar))
    specs = [
        ("platform", Decimal(str(rule.platform_rate))),
        ("technician", Decimal(str(rule.technician_rate))),
        ("reserve", Decimal(str(rule.reserve_rate))),
    ]
    legs = []
    for recipient_type, rate in specs:
        amount = (net * rate).quantize(Decimal("0.01"))
        legs.append(
            {
                "recipient_type": recipient_type,
                "label_ar": RECIPIENT_LABELS[recipient_type],
                "rate": float(rate),
                "amount_sar": float(amount),
            }
        )
    return legs


def preview_split(db: Session, amount_sar: float) -> dict:
    rule = get_default_rule(db)
    return {
        "amount_sar": amount_sar,
        "rule_slug": rule.slug,
        "rule_name_ar": rule.name_ar,
        "legs": calculate_split_legs(amount_sar, rule),
    }


def create_split_legs_for_payment(
    db: Session,
    *,
    payment: Payment,
    booking: Booking,
    net_sar: float,
    technician_id: UUID | None,
) -> list[PaymentSplitLeg]:
    rule = get_default_rule(db)
    now = datetime.now(timezone.utc)
    created: list[PaymentSplitLeg] = []

    for leg in calculate_split_legs(net_sar, rule):
        recipient_type = leg["recipient_type"]
        status = INITIAL_LEG_STATUS[recipient_type]
        split_leg = PaymentSplitLeg(
            id=uuid4(),
            payment_id=payment.id,
            booking_id=booking.id,
            rule_id=rule.id,
            recipient_type=recipient_type,
            recipient_id=technician_id if recipient_type == "technician" else None,
            amount_sar=leg["amount_sar"],
            rate_applied=leg["rate"],
            status=status,
            released_at=now if status == "released" else None,
            created_at=now,
        )
        db.add(split_leg)
        created.append(split_leg)

    return created


def get_booking_split(db: Session, booking_id: UUID) -> dict | None:
    legs = db.scalars(
        select(PaymentSplitLeg)
        .where(PaymentSplitLeg.booking_id == booking_id)
        .order_by(PaymentSplitLeg.recipient_type)
    ).all()
    if not legs:
        return None

    payment_id = legs[0].payment_id
    net_sar = sum(float(leg.amount_sar) for leg in legs)
    return {
        "booking_id": str(booking_id),
        "payment_id": str(payment_id),
        "net_sar": round(net_sar, 2),
        "legs": [serialize_split_leg(leg) for leg in legs],
    }


def serialize_split_leg(leg: PaymentSplitLeg) -> dict:
    return {
        "id": str(leg.id),
        "recipient_type": leg.recipient_type,
        "label_ar": RECIPIENT_LABELS.get(leg.recipient_type, leg.recipient_type),
        "recipient_id": str(leg.recipient_id) if leg.recipient_id else None,
        "amount_sar": float(leg.amount_sar),
        "rate_applied": float(leg.rate_applied),
        "status": leg.status,
        "released_at": leg.released_at.isoformat() if leg.released_at else None,
    }


def release_technician_splits(db: Session, booking_id: UUID) -> int:
    now = datetime.now(timezone.utc)
    legs = db.scalars(
        select(PaymentSplitLeg).where(
            PaymentSplitLeg.booking_id == booking_id,
            PaymentSplitLeg.recipient_type == "technician",
            PaymentSplitLeg.status == "held",
        )
    ).all()
    for leg in legs:
        leg.status = "released"
        leg.released_at = now
    return len(legs)


def release_splits_for_booking(
    db: Session, booking_id: UUID, *, recipient_type: str | None = None
) -> int:
    now = datetime.now(timezone.utc)
    stmt = select(PaymentSplitLeg).where(
        PaymentSplitLeg.booking_id == booking_id,
        PaymentSplitLeg.status == "held",
    )
    if recipient_type:
        stmt = stmt.where(PaymentSplitLeg.recipient_type == recipient_type)

    legs = db.scalars(stmt).all()
    for leg in legs:
        leg.status = "released"
        leg.released_at = now
    return len(legs)
