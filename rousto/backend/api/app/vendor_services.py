import re
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import PaymentSplitLeg, Technician, Vendor, VendorBankAccount, VendorProfile
from app.tier_services import get_default_tier

IBAN_PATTERN = re.compile(r"^SA\d{22}$")
RELEASED_STATUSES = frozenset({"released", "paid"})


def normalize_iban(iban: str) -> str:
    return iban.replace(" ", "").upper()


def validate_iban(iban: str) -> str:
    normalized = normalize_iban(iban)
    if not IBAN_PATTERN.match(normalized):
        raise ValueError("رقم IBAN غير صالح — يجب أن يبدأ بـ SA ويتبعه 22 رقمًا")
    return normalized


def mask_iban(iban: str) -> str:
    normalized = normalize_iban(iban)
    if len(normalized) < 8:
        return normalized
    return f"{normalized[:4]}****{normalized[-4:]}"


def bank_account_out(account: VendorBankAccount) -> dict:
    return {
        "id": account.id,
        "bank_name": account.bank_name,
        "account_holder": account.account_holder,
        "iban_masked": mask_iban(account.iban),
        "is_primary": account.is_primary,
        "is_verified": account.is_verified,
    }


def payout_summary_for_technician(db: Session, technician_id: uuid.UUID) -> dict:
    legs = db.scalars(
        select(PaymentSplitLeg).where(
            PaymentSplitLeg.recipient_type == "technician",
            PaymentSplitLeg.recipient_id == technician_id,
        )
    ).all()

    total = sum(float(leg.amount_sar) for leg in legs)
    released = sum(
        float(leg.amount_sar) for leg in legs if leg.status in RELEASED_STATUSES
    )
    pending = total - released

    return {
        "total_earned_sar": round(total, 2),
        "pending_sar": round(pending, 2),
        "released_sar": round(released, 2),
        "legs_count": len(legs),
    }


def vendor_out(db: Session, vendor: Vendor, *, include_summary: bool = True) -> dict:
    bank = db.scalar(
        select(VendorBankAccount).where(
            VendorBankAccount.vendor_id == vendor.id,
            VendorBankAccount.is_primary.is_(True),
        )
    )

    data = {
        "id": vendor.id,
        "business_name": vendor.business_name,
        "contact_name": vendor.contact_name,
        "email": vendor.email,
        "phone": vendor.phone,
        "city": vendor.city,
        "national_id": vendor.national_id,
        "commercial_reg": vendor.commercial_reg,
        "status": vendor.status,
        "is_active": vendor.is_active,
        "technician_id": vendor.technician_id,
        "rejection_reason": vendor.rejection_reason,
        "approved_at": vendor.approved_at,
        "created_at": vendor.created_at,
        "updated_at": vendor.updated_at,
        "bank_account": bank_account_out(bank) if bank else None,
    }

    if include_summary and vendor.status == "approved" and vendor.technician_id:
        data["payout_summary"] = payout_summary_for_technician(db, vendor.technician_id)
    else:
        data["payout_summary"] = None

    return data


def payout_leg_out(leg: PaymentSplitLeg) -> dict:
    return {
        "id": leg.id,
        "booking_id": leg.booking_id,
        "payment_id": leg.payment_id,
        "amount_sar": float(leg.amount_sar),
        "rate_applied": float(leg.rate_applied),
        "status": leg.status,
        "released_at": leg.released_at,
        "created_at": leg.created_at,
    }


def submit_application(
    db: Session,
    *,
    business_name: str,
    contact_name: str,
    email: str,
    phone: str,
    city: str,
    bank_name: str,
    account_holder: str,
    iban: str,
    national_id: str | None = None,
    commercial_reg: str | None = None,
) -> Vendor:
    normalized_iban = validate_iban(iban)
    now = datetime.now(timezone.utc)

    default_tier = get_default_tier(db)
    vendor = Vendor(
        id=uuid.uuid4(),
        business_name=business_name,
        contact_name=contact_name,
        email=email.strip().lower(),
        phone=phone.strip(),
        city=city,
        national_id=national_id,
        commercial_reg=commercial_reg,
        status="pending",
        tier_id=default_tier.id if default_tier else None,
        created_at=now,
        updated_at=now,
    )
    db.add(vendor)
    db.flush()

    account = VendorBankAccount(
        id=uuid.uuid4(),
        vendor_id=vendor.id,
        bank_name=bank_name,
        account_holder=account_holder,
        iban=normalized_iban,
        is_primary=True,
        is_verified=False,
        created_at=now,
        updated_at=now,
    )
    db.add(account)
    return vendor


def _find_or_create_technician(db: Session, vendor: Vendor) -> Technician:
    existing = db.scalar(select(Technician).where(Technician.phone == vendor.phone))
    if existing:
        return existing

    initials = vendor.contact_name.strip()[:1] if vendor.contact_name else None
    now = datetime.now(timezone.utc)
    technician = Technician(
        id=uuid.uuid4(),
        full_name=vendor.contact_name,
        phone=vendor.phone,
        rating=5.0,
        avatar_initials=initials,
        is_available=True,
        created_at=now,
    )
    db.add(technician)
    db.flush()
    return technician


def approve_vendor(db: Session, vendor: Vendor, *, approved_by: str = "admin") -> Vendor:
    if vendor.status != "pending":
        raise ValueError("يمكن الموافقة فقط على الطلبات المعلّقة")

    technician = _find_or_create_technician(db, vendor)
    now = datetime.now(timezone.utc)

    vendor.status = "approved"
    vendor.technician_id = technician.id
    if not vendor.tier_id:
        default_tier = get_default_tier(db)
        if default_tier:
            vendor.tier_id = default_tier.id
    vendor.approved_at = now
    vendor.approved_by = approved_by
    vendor.rejection_reason = None
    vendor.updated_at = now

    bank = db.scalar(
        select(VendorBankAccount).where(
            VendorBankAccount.vendor_id == vendor.id,
            VendorBankAccount.is_primary.is_(True),
        )
    )
    if bank:
        bank.is_verified = True
        bank.updated_at = now

    return vendor


def reject_vendor(db: Session, vendor: Vendor, *, reason: str) -> Vendor:
    if vendor.status != "pending":
        raise ValueError("يمكن رفض الطلبات المعلّقة فقط")

    now = datetime.now(timezone.utc)
    vendor.status = "rejected"
    vendor.rejection_reason = reason.strip()
    vendor.updated_at = now
    return vendor


def update_vendor_financials(
    db: Session,
    vendor: Vendor,
    *,
    bank_name: str,
    account_holder: str,
    iban: str,
) -> VendorBankAccount:
    if vendor.status != "approved":
        raise ValueError("تحديث البيانات المالية متاح للفنيين المُوافَق عليهم فقط")

    normalized_iban = validate_iban(iban)
    now = datetime.now(timezone.utc)

    account = db.scalar(
        select(VendorBankAccount).where(
            VendorBankAccount.vendor_id == vendor.id,
            VendorBankAccount.is_primary.is_(True),
        )
    )
    if not account:
        account = VendorBankAccount(
            id=uuid.uuid4(),
            vendor_id=vendor.id,
            is_primary=True,
            is_verified=False,
            created_at=now,
        )
        db.add(account)

    account.bank_name = bank_name
    account.account_holder = account_holder
    account.iban = normalized_iban
    account.updated_at = now
    return account


def list_vendor_payouts(db: Session, vendor: Vendor) -> list[PaymentSplitLeg]:
    if vendor.status != "approved" or not vendor.technician_id:
        raise ValueError("عرض المدفوعات يتطلب فنيًا مُوافَقًا عليه ومرتبطًا")

    return db.scalars(
        select(PaymentSplitLeg)
        .where(
            PaymentSplitLeg.recipient_type == "technician",
            PaymentSplitLeg.recipient_id == vendor.technician_id,
        )
        .order_by(PaymentSplitLeg.created_at.desc())
    ).all()


def count_vendors_by_status(db: Session) -> dict[str, int]:
    rows = db.execute(
        select(Vendor.status, func.count()).group_by(Vendor.status)
    ).all()
    return {status: count for status, count in rows}


def toggle_vendor_store_status(db: Session, vendor: Vendor) -> dict:
    if vendor.status != "approved":
        raise ValueError("لا يمكن تغيير حالة المحل قبل اعتماد الطلب")

    now = datetime.now(timezone.utc)
    vendor.is_active = not vendor.is_active
    vendor.updated_at = now

    profile = db.scalar(
        select(VendorProfile).where(VendorProfile.vendor_id == vendor.id)
    )
    if profile:
        profile.is_active = vendor.is_active
        profile.updated_at = now

    return {
        "vendor_id": str(vendor.id),
        "is_active": vendor.is_active,
        "message_ar": (
            "المحل يستقبل طلبات"
            if vendor.is_active
            else "المتجر مغلق مؤقتاً — بضاعتك مخفية الآن عن الزبائن"
        ),
    }
