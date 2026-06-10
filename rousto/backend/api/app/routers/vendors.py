from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_vendor, require_admin_key
from app.models import Vendor
from app.schemas import (
    VendorApplicationIn,
    VendorFinancialsUpdateIn,
    VendorRejectIn,
)
from app.vendor_services import (
    approve_vendor,
    bank_account_out,
    list_vendor_payouts,
    payout_leg_out,
    reject_vendor,
    submit_application,
    update_vendor_financials,
    vendor_out,
)

router = APIRouter(tags=["vendors"])


@router.post("/vendors/applications")
def create_vendor_application(body: VendorApplicationIn, db: Session = Depends(get_db)):
    try:
        vendor = submit_application(
            db,
            business_name=body.business_name,
            contact_name=body.contact_name,
            email=body.email,
            phone=body.phone,
            city=body.city,
            bank_name=body.bank_name,
            account_holder=body.account_holder,
            iban=body.iban,
            national_id=body.national_id,
            commercial_reg=body.commercial_reg,
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "VALIDATION_ERROR", "message": str(exc)},
        ) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail={
                "code": "DUPLICATE_VENDOR",
                "message": "البريد أو رقم الجوال مسجّل مسبقًا",
            },
        ) from exc

    return {"data": vendor_out(db, vendor)}


@router.get("/vendor/me")
def get_vendor_profile(
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db),
):
    return {"data": vendor_out(db, vendor)}


@router.put("/vendor/me/financials")
def update_vendor_profile_financials(
    body: VendorFinancialsUpdateIn,
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db),
):
    try:
        account = update_vendor_financials(
            db,
            vendor,
            bank_name=body.bank_name,
            account_holder=body.account_holder,
            iban=body.iban,
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "FINANCIALS_ERROR", "message": str(exc)},
        ) from exc

    data = vendor_out(db, vendor)
    data["bank_account"] = bank_account_out(account)
    return {"data": data}


@router.get("/vendor/me/payouts")
def get_vendor_payouts(
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db),
):
    try:
        legs = list_vendor_payouts(db, vendor)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "PAYOUTS_ERROR", "message": str(exc)},
        ) from exc

    data = [payout_leg_out(leg) for leg in legs]
    summary = vendor_out(db, vendor)["payout_summary"]
    return {"data": data, "meta": {"total": len(data), "summary": summary}}


@router.get("/admin/vendors")
def admin_list_vendors(
    status: str | None = Query(default=None),
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    query = select(Vendor).order_by(Vendor.created_at.desc())
    if status:
        query = query.where(Vendor.status == status)

    vendors = db.scalars(query).all()
    data = [vendor_out(db, v, include_summary=False) for v in vendors]
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/admin/vendors/{vendor_id}")
def admin_get_vendor(
    vendor_id: UUID,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    vendor = db.get(Vendor, vendor_id)
    if not vendor:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "طلب الفني غير موجود"},
        )
    return {"data": vendor_out(db, vendor)}


@router.post("/admin/vendors/{vendor_id}/approve")
def admin_approve_vendor(
    vendor_id: UUID,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    vendor = db.get(Vendor, vendor_id)
    if not vendor:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "طلب الفني غير موجود"},
        )

    try:
        approve_vendor(db, vendor)
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "APPROVE_ERROR", "message": str(exc)},
        ) from exc

    return {"data": vendor_out(db, vendor)}


@router.post("/admin/vendors/{vendor_id}/reject")
def admin_reject_vendor(
    vendor_id: UUID,
    body: VendorRejectIn,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    vendor = db.get(Vendor, vendor_id)
    if not vendor:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "طلب الفني غير موجود"},
        )

    try:
        reject_vendor(db, vendor, reason=body.reason)
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "REJECT_ERROR", "message": str(exc)},
        ) from exc

    return {"data": vendor_out(db, vendor)}
