from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api_responses import success
from app.db import get_db
from app.deps import get_current_principal, get_current_vendor
from app.models import Vendor
from app.permissions import AuthPrincipal
from app.vendor_staff_rbac import require_vendor_owner_or_manager
from app.vendor_staff_services import (
    create_vendor_staff,
    delete_vendor_staff,
    list_vendor_staff,
    staff_out,
    update_vendor_staff,
)

router = APIRouter(prefix="/vendor/staff", tags=["vendor-staff"])


class StaffCreateIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=10, max_length=20)
    password: str = Field(min_length=6, max_length=128)
    role: str = Field(pattern=r"^(manager|sales|accountant)$")


class StaffUpdateIn(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    phone: str | None = Field(default=None, min_length=10, max_length=20)
    password: str | None = Field(default=None, min_length=6, max_length=128)
    role: str | None = Field(default=None, pattern=r"^(manager|sales|accountant)$")
    is_active: bool | None = None


class StaffToggleIn(BaseModel):
    is_active: bool


@router.get("")
def get_vendor_staff_list(
    vendor: Vendor = Depends(get_current_vendor),
    _: AuthPrincipal = Depends(require_vendor_owner_or_manager),
    db: Session = Depends(get_db),
):
    data = list_vendor_staff(db, vendor.id)
    return success(data, meta={"total": len(data)})


@router.post("", status_code=201)
def post_vendor_staff(
    body: StaffCreateIn,
    vendor: Vendor = Depends(get_current_vendor),
    _: AuthPrincipal = Depends(require_vendor_owner_or_manager),
    db: Session = Depends(get_db),
):
    try:
        staff = create_vendor_staff(
            db,
            vendor,
            name=body.name,
            phone=body.phone,
            password=body.password,
            role=body.role,
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "STAFF_CREATE_ERROR", "message": str(exc)},
        ) from exc
    return success(staff_out(staff), message="تم إضافة الموظف")


@router.put("/{staff_id}")
def put_vendor_staff(
    staff_id: UUID,
    body: StaffUpdateIn,
    vendor: Vendor = Depends(get_current_vendor),
    principal: AuthPrincipal = Depends(require_vendor_owner_or_manager),
    db: Session = Depends(get_db),
):
    if principal.is_staff and principal.staff_id == staff_id:
        raise HTTPException(
            status_code=400,
            detail={"code": "SELF_EDIT", "message": "لا يمكنك تعديل حسابك من هنا"},
        )
    try:
        staff = update_vendor_staff(
            db,
            vendor.id,
            staff_id,
            name=body.name,
            phone=body.phone,
            password=body.password,
            role=body.role,
            is_active=body.is_active,
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "STAFF_UPDATE_ERROR", "message": str(exc)},
        ) from exc
    return success(staff_out(staff), message="تم تحديث الموظف")


@router.patch("/{staff_id}/active")
def patch_vendor_staff_active(
    staff_id: UUID,
    body: StaffToggleIn,
    vendor: Vendor = Depends(get_current_vendor),
    principal: AuthPrincipal = Depends(require_vendor_owner_or_manager),
    db: Session = Depends(get_db),
):
    if principal.is_staff and principal.staff_id == staff_id and not body.is_active:
        raise HTTPException(
            status_code=400,
            detail={"code": "SELF_DISABLE", "message": "لا يمكنك تعطيل حسابك"},
        )
    try:
        staff = update_vendor_staff(
            db,
            vendor.id,
            staff_id,
            is_active=body.is_active,
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "STAFF_TOGGLE_ERROR", "message": str(exc)},
        ) from exc
    msg = "تم تفعيل الموظف" if body.is_active else "تم تعطيل الموظف وسحب صلاحية الدخول"
    return success(staff_out(staff), message=msg)


@router.delete("/{staff_id}", status_code=200)
def delete_vendor_staff_row(
    staff_id: UUID,
    vendor: Vendor = Depends(get_current_vendor),
    principal: AuthPrincipal = Depends(require_vendor_owner_or_manager),
    db: Session = Depends(get_db),
):
    if principal.is_staff and principal.staff_id == staff_id:
        raise HTTPException(
            status_code=400,
            detail={"code": "SELF_DELETE", "message": "لا يمكنك حذف حسابك"},
        )
    try:
        delete_vendor_staff(db, vendor.id, staff_id)
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": str(exc)},
        ) from exc
    return success({"deleted": True, "id": str(staff_id)}, message="تم حذف الموظف")
