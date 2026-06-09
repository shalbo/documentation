import uuid

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.auth_services import decode_access_token
from app.config import settings
from app.db import get_db
from app.models import User, Vendor
from app.permissions import ROLE_ADMIN, AuthPrincipal, build_principal


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


def get_current_principal(
    authorization: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    db: Session = Depends(get_db),
) -> AuthPrincipal:
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        try:
            payload = decode_access_token(token)
            user = _user_from_id(db, payload["sub"])
            principal = build_principal(db, user, auth_method="jwt")
            if payload.get("vendor_id") and not principal.vendor_id:
                principal.vendor_id = uuid.UUID(payload["vendor_id"])
            return principal
        except ValueError as exc:
            raise HTTPException(
                status_code=401,
                detail={"code": "INVALID_TOKEN", "message": str(exc)},
            ) from exc

    if x_user_id:
        user = _user_from_id(db, x_user_id)
        return build_principal(db, user, auth_method="legacy_header")

    raise HTTPException(
        status_code=401,
        detail={
            "code": "UNAUTHORIZED",
            "message": "مطلوب Authorization Bearer أو هيدر X-User-Id",
        },
    )


def get_current_user(
    principal: AuthPrincipal = Depends(get_current_principal),
) -> User:
    return principal.user


def require_admin_key(
    authorization: str | None = Header(default=None),
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
    db: Session = Depends(get_db),
) -> None:
    if x_admin_key and x_admin_key == settings.admin_api_key:
        return

    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        try:
            payload = decode_access_token(token)
            if ROLE_ADMIN in payload.get("roles", []):
                return
        except ValueError:
            pass

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
    authorization: str | None = Header(default=None),
    x_vendor_id: str | None = Header(default=None, alias="X-Vendor-Id"),
    db: Session = Depends(get_db),
) -> Vendor:
    if x_vendor_id:
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

    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        try:
            payload = decode_access_token(token)
            vendor_claim = payload.get("vendor_id")
            if vendor_claim:
                vendor = db.get(Vendor, uuid.UUID(vendor_claim))
                if vendor:
                    return vendor
        except ValueError:
            pass

    raise HTTPException(
        status_code=401,
        detail={
            "code": "UNAUTHORIZED",
            "message": "مطلوب JWT فني أو هيدر X-Vendor-Id",
        },
    )
