import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
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
    sort_order: Mapped[int] = mapped_column(SmallInteger, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    services: Mapped[list["Service"]] = relationship(back_populates="category")


class Service(Base):
    __tablename__ = "services"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("service_categories.id"))
    slug: Mapped[str] = mapped_column(String(60), unique=True)
    name_ar: Mapped[str] = mapped_column(String(120))
    subtitle_ar: Mapped[str | None] = mapped_column(String(200))
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
    current_lat: Mapped[float | None] = mapped_column(Numeric(10, 7))
    current_lng: Mapped[float | None] = mapped_column(Numeric(10, 7))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Promotion(Base):
    __tablename__ = "promotions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True)
    title_ar: Mapped[str] = mapped_column(String(120))
    description_ar: Mapped[str | None] = mapped_column(String(300))
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
    description_ar: Mapped[str | None] = mapped_column(String(300))
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
    description_ar: Mapped[str | None] = mapped_column(String(300))
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
