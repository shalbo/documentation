import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import AuthOtpRequest, AuthRefreshToken, User
from app.permissions import AuthPrincipal, build_principal

OTP_LENGTH = 6
OTP_TTL_MINUTES = 5
MAX_OTP_ATTEMPTS = 5
PASSWORD_SALT = b"rousto_auth_v1"


def _hash_value(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        PASSWORD_SALT,
        settings.password_pbkdf2_iterations,
    )
    return f"pbkdf2_sha256${settings.password_pbkdf2_iterations}${digest.hex()}"


def verify_password(password: str, stored_hash: str | None) -> bool:
    if not stored_hash:
        return False
    if stored_hash.startswith("pbkdf2_sha256$"):
        parts = stored_hash.split("$")
        if len(parts) != 3:
            return False
        try:
            iterations = int(parts[1])
        except ValueError:
            return False
        expected = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            PASSWORD_SALT,
            iterations,
        ).hex()
        return secrets.compare_digest(parts[2], expected)
    return secrets.compare_digest(_hash_value(password), stored_hash)


def authenticate_user(db: Session, phone: str, password: str) -> User:
    normalized = _normalize_phone(phone)
    user = db.scalar(
        select(User).where(User.phone == normalized, User.is_active.is_(True))
    )
    if not user:
        raise ValueError("رقم الجوال أو كلمة المرور غير صحيحة")
    if not verify_password(password, user.password_hash):
        raise ValueError("رقم الجوال أو كلمة المرور غير صحيحة")
    return user


def set_user_password(db: Session, user: User, password: str) -> None:
    if len(password) < 6:
        raise ValueError("كلمة المرور قصيرة جداً (6 أحرف على الأقل)")
    user.password_hash = hash_password(password)
    user.updated_at = datetime.now(timezone.utc)


def _normalize_phone(phone: str) -> str:
    cleaned = phone.strip().replace(" ", "")
    if cleaned.startswith("05") and len(cleaned) == 10:
        return "+966" + cleaned[1:]
    if cleaned.startswith("966") and not cleaned.startswith("+"):
        return "+" + cleaned
    return cleaned


def create_otp_request(db: Session, phone: str) -> tuple[AuthOtpRequest, str]:
    normalized = _normalize_phone(phone)
    user = db.scalar(select(User).where(User.phone == normalized, User.is_active.is_(True)))
    if not user:
        raise ValueError("رقم الجوال غير مسجّل")

    code = "".join(str(secrets.randbelow(10)) for _ in range(OTP_LENGTH))
    if settings.otp_dev_mode and not settings.is_production:
        code = settings.otp_dev_code

    now = datetime.now(timezone.utc)
    entry = AuthOtpRequest(
        id=uuid.uuid4(),
        phone=normalized,
        code_hash=_hash_value(code),
        expires_at=now + timedelta(minutes=OTP_TTL_MINUTES),
        created_at=now,
    )
    db.add(entry)
    db.flush()
    return entry, code


def verify_otp(db: Session, phone: str, code: str, request_id: uuid.UUID | None = None) -> User:
    normalized = _normalize_phone(phone)
    now = datetime.now(timezone.utc)

    stmt = (
        select(AuthOtpRequest)
        .where(
            AuthOtpRequest.phone == normalized,
            AuthOtpRequest.verified_at.is_(None),
            AuthOtpRequest.expires_at > now,
        )
        .order_by(AuthOtpRequest.created_at.desc())
        .limit(1)
    )
    if request_id:
        stmt = select(AuthOtpRequest).where(AuthOtpRequest.id == request_id)

    otp = db.scalar(stmt)
    if not otp or otp.expires_at <= now:
        raise ValueError("انتهت صلاحية الرمز أو الطلب غير موجود")

    if otp.attempts >= MAX_OTP_ATTEMPTS:
        raise ValueError("تجاوزت عدد المحاولات المسموح")

    otp.attempts += 1
    if _hash_value(code.strip()) != otp.code_hash:
        db.flush()
        raise ValueError("رمز التحقق غير صحيح")

    otp.verified_at = now
    user = db.scalar(select(User).where(User.phone == normalized, User.is_active.is_(True)))
    if not user:
        raise ValueError("المستخدم غير موجود")
    return user


def _jwt_payload(principal: AuthPrincipal, token_type: str, expires_delta: timedelta) -> dict:
    now = datetime.now(timezone.utc)
    exp = now + expires_delta
    return {
        "sub": str(principal.user.id),
        "type": token_type,
        "roles": principal.roles,
        "permissions": principal.permissions,
        "vendor_id": str(principal.vendor_id) if principal.vendor_id else None,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }


def issue_tokens(db: Session, user: User) -> dict:
    principal = build_principal(db, user)
    access = jwt.encode(
        _jwt_payload(principal, "access", timedelta(minutes=settings.jwt_access_minutes)),
        settings.jwt_secret,
        algorithm="HS256",
    )
    refresh_raw = secrets.token_urlsafe(48)
    refresh_exp = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_days)
    db.add(
        AuthRefreshToken(
            id=uuid.uuid4(),
            user_id=user.id,
            token_hash=_hash_value(refresh_raw),
            expires_at=refresh_exp,
            created_at=datetime.now(timezone.utc),
        )
    )
    db.flush()
    return {
        "access_token": access,
        "refresh_token": refresh_raw,
        "token_type": "bearer",
        "expires_in": settings.jwt_access_minutes * 60,
        "principal": serialize_tokens_principal(principal),
    }


def serialize_tokens_principal(principal: AuthPrincipal) -> dict:
    from app.permissions import serialize_principal

    return serialize_principal(principal)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise ValueError("رمز الدخول غير صالح") from exc
    if payload.get("type") != "access":
        raise ValueError("نوع الرمز غير صالح")
    return payload


def refresh_access_token(db: Session, refresh_token: str) -> dict:
    token_hash = _hash_value(refresh_token)
    now = datetime.now(timezone.utc)
    stored = db.scalar(
        select(AuthRefreshToken).where(
            AuthRefreshToken.token_hash == token_hash,
            AuthRefreshToken.revoked_at.is_(None),
            AuthRefreshToken.expires_at > now,
        )
    )
    if not stored:
        raise ValueError("رمز التجديد غير صالح")

    user = db.get(User, stored.user_id)
    if not user or not user.is_active:
        raise ValueError("المستخدم غير نشط")

    principal = build_principal(db, user)
    access = jwt.encode(
        _jwt_payload(principal, "access", timedelta(minutes=settings.jwt_access_minutes)),
        settings.jwt_secret,
        algorithm="HS256",
    )
    return {
        "access_token": access,
        "token_type": "bearer",
        "expires_in": settings.jwt_access_minutes * 60,
        "principal": serialize_tokens_principal(principal),
    }


def revoke_refresh_token(db: Session, refresh_token: str) -> None:
    token_hash = _hash_value(refresh_token)
    stored = db.scalar(select(AuthRefreshToken).where(AuthRefreshToken.token_hash == token_hash))
    if stored and stored.revoked_at is None:
        stored.revoked_at = datetime.now(timezone.utc)


def assign_user_roles(db: Session, user_id: uuid.UUID, role_slugs: list[str]) -> list[str]:
    from app.models import Role, UserRole

    roles = db.scalars(select(Role).where(Role.slug.in_(role_slugs))).all()
    if len(roles) != len(set(role_slugs)):
        raise ValueError("دور غير موجود")

    existing = db.scalars(select(UserRole).where(UserRole.user_id == user_id)).all()
    for row in existing:
        db.delete(row)
    db.flush()

    for role in roles:
        db.add(
            UserRole(
                user_id=user_id,
                role_id=role.id,
                granted_by="admin_api",
                granted_at=datetime.now(timezone.utc),
            )
        )
    db.flush()
    return [r.slug for r in roles]
