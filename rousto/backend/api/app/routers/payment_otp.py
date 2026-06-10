from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api_responses import success
from app.db import get_db
from app.deps import get_current_user
from app.models import User
from app.payment_otp_services import (
    generate_payment_otp,
    generate_payment_otp_for_profile,
    verify_payment_otp_and_execute,
    verify_payment_otp_for_profile,
)
from app.rate_limit import check_rate_limit

router = APIRouter(tags=["payment-otp"])


class PaymentOtpGenerateIn(BaseModel):
    order_id: UUID
    amount_lyd: float | None = Field(default=None, gt=0, le=500000)


class PaymentOtpVerifyIn(BaseModel):
    order_id: UUID
    code: str = Field(min_length=4, max_length=6)


class PaymentOtpGeneratePublicIn(BaseModel):
    order_id: UUID
    phone: str = Field(min_length=10, max_length=20)
    amount_lyd: float | None = Field(default=None, gt=0, le=500000)


class PaymentOtpVerifyPublicIn(BaseModel):
    order_id: UUID
    phone: str = Field(min_length=10, max_length=20)
    code: str = Field(min_length=4, max_length=6)


@router.post("/payments/otp/generate")
def post_payment_otp_generate(
    body: PaymentOtpGenerateIn,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_rate_limit(request, suffix=f"pay-otp-gen:{user.id}")
    try:
        data = generate_payment_otp(
            db,
            user,
            order_id=body.order_id,
            amount_lyd=body.amount_lyd,
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail={"code": "OTP_GENERATE_FAILED", "message": str(exc)},
        ) from exc
    return success(data, message=data.pop("message", "تم إرسال الرمز"))


@router.post("/payments/otp/verify")
def post_payment_otp_verify(
    body: PaymentOtpVerifyIn,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_rate_limit(request, suffix=f"pay-otp-verify:{user.id}")
    try:
        data = verify_payment_otp_and_execute(
            db,
            user,
            order_id=body.order_id,
            code=body.code,
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail={"code": "OTP_VERIFY_FAILED", "message": str(exc)},
        ) from exc
    return success(data, message="تمت العملية بنجاح")


@router.post("/payments/otp/generate-registration")
def post_payment_otp_generate_registration(
    body: PaymentOtpGeneratePublicIn,
    request: Request,
    db: Session = Depends(get_db),
):
    """توليد OTP مالي لتسجيل الساحبة (بدون JWT — يُتحقق بالجوال)."""
    check_rate_limit(request, suffix=f"pay-otp-gen-reg:{body.phone[-4:]}")
    try:
        data = generate_payment_otp_for_profile(
            db,
            intent_id=body.order_id,
            phone=body.phone,
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail={"code": "OTP_GENERATE_FAILED", "message": str(exc)},
        ) from exc
    return success(data, message=data.pop("message", "تم إرسال الرمز"))


@router.post("/payments/otp/verify-registration")
def post_payment_otp_verify_registration(
    body: PaymentOtpVerifyPublicIn,
    request: Request,
    db: Session = Depends(get_db),
):
    check_rate_limit(request, suffix=f"pay-otp-verify-reg:{body.phone[-4:]}")
    try:
        data = verify_payment_otp_for_profile(
            db,
            intent_id=body.order_id,
            phone=body.phone,
            code=body.code,
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail={"code": "OTP_VERIFY_FAILED", "message": str(exc)},
        ) from exc
    return success(data, message="تمت العملية بنجاح")
