"""Vendor staff sub-accounts — CRUD, auth, token revocation."""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth_services import hash_password, verify_password
from app.models import AuthRefreshToken, Vendor, VendorStaff

STAFF_ROLES = frozenset({"manager", "sales", "accountant"})
PHONE_RE = re.compile(r"^\+(?:9665\d{8}|2189\d{8})$")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_staff_phone(phone: str) -> str:
    cleaned = phone.strip().replace(" ", "").replace("-", "")
    if cleaned.startswith("05") and len(cleaned) == 10:
        cleaned = "+966" + cleaned[1:]
    elif cleaned.startswith("09") and len(cleaned) == 10:
        cleaned = "+218" + cleaned[1:]
    elif cleaned.startswith("966") and not cleaned.startswith("+"):
        cleaned = "+" + cleaned
    elif cleaned.startswith("218") and not cleaned.startswith("+"):
        cleaned = "+" + cleaned
    if not PHONE_RE.match(cleaned):
        raise ValueError("صيغة الجوال غير صالحة")
    return cleaned


def staff_out(s: VendorStaff) -> dict:
    return {
        "id": str(s.id),
        "vendor_id": str(s.vendor_id),
        "name": s.name,
        "phone": s.phone,
        "role": s.role,
        "is_active": s.is_active,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
    }


def list_vendor_staff(db: Session, vendor_id: uuid.UUID) -> list[dict]:
    rows = db.scalars(
        select(VendorStaff)
        .where(VendorStaff.vendor_id == vendor_id)
        .order_by(VendorStaff.created_at.desc())
    ).all()
    return [staff_out(s) for s in rows]


def create_vendor_staff(
    db: Session,
    vendor: Vendor,
    *,
    name: str,
    phone: str,
    password: str,
    role: str,
) -> VendorStaff:
    if role not in STAFF_ROLES:
        raise ValueError("الدور غير صالح — manager أو sales أو accountant")
    if len(password) < 6:
        raise ValueError("كلمة المرور قصيرة (6 أحرف على الأقل)")
    normalized = normalize_staff_phone(phone)
    exists = db.scalar(
        select(VendorStaff).where(
            VendorStaff.vendor_id == vendor.id,
            VendorStaff.phone == normalized,
        )
    )
    if exists:
        raise ValueError("رقم الجوال مسجّل لموظف في هذا المحل")
    now = _now()
    staff = VendorStaff(
        id=uuid.uuid4(),
        vendor_id=vendor.id,
        name=name.strip(),
        phone=normalized,
        password_hash=hash_password(password),
        role=role,
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    db.add(staff)
    db.flush()
    return staff


def update_vendor_staff(
    db: Session,
    vendor_id: uuid.UUID,
    staff_id: uuid.UUID,
    *,
    name: str | None = None,
    phone: str | None = None,
    password: str | None = None,
    role: str | None = None,
    is_active: bool | None = None,
) -> VendorStaff:
    staff = db.get(VendorStaff, staff_id)
    if not staff or staff.vendor_id != vendor_id:
        raise ValueError("الموظف غير موجود")
    now = _now()
    if name is not None:
        staff.name = name.strip()
    if phone is not None:
        normalized = normalize_staff_phone(phone)
        clash = db.scalar(
            select(VendorStaff).where(
                VendorStaff.vendor_id == vendor_id,
                VendorStaff.phone == normalized,
                VendorStaff.id != staff_id,
            )
        )
        if clash:
            raise ValueError("رقم الجوال مستخدم لموظف آخر")
        staff.phone = normalized
    if password is not None:
        if len(password) < 6:
            raise ValueError("كلمة المرور قصيرة")
        staff.password_hash = hash_password(password)
    if role is not None:
        if role not in STAFF_ROLES:
            raise ValueError("الدور غير صالح")
        staff.role = role
    if is_active is not None and is_active != staff.is_active:
        staff.is_active = is_active
        if not is_active:
            revoke_staff_tokens(db, staff.id)
    staff.updated_at = now
    return staff


def delete_vendor_staff(db: Session, vendor_id: uuid.UUID, staff_id: uuid.UUID) -> None:
    staff = db.get(VendorStaff, staff_id)
    if not staff or staff.vendor_id != vendor_id:
        raise ValueError("الموظف غير موجود")
    revoke_staff_tokens(db, staff.id)
    db.delete(staff)


def revoke_staff_tokens(db: Session, staff_id: uuid.UUID) -> int:
    now = _now()
    tokens = db.scalars(
        select(AuthRefreshToken).where(
            AuthRefreshToken.vendor_staff_id == staff_id,
            AuthRefreshToken.revoked_at.is_(None),
        )
    ).all()
    for t in tokens:
        t.revoked_at = now
    return len(tokens)


def authenticate_vendor_staff(db: Session, phone: str, password: str) -> VendorStaff:
    normalized = normalize_staff_phone(phone)
    staff = db.scalar(select(VendorStaff).where(VendorStaff.phone == normalized))
    if not staff:
        raise ValueError("رقم الجوال أو كلمة المرور غير صحيحة")
    if not staff.is_active:
        raise ValueError("الحساب معطّل — تواصل مع صاحب المحل")
    if not verify_password(password, staff.password_hash):
        raise ValueError("رقم الجوال أو كلمة المرور غير صحيحة")
    return staff


def get_active_staff(db: Session, staff_id: uuid.UUID) -> VendorStaff:
    staff = db.get(VendorStaff, staff_id)
    if not staff or not staff.is_active:
        raise ValueError("الموظف غير نشط")
    return staff
