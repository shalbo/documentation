from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User
from app.registration_services import (
    attach_driver_documents,
    driver_profile_out,
    get_driver_registration_payment_status,
    initiate_driver_registration_payment,
    register_driver,
)

router = APIRouter(tags=["driver-registration-auth"])


class DriverPaymentInitIn(BaseModel):
    profile_id: UUID
    phone: str = Field(min_length=10, max_length=20)
    gateway: str = Field(pattern=r"^(muamalat|sadad)$")
    return_url: str = Field(default="rousto://payment/return", max_length=500)


@router.post("/auth/register/driver", status_code=201)
async def auth_register_driver(
    full_name: str = Form(..., min_length=2, max_length=120),
    phone: str = Form(..., min_length=10, max_length=20),
    city: str = Form(..., min_length=2, max_length=60),
    service_type: str = Form(..., pattern=r"^(courier|tow)$"),
    plate_number: str = Form(..., min_length=3, max_length=20),
    vehicle_type: str | None = Form(default=None, pattern=r"^(tow_truck|flatbed)$"),
    license_doc: UploadFile = File(...),
    id_doc: UploadFile = File(...),
    vehicle_doc: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """تسجيل سائق مع البيانات والوثائق — is_verified=false ورسوم unpaid لسائقي الساحبات."""
    try:
        profile = register_driver(
            db,
            full_name=full_name,
            phone=phone,
            city=city,
            service_type=service_type,
            plate_number=plate_number,
            vehicle_type=vehicle_type,
        )
        profile = await attach_driver_documents(
            db,
            profile.id,
            license_file=license_doc,
            id_file=id_doc,
            vehicle_file=vehicle_doc,
        )
        user = db.get(User, profile.user_id)
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail={"code": "VALIDATION_ERROR", "message": str(exc)},
        ) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail={"code": "DUPLICATE", "message": "البيانات مسجّلة مسبقاً"},
        ) from exc

    data = driver_profile_out(profile, user)  # type: ignore[arg-type]
    next_step = (
        "POST /auth/register/driver/initiate-payment"
        if service_type == "tow"
        else "بانتظار اعتماد الإدارة"
    )
    return {
        "data": data,
        "meta": {
            "next_step": next_step,
            "payment_required": service_type == "tow",
        },
    }


@router.post("/auth/register/driver/initiate-payment")
def auth_initiate_driver_payment(body: DriverPaymentInitIn, db: Session = Depends(get_db)):
    """توليد رابط الدفع لرسوم تفعيل حساب سائق الساحبة."""
    try:
        result = initiate_driver_registration_payment(
            db,
            profile_id=body.profile_id,
            phone=body.phone,
            gateway=body.gateway,
            return_url=body.return_url,
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail={"code": "PAYMENT_INIT_ERROR", "message": str(exc)},
        ) from exc
    return {"data": result}


@router.get("/auth/register/driver/{profile_id}/payment-status")
def auth_driver_payment_status(
    profile_id: UUID,
    phone: str = Query(..., min_length=10, max_length=20),
    db: Session = Depends(get_db),
):
    """التحقق من حالة سداد رسوم التسجيل (للاستطلاع بعد WebView)."""
    try:
        data = get_driver_registration_payment_status(
            db,
            profile_id=profile_id,
            phone=phone,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "STATUS_ERROR", "message": str(exc)},
        ) from exc
    return {"data": data}
