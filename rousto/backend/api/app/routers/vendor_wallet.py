from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_vendor
from app.vendor_staff_rbac import require_wallet_access
from app.models import Vendor, WalletTransaction, WithdrawalRequest
from app.api_responses import success
from app.service_layer.payments import (
    get_or_create_wallet,
    list_wallet_transactions,
    request_withdrawal,
    wallet_out,
)

router = APIRouter(prefix="/vendor/wallet", tags=["vendor-wallet"])


class WithdrawalIn(BaseModel):
    amount_lyd: float = Field(gt=0, le=500000)
    bank_name: str | None = Field(default=None, max_length=80)
    iban: str | None = Field(default=None, max_length=34)
    note: str | None = Field(default=None, max_length=300)


def _tx_out_full(tx: WalletTransaction) -> dict:
    return {
        "id": tx.id,
        "amount_lyd": float(tx.amount_lyd),
        "direction": tx.direction,
        "transaction_type": tx.transaction_type,
        "status": tx.status,
        "description_ar": tx.description_ar,
        "created_at": tx.created_at.isoformat() if tx.created_at else None,
    }


@router.get("")
def vendor_wallet_summary(
    vendor: Vendor = Depends(get_current_vendor),
    _: None = Depends(require_wallet_access),
    db: Session = Depends(get_db),
):
    wallet = get_or_create_wallet(db, owner_type="vendor", owner_id=vendor.id)
    txs = list_wallet_transactions(db, wallet.id, limit=40)
    pending_withdrawals = db.scalar(
        select(func.coalesce(func.sum(WithdrawalRequest.amount_lyd), 0)).where(
            WithdrawalRequest.vendor_id == vendor.id,
            WithdrawalRequest.status == "pending",
        )
    )
    return success(
        {
            **wallet_out(wallet),
            "pending_withdrawals_lyd": float(pending_withdrawals or 0),
            "transactions": txs,
        }
    )


@router.post("/withdraw", status_code=201)
def vendor_request_withdrawal(
    body: WithdrawalIn,
    vendor: Vendor = Depends(get_current_vendor),
    _: None = Depends(require_wallet_access),
    db: Session = Depends(get_db),
):
    try:
        req = request_withdrawal(
            db,
            vendor,
            amount_lyd=body.amount_lyd,
            bank_name=body.bank_name,
            iban=body.iban,
            note=body.note,
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "WITHDRAWAL_ERROR", "message": str(exc)},
        ) from exc
    return success(
        {
            "id": req.id,
            "amount_lyd": float(req.amount_lyd),
            "status": req.status,
        },
        message="تم إرسال طلب السحب — بانتظار اعتماد الإدارة",
    )
