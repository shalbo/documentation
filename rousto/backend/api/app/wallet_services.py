"""In-app wallet ledger — customers, vendors, drivers, platform."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Vendor, Wallet, WalletTransaction, WithdrawalRequest
from app.payment_audit_services import log_payment_event

logger = logging.getLogger("rousto.wallet")
PLATFORM_OWNER_ID = uuid.UUID("00000000-0000-4000-8000-000000000099")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _d(val: float | Decimal) -> Decimal:
    return Decimal(str(val)).quantize(Decimal("0.01"))


def wallet_out(wallet: Wallet) -> dict:
    return {
        "id": wallet.id,
        "owner_type": wallet.owner_type,
        "owner_id": wallet.owner_id,
        "balance_lyd": float(wallet.balance_lyd),
        "pending_lyd": float(wallet.pending_lyd),
        "currency": wallet.currency,
        "is_active": wallet.is_active,
    }


def tx_out(tx: WalletTransaction) -> dict:
    return {
        "id": tx.id,
        "amount_lyd": float(tx.amount_lyd),
        "direction": tx.direction,
        "transaction_type": tx.transaction_type,
        "status": tx.status,
        "gateway": tx.gateway,
        "description_ar": tx.description_ar,
        "created_at": tx.created_at.isoformat() if tx.created_at else None,
    }


def get_or_create_wallet(
    db: Session,
    *,
    owner_type: str,
    owner_id: uuid.UUID,
) -> Wallet:
    wallet = db.scalar(
        select(Wallet).where(
            Wallet.owner_type == owner_type,
            Wallet.owner_id == owner_id,
        )
    )
    if wallet:
        return wallet
    now = _now()
    wallet = Wallet(
        id=uuid.uuid4(),
        owner_type=owner_type,
        owner_id=owner_id,
        balance_lyd=0,
        pending_lyd=0,
        currency="LYD",
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    db.add(wallet)
    db.flush()
    return wallet


def _record_tx(
    db: Session,
    wallet: Wallet,
    *,
    amount_lyd: float,
    direction: str,
    transaction_type: str,
    status: str = "completed",
    reference_type: str | None = None,
    reference_id: uuid.UUID | None = None,
    gateway: str | None = None,
    gateway_ref: str | None = None,
    description_ar: str | None = None,
) -> WalletTransaction:
    tx = WalletTransaction(
        id=uuid.uuid4(),
        wallet_id=wallet.id,
        amount_lyd=float(_d(amount_lyd)),
        direction=direction,
        transaction_type=transaction_type,
        status=status,
        reference_type=reference_type,
        reference_id=reference_id,
        gateway=gateway,
        gateway_ref=gateway_ref,
        description_ar=description_ar,
        metadata_json={},
        created_at=_now(),
    )
    db.add(tx)
    return tx


def credit_wallet(
    db: Session,
    wallet: Wallet,
    amount_lyd: float,
    *,
    transaction_type: str = "deposit",
    **kwargs,
) -> WalletTransaction:
    amt = _d(amount_lyd)
    if amt <= 0:
        raise ValueError("المبلغ يجب أن يكون موجباً")
    wallet.balance_lyd = float(_d(wallet.balance_lyd) + amt)
    wallet.updated_at = _now()
    return _record_tx(
        db, wallet, amount_lyd=float(amt), direction="credit", transaction_type=transaction_type, **kwargs
    )


def debit_wallet(
    db: Session,
    wallet: Wallet,
    amount_lyd: float,
    *,
    transaction_type: str = "payment",
    **kwargs,
) -> WalletTransaction:
    amt = _d(amount_lyd)
    if amt <= 0:
        raise ValueError("المبلغ يجب أن يكون موجباً")
    if _d(wallet.balance_lyd) < amt:
        raise ValueError("رصيد المحفظة غير كافٍ")
    wallet.balance_lyd = float(_d(wallet.balance_lyd) - amt)
    wallet.updated_at = _now()
    return _record_tx(
        db, wallet, amount_lyd=float(amt), direction="debit", transaction_type=transaction_type, **kwargs
    )


def settle_vendor_sale(
    db: Session,
    *,
    vendor: Vendor,
    gross_lyd: float,
    commission_rate: float,
    order_type: str,
    order_id: uuid.UUID,
    gateway: str,
) -> dict:
    """Atomic: platform commission + vendor net credit."""
    gross = _d(gross_lyd)
    commission = (gross * _d(commission_rate)).quantize(Decimal("0.01"))
    net = gross - commission

    vendor_wallet = get_or_create_wallet(db, owner_type="vendor", owner_id=vendor.id)
    platform_wallet = get_or_create_wallet(
        db, owner_type="platform", owner_id=PLATFORM_OWNER_ID
    )

    credit_wallet(
        db,
        vendor_wallet,
        float(net),
        transaction_type="payment",
        reference_type=order_type,
        reference_id=order_id,
        gateway=gateway,
        description_ar=f"صافي مبيعات بعد عمولة {float(commission_rate)*100:.0f}%",
    )
    credit_wallet(
        db,
        platform_wallet,
        float(commission),
        transaction_type="commission",
        reference_type=order_type,
        reference_id=order_id,
        gateway=gateway,
        description_ar="عمولة المنصة",
    )
    log_payment_event(
        db,
        event_type="vendor.settlement",
        gateway=gateway,
        reference_id=order_id,
        details={
            "gross_lyd": float(gross),
            "commission_lyd": float(commission),
            "net_lyd": float(net),
            "vendor_id": str(vendor.id),
        },
    )
    return {
        "gross_lyd": float(gross),
        "commission_lyd": float(commission),
        "net_lyd": float(net),
        "commission_rate": commission_rate,
    }


def deduct_driver_commission(
    db: Session,
    *,
    driver_user_id: uuid.UUID,
    amount_lyd: float,
    trip_ref: str,
) -> WalletTransaction:
    wallet = get_or_create_wallet(db, owner_type="driver", owner_id=driver_user_id)
    return debit_wallet(
        db,
        wallet,
        amount_lyd,
        transaction_type="commission",
        reference_type="trip",
        description_ar=f"عمولة مشوار {trip_ref}",
    )


def request_withdrawal(
    db: Session,
    vendor: Vendor,
    *,
    amount_lyd: float,
    bank_name: str | None,
    iban: str | None,
    note: str | None,
) -> WithdrawalRequest:
    wallet = get_or_create_wallet(db, owner_type="vendor", owner_id=vendor.id)
    amt = _d(amount_lyd)
    if amt <= 0:
        raise ValueError("مبلغ السحب غير صالح")
    if _d(wallet.balance_lyd) < amt:
        raise ValueError("الرصيد المتاح غير كافٍ لطلب السحب")
    wallet.pending_lyd = float(_d(wallet.pending_lyd) + amt)
    wallet.updated_at = _now()
    now = _now()
    req = WithdrawalRequest(
        id=uuid.uuid4(),
        wallet_id=wallet.id,
        vendor_id=vendor.id,
        amount_lyd=float(amt),
        status="pending",
        bank_name=bank_name,
        iban=iban,
        note=note,
        created_at=now,
        updated_at=now,
    )
    db.add(req)
    log_payment_event(
        db,
        event_type="withdrawal.requested",
        reference_id=req.id,
        details={"vendor_id": str(vendor.id), "amount_lyd": float(amt)},
    )
    return req


def approve_withdrawal(
    db: Session,
    request: WithdrawalRequest,
    *,
    approved_by: str,
    admin_note: str | None = None,
    mark_paid: bool = False,
) -> WithdrawalRequest:
    if request.status not in {"pending", "approved"}:
        raise ValueError("لا يمكن معالجة هذا الطلب")
    wallet = db.get(Wallet, request.wallet_id)
    if not wallet:
        raise ValueError("المحفظة غير موجودة")
    now = _now()
    if mark_paid:
        amt = _d(request.amount_lyd)
        if _d(wallet.balance_lyd) < amt:
            raise ValueError("رصيد المحفظة غير كافٍ")
        debit_wallet(
            db,
            wallet,
            float(amt),
            transaction_type="withdraw",
            reference_type="withdrawal",
            reference_id=request.id,
            description_ar="سحب أرباح معتمد",
        )
        wallet.pending_lyd = float(max(_d(wallet.pending_lyd) - amt, Decimal("0")))
        request.status = "paid"
        request.paid_at = now
    else:
        request.status = "approved"
    request.approved_by = approved_by
    request.admin_note = admin_note
    request.updated_at = now
    log_payment_event(
        db,
        event_type="withdrawal.paid" if mark_paid else "withdrawal.approved",
        reference_id=request.id,
        details={"approved_by": approved_by},
    )
    return request


def list_wallet_transactions(
    db: Session,
    wallet_id: uuid.UUID,
    *,
    limit: int = 50,
) -> list[dict]:
    rows = db.scalars(
        select(WalletTransaction)
        .where(WalletTransaction.wallet_id == wallet_id)
        .order_by(WalletTransaction.created_at.desc())
        .limit(limit)
    ).all()
    return [tx_out(r) for r in rows]
