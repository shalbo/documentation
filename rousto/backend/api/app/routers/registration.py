from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field, field_validator  # noqa: F401 used by validators
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_admin_key
from app.models import User
from app.city_services import list_cities
from app.registration_services import (
    approve_registration,
    attach_driver_documents,
    driver_profile_out,
    list_pending_approvals,
    register_customer,
    register_driver,
    register_vendor,
    register_workshop,
    reject_registration,
    vendor_profile_out,
    workshop_profile_out,
)

router = APIRouter(tags=["registration"])


class CustomerRegisterIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=10, max_length=20)
    city: str = Field(min_length=2, max_length=60)


class VendorRegisterIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=10, max_length=20)
    email: str = Field(min_length=5, max_length=255)
    shop_name: str = Field(min_length=2, max_length=120)
    specialty: str | None = Field(default=None, max_length=120)
    city: str = Field(min_length=2, max_length=60)
    latitude: float | None = None
    longitude: float | None = None

    @field_validator("email")
    @classmethod
    def _email_fmt(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("صيغة البريد غير صالحة")
        return v.lower()


class WorkshopRegisterIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=10, max_length=20)
    email: str = Field(min_length=5, max_length=255)
    center_name: str = Field(min_length=2, max_length=120)
    specialty: str | None = Field(default=None, max_length=120)
    city: str = Field(min_length=2, max_length=60)
    latitude: float | None = None
    longitude: float | None = None

    @field_validator("email")
    @classmethod
    def _email_fmt(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("صيغة البريد غير صالحة")
        return v.lower()


class DriverRegisterIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=10, max_length=20)
    city: str = Field(min_length=2, max_length=60)
    service_type: str = Field(pattern=r"^(courier|tow)$")
    plate_number: str = Field(min_length=3, max_length=20)


class RejectIn(BaseModel):
    reason: str = Field(min_length=5, max_length=500)


@router.get("/registration/cities")
def registration_cities(db: Session = Depends(get_db)):
    data = list_cities(db)
    return {"data": data, "meta": {"total": len(data)}}


@router.post("/registration/customer", status_code=201)
def post_register_customer(body: CustomerRegisterIn, db: Session = Depends(get_db)):
    try:
        user = register_customer(
            db,
            full_name=body.full_name,
            phone=body.phone,
            city=body.city,
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
            detail={"code": "DUPLICATE", "message": "البيانات مسجّلة مسبقاً"},
        ) from exc
    return {
        "data": {
            "user_id": str(user.id),
            "full_name": user.full_name,
            "phone": user.phone,
            "city": user.city,
            "role": "customer",
        },
        "meta": {"message": "تم التسجيل — يمكنك تسجيل الدخول برمز OTP"},
    }


@router.post("/registration/vendor", status_code=201)
def post_register_vendor(body: VendorRegisterIn, db: Session = Depends(get_db)):
    try:
        profile = register_vendor(db, **body.model_dump())
        user = db.get(User, profile.user_id)
        db.commit()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"code": "VALIDATION_ERROR", "message": str(exc)}) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail={"code": "DUPLICATE", "message": "البيانات مسجّلة مسبقاً"}) from exc
    return {"data": vendor_profile_out(profile, user)}


@router.post("/registration/workshop", status_code=201)
def post_register_workshop(body: WorkshopRegisterIn, db: Session = Depends(get_db)):
    try:
        profile = register_workshop(db, **body.model_dump())
        user = db.get(User, profile.user_id)
        db.commit()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"code": "VALIDATION_ERROR", "message": str(exc)}) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail={"code": "DUPLICATE", "message": "البيانات مسجّلة مسبقاً"}) from exc
    return {"data": workshop_profile_out(profile, user)}


@router.post("/registration/driver", status_code=201)
def post_register_driver(body: DriverRegisterIn, db: Session = Depends(get_db)):
    try:
        profile = register_driver(db, **body.model_dump())
        user = db.get(User, profile.user_id)
        db.commit()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"code": "VALIDATION_ERROR", "message": str(exc)}) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail={"code": "DUPLICATE", "message": "البيانات مسجّلة مسبقاً"}) from exc
    return {
        "data": driver_profile_out(profile, user),
        "meta": {"next_step": f"POST /registration/driver/{profile.id}/documents"},
    }


@router.post("/registration/driver/{profile_id}/documents")
async def post_driver_documents(
    profile_id: UUID,
    license_doc: UploadFile = File(...),
    id_doc: UploadFile = File(...),
    vehicle_doc: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        profile = await attach_driver_documents(
            db,
            profile_id,
            license_file=license_doc,
            id_file=id_doc,
            vehicle_file=vehicle_doc,
        )
        user = db.get(User, profile.user_id)
        db.commit()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"code": "VALIDATION_ERROR", "message": str(exc)}) from exc
    return {"data": driver_profile_out(profile, user)}


@router.get("/admin/registration/pending")
def admin_pending_registrations(
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    data = list_pending_approvals(db)
    return {"data": data, "meta": {"total": len(data)}}


@router.post("/admin/registration/{role}/{profile_id}/approve")
def admin_approve_registration(
    role: str,
    profile_id: UUID,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    if role not in ("vendor", "driver", "workshop"):
        raise HTTPException(status_code=400, detail={"code": "INVALID_ROLE", "message": "دور غير صالح"})
    try:
        data = approve_registration(db, role=role, profile_id=profile_id)
        db.commit()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"code": "APPROVE_ERROR", "message": str(exc)}) from exc
    return {"data": data}


@router.post("/admin/registration/{role}/{profile_id}/reject")
def admin_reject_registration(
    role: str,
    profile_id: UUID,
    body: RejectIn,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    if role not in ("vendor", "driver", "workshop"):
        raise HTTPException(status_code=400, detail={"code": "INVALID_ROLE", "message": "دور غير صالح"})
    try:
        data = reject_registration(db, role=role, profile_id=profile_id, reason=body.reason)
        db.commit()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"code": "REJECT_ERROR", "message": str(exc)}) from exc
    return {"data": data}
