from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth_services import (
    assign_user_roles,
    create_otp_request,
    issue_tokens,
    refresh_access_token,
    revoke_refresh_token,
    verify_otp,
)
from app.config import settings
from app.db import get_db
from app.deps import get_current_principal, require_admin_key
from app.rate_limit import check_rate_limit
from app.security_audit import audit_security_event
from app.models import Permission, Role, User, UserRole
from app.permissions import ROLE_ADMIN, serialize_principal

router = APIRouter(tags=["auth"])


class OtpSendIn(BaseModel):
    phone: str = Field(min_length=8, max_length=20)


class OtpVerifyIn(BaseModel):
    phone: str = Field(min_length=8, max_length=20)
    code: str = Field(min_length=4, max_length=8)
    request_id: str | None = None


class RefreshIn(BaseModel):
    refresh_token: str = Field(min_length=10)


class LogoutIn(BaseModel):
    refresh_token: str = Field(min_length=10)


class AssignRolesIn(BaseModel):
    roles: list[str] = Field(min_length=1)


@router.post("/auth/otp/send")
def send_otp(body: OtpSendIn, request: Request, db: Session = Depends(get_db)):
    check_rate_limit(request, suffix=f"otp-send:{body.phone}")
    try:
        otp, code = create_otp_request(db, body.phone)
        db.commit()
        meta = {"expires_in_seconds": 300}
        if settings.otp_dev_mode and not settings.is_production:
            meta["dev_otp"] = code
        return {
            "data": {
                "request_id": str(otp.id),
                "phone": otp.phone,
                "message": "تم إرسال رمز التحقق",
            },
            "meta": meta,
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "OTP_SEND_FAILED", "message": str(exc)},
        ) from exc


@router.post("/auth/otp/verify")
def verify_otp_code(body: OtpVerifyIn, request: Request, db: Session = Depends(get_db)):
    check_rate_limit(request, suffix=f"otp-verify:{body.phone}")
    try:
        request_id = UUID(body.request_id) if body.request_id else None
        user = verify_otp(db, body.phone, body.code, request_id)
        tokens = issue_tokens(db, user)
        db.commit()
        return {"data": tokens}
    except ValueError as exc:
        db.rollback()
        audit_security_event(
            db,
            request,
            event_type="auth.otp_verify_failed",
            severity="warn",
            metadata={"phone": body.phone[-4:]},
        )
        raise HTTPException(
            status_code=400,
            detail={"code": "OTP_VERIFY_FAILED", "message": str(exc)},
        ) from exc


@router.post("/auth/refresh")
def refresh_token(body: RefreshIn, request: Request, db: Session = Depends(get_db)):
    check_rate_limit(request, suffix="auth-refresh")
    try:
        data = refresh_access_token(db, body.refresh_token)
        db.commit()
        return {"data": data}
    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail={"code": "REFRESH_FAILED", "message": str(exc)},
        ) from exc


@router.post("/auth/logout")
def logout(body: LogoutIn, db: Session = Depends(get_db)):
    revoke_refresh_token(db, body.refresh_token)
    db.commit()
    return {"data": {"logged_out": True}}


@router.get("/auth/me")
def auth_me(principal=Depends(get_current_principal)):
    return {"data": serialize_principal(principal)}


@router.get("/auth/permissions")
def list_permissions(
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    perms = db.scalars(select(Permission).order_by(Permission.slug)).all()
    data = [
        {
            "slug": p.slug,
            "name_ar": p.name_ar,
            "resource": p.resource,
            "action": p.action,
        }
        for p in perms
    ]
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/auth/roles")
def list_roles(db: Session = Depends(get_db)):
    roles = db.scalars(select(Role).order_by(Role.slug)).all()
    data = [
        {"slug": r.slug, "name_ar": r.name_ar, "description_ar": r.description_ar}
        for r in roles
    ]
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/admin/auth/users/{user_id}/roles")
def get_user_roles(
    user_id: UUID,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "المستخدم غير موجود"},
        )
    slugs = db.scalars(
        select(Role.slug)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user_id)
    ).all()
    return {"data": {"user_id": str(user_id), "roles": list(slugs)}}


@router.put("/admin/auth/users/{user_id}/roles")
def set_user_roles(
    user_id: UUID,
    body: AssignRolesIn,
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "المستخدم غير موجود"},
        )
    if ROLE_ADMIN in body.roles and len(body.roles) > 1:
        pass
    try:
        slugs = assign_user_roles(db, user_id, body.roles)
        db.commit()
        return {"data": {"user_id": str(user_id), "roles": slugs}}
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "ASSIGN_ROLES_FAILED", "message": str(exc)},
        ) from exc
