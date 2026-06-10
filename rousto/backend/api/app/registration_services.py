"""Multi-role registration: customer, vendor, driver, workshop."""

import mimetypes
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.city_services import validate_city_name
from app.config import settings
from app.models import (
    DriverProfile,
    GatewayPayment,
    Role,
    Technician,
    User,
    UserRole,
    UserVendorLink,
    Vendor,
    VendorProfile,
    WorkshopProfile,
)

PHONE_RE = re.compile(r"^\+(?:9665\d{8}|2189\d{8})$")
PLATE_RE = re.compile(r"^[A-Za-z0-9\u0600-\u06FF\-]{3,20}$")
ALLOWED_DOC_MIME = {"image/jpeg", "image/png", "image/webp"}
DRIVER_REGISTRATION_FEE_ORDER_TYPE = "driver_registration_fee"
DRIVER_PAYMENT_GATEWAYS = frozenset({"muamalat", "sadad"})


def normalize_phone(phone: str) -> str:
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
        raise ValueError("صيغة الجوال غير صالحة — استخدم +9665XXXXXXXX أو +2189XXXXXXXX")
    return cleaned


def _initials(name: str) -> str:
    return name.strip()[:1] or "?"


def _assign_role(db: Session, user_id: uuid.UUID, role_slug: str) -> None:
    role = db.scalar(select(Role).where(Role.slug == role_slug))
    if not role:
        raise ValueError(f"الدور {role_slug} غير موجود")
    exists = db.scalar(
        select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role.id)
    )
    if not exists:
        db.add(
            UserRole(
                user_id=user_id,
                role_id=role.id,
                granted_at=datetime.now(timezone.utc),
                granted_by="registration",
            )
        )


def _create_user(
    db: Session,
    *,
    full_name: str,
    phone: str,
    city: str,
    email: str | None = None,
) -> User:
    normalized = normalize_phone(phone)
    if db.scalar(select(User).where(User.phone == normalized)):
        raise ValueError("رقم الجوال مسجّل مسبقاً")
    email_val = (email or f"{normalized.replace('+', '')}@rousto.app").lower()
    if db.scalar(select(User).where(User.email == email_val)):
        raise ValueError("البريد الإلكتروني مسجّل مسبقاً")
    now = datetime.now(timezone.utc)
    user = User(
        id=uuid.uuid4(),
        full_name=full_name.strip(),
        email=email_val,
        phone=normalized,
        avatar_initials=_initials(full_name),
        city=city.strip(),
        loyalty_points=0,
        locale="ar",
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    db.add(user)
    db.flush()
    return user


def register_customer(
    db: Session,
    *,
    full_name: str,
    phone: str,
    city: str,
) -> User:
    city_row = validate_city_name(db, city)
    user = _create_user(db, full_name=full_name, phone=phone, city=city_row.name_ar)
    user.city_id = city_row.id
    _assign_role(db, user.id, "customer")
    return user


def register_vendor(
    db: Session,
    *,
    full_name: str,
    phone: str,
    email: str,
    shop_name: str,
    specialty: str | None,
    city: str,
    latitude: float | None,
    longitude: float | None,
) -> VendorProfile:
    city_row = validate_city_name(db, city)
    if not shop_name.strip():
        raise ValueError("اسم المحل مطلوب")
    user = _create_user(
        db, full_name=full_name, phone=phone, city=city_row.name_ar, email=email
    )
    user.city_id = city_row.id
    _assign_role(db, user.id, "vendor")
    from app.tier_services import get_default_tier

    default_tier = get_default_tier(db)
    now = datetime.now(timezone.utc)
    profile = VendorProfile(
        id=uuid.uuid4(),
        user_id=user.id,
        shop_name=shop_name.strip(),
        specialty=(specialty or "").strip() or None,
        city=city_row.name_ar,
        city_id=city_row.id,
        latitude=latitude,
        longitude=longitude,
        tier_id=default_tier.id if default_tier else None,
        verification_status="pending",
        is_approved=False,
        created_at=now,
        updated_at=now,
    )
    db.add(profile)
    db.flush()
    return profile


def register_workshop(
    db: Session,
    *,
    full_name: str,
    phone: str,
    email: str,
    center_name: str,
    specialty: str | None,
    city: str,
    latitude: float | None,
    longitude: float | None,
) -> WorkshopProfile:
    city_row = validate_city_name(db, city)
    user = _create_user(
        db, full_name=full_name, phone=phone, city=city_row.name_ar, email=email
    )
    user.city_id = city_row.id
    _assign_role(db, user.id, "workshop")
    now = datetime.now(timezone.utc)
    profile = WorkshopProfile(
        id=uuid.uuid4(),
        user_id=user.id,
        center_name=center_name.strip(),
        specialty=(specialty or "").strip() or None,
        city=city_row.name_ar,
        city_id=city_row.id,
        latitude=latitude,
        longitude=longitude,
        verification_status="pending",
        is_approved=False,
        created_at=now,
        updated_at=now,
    )
    db.add(profile)
    db.flush()
    return profile


def register_driver(
    db: Session,
    *,
    full_name: str,
    phone: str,
    city: str,
    service_type: str,
    plate_number: str,
) -> DriverProfile:
    city_row = validate_city_name(db, city)
    if service_type not in ("courier", "tow"):
        raise ValueError("نوع الخدمة: courier (قطع غيار) أو tow (ساحبة)")
    plate = plate_number.strip().upper()
    if not PLATE_RE.match(plate):
        raise ValueError("رقم اللوحة غير صالح")
    user = _create_user(db, full_name=full_name, phone=phone, city=city_row.name_ar)
    user.city_id = city_row.id
    _assign_role(db, user.id, "driver")
    now = datetime.now(timezone.utc)
    fee_status = "unpaid" if service_type == "tow" else "waived"
    profile = DriverProfile(
        id=uuid.uuid4(),
        user_id=user.id,
        service_type=service_type,
        plate_number=plate,
        city=city_row.name_ar,
        city_id=city_row.id,
        is_approved=False,
        verification_status="pending",
        registration_fee_status=fee_status,
        created_at=now,
        updated_at=now,
    )
    db.add(profile)
    db.flush()
    return profile


def _storage_root() -> Path:
    root = Path(settings.scan_storage_path) / "registrations"
    root.mkdir(parents=True, exist_ok=True)
    return root


async def save_driver_document(
    profile: DriverProfile,
    field: str,
    upload: UploadFile,
) -> str:
    if field not in ("license", "id", "vehicle"):
        raise ValueError("نوع المستند غير صالح")
    mime = upload.content_type or mimetypes.guess_type(upload.filename or "")[0]
    if mime not in ALLOWED_DOC_MIME:
        raise ValueError("ارفع صورة JPEG أو PNG أو WebP فقط")
    content = await upload.read()
    if not content:
        raise ValueError("الملف فارغ")
    if len(content) > settings.max_upload_bytes:
        raise ValueError("حجم الملف يتجاوز الحد المسموح")
    ext = ".jpg" if mime == "image/jpeg" else ".png" if mime == "image/png" else ".webp"
    rel = f"registrations/{profile.id}/{field}{ext}"
    dest = Path(settings.scan_storage_path) / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content)
    return rel


async def attach_driver_documents(
    db: Session,
    profile_id: uuid.UUID,
    *,
    license_file: UploadFile | None,
    id_file: UploadFile | None,
    vehicle_file: UploadFile | None,
) -> DriverProfile:
    profile = db.get(DriverProfile, profile_id)
    if not profile:
        raise ValueError("طلب السائق غير موجود")
    if not license_file or not id_file or not vehicle_file:
        raise ValueError("رفع الرخصة والهوية وصورة السيارة إلزامي")
    profile.license_doc_path = await save_driver_document(profile, "license", license_file)
    profile.id_doc_path = await save_driver_document(profile, "id", id_file)
    profile.vehicle_doc_path = await save_driver_document(profile, "vehicle", vehicle_file)
    profile.updated_at = datetime.now(timezone.utc)
    return profile


def _profile_user_out(user: User) -> dict:
    return {
        "id": str(user.id),
        "full_name": user.full_name,
        "phone": user.phone,
        "email": user.email,
        "city": user.city,
    }


def vendor_profile_out(p: VendorProfile, user: User) -> dict:
    return {
        "id": str(p.id),
        "role": "vendor",
        "user": _profile_user_out(user),
        "shop_name": p.shop_name,
        "specialty": p.specialty,
        "city": p.city,
        "latitude": float(p.latitude) if p.latitude is not None else None,
        "longitude": float(p.longitude) if p.longitude is not None else None,
        "is_approved": p.is_approved,
        "verification_status": p.verification_status,
    }


def driver_profile_out(p: DriverProfile, user: User) -> dict:
    return {
        "id": str(p.id),
        "role": "driver",
        "user": _profile_user_out(user),
        "service_type": p.service_type,
        "plate_number": p.plate_number,
        "city": p.city,
        "license_doc_path": p.license_doc_path,
        "id_doc_path": p.id_doc_path,
        "vehicle_doc_path": p.vehicle_doc_path,
        "is_approved": p.is_approved,
        "is_verified": p.is_approved,
        "verification_status": p.verification_status,
        "registration_fee_status": p.registration_fee_status,
        "payment_reference_id": str(p.payment_reference_id) if p.payment_reference_id else None,
        "registration_fee_gateway": p.registration_fee_gateway,
        "registration_fee_lyd": (
            float(settings.driver_registration_fee_lyd) if p.service_type == "tow" else 0.0
        ),
    }


def _load_driver_profile_for_phone(
    db: Session,
    profile_id: uuid.UUID,
    phone: str,
) -> tuple[DriverProfile, User]:
    profile = db.get(DriverProfile, profile_id)
    if not profile:
        raise ValueError("طلب السائق غير موجود")
    user = db.get(User, profile.user_id)
    if not user:
        raise ValueError("المستخدم غير موجود")
    if normalize_phone(phone) != user.phone:
        raise ValueError("رقم الجوال لا يطابق طلب التسجيل")
    return profile, user


def driver_registration_fee_info(profile: DriverProfile) -> dict:
    return {
        "profile_id": str(profile.id),
        "service_type": profile.service_type,
        "registration_fee_status": profile.registration_fee_status,
        "registration_fee_lyd": (
            float(settings.driver_registration_fee_lyd) if profile.service_type == "tow" else 0.0
        ),
        "payment_required": profile.service_type == "tow",
        "payment_reference_id": (
            str(profile.payment_reference_id) if profile.payment_reference_id else None
        ),
        "registration_fee_gateway": profile.registration_fee_gateway,
        "is_verified": profile.is_approved,
    }


def get_driver_registration_payment_status(
    db: Session,
    *,
    profile_id: uuid.UUID,
    phone: str,
) -> dict:
    profile, _user = _load_driver_profile_for_phone(db, profile_id, phone)
    payment_status = None
    if profile.payment_reference_id:
        gp = db.get(GatewayPayment, profile.payment_reference_id)
        if gp:
            payment_status = gp.status
    return {
        **driver_registration_fee_info(profile),
        "gateway_payment_status": payment_status,
        "documents_complete": bool(
            profile.license_doc_path and profile.id_doc_path and profile.vehicle_doc_path
        ),
    }


def initiate_driver_registration_payment(
    db: Session,
    *,
    profile_id: uuid.UUID,
    phone: str,
    gateway: str,
    return_url: str,
) -> dict:
    profile, user = _load_driver_profile_for_phone(db, profile_id, phone)
    if profile.service_type != "tow":
        raise ValueError("رسوم التفعيل مطلوبة لسائقي الساحبات فقط")
    if not (profile.license_doc_path and profile.id_doc_path and profile.vehicle_doc_path):
        raise ValueError("أكمل رفع المستندات قبل الدفع")
    if profile.registration_fee_status == "paid":
        return {
            "already_paid": True,
            **driver_registration_fee_info(profile),
        }

    slug = gateway.strip().lower()
    if slug not in DRIVER_PAYMENT_GATEWAYS:
        raise ValueError("اختر بوابة معاملات أو سداد")

    if profile.payment_reference_id:
        existing = db.get(GatewayPayment, profile.payment_reference_id)
        if existing and existing.status == "pending" and existing.redirect_url:
            return {
                "already_paid": False,
                "payment_id": str(existing.id),
                "gateway": existing.gateway,
                "status": existing.status,
                "amount_lyd": float(existing.amount_lyd),
                "gateway_ref": existing.gateway_ref,
                "redirect_url": existing.redirect_url,
                "requires_webview": True,
                "profile_id": str(profile.id),
            }

    from app.service_layer.payments.checkout_service import initiate_checkout

    amount = float(settings.driver_registration_fee_lyd)
    result = initiate_checkout(
        db,
        user,
        amount_lyd=amount,
        gateway=slug,
        order_type=DRIVER_REGISTRATION_FEE_ORDER_TYPE,
        order_id=profile.id,
        return_url=return_url,
    )
    gp = db.get(GatewayPayment, result["payment_id"])
    if gp:
        profile.payment_reference_id = gp.id
        profile.registration_fee_gateway = slug
        profile.updated_at = datetime.now(timezone.utc)
    return {
        "already_paid": False,
        "profile_id": str(profile.id),
        **result,
    }


def complete_driver_registration_payment(
    db: Session,
    profile_id: uuid.UUID,
    payment: GatewayPayment,
) -> DriverProfile | None:
    profile = db.get(DriverProfile, profile_id)
    if not profile:
        return None
    if profile.registration_fee_status == "paid":
        return profile

    profile.registration_fee_status = "paid"
    profile.payment_reference_id = payment.id
    profile.registration_fee_gateway = payment.gateway
    profile.updated_at = datetime.now(timezone.utc)

    user = db.get(User, profile.user_id)
    if user:
        _notify_admins_driver_fee_paid(db, profile, user, payment.gateway)
    return profile


def _notify_admins_driver_fee_paid(
    db: Session,
    profile: DriverProfile,
    user: User,
    gateway: str,
) -> None:
    from app.notification_engine_services import engine_dispatch

    admin_role = db.scalar(select(Role).where(Role.slug == "admin"))
    if not admin_role:
        return

    admin_ids = db.scalars(
        select(UserRole.user_id).where(UserRole.role_id == admin_role.id)
    ).all()
    gateway_label = "معاملات" if gateway == "muamalat" else "سداد" if gateway == "sadad" else gateway
    title = "سائق ساحبة سدّد رسوم التفعيل"
    body = (
        f"{user.full_name} ({user.phone}) سدّد رسوم التسجيل عبر {gateway_label} "
        f"— بانتظار مراجعة الأوراق"
    )
    for admin_user_id in admin_ids:
        try:
            engine_dispatch(
                db,
                admin_user_id,
                event_source="driver_registration_fee",
                category="system",
                title=title,
                body=body,
                send_push=False,
                data={
                    "profile_id": str(profile.id),
                    "driver_phone": user.phone,
                    "gateway": gateway,
                },
            )
        except Exception:
            pass


def workshop_profile_out(p: WorkshopProfile, user: User) -> dict:
    return {
        "id": str(p.id),
        "role": "workshop",
        "user": _profile_user_out(user),
        "center_name": p.center_name,
        "specialty": p.specialty,
        "city": p.city,
        "latitude": float(p.latitude) if p.latitude is not None else None,
        "longitude": float(p.longitude) if p.longitude is not None else None,
        "is_approved": p.is_approved,
        "verification_status": p.verification_status,
    }


def list_pending_approvals(db: Session) -> list[dict]:
    out: list[dict] = []
    for p in db.scalars(
        select(VendorProfile).where(
            VendorProfile.is_approved.is_(False),
            VendorProfile.verification_status == "pending",
        )
    ).all():
        user = db.get(User, p.user_id)
        if user:
            out.append(vendor_profile_out(p, user))
    for p in db.scalars(
        select(DriverProfile).where(
            DriverProfile.is_approved.is_(False),
            DriverProfile.verification_status == "pending",
        )
    ).all():
        user = db.get(User, p.user_id)
        if user:
            out.append(driver_profile_out(p, user))
    for p in db.scalars(
        select(WorkshopProfile).where(
            WorkshopProfile.is_approved.is_(False),
            WorkshopProfile.verification_status == "pending",
        )
    ).all():
        user = db.get(User, p.user_id)
        if user:
            out.append(workshop_profile_out(p, user))
    return out


def approve_registration(
    db: Session,
    *,
    role: str,
    profile_id: uuid.UUID,
    approved_by: str = "admin",
) -> dict:
    now = datetime.now(timezone.utc)
    if role == "vendor":
        p = db.get(VendorProfile, profile_id)
        if not p:
            raise ValueError("طلب التاجر غير موجود")
        user = db.get(User, p.user_id)
        vendor = Vendor(
            id=uuid.uuid4(),
            business_name=p.shop_name,
            contact_name=user.full_name if user else "",
            email=user.email if user else f"v{p.id}@rousto.app",
            phone=user.phone if user else "",
            city=p.city,
            city_id=str(p.city_id) if p.city_id else None,
            status="approved",
            base_lat=p.latitude,
            base_lng=p.longitude,
            approved_at=now,
            approved_by=approved_by,
            created_at=now,
            updated_at=now,
        )
        db.add(vendor)
        db.flush()
        p.vendor_id = vendor.id
        p.is_approved = True
        p.verification_status = "approved"
        p.updated_at = now
        if user:
            db.add(
                UserVendorLink(
                    user_id=user.id,
                    vendor_id=vendor.id,
                    linked_at=now,
                )
            )
        return vendor_profile_out(p, user)  # type: ignore[arg-type]

    if role == "driver":
        p = db.get(DriverProfile, profile_id)
        if not p:
            raise ValueError("طلب السائق غير موجود")
        if not (p.license_doc_path and p.id_doc_path and p.vehicle_doc_path):
            raise ValueError("المستندات غير مكتملة")
        if p.service_type == "tow" and p.registration_fee_status != "paid":
            raise ValueError("يجب سداد رسوم التفعيل قبل اعتماد سائق الساحبة")
        user = db.get(User, p.user_id)
        driver_type = "courier" if p.service_type == "courier" else "tow"
        tech = Technician(
            id=uuid.uuid4(),
            full_name=user.full_name if user else "",
            phone=user.phone if user else "",
            rating=5.0,
            avatar_initials=user.avatar_initials if user else "?",
            is_available=False,
            driver_type=driver_type,
            created_at=now,
        )
        db.add(tech)
        db.flush()
        p.technician_id = tech.id
        p.is_approved = True
        p.verification_status = "approved"
        p.updated_at = now
        return driver_profile_out(p, user)  # type: ignore[arg-type]

    if role == "workshop":
        p = db.get(WorkshopProfile, profile_id)
        if not p:
            raise ValueError("طلب الورشة غير موجود")
        user = db.get(User, p.user_id)
        vendor = Vendor(
            id=uuid.uuid4(),
            business_name=p.center_name,
            contact_name=user.full_name if user else "",
            email=user.email if user else f"w{p.id}@rousto.app",
            phone=user.phone if user else "",
            city=p.city,
            city_id=str(p.city_id) if p.city_id else None,
            status="approved",
            base_lat=p.latitude,
            base_lng=p.longitude,
            approved_at=now,
            approved_by=approved_by,
            created_at=now,
            updated_at=now,
        )
        db.add(vendor)
        db.flush()
        p.vendor_id = vendor.id
        p.is_approved = True
        p.verification_status = "approved"
        p.updated_at = now
        if user:
            db.add(
                UserVendorLink(
                    user_id=user.id,
                    vendor_id=vendor.id,
                    linked_at=now,
                )
            )
        return workshop_profile_out(p, user)  # type: ignore[arg-type]

    raise ValueError("دور غير مدعوم")


def reject_registration(
    db: Session,
    *,
    role: str,
    profile_id: uuid.UUID,
    reason: str,
) -> dict:
    now = datetime.now(timezone.utc)
    reason = reason.strip()
    if len(reason) < 5:
        raise ValueError("سبب الرفض مطلوب (5 أحرف على الأقل)")
    if role == "vendor":
        p = db.get(VendorProfile, profile_id)
        if not p:
            raise ValueError("طلب التاجر غير موجود")
        p.is_approved = False
        p.verification_status = "rejected"
        p.rejection_reason = reason
        p.updated_at = now
        user = db.get(User, p.user_id)
        return vendor_profile_out(p, user)  # type: ignore[arg-type]
    if role == "driver":
        p = db.get(DriverProfile, profile_id)
        if not p:
            raise ValueError("طلب السائق غير موجود")
        p.is_approved = False
        p.verification_status = "rejected"
        p.rejection_reason = reason
        p.updated_at = now
        user = db.get(User, p.user_id)
        return driver_profile_out(p, user)  # type: ignore[arg-type]
    if role == "workshop":
        p = db.get(WorkshopProfile, profile_id)
        if not p:
            raise ValueError("طلب الورشة غير موجود")
        p.is_approved = False
        p.verification_status = "rejected"
        p.rejection_reason = reason
        p.updated_at = now
        user = db.get(User, p.user_id)
        return workshop_profile_out(p, user)  # type: ignore[arg-type]
    raise ValueError("دور غير مدعوم")
