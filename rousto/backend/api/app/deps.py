import uuid

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import User, Vendor


def get_current_user(
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    db: Session = Depends(get_db),
) -> User:
    if not x_user_id:
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "مطلوب هيدر X-User-Id"},
        )
    try:
        user_uuid = uuid.UUID(x_user_id)
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


def require_admin_key(
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
) -> None:
    if not x_admin_key or x_admin_key != settings.admin_api_key:
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "مفتاح الإدارة غير صالح"},
        )


def get_current_vendor(
    x_vendor_id: str | None = Header(default=None, alias="X-Vendor-Id"),
    db: Session = Depends(get_db),
) -> Vendor:
    if not x_vendor_id:
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "مطلوب هيدر X-Vendor-Id"},
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
