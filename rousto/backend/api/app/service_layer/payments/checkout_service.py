"""Checkout orchestration — Libyan gateways + wallet + commission."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.gateways.registry import get_gateway, list_libyan_gateways, validate_gateway
from app.models import GatewayPayment, User, Vendor
from app.service_layer.payments.audit_service import log_payment_event
from app.service_layer.payments.wallet_service import (
    credit_wallet,
    debit_wallet,
    get_or_create_wallet,
    settle_vendor_sale,
    wallet_out,
)
from app.tier_services import resolve_vendor_tier

PLATFORM_COMMISSION_DEFAULT = 0.15


def _now() -> datetime:
    return datetime.now(timezone.utc)


def checkout_options(db: Session, user: User) -> dict:
    wallet = get_or_create_wallet(db, owner_type="customer", owner_id=user.id)
    return {
        "currency": "LYD",
        "gateways": list_libyan_gateways(),
        "wallet": wallet_out(wallet),
        "blocked_international": True,
    }


def initiate_checkout(
    db: Session,
    user: User,
    *,
    amount_lyd: float,
    gateway: str,
    order_type: str,
    order_id: uuid.UUID | None,
    return_url: str,
    vendor: Vendor | None = None,
) -> dict:
    if amount_lyd <= 0:
        raise ValueError("المبلغ غير صالح")
    slug = validate_gateway(gateway)
    now = _now()

    gp = GatewayPayment(
        id=uuid.uuid4(),
        user_id=user.id,
        amount_lyd=round(amount_lyd, 2),
        gateway=slug,
        status="pending",
        order_type=order_type,
        order_id=order_id,
        metadata_json={"vendor_id": str(vendor.id) if vendor else None},
        created_at=now,
        updated_at=now,
    )
    db.add(gp)
    db.flush()

    log_payment_event(
        db,
        event_type="checkout.initiated",
        gateway=slug,
        reference_id=gp.id,
        details={"amount_lyd": amount_lyd, "order_type": order_type},
    )

    if slug == "cod":
        gp.status = "completed"
        gp.completed_at = now
        if vendor and order_id:
            _apply_vendor_settlement(db, vendor, amount_lyd, order_type, order_id, slug)
        return _checkout_response(gp, redirect_url=None)

    if slug == "wallet":
        customer_wallet = get_or_create_wallet(db, owner_type="customer", owner_id=user.id)
        debit_wallet(
            db,
            customer_wallet,
            amount_lyd,
            transaction_type="payment",
            reference_type=order_type,
            reference_id=order_id,
            gateway="wallet",
            description_ar="دفع من محفظة Rousto",
        )
        gp.status = "completed"
        gp.completed_at = now
        gp.gateway_ref = f"WLT-{gp.id.hex[:12].upper()}"
        if vendor and order_id:
            _apply_vendor_settlement(db, vendor, amount_lyd, order_type, order_id, slug)
        return _checkout_response(gp, redirect_url=None)

    adapter = get_gateway(slug)
    if not adapter:
        raise ValueError("بوابة غير مدعومة")
    result = adapter.create_payment(
        amount_lyd=amount_lyd,
        user_id=user.id,
        order_type=order_type,
        order_id=order_id,
        return_url=return_url,
    )
    gp.gateway_ref = result.gateway_ref
    gp.redirect_url = result.redirect_url
    gp.status = result.status
    gp.expires_at = result.expires_at
    return _checkout_response(gp, redirect_url=result.redirect_url)


def complete_gateway_webhook(
    db: Session,
    *,
    gateway: str,
    payload: dict,
    raw_body: bytes,
    signature: str,
    ip_address: str | None = None,
) -> GatewayPayment | None:
    slug = validate_gateway(gateway)
    adapter = get_gateway(slug)
    if not adapter:
        return None
    if not adapter.verify_webhook_signature(raw_body, signature):
        log_payment_event(
            db,
            event_type="webhook.signature_failed",
            gateway=slug,
            ip_address=ip_address,
            payload=raw_body,
        )
        raise ValueError("توقيع Webhook غير صالح")

    ref, status = adapter.parse_webhook_status(payload)
    gp = db.scalar(
        select(GatewayPayment).where(
            GatewayPayment.gateway_ref == ref,
            GatewayPayment.gateway == slug,
        )
    )
    if not gp:
        log_payment_event(db, event_type="webhook.unknown_ref", gateway=slug, payload=raw_body)
        return None

    log_payment_event(
        db,
        event_type="webhook.received",
        gateway=slug,
        reference_id=gp.id,
        ip_address=ip_address,
        payload=raw_body,
        details={"status": status},
    )

    if gp.status == "completed":
        return gp

    now = _now()
    if status == "completed":
        gp.status = "completed"
        gp.completed_at = now
        if gp.order_type == "wallet_topup":
            user_wallet = get_or_create_wallet(
                db, owner_type="customer", owner_id=gp.user_id
            )
            credit_wallet(
                db,
                user_wallet,
                float(gp.amount_lyd),
                transaction_type="deposit",
                gateway=slug,
                gateway_ref=ref,
                description_ar="شحن محفظة عبر بوابة محلية",
            )
        else:
            vendor_id = gp.metadata_json.get("vendor_id")
            if vendor_id and gp.order_id:
                vendor = db.get(Vendor, uuid.UUID(vendor_id))
                if vendor:
                    _apply_vendor_settlement(
                        db,
                        vendor,
                        float(gp.amount_lyd),
                        gp.order_type,
                        gp.order_id,
                        slug,
                    )
    else:
        gp.status = "failed"
    gp.updated_at = now
    return gp


def wallet_topup_via_gateway(
    db: Session,
    user: User,
    *,
    amount_lyd: float,
    gateway: str,
    return_url: str,
) -> dict:
    return initiate_checkout(
        db,
        user,
        amount_lyd=amount_lyd,
        gateway=gateway,
        order_type="wallet_topup",
        order_id=None,
        return_url=return_url,
    )


def _apply_vendor_settlement(
    db: Session,
    vendor: Vendor,
    amount_lyd: float,
    order_type: str,
    order_id: uuid.UUID,
    gateway: str,
) -> dict:
    tier = resolve_vendor_tier(db, vendor)
    rate = float(getattr(tier, "platform_commission_rate", None) or PLATFORM_COMMISSION_DEFAULT)
    return settle_vendor_sale(
        db,
        vendor=vendor,
        gross_lyd=amount_lyd,
        commission_rate=rate,
        order_type=order_type,
        order_id=order_id,
        gateway=gateway,
    )


def _checkout_response(gp: GatewayPayment, redirect_url: str | None) -> dict:
    return {
        "payment_id": gp.id,
        "gateway": gp.gateway,
        "status": gp.status,
        "amount_lyd": float(gp.amount_lyd),
        "gateway_ref": gp.gateway_ref,
        "redirect_url": redirect_url,
        "requires_webview": redirect_url is not None,
    }
