"""Payment-only OTP — gates all monetary operations behind SMS verification."""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import GatewayPayment, OtpCode, PaymentIntent, User, Vendor
from app.service_layer.payments.checkout_service import initiate_checkout
from app.sms_service import send_payment_otp_sms

PAYMENT_OTP_LENGTH = 4
PAYMENT_OTP_TTL_SECONDS = 60
PAYMENT_OTP_MAX_ATTEMPTS = 5
INTENT_TTL_MINUTES = 15
OTP_EXECUTE_GRACE_SECONDS = 120


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def create_payment_intent(
    db: Session,
    user: User,
    *,
    amount_lyd: float,
    gateway: str,
    order_type: str,
    order_ref_id: uuid.UUID | None,
    return_url: str,
    vendor: Vendor | None = None,
) -> PaymentIntent:
    if amount_lyd <= 0:
        raise ValueError("المبلغ غير صالح")
    now = _now()
    intent = PaymentIntent(
        id=uuid.uuid4(),
        user_id=user.id,
        amount_lyd=round(amount_lyd, 2),
        gateway=gateway.strip().lower(),
        order_type=order_type,
        order_ref_id=order_ref_id,
        vendor_id=vendor.id if vendor else None,
        return_url=return_url,
        status="pending_otp",
        expires_at=now + timedelta(minutes=INTENT_TTL_MINUTES),
        created_at=now,
        updated_at=now,
    )
    db.add(intent)
    db.flush()
    return intent


def payment_intent_out(intent: PaymentIntent) -> dict:
    return {
        "order_id": str(intent.id),
        "intent_id": str(intent.id),
        "amount_lyd": float(intent.amount_lyd),
        "gateway": intent.gateway,
        "order_type": intent.order_type,
        "status": intent.status,
        "requires_otp": intent.status == "pending_otp",
        "expires_at": intent.expires_at.isoformat(),
    }


def get_payment_intent_for_user(
    db: Session,
    intent_id: uuid.UUID,
    user_id: uuid.UUID,
) -> PaymentIntent:
    intent = db.get(PaymentIntent, intent_id)
    if not intent or intent.user_id != user_id:
        raise ValueError("طلب الدفع غير موجود")
    if intent.expires_at <= _now():
        intent.status = "expired"
        intent.updated_at = _now()
        raise ValueError("انتهت صلاحية طلب الدفع — أعد المحاولة")
    if intent.status != "pending_otp":
        raise ValueError("طلب الدفع لم يعد قابلاً للتنفيذ")
    return intent


def generate_payment_otp(
    db: Session,
    user: User,
    *,
    order_id: uuid.UUID,
    amount_lyd: float | None = None,
) -> dict:
    intent = get_payment_intent_for_user(db, order_id, user.id)
    if amount_lyd is not None and round(amount_lyd, 2) != float(intent.amount_lyd):
        raise ValueError("المبلغ لا يطابق طلب الدفع")

    code = "".join(str(secrets.randbelow(10)) for _ in range(PAYMENT_OTP_LENGTH))
    if settings.otp_dev_mode and not settings.is_production:
        code = settings.payment_otp_dev_code

    now = _now()
    otp = OtpCode(
        id=uuid.uuid4(),
        user_id=user.id,
        order_id=intent.id,
        code_hash=_hash_code(code),
        expires_at=now + timedelta(seconds=PAYMENT_OTP_TTL_SECONDS),
        is_used=False,
        created_at=now,
    )
    db.add(otp)
    db.flush()

    send_payment_otp_sms(
        phone=user.phone,
        code=code,
        amount_lyd=float(intent.amount_lyd),
    )

    meta: dict = {
        "expires_in_seconds": PAYMENT_OTP_TTL_SECONDS,
        "order_id": str(intent.id),
    }
    if settings.otp_dev_mode and not settings.is_production:
        meta["dev_otp"] = code

    return {
        "message": "تم إرسال رمز التحقق المالي",
        "phone_masked": user.phone[-4:].rjust(len(user.phone), "*"),
        "meta": meta,
    }


def verify_payment_otp_and_execute(
    db: Session,
    user: User,
    *,
    order_id: uuid.UUID,
    code: str,
) -> dict:
    intent = get_payment_intent_for_user(db, order_id, user.id)

    now = _now()
    otp = db.scalar(
        select(OtpCode)
        .where(
            OtpCode.order_id == intent.id,
            OtpCode.user_id == user.id,
            OtpCode.is_used.is_(False),
            OtpCode.expires_at > now,
        )
        .order_by(OtpCode.created_at.desc())
        .limit(1)
    )
    if not otp:
        raise ValueError("انتهت صلاحية الرمز أو لم يُرسل بعد")

    if _hash_code(code.strip()) != otp.code_hash:
        raise ValueError("رمز التحقق غير صحيح")

    otp.is_used = True
    intent.otp_verified_at = now
    intent.updated_at = now
    db.flush()

    vendor = db.get(Vendor, intent.vendor_id) if intent.vendor_id else None
    result = initiate_checkout(
        db,
        user,
        amount_lyd=float(intent.amount_lyd),
        gateway=intent.gateway,
        order_type=intent.order_type,
        order_id=intent.order_ref_id,
        return_url=intent.return_url or "rousto://payment/return",
        vendor=vendor,
    )

    gp = db.get(GatewayPayment, result["payment_id"])
    intent.status = "completed" if result.get("status") == "completed" else "processing"
    intent.gateway_payment_id = gp.id if gp else None
    intent.updated_at = _now()

    if intent.order_type == "driver_registration_fee" and intent.order_ref_id and gp:
        from app.models import DriverProfile

        profile = db.get(DriverProfile, intent.order_ref_id)
        if profile:
            profile.payment_reference_id = gp.id
            profile.registration_fee_gateway = intent.gateway
            profile.updated_at = _now()

    return {
        **result,
        "intent_id": str(intent.id),
        "order_id": str(intent.id),
        "payment_completed": True,
    }


def generate_payment_otp_for_profile(
    db: Session,
    *,
    intent_id: uuid.UUID,
    phone: str,
) -> dict:
    from app.registration_services import normalize_phone

    normalized = normalize_phone(phone)
    intent = db.get(PaymentIntent, intent_id)
    if not intent:
        raise ValueError("طلب الدفع غير موجود")
    user = db.get(User, intent.user_id)
    if not user or user.phone != normalized:
        raise ValueError("رقم الجوال لا يطابق طلب الدفع")
    return generate_payment_otp(db, user, order_id=intent_id)


def verify_payment_otp_for_profile(
    db: Session,
    *,
    intent_id: uuid.UUID,
    phone: str,
    code: str,
) -> dict:
    from app.registration_services import normalize_phone

    normalized = normalize_phone(phone)
    intent = db.get(PaymentIntent, intent_id)
    if not intent:
        raise ValueError("طلب الدفع غير موجود")
    user = db.get(User, intent.user_id)
    if not user or user.phone != normalized:
        raise ValueError("رقم الجوال لا يطابق طلب الدفع")
    return verify_payment_otp_and_execute(db, user, order_id=intent_id, code=code)
