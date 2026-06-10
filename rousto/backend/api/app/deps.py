import uuid

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth_services import decode_access_token
from app.config import settings
from app.db import get_db
from app.rate_limit import check_rate_limit
from app.security_audit import audit_security_event
from app.models import User, UserVendorLink, Vendor, VendorStaff
from app.permissions import ROLE_ADMIN, AuthPrincipal, build_principal, build_staff_principal
from app.vendor_staff_services import get_active_staff


def _user_from_id(db: Session, user_id: str) -> User:
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_USER_ID", "message": "معرّف المستخدم غير صالح"},
        ) from exc

    user = db.get(User, user_uuid)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "المستخدم غير موجود أو غير نشط"},
        )
    return user


def _staff_from_token(db: Session, staff_id: str) -> VendorStaff:
    try:
        staff_uuid = uuid.UUID(staff_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_STAFF_ID", "message": "معرّف الموظف غير صالح"},
        ) from exc
    try:
        return get_active_staff(db, staff_uuid)
    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail={"code": "STAFF_INACTIVE", "message": str(exc)},
        ) from exc


def _verify_vendor_link(db: Session, user_id: uuid.UUID, vendor_id: uuid.UUID) -> Vendor:
    link = db.scalar(
        select(UserVendorLink).where(
            UserVendorLink.user_id == user_id,
            UserVendorLink.vendor_id == vendor_id,
        )
    )
    if not link:
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "لا تملك صلاحية الوصول لهذا الفني"},
        )
    vendor = db.get(Vendor, vendor_id)
    if not vendor:
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "الفني غير موجود"},
        )
    return vendor


def _vendor_for_staff(db: Session, staff: VendorStaff) -> Vendor:
    vendor = db.get(Vendor, staff.vendor_id)
    if not vendor:
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "المحل غير موجود"},
        )
    return vendor


def get_current_principal(
    request: Request,
    authorization: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    db: Session = Depends(get_db),
) -> AuthPrincipal:
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        try:
            payload = decode_access_token(token)
            if payload.get("actor_type") == "vendor_staff":
                staff = _staff_from_token(db, payload["sub"])
                principal = build_staff_principal(staff)
                if payload.get("vendor_id"):
                    principal.vendor_id = uuid.UUID(payload["vendor_id"])
                return principal
            user = _user_from_id(db, payload["sub"])
            principal = build_principal(db, user, auth_method="jwt")
            if payload.get("vendor_id") and not principal.vendor_id:
                principal.vendor_id = uuid.UUID(payload["vendor_id"])
            return principal
        except HTTPException:
            raise
        except ValueError as exc:
            audit_security_event(
                db,
                request,
                event_type="auth.invalid_token",
                severity="warn",
                metadata={"reason": str(exc)},
            )
            raise HTTPException(
                status_code=401,
                detail={"code": "INVALID_TOKEN", "message": str(exc)},
            ) from exc

    if x_user_id:
        if not settings.allow_legacy_headers:
            audit_security_event(
                db,
                request,
                event_type="auth.legacy_disabled",
                severity="warn",
                metadata={"header": "X-User-Id"},
            )
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "LEGACY_AUTH_DISABLED",
                    "message": "مطلوب Authorization Bearer في بيئة الإنتاج",
                },
            )
        user = _user_from_id(db, x_user_id)
        return build_principal(db, user, auth_method="legacy_header")

    raise HTTPException(
        status_code=401,
        detail={
            "code": "UNAUTHORIZED",
            "message": "مطلوب Authorization Bearer",
        },
    )


def get_current_user(
    principal: AuthPrincipal = Depends(get_current_principal),
) -> User:
    if principal.is_staff or not principal.user:
        raise HTTPException(
            status_code=403,
            detail={"code": "STAFF_ACCOUNT", "message": "حساب موظف — استخدم واجهة التاجر"},
        )
    return principal.user


def require_admin_key(
    request: Request,
    authorization: str | None = Header(default=None),
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
    db: Session = Depends(get_db),
) -> None:
    check_rate_limit(
        request,
        suffix="admin-api",
        limit=settings.admin_rate_limit_per_minute,
    )

    if x_admin_key and x_admin_key == settings.admin_api_key:
        return

    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        try:
            payload = decode_access_token(token)
            if payload.get("actor_type") == "vendor_staff":
                raise ValueError("staff not admin")
            if ROLE_ADMIN in payload.get("roles", []):
                user = _user_from_id(db, payload["sub"])
                principal = build_principal(db, user, auth_method="jwt")
                if principal.has_role(ROLE_ADMIN):
                    return
        except (ValueError, HTTPException):
            pass

    audit_security_event(
        db,
        request,
        event_type="auth.admin_key_failed",
        severity="critical",
    )
    raise HTTPException(
        status_code=401,
        detail={"code": "UNAUTHORIZED", "message": "مفتاح الإدارة أو JWT مدير غير صالح"},
    )


def require_permission(permission: str):
    def checker(
        authorization: str | None = Header(default=None),
        x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
        principal: AuthPrincipal = Depends(get_current_principal),
    ) -> AuthPrincipal:
        if x_admin_key and x_admin_key == settings.admin_api_key:
            return principal
        if authorization and authorization.lower().startswith("bearer "):
            token = authorization.split(" ", 1)[1].strip()
            try:
                payload = decode_access_token(token)
                if permission in payload.get("permissions", []):
                    return principal
                if ROLE_ADMIN in payload.get("roles", []):
                    return principal
            except ValueError:
                pass
        if principal.has_permission(permission):
            return principal
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": f"صلاحية {permission} مطلوبة"},
        )

    return checker


def get_current_vendor(
    request: Request,
    authorization: str | None = Header(default=None),
    x_vendor_id: str | None = Header(default=None, alias="X-Vendor-Id"),
    db: Session = Depends(get_db),
) -> Vendor:
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        try:
            payload = decode_access_token(token)
            if payload.get("actor_type") == "vendor_staff":
                staff = _staff_from_token(db, payload["sub"])
                return _vendor_for_staff(db, staff)
            user = _user_from_id(db, payload["sub"])
            vendor_claim = payload.get("vendor_id")
            if vendor_claim:
                return _verify_vendor_link(db, user.id, uuid.UUID(vendor_claim))
            principal = build_principal(db, user, auth_method="jwt")
            if principal.vendor_id:
                return _verify_vendor_link(db, user.id, principal.vendor_id)
        except HTTPException:
            raise
        except ValueError as exc:
            raise HTTPException(
                status_code=401,
                detail={"code": "INVALID_TOKEN", "message": str(exc)},
            ) from exc

    if x_vendor_id:
        if not settings.allow_legacy_headers:
            audit_security_event(
                db,
                request,
                event_type="auth.legacy_disabled",
                severity="warn",
                metadata={"header": "X-Vendor-Id"},
            )
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "LEGACY_AUTH_DISABLED",
                    "message": "مطلوب JWT فني في بيئة الإنتاج",
                },
            )
        try:
            vendor_uuid = uuid.UUID(x_vendor_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail={"code": "INVALID_VENDOR_ID", "message": "معرّف الفني غير صالح"},
            ) from exc

        vendor = db.get(Vendor, vendor_uuid)
        if not vendor:
            raise HTTPException(
                status_code=401,
                detail={"code": "UNAUTHORIZED", "message": "الفني غير موجود"},
            )
        return vendor

    raise HTTPException(
        status_code=401,
        detail={
            "code": "UNAUTHORIZED",
            "message": "مطلوب JWT فني",
        },
    )
