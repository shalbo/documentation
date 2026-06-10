from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api_responses import success
from app.db import get_db
from app.deps import get_current_user
from app.gateways.registry import BLOCKED_GATEWAYS
from app.models import User, Vendor
from app.payment_otp_services import create_payment_intent, payment_intent_out
from app.service_layer.payments import (
    checkout_options,
    get_or_create_wallet,
    list_wallet_transactions,
    wallet_out,
)

router = APIRouter(tags=["libyan-payments"])


class CheckoutIn(BaseModel):
    amount_lyd: float = Field(gt=0, le=500000)
    gateway: str = Field(min_length=2, max_length=20)
    order_type: str = Field(min_length=2, max_length=40)
    order_id: UUID | None = None
    vendor_id: UUID | None = None
    return_url: str = Field(default="rousto://payment/return", max_length=500)


class GatewayInitiateIn(BaseModel):
    amount_lyd: float = Field(gt=0, le=500000)
    order_type: str = Field(min_length=2, max_length=40)
    order_id: UUID | None = None
    vendor_id: UUID | None = None
    return_url: str = Field(default="rousto://payment/return", max_length=500)


class WalletTopupIn(BaseModel):
    amount_lyd: float = Field(gt=0, le=100000)
    gateway: str = Field(pattern=r"^(muamalat|sadad|edfali)$")
    return_url: str = Field(default="rousto://payment/return", max_length=500)


def _resolve_vendor(db: Session, vendor_id: UUID | None) -> Vendor | None:
    return db.get(Vendor, vendor_id) if vendor_id else None


def _run_checkout(
    db: Session,
    user: User,
    *,
    amount_lyd: float,
    gateway: str,
    order_type: str,
    order_id: UUID | None,
    return_url: str,
    vendor: Vendor | None,
) -> dict:
    if gateway.lower() in BLOCKED_GATEWAYS:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "GATEWAY_BLOCKED",
                "message": "بوابات الدفع الدولية غير مدعومة في ليبيا",
            },
        )
    try:
        intent = create_payment_intent(
            db,
            user,
            amount_lyd=amount_lyd,
            gateway=gateway,
            order_type=order_type,
            order_ref_id=order_id,
            return_url=return_url,
            vendor=vendor,
        )
        db.commit()
        result = payment_intent_out(intent)
        result["requires_otp"] = True
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "CHECKOUT_ERROR", "message": str(exc)},
        ) from exc
    return result


@router.get("/payments/libyan/options")
def get_checkout_options(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return success(checkout_options(db, user))


@router.get("/me/wallet")
def get_my_wallet(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallet = get_or_create_wallet(db, owner_type="customer", owner_id=user.id)
    txs = list_wallet_transactions(db, wallet.id, limit=30)
    return success({**wallet_out(wallet), "transactions": txs})


@router.post("/payments/checkout")
def post_checkout(
    body: CheckoutIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    vendor = _resolve_vendor(db, body.vendor_id)
    result = _run_checkout(
        db,
        user,
        amount_lyd=body.amount_lyd,
        gateway=body.gateway,
        order_type=body.order_type,
        order_id=body.order_id,
        return_url=body.return_url,
        vendor=vendor,
    )
    return success(result, message="تم بدء عملية الدفع")


@router.post("/payments/muamalat/initiate")
def post_muamalat_initiate(
    body: GatewayInitiateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = _run_checkout(
        db,
        user,
        amount_lyd=body.amount_lyd,
        gateway="muamalat",
        order_type=body.order_type,
        order_id=body.order_id,
        return_url=body.return_url,
        vendor=_resolve_vendor(db, body.vendor_id),
    )
    return success(result, message="تم إنشاء طلب دفع — أكمل OTP المالي")


@router.post("/payments/sadad/initiate")
def post_sadad_initiate(
    body: GatewayInitiateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = _run_checkout(
        db,
        user,
        amount_lyd=body.amount_lyd,
        gateway="sadad",
        order_type=body.order_type,
        order_id=body.order_id,
        return_url=body.return_url,
        vendor=_resolve_vendor(db, body.vendor_id),
    )
    return success(result, message="تم إنشاء طلب دفع — أكمل OTP المالي")


@router.post("/payments/edfali/initiate")
def post_edfali_initiate(
    body: GatewayInitiateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = _run_checkout(
        db,
        user,
        amount_lyd=body.amount_lyd,
        gateway="edfali",
        order_type=body.order_type,
        order_id=body.order_id,
        return_url=body.return_url,
        vendor=_resolve_vendor(db, body.vendor_id),
    )
    return success(result, message="تم إنشاء طلب دفع — أكمل OTP المالي")


@router.post("/me/wallet/topup")
def post_wallet_topup(
    body: WalletTopupIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = _run_checkout(
        db,
        user,
        amount_lyd=body.amount_lyd,
        gateway=body.gateway,
        order_type="wallet_topup",
        order_id=None,
        return_url=body.return_url,
        vendor=None,
    )
    return success(result, message="تم إنشاء طلب شحن — أكمل OTP المالي")
