from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.gateways.registry import BLOCKED_GATEWAYS
from app.libyan_payment_services import checkout_options, initiate_checkout, wallet_topup_via_gateway
from app.models import User, Vendor
from app.wallet_services import get_or_create_wallet, list_wallet_transactions, wallet_out

router = APIRouter(tags=["libyan-payments"])


class CheckoutIn(BaseModel):
    amount_lyd: float = Field(gt=0, le=500000)
    gateway: str = Field(min_length=2, max_length=20)
    order_type: str = Field(min_length=2, max_length=40)
    order_id: UUID | None = None
    vendor_id: UUID | None = None
    return_url: str = Field(default="rousto://payment/return", max_length=500)


class WalletTopupIn(BaseModel):
    amount_lyd: float = Field(gt=0, le=100000)
    gateway: str = Field(pattern=r"^(muamalat|sadad|edfali)$")
    return_url: str = Field(default="rousto://payment/return", max_length=500)


@router.get("/payments/libyan/options")
def get_checkout_options(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {"data": checkout_options(db, user)}


@router.get("/me/wallet")
def get_my_wallet(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallet = get_or_create_wallet(db, owner_type="customer", owner_id=user.id)
    txs = list_wallet_transactions(db, wallet.id, limit=30)
    return {"data": {**wallet_out(wallet), "transactions": txs}}


@router.post("/payments/checkout")
def post_checkout(
    body: CheckoutIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if body.gateway.lower() in BLOCKED_GATEWAYS:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "GATEWAY_BLOCKED",
                "message": "بوابات الدفع الدولية غير مدعومة في ليبيا",
            },
        )
    vendor = db.get(Vendor, body.vendor_id) if body.vendor_id else None
    try:
        result = initiate_checkout(
            db,
            user,
            amount_lyd=body.amount_lyd,
            gateway=body.gateway,
            order_type=body.order_type,
            order_id=body.order_id,
            return_url=body.return_url,
            vendor=vendor,
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "CHECKOUT_ERROR", "message": str(exc)},
        ) from exc
    return {"data": result}


@router.post("/me/wallet/topup")
def post_wallet_topup(
    body: WalletTopupIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        result = wallet_topup_via_gateway(
            db,
            user,
            amount_lyd=body.amount_lyd,
            gateway=body.gateway,
            return_url=body.return_url,
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "TOPUP_ERROR", "message": str(exc)},
        ) from exc
    return {"data": result}
