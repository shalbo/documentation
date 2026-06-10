import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class PaymentMethodType(str, enum.Enum):
    mada = "mada"
    apple_pay = "apple_pay"
    visa = "visa"
    mastercard = "mastercard"


class DiscountType(str, enum.Enum):
    percentage = "percentage"
    fixed_amount = "fixed_amount"


class BookingStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    technician_assigned = "technician_assigned"
    en_route = "en_route"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    captured = "captured"
    refunded = "refunded"
    failed = "failed"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True)
    avatar_initials: Mapped[str | None] = mapped_column(String(1))
    loyalty_points: Mapped[int] = mapped_column(Integer, default=0)
    locale: Mapped[str] = mapped_column(String(5), default="ar")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    vehicles: Mapped[list["Vehicle"]] = relationship(back_populates="user")
    addresses: Mapped[list["Address"]] = relationship(back_populates="user")
    payment_methods: Mapped[list["PaymentMethod"]] = relationship(back_populates="user")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="user")
    loyalty_transactions: Mapped[list["LoyaltyTransaction"]] = relationship(
        back_populates="user"
    )


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    make: Mapped[str] = mapped_column(String(60))
    model: Mapped[str] = mapped_column(String(60))
    year: Mapped[int] = mapped_column(SmallInteger)
    color: Mapped[str | None] = mapped_column(String(40))
    plate_number: Mapped[str] = mapped_column(String(20))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="vehicles")


class ServiceCategory(Base):
    __tablename__ = "service_categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    slug: Mapped[str] = mapped_column(String(40), unique=True)
    name_ar: Mapped[str] = mapped_column(String(80))
    name_en: Mapped[str | None] = mapped_column(String(80))
    sort_order: Mapped[int] = mapped_column(SmallInteger, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    services: Mapped[list["Service"]] = relationship(back_populates="category")


class Service(Base):
    __tablename__ = "services"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("service_categories.id"))
    slug: Mapped[str] = mapped_column(String(60), unique=True)
    name_ar: Mapped[str] = mapped_column(String(120))
    name_en: Mapped[str | None] = mapped_column(String(120))
    subtitle_ar: Mapped[str | None] = mapped_column(String(200))
    subtitle_en: Mapped[str | None] = mapped_column(String(200))
    icon_key: Mapped[str | None] = mapped_column(String(40))
    price_sar: Mapped[float] = mapped_column(Numeric(10, 2))
    duration_minutes: Mapped[int] = mapped_column(SmallInteger)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    category: Mapped["ServiceCategory"] = relationship(back_populates="services")


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    label: Mapped[str] = mapped_column(String(40))
    district: Mapped[str] = mapped_column(String(80))
    city: Mapped[str] = mapped_column(String(60))
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7))
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="addresses")


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    type: Mapped[str] = mapped_column(String(20))
    last_four: Mapped[str | None] = mapped_column(String(4))
    label_ar: Mapped[str] = mapped_column(String(60))
    label_en: Mapped[str | None] = mapped_column(String(60))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="payment_methods")


class Technician(Base):
    __tablename__ = "technicians"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(20), unique=True)
    rating: Mapped[float] = mapped_column(Numeric(2, 1))
    avatar_initials: Mapped[str | None] = mapped_column(String(1))
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    driver_type: Mapped[str] = mapped_column(String(20), default="service")
    current_lat: Mapped[float | None] = mapped_column(Numeric(10, 7))
    current_lng: Mapped[float | None] = mapped_column(Numeric(10, 7))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Promotion(Base):
    __tablename__ = "promotions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True)
    title_ar: Mapped[str] = mapped_column(String(120))
    title_en: Mapped[str | None] = mapped_column(String(120))
    description_ar: Mapped[str | None] = mapped_column(String(300))
    description_en: Mapped[str | None] = mapped_column(String(300))
    discount_type: Mapped[str] = mapped_column(String(20))
    discount_value: Mapped[float] = mapped_column(Numeric(10, 2))
    min_order_sar: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    max_uses_per_user: Mapped[int] = mapped_column(SmallInteger, default=1)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    reference: Mapped[str] = mapped_column(String(12), unique=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    service_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("services.id"))
    vehicle_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vehicles.id"))
    address_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("addresses.id"))
    payment_method_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("payment_methods.id"))
    technician_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("technicians.id"))
    promotion_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("promotions.id"))
    scan_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("vehicle_scans.id"))
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    service_price_sar: Mapped[float] = mapped_column(Numeric(10, 2))
    discount_sar: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    membership_discount_sar: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    points_discount_sar: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    total_sar: Mapped[float] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(30))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="bookings")
    service: Mapped["Service"] = relationship()
    vehicle: Mapped["Vehicle"] = relationship()
    address: Mapped["Address"] = relationship()
    payment_method: Mapped["PaymentMethod | None"] = relationship()
    technician: Mapped["Technician | None"] = relationship()
    promotion: Mapped["Promotion | None"] = relationship()
    status_events: Mapped[list["BookingStatusEvent"]] = relationship(
        back_populates="booking", order_by="BookingStatusEvent.occurred_at"
    )
    payments: Mapped[list["Payment"]] = relationship(back_populates="booking")


class BookingStatusEvent(Base):
    __tablename__ = "booking_status_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    booking_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bookings.id"))
    status: Mapped[str] = mapped_column(String(30))
    label_ar: Mapped[str] = mapped_column(String(120))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    booking: Mapped["Booking"] = relationship(back_populates="status_events")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    booking_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bookings.id"))
    amount_sar: Mapped[float] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(20))
    gateway_ref: Mapped[str | None] = mapped_column(String(100))
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    booking: Mapped["Booking"] = relationship(back_populates="payments")


class LoyaltyTransaction(Base):
    __tablename__ = "loyalty_transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    booking_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("bookings.id"))
    points: Mapped[int] = mapped_column(Integer)
    reason_ar: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="loyalty_transactions")


class Testimonial(Base):
    __tablename__ = "testimonials"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    author_name: Mapped[str] = mapped_column(String(80))
    city: Mapped[str] = mapped_column(String(60))
    quote_ar: Mapped[str] = mapped_column(Text)
    rating: Mapped[int] = mapped_column(SmallInteger)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MembershipPlan(Base):
    __tablename__ = "membership_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    slug: Mapped[str] = mapped_column(String(40), unique=True)
    name_ar: Mapped[str] = mapped_column(String(80))
    name_en: Mapped[str | None] = mapped_column(String(80))
    description_ar: Mapped[str | None] = mapped_column(String(300))
    description_en: Mapped[str | None] = mapped_column(String(300))
    price_sar: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    billing_period: Mapped[str] = mapped_column(String(20))
    discount_percent: Mapped[int] = mapped_column(SmallInteger, default=0)
    priority_booking: Mapped[bool] = mapped_column(Boolean, default=False)
    free_inspection: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(SmallInteger, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class UserMembership(Base):
    __tablename__ = "user_memberships"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("membership_plans.id"))
    status: Mapped[str] = mapped_column(String(20))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    plan: Mapped["MembershipPlan"] = relationship()


class ServicePackage(Base):
    __tablename__ = "service_packages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    slug: Mapped[str] = mapped_column(String(40), unique=True)
    name_ar: Mapped[str] = mapped_column(String(120))
    description_ar: Mapped[str | None] = mapped_column(String(300))
    price_sar: Mapped[float] = mapped_column(Numeric(10, 2))
    visits_count: Mapped[int] = mapped_column(SmallInteger)
    validity_days: Mapped[int] = mapped_column(SmallInteger)
    savings_sar: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class LoyaltyReward(Base):
    __tablename__ = "loyalty_rewards"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    slug: Mapped[str] = mapped_column(String(40), unique=True)
    title_ar: Mapped[str] = mapped_column(String(120))
    title_en: Mapped[str | None] = mapped_column(String(120))
    description_ar: Mapped[str | None] = mapped_column(String(300))
    description_en: Mapped[str | None] = mapped_column(String(300))
    points_cost: Mapped[int] = mapped_column(Integer)
    discount_sar: Mapped[float] = mapped_column(Numeric(10, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class PromotionRedemption(Base):
    __tablename__ = "promotion_redemptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    promotion_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("promotions.id"))
    booking_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("bookings.id"))
    discount_sar: Mapped[float] = mapped_column(Numeric(10, 2))
    redeemed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class SplitRule(Base):
    __tablename__ = "split_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    slug: Mapped[str] = mapped_column(String(40), unique=True)
    name_ar: Mapped[str] = mapped_column(String(80))
    platform_rate: Mapped[float] = mapped_column(Numeric(5, 4))
    technician_rate: Mapped[float] = mapped_column(Numeric(5, 4))
    reserve_rate: Mapped[float] = mapped_column(Numeric(5, 4))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PaymentSplitLeg(Base):
    __tablename__ = "payment_split_legs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    payment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("payments.id"))
    booking_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bookings.id"))
    rule_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("split_rules.id"))
    recipient_type: Mapped[str] = mapped_column(String(20))
    recipient_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("technicians.id"))
    amount_sar: Mapped[float] = mapped_column(Numeric(10, 2))
    rate_applied: Mapped[float] = mapped_column(Numeric(5, 4))
    status: Mapped[str] = mapped_column(String(20), default="held")
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class BookingRevenue(Base):
    __tablename__ = "booking_revenue"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    booking_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bookings.id"), unique=True)
    gross_sar: Mapped[float] = mapped_column(Numeric(10, 2))
    membership_discount_sar: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    promo_discount_sar: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    points_discount_sar: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    net_sar: Mapped[float] = mapped_column(Numeric(10, 2))
    platform_fee_sar: Mapped[float] = mapped_column(Numeric(10, 2))
    technician_payout_sar: Mapped[float] = mapped_column(Numeric(10, 2))
    reserve_sar: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class VehicleScan(Base):
    __tablename__ = "vehicle_scans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    vehicle_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vehicles.id"))
    scan_type: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    images: Mapped[list["ScanImage"]] = relationship(back_populates="scan")
    findings: Mapped[list["ScanFinding"]] = relationship(back_populates="scan")


class ScanImage(Base):
    __tablename__ = "scan_images"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    scan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vehicle_scans.id"))
    storage_key: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(80))
    sort_order: Mapped[int] = mapped_column(SmallInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    scan: Mapped["VehicleScan"] = relationship(back_populates="images")


class ScanFinding(Base):
    __tablename__ = "scan_findings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    scan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vehicle_scans.id"))
    code: Mapped[str] = mapped_column(String(60))
    label_ar: Mapped[str] = mapped_column(String(200))
    severity: Mapped[str] = mapped_column(String(20))
    confidence: Mapped[float] = mapped_column(Numeric(4, 3))
    suggested_service_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("services.id"))
    details: Mapped[dict] = mapped_column(JSONB, default=dict)

    scan: Mapped["VehicleScan"] = relationship(back_populates="findings")
    suggested_service: Mapped["Service | None"] = relationship()


class TechnicianLocationUpdate(Base):
    __tablename__ = "technician_location_updates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    technician_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("technicians.id"))
    booking_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("bookings.id"))
    lat: Mapped[float] = mapped_column(Numeric(10, 7))
    lng: Mapped[float] = mapped_column(Numeric(10, 7))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    business_name: Mapped[str] = mapped_column(String(120))
    contact_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True)
    city: Mapped[str] = mapped_column(String(60), default="الرياض")
    national_id: Mapped[str | None] = mapped_column(String(20))
    commercial_reg: Mapped[str | None] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    technician_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("technicians.id"))
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approved_by: Mapped[str | None] = mapped_column(String(80))
    base_lat: Mapped[float | None] = mapped_column(Numeric(10, 7))
    base_lng: Mapped[float | None] = mapped_column(Numeric(10, 7))
    service_radius_km: Mapped[float] = mapped_column(Numeric(5, 2), default=15.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    bank_accounts: Mapped[list["VendorBankAccount"]] = relationship(back_populates="vendor")


class VendorBankAccount(Base):
    __tablename__ = "vendor_bank_accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    vendor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vendors.id"))
    bank_name: Mapped[str] = mapped_column(String(80))
    account_holder: Mapped[str] = mapped_column(String(120))
    iban: Mapped[str] = mapped_column(String(34))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    vendor: Mapped["Vendor"] = relationship(back_populates="bank_accounts")


class TowingDispatch(Base):
    __tablename__ = "towing_dispatches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    reference: Mapped[str] = mapped_column(String(12), unique=True)
    booking_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bookings.id"), unique=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    technician_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("technicians.id"))
    pickup_label: Mapped[str] = mapped_column(String(120))
    pickup_lat: Mapped[float] = mapped_column(Numeric(10, 7))
    pickup_lng: Mapped[float] = mapped_column(Numeric(10, 7))
    dropoff_label: Mapped[str] = mapped_column(String(120))
    dropoff_lat: Mapped[float] = mapped_column(Numeric(10, 7))
    dropoff_lng: Mapped[float] = mapped_column(Numeric(10, 7))
    status: Mapped[str] = mapped_column(String(30), default="pending")
    total_route_km: Mapped[float | None] = mapped_column(Numeric(6, 2))
    base_fare_sar: Mapped[float | None] = mapped_column(Numeric(10, 2))
    per_km_rate_sar: Mapped[float | None] = mapped_column(Numeric(6, 2))
    total_fare_sar: Mapped[float | None] = mapped_column(Numeric(10, 2))
    customer_rating: Mapped[int | None] = mapped_column(SmallInteger)
    notes: Mapped[str | None] = mapped_column(Text)
    dispatched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancel_reason: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    booking: Mapped["Booking"] = relationship()
    technician: Mapped["Technician | None"] = relationship()
    events: Mapped[list["TowingDispatchEvent"]] = relationship(
        back_populates="dispatch", order_by="TowingDispatchEvent.occurred_at"
    )


class TowingDispatchEvent(Base):
    __tablename__ = "towing_dispatch_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    dispatch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("towing_dispatches.id"))
    status: Mapped[str] = mapped_column(String(30))
    label_ar: Mapped[str] = mapped_column(String(120))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    dispatch: Mapped["TowingDispatch"] = relationship(back_populates="events")


class SupportFaq(Base):
    __tablename__ = "support_faq"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    slug: Mapped[str] = mapped_column(String(60), unique=True)
    category: Mapped[str] = mapped_column(String(40))
    question_ar: Mapped[str] = mapped_column(String(300))
    question_en: Mapped[str | None] = mapped_column(String(300))
    answer_ar: Mapped[str] = mapped_column(Text)
    answer_en: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(SmallInteger, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    reference: Mapped[str] = mapped_column(String(12), unique=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    booking_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("bookings.id"))
    category: Mapped[str] = mapped_column(String(40))
    priority: Mapped[str] = mapped_column(String(20), default="normal")
    status: Mapped[str] = mapped_column(String(30), default="open")
    subject: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    messages: Mapped[list["SupportTicketMessage"]] = relationship(
        back_populates="ticket", order_by="SupportTicketMessage.created_at"
    )


class SupportTicketMessage(Base):
    __tablename__ = "support_ticket_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    ticket_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("support_tickets.id"))
    author_type: Mapped[str] = mapped_column(String(20))
    author_label: Mapped[str] = mapped_column(String(80))
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    ticket: Mapped["SupportTicket"] = relationship(back_populates="messages")


class SecurityAuditLog(Base):
    __tablename__ = "security_audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    event_type: Mapped[str] = mapped_column(String(60))
    severity: Mapped[str] = mapped_column(String(20), default="info")
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String(300))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class UserSecurityProfile(Base):
    __tablename__ = "user_security_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    login_alerts_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    suspicious_activity_reported_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    last_security_review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class LandingHeroStat(Base):
    __tablename__ = "landing_hero_stats"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    slug: Mapped[str] = mapped_column(String(40), unique=True)
    value_ar: Mapped[str] = mapped_column(String(40))
    label_ar: Mapped[str] = mapped_column(String(80))
    sort_order: Mapped[int] = mapped_column(SmallInteger, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class LandingPricingPlan(Base):
    __tablename__ = "landing_pricing_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    slug: Mapped[str] = mapped_column(String(40), unique=True)
    name_ar: Mapped[str] = mapped_column(String(80))
    description_ar: Mapped[str | None] = mapped_column(String(300))
    price_sar: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    price_label_ar: Mapped[str] = mapped_column(String(60), default="شهرياً")
    billing_period: Mapped[str] = mapped_column(String(20), default="monthly")
    features: Mapped[list] = mapped_column(JSONB, default=list)
    cta_text_ar: Mapped[str] = mapped_column(String(60), default="ابدأ الآن")
    cta_url: Mapped[str | None] = mapped_column(String(200))
    badge_ar: Mapped[str | None] = mapped_column(String(40))
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(SmallInteger, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class LandingPageFeature(Base):
    __tablename__ = "landing_page_features"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    slug: Mapped[str] = mapped_column(String(40), unique=True)
    title_ar: Mapped[str] = mapped_column(String(120))
    description_ar: Mapped[str | None] = mapped_column(String(300))
    icon_key: Mapped[str | None] = mapped_column(String(40))
    sort_order: Mapped[int] = mapped_column(SmallInteger, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


role_permissions_table = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True),
    Column(
        "permission_id",
        UUID(as_uuid=True),
        ForeignKey("permissions.id"),
        primary_key=True,
    ),
)


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    slug: Mapped[str] = mapped_column(String(40), unique=True)
    name_ar: Mapped[str] = mapped_column(String(80))
    description_ar: Mapped[str | None] = mapped_column(String(200))
    is_system: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    permissions: Mapped[list["Permission"]] = relationship(
        secondary=role_permissions_table, back_populates="roles"
    )


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    slug: Mapped[str] = mapped_column(String(60), unique=True)
    name_ar: Mapped[str] = mapped_column(String(120))
    resource: Mapped[str] = mapped_column(String(40))
    action: Mapped[str] = mapped_column(String(40))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    roles: Mapped[list["Role"]] = relationship(
        secondary=role_permissions_table, back_populates="permissions"
    )


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), primary_key=True
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roles.id"), primary_key=True
    )
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    granted_by: Mapped[str | None] = mapped_column(String(80))


class UserVendorLink(Base):
    __tablename__ = "user_vendor_links"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), primary_key=True
    )
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vendors.id"), primary_key=True
    )
    linked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AuthOtpRequest(Base):
    __tablename__ = "auth_otp_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    phone: Mapped[str] = mapped_column(String(20))
    code_hash: Mapped[str] = mapped_column(String(128))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(SmallInteger, default=0)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AuthRefreshToken(Base):
    __tablename__ = "auth_refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    token_hash: Mapped[str] = mapped_column(String(128), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MarketingCampaign(Base):
    __tablename__ = "marketing_campaigns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    slug: Mapped[str] = mapped_column(String(40), unique=True)
    name_ar: Mapped[str] = mapped_column(String(120))
    description_ar: Mapped[str | None] = mapped_column(String(300))
    channel: Mapped[str] = mapped_column(String(30), default="web")
    utm_source: Mapped[str | None] = mapped_column(String(60))
    utm_medium: Mapped[str | None] = mapped_column(String(60))
    utm_campaign: Mapped[str | None] = mapped_column(String(60))
    utm_content: Mapped[str | None] = mapped_column(String(60))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MarketingBanner(Base):
    __tablename__ = "marketing_banners"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    slug: Mapped[str] = mapped_column(String(40), unique=True)
    title_ar: Mapped[str] = mapped_column(String(120))
    title_en: Mapped[str | None] = mapped_column(String(120))
    subtitle_ar: Mapped[str | None] = mapped_column(String(200))
    subtitle_en: Mapped[str | None] = mapped_column(String(200))
    placement: Mapped[str] = mapped_column(String(30))
    image_url: Mapped[str | None] = mapped_column(String(300))
    cta_text_ar: Mapped[str | None] = mapped_column(String(60))
    cta_text_en: Mapped[str | None] = mapped_column(String(60))
    cta_url: Mapped[str | None] = mapped_column(String(200))
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("marketing_campaigns.id")
    )
    promotion_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("promotions.id"))
    sort_order: Mapped[int] = mapped_column(SmallInteger, default=0)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class MarketingPartner(Base):
    __tablename__ = "marketing_partners"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    slug: Mapped[str] = mapped_column(String(40), unique=True)
    name_ar: Mapped[str] = mapped_column(String(80))
    logo_url: Mapped[str | None] = mapped_column(String(300))
    website_url: Mapped[str | None] = mapped_column(String(200))
    sort_order: Mapped[int] = mapped_column(SmallInteger, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class MarketingNewsletterSubscriber(Base):
    __tablename__ = "marketing_newsletter_subscribers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    phone: Mapped[str | None] = mapped_column(String(20))
    source: Mapped[str] = mapped_column(String(40), default="landing")
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("marketing_campaigns.id")
    )
    subscribed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    unsubscribed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class MarketingReferral(Base):
    __tablename__ = "marketing_referrals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    referrer_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    code: Mapped[str] = mapped_column(String(20), unique=True)
    reward_points: Mapped[int] = mapped_column(Integer, default=100)
    max_uses: Mapped[int | None] = mapped_column(SmallInteger)
    uses_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MarketingReferralEvent(Base):
    __tablename__ = "marketing_referral_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    referral_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("marketing_referrals.id"))
    referred_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    booking_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("bookings.id"))
    reward_granted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class UserDeviceToken(Base):
    __tablename__ = "user_device_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    fcm_token: Mapped[str] = mapped_column(String(512))
    platform: Mapped[str] = mapped_column(String(20), default="unknown")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class NotificationTemplate(Base):
    __tablename__ = "notification_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    slug: Mapped[str] = mapped_column(String(60), unique=True)
    category: Mapped[str] = mapped_column(String(30))
    title_template: Mapped[str] = mapped_column(String(200))
    title_template_en: Mapped[str | None] = mapped_column(String(200))
    body_template: Mapped[str] = mapped_column(Text)
    body_template_en: Mapped[str | None] = mapped_column(Text)
    action_url_template: Mapped[str | None] = mapped_column(String(300))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class UserNotificationPreference(Base):
    __tablename__ = "user_notification_preferences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    category: Mapped[str] = mapped_column(String(30))
    push_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    category: Mapped[str] = mapped_column(String(30))
    template_slug: Mapped[str | None] = mapped_column(String(60))
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    data_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    action_url: Mapped[str | None] = mapped_column(String(300))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    push_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class NotificationBroadcast(Base):
    __tablename__ = "notification_broadcasts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    reference: Mapped[str] = mapped_column(String(20), unique=True)
    category: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    target_segment: Mapped[str] = mapped_column(String(40))
    template_slug: Mapped[str | None] = mapped_column(String(60))
    recipients_count: Mapped[int] = mapped_column(Integer, default=0)
    push_sent_count: Mapped[int] = mapped_column(Integer, default=0)
    in_app_count: Mapped[int] = mapped_column(Integer, default=0)
    skipped_count: Mapped[int] = mapped_column(Integer, default=0)
    created_by: Mapped[str | None] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class NotificationDispatchLog(Base):
    __tablename__ = "notification_dispatch_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    event_source: Mapped[str] = mapped_column(String(60))
    notification_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("notifications.id")
    )
    broadcast_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("notification_broadcasts.id")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    category: Mapped[str] = mapped_column(String(30))
    template_slug: Mapped[str | None] = mapped_column(String(60))
    title: Mapped[str] = mapped_column(String(200))
    channel: Mapped[str] = mapped_column(String(20), default="both")
    push_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    in_app_created: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="delivered")
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PartSupplier(Base):
    __tablename__ = "part_suppliers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    slug: Mapped[str] = mapped_column(String(40), unique=True)
    name_ar: Mapped[str] = mapped_column(String(120))
    name_en: Mapped[str | None] = mapped_column(String(120))
    is_oem: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PartCategory(Base):
    __tablename__ = "part_categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    slug: Mapped[str] = mapped_column(String(40), unique=True)
    name_ar: Mapped[str] = mapped_column(String(120))
    name_en: Mapped[str | None] = mapped_column(String(120))
    sort_order: Mapped[int] = mapped_column(SmallInteger, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Part(Base):
    __tablename__ = "parts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    part_number: Mapped[str] = mapped_column(String(60), unique=True)
    oem_number: Mapped[str | None] = mapped_column(String(60))
    vin_prefix: Mapped[str | None] = mapped_column(String(11))
    slug: Mapped[str] = mapped_column(String(80), unique=True)
    name_ar: Mapped[str] = mapped_column(String(200))
    name_en: Mapped[str | None] = mapped_column(String(200))
    description_ar: Mapped[str | None] = mapped_column(Text)
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("part_categories.id"))
    supplier_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("part_suppliers.id")
    )
    is_oem: Mapped[bool] = mapped_column(Boolean, default=False)
    price_sar: Mapped[float] = mapped_column(Numeric(10, 2))
    warranty_months: Mapped[int] = mapped_column(SmallInteger, default=6)
    vehicle_compatibility: Mapped[list] = mapped_column(JSONB, default=list)
    image_url: Mapped[str | None] = mapped_column(String(300))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    category: Mapped["PartCategory"] = relationship()
    supplier: Mapped["PartSupplier | None"] = relationship()


class PartInventory(Base):
    __tablename__ = "part_inventory"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    vendor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vendors.id"))
    part_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("parts.id"))
    qty_available: Mapped[int] = mapped_column(Integer, default=0)
    cost_sar: Mapped[float | None] = mapped_column(Numeric(10, 2))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class BookingPart(Base):
    __tablename__ = "booking_parts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    booking_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bookings.id"))
    part_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("parts.id"))
    vendor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("vendors.id"))
    qty: Mapped[int] = mapped_column(SmallInteger, default=1)
    unit_price_sar: Mapped[float] = mapped_column(Numeric(10, 2))
    warranty_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    installed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    part: Mapped["Part"] = relationship()


class PartWarrantyClaim(Base):
    __tablename__ = "part_warranty_claims"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    booking_part_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("booking_parts.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="open")
    admin_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class CarMake(Base):
    __tablename__ = "car_makes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    slug: Mapped[str] = mapped_column(String(40), unique=True)
    name_ar: Mapped[str] = mapped_column(String(80))
    name_en: Mapped[str | None] = mapped_column(String(80))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(SmallInteger, default=0)


class CarModel(Base):
    __tablename__ = "car_models"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    make_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("car_makes.id"))
    slug: Mapped[str] = mapped_column(String(40))
    name_ar: Mapped[str] = mapped_column(String(80))
    name_en: Mapped[str | None] = mapped_column(String(80))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    make: Mapped["CarMake"] = relationship()
    years: Mapped[list["CarYear"]] = relationship(back_populates="model")


class CarYear(Base):
    __tablename__ = "car_years"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    model_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("car_models.id"))
    year: Mapped[int] = mapped_column(SmallInteger)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    model: Mapped["CarModel"] = relationship()


class PartVehicleCompatibility(Base):
    __tablename__ = "part_vehicle_compatibilities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    part_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("parts.id"))
    car_year_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("car_years.id"))
    fitment_note_ar: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class IntercityShippingRate(Base):
    __tablename__ = "intercity_shipping_rates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    origin_city: Mapped[str] = mapped_column(String(60))
    destination_city: Mapped[str] = mapped_column(String(60))
    flat_fee_sar: Mapped[float] = mapped_column(Numeric(10, 2))
    carrier_name: Mapped[str] = mapped_column(String(80))
    carrier_slug: Mapped[str] = mapped_column(String(40))
    eta_days: Mapped[int] = mapped_column(SmallInteger, default=2)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PartOrder(Base):
    __tablename__ = "part_orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    reference: Mapped[str] = mapped_column(String(12), unique=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    part_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("parts.id"))
    vendor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vendors.id"))
    qty: Mapped[int] = mapped_column(SmallInteger, default=1)
    subtotal_sar: Mapped[float] = mapped_column(Numeric(10, 2))
    shipping_type: Mapped[str] = mapped_column(String(24))
    shipping_fee_sar: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    total_sar: Mapped[float] = mapped_column(Numeric(10, 2))
    origin_city: Mapped[str | None] = mapped_column(String(60))
    destination_city: Mapped[str] = mapped_column(String(60))
    dest_lat: Mapped[float | None] = mapped_column(Numeric(10, 7))
    dest_lng: Mapped[float | None] = mapped_column(Numeric(10, 7))
    courier_technician_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("technicians.id")
    )
    intercity_carrier: Mapped[str | None] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PartOrderSettlement(Base):
    __tablename__ = "part_order_settlements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    part_order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("part_orders.id"))
    recipient_type: Mapped[str] = mapped_column(String(20))
    recipient_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    amount_sar: Mapped[float] = mapped_column(Numeric(10, 2))
    label_ar: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(20), default="held")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class TowVehicle(Base):
    __tablename__ = "tow_vehicles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    technician_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("technicians.id"))
    vehicle_type: Mapped[str] = mapped_column(String(20))
    plate_number: Mapped[str] = mapped_column(String(20))
    max_capacity_kg: Mapped[float | None] = mapped_column(Numeric(8, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MarketingAttributionEvent(Base):
    __tablename__ = "marketing_attribution_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("marketing_campaigns.id")
    )
    event_type: Mapped[str] = mapped_column(String(30))
    utm_source: Mapped[str | None] = mapped_column(String(60))
    utm_medium: Mapped[str | None] = mapped_column(String(60))
    utm_campaign: Mapped[str | None] = mapped_column(String(60))
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    session_id: Mapped[str | None] = mapped_column(String(64))
    metadata_json: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
