from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


class Meta(BaseModel):
    total: int


class CategoryOut(BaseModel):
    id: UUID
    slug: str
    name_ar: str
    sort_order: int

    model_config = {"from_attributes": True}


class CategoryBrief(BaseModel):
    slug: str
    name_ar: str


class ServiceInTreeOut(BaseModel):
    id: UUID
    slug: str
    name_ar: str
    subtitle_ar: str | None
    icon_key: str | None
    price_sar: float
    duration_minutes: int


class CategoryTreeOut(BaseModel):
    id: UUID
    slug: str
    name_ar: str
    sort_order: int
    services_count: int
    services: list[ServiceInTreeOut]


class CategoryTreeMeta(BaseModel):
    total_categories: int
    total_services: int


class ServiceOut(BaseModel):
    id: UUID
    slug: str
    name_ar: str
    subtitle_ar: str | None
    icon_key: str | None
    price_sar: float
    duration_minutes: int
    category: CategoryBrief

    model_config = {"from_attributes": True}


class VehicleOut(BaseModel):
    id: UUID
    make: str
    model: str
    year: int
    color: str | None
    plate_number: str
    is_default: bool
    display_name: str | None = None

    model_config = {"from_attributes": True}


class AddressOut(BaseModel):
    id: UUID
    label: str
    district: str
    city: str
    latitude: float | None
    longitude: float | None
    is_default: bool

    model_config = {"from_attributes": True}


class PaymentMethodOut(BaseModel):
    id: UUID
    type: str
    last_four: str | None
    label_ar: str
    is_default: bool

    model_config = {"from_attributes": True}


class UserStats(BaseModel):
    services_count: int
    vehicles_count: int


class UserOut(BaseModel):
    id: UUID
    full_name: str
    email: str
    phone: str
    avatar_initials: str | None
    loyalty_points: int
    stats: UserStats | None = None

    model_config = {"from_attributes": True}


class LoyaltyTransactionOut(BaseModel):
    id: UUID
    points: int
    reason_ar: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LoyaltyOut(BaseModel):
    balance: int
    transactions: list[LoyaltyTransactionOut]


class PromotionOut(BaseModel):
    id: UUID
    code: str
    title_ar: str
    description_ar: str | None
    discount_type: str
    discount_value: float
    min_order_sar: float

    model_config = {"from_attributes": True}


class PromotionValidateIn(BaseModel):
    code: str = Field(min_length=1, max_length=30)
    service_price_sar: float = Field(gt=0)


class PromotionValidateOut(BaseModel):
    valid: bool
    discount_sar: float = 0
    total_sar: float = 0
    promotion: PromotionOut | None = None
    message: str | None = None


class BookingCreateIn(BaseModel):
    service_id: UUID
    vehicle_id: UUID
    address_id: UUID
    payment_method_id: UUID | None = None
    promotion_code: str | None = None
    reward_slug: str | None = None
    scheduled_at: datetime
    notes: str | None = None
    scan_id: UUID | None = None


class BookingServiceBrief(BaseModel):
    name_ar: str
    icon_key: str | None
    duration_minutes: int


class BookingOut(BaseModel):
    id: UUID
    reference: str
    status: str
    status_label_ar: str
    scheduled_at: datetime
    service_price_sar: float
    discount_sar: float
    total_sar: float
    notes: str | None
    created_at: datetime
    service: BookingServiceBrief | None = None
    vehicle: VehicleOut | None = None
    address: AddressOut | None = None

    model_config = {"from_attributes": True}


class TechnicianOut(BaseModel):
    full_name: str
    rating: float
    avatar_initials: str | None
    eta_minutes: int | None = None
    location: dict | None = None

    model_config = {"from_attributes": True}


class TrackingStepOut(BaseModel):
    status: str
    label_ar: str
    occurred_at: datetime
    is_current: bool
    is_done: bool


class TrackingOut(BaseModel):
    booking: dict
    technician: TechnicianOut | None
    steps: list[TrackingStepOut]


class TestimonialOut(BaseModel):
    id: UUID
    author_name: str
    city: str
    quote_ar: str
    rating: int

    model_config = {"from_attributes": True}


class HealthOut(BaseModel):
    status: str
    database: str


class AdminCategoryOut(BaseModel):
    id: UUID
    slug: str
    name_ar: str
    sort_order: int
    is_active: bool

    model_config = {"from_attributes": True}


class AdminCategoryCreate(BaseModel):
    slug: str = Field(..., min_length=2, max_length=40, pattern=r"^[a-z][a-z0-9-]*$")
    name_ar: str = Field(..., min_length=1, max_length=80)
    sort_order: int = 0
    is_active: bool = True


class AdminCategoryUpdate(BaseModel):
    name_ar: str | None = Field(default=None, min_length=1, max_length=80)
    sort_order: int | None = None
    is_active: bool | None = None


class AdminCategoryReorderItem(BaseModel):
    id: UUID
    sort_order: int


class AdminCategoryReorderIn(BaseModel):
    items: list[AdminCategoryReorderItem] = Field(..., min_length=1)


class AdminServiceOut(BaseModel):
    id: UUID
    slug: str
    name_ar: str
    subtitle_ar: str | None
    icon_key: str | None
    price_sar: float
    duration_minutes: int
    category_id: UUID
    category_slug: str
    category_name_ar: str
    is_active: bool
    created_at: datetime | None = None


class AdminServiceCreate(BaseModel):
    category_id: UUID
    slug: str = Field(..., min_length=2, max_length=60, pattern=r"^[a-z][a-z0-9-]*$")
    name_ar: str = Field(..., min_length=1, max_length=120)
    subtitle_ar: str | None = Field(default=None, max_length=200)
    icon_key: str | None = Field(default=None, max_length=40)
    price_sar: float = Field(gt=0)
    duration_minutes: int = Field(gt=0, le=480)
    is_active: bool = True


class BookingStatusUpdateIn(BaseModel):
    status: str = Field(
        pattern=r"^(confirmed|technician_assigned|en_route|in_progress|completed)$"
    )
    metadata: dict | None = None


class TechnicianLocationUpdateIn(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    booking_id: UUID | None = None


class AdminServiceUpdate(BaseModel):
    category_id: UUID | None = None
    name_ar: str | None = Field(default=None, min_length=1, max_length=120)
    subtitle_ar: str | None = Field(default=None, max_length=200)
    icon_key: str | None = Field(default=None, max_length=40)
    price_sar: float | None = Field(default=None, gt=0)
    duration_minutes: int | None = Field(default=None, gt=0, le=480)
    is_active: bool | None = None


class VendorApplicationIn(BaseModel):
    business_name: str = Field(..., min_length=2, max_length=120)
    contact_name: str = Field(..., min_length=2, max_length=120)
    email: str = Field(..., min_length=5, max_length=255)
    phone: str = Field(..., min_length=8, max_length=20)
    city: str = Field(default="الرياض", min_length=2, max_length=60)
    bank_name: str = Field(..., min_length=2, max_length=80)
    account_holder: str = Field(..., min_length=2, max_length=120)
    iban: str = Field(..., min_length=15, max_length=34)
    national_id: str | None = Field(default=None, max_length=20)
    commercial_reg: str | None = Field(default=None, max_length=40)


class VendorFinancialsUpdateIn(BaseModel):
    bank_name: str = Field(..., min_length=2, max_length=80)
    account_holder: str = Field(..., min_length=2, max_length=120)
    iban: str = Field(..., min_length=15, max_length=34)


class VendorRejectIn(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500)


class VendorBaseLocationIn(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    service_radius_km: float | None = Field(default=None, gt=0, le=100)


class VendorLiveLocationIn(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    booking_id: UUID | None = None


class VendorAvailabilityIn(BaseModel):
    is_available: bool


class TowingDispatchCreateIn(BaseModel):
    booking_id: UUID
    pickup_label: str = Field(..., min_length=2, max_length=120)
    pickup_lat: float = Field(ge=-90, le=90)
    pickup_lng: float = Field(ge=-180, le=180)
    dropoff_label: str = Field(..., min_length=2, max_length=120)
    dropoff_lat: float = Field(ge=-90, le=90)
    dropoff_lng: float = Field(ge=-180, le=180)
    notes: str | None = Field(default=None, max_length=500)


class TowingDispatchAssignIn(BaseModel):
    technician_id: UUID


class TowingLocationUpdateIn(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
