from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api_responses import success, success_list
from app.db import get_db
from app.deps import require_admin_key
from app.models import PaymentAuditLog, Wallet, WithdrawalRequest
from app.service_layer.payments import PLATFORM_OWNER_ID, approve_withdrawal

router = APIRouter(prefix="/admin", tags=["admin-payments"])


class WithdrawalActionIn(BaseModel):
    admin_note: str | None = Field(default=None, max_length=500)
    mark_paid: bool = False


@router.get("/payments/overview")
def admin_payments_overview(
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    platform_wallet = db.scalar(
        select(Wallet).where(
            Wallet.owner_type == "platform",
            Wallet.owner_id == PLATFORM_OWNER_ID,
        )
    )
    pending = db.scalar(
        select(func.count()).select_from(WithdrawalRequest).where(
            WithdrawalRequest.status == "pending"
        )
    ) or 0
    pending_amount = db.scalar(
        select(func.coalesce(func.sum(WithdrawalRequest.amount_lyd), 0)).where(
            WithdrawalRequest.status == "pending"
        )
    ) or 0
    return success(
        {
            "platform_commission_lyd": float(platform_wallet.balance_lyd) if platform_wallet else 0,
            "pending_withdrawals_count": pending,
            "pending_withdrawals_lyd": float(pending_amount),
            "currency": "LYD",
        }
    )


@router.get("/withdrawals")
def admin_list_withdrawals(
    status: str | None = Query(default=None),
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    stmt = select(WithdrawalRequest).order_by(WithdrawalRequest.created_at.desc())
    if status:
        stmt = stmt.where(WithdrawalRequest.status == status)
    rows = db.scalars(stmt.limit(200)).all()
    data = [
        {
            "id": r.id,
            "vendor_id": r.vendor_id,
            "amount_lyd": float(r.amount_lyd),
            "status": r.status,
            "bank_name": r.bank_name,
            "iban": r.iban,
            "note": r.note,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
    return success_list(data)


@router.patch("/withdrawals/{request_id}")
def admin_process_withdrawal(
    request_id: UUID,
    body: WithdrawalActionIn,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    req = db.get(WithdrawalRequest, request_id)
    if not req:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "الطلب غير موجود"})
    try:
        updated = approve_withdrawal(
            db,
            req,
            approved_by="admin",
            admin_note=body.admin_note,
            mark_paid=body.mark_paid,
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "WITHDRAWAL_ERROR", "message": str(exc)},
        ) from exc
    msg = "تم تحويل المبلغ وتحديث المحفظة" if body.mark_paid else "تم اعتماد الطلب"
    return success(
        {
            "id": updated.id,
            "status": updated.status,
            "paid_at": updated.paid_at.isoformat() if updated.paid_at else None,
        },
        message=msg,
    )


@router.get("/payments/audit")
def admin_payment_audit(
    limit: int = Query(default=50, ge=1, le=200),
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    rows = db.scalars(
        select(PaymentAuditLog).order_by(PaymentAuditLog.created_at.desc()).limit(limit)
    ).all()
    return success_list(
        [
            {
                "id": r.id,
                "event_type": r.event_type,
                "gateway": r.gateway,
                "reference_id": str(r.reference_id) if r.reference_id else None,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]
    )
