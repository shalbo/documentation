"""Locale resolution and bilingual content helpers."""

from fastapi import Header, Query

SUPPORTED_LOCALES = frozenset({"ar", "en"})
DEFAULT_LOCALE = "ar"


def parse_locale(
    accept_language: str | None = None,
    lang: str | None = None,
) -> str:
    if lang and lang.lower() in SUPPORTED_LOCALES:
        return lang.lower()
    if accept_language:
        primary = accept_language.split(",")[0].strip().split("-")[0].lower()
        if primary in SUPPORTED_LOCALES:
            return primary
    return DEFAULT_LOCALE


def resolve_locale(
    accept_language: str | None = Header(default=None, alias="Accept-Language"),
    lang: str | None = Query(default=None, alias="lang"),
) -> str:
    return parse_locale(accept_language, lang)


def pick_localized(obj, field_base: str, locale: str, *, fallback: str = "") -> str:
    ar_val = getattr(obj, f"{field_base}_ar", None)
    if locale == "en":
        en_val = getattr(obj, f"{field_base}_en", None)
        if en_val:
            return en_val
    return ar_val or fallback


def label_from_map(labels: dict[str, dict[str, str]], key: str, locale: str) -> str:
    bucket = labels.get(key, {})
    return bucket.get(locale) or bucket.get("ar") or key


BOOKING_STATUS_LABELS: dict[str, dict[str, str]] = {
    "pending": {"ar": "بانتظار التأكيد", "en": "Pending confirmation"},
    "confirmed": {"ar": "مؤكد", "en": "Confirmed"},
    "technician_assigned": {"ar": "تم تعيين الفني", "en": "Technician assigned"},
    "en_route": {"ar": "جارية", "en": "En route"},
    "in_progress": {"ar": "قيد التنفيذ", "en": "In progress"},
    "completed": {"ar": "مكتمل", "en": "Completed"},
    "cancelled": {"ar": "ملغى", "en": "Cancelled"},
}

BOOKING_EVENT_LABELS: dict[str, dict[str, str]] = {
    "confirmed": {"ar": "تم تأكيد الحجز", "en": "Booking confirmed"},
    "technician_assigned": {"ar": "تم تعيين الفني", "en": "Technician assigned"},
    "en_route": {"ar": "الفني في الطريق إليك", "en": "Technician is on the way"},
    "in_progress": {"ar": "تنفيذ الخدمة", "en": "Service in progress"},
    "completed": {"ar": "اكتمال الخدمة", "en": "Service completed"},
}

SUPPORT_CATEGORY_LABELS: dict[str, dict[str, str]] = {
    "booking": {"ar": "الحجوزات", "en": "Bookings"},
    "payment": {"ar": "المدفوعات", "en": "Payments"},
    "account": {"ar": "الحساب", "en": "Account"},
    "technical": {"ar": "تقني", "en": "Technical"},
    "other": {"ar": "أخرى", "en": "Other"},
}

SUPPORT_STATUS_LABELS: dict[str, dict[str, str]] = {
    "open": {"ar": "مفتوحة", "en": "Open"},
    "in_progress": {"ar": "قيد المعالجة", "en": "In progress"},
    "waiting_customer": {"ar": "بانتظار العميل", "en": "Waiting for customer"},
    "resolved": {"ar": "محلولة", "en": "Resolved"},
    "closed": {"ar": "مغلقة", "en": "Closed"},
}

TOWING_STATUS_LABELS: dict[str, dict[str, str]] = {
    "pending": {"ar": "طلب سحب جديد", "en": "New towing request"},
    "dispatched": {"ar": "تم تعيين السطحة", "en": "Tow truck assigned"},
    "en_route_pickup": {"ar": "متجه لموقع العطل", "en": "En route to pickup"},
    "at_pickup": {"ar": "عند السيارة", "en": "At vehicle location"},
    "en_route_dropoff": {"ar": "متجه للورشة", "en": "En route to workshop"},
    "completed": {"ar": "تم التسليم", "en": "Delivered"},
    "cancelled": {"ar": "ملغى", "en": "Cancelled"},
}

NOTIFICATION_CATEGORY_LABELS: dict[str, dict[str, str]] = {
    "booking": {"ar": "الحجوزات", "en": "Bookings"},
    "support": {"ar": "الدعم", "en": "Support"},
    "towing": {"ar": "السطحات", "en": "Towing"},
    "promo": {"ar": "العروض", "en": "Promotions"},
    "security": {"ar": "الأمان", "en": "Security"},
    "system": {"ar": "النظام", "en": "System"},
}

ERROR_MESSAGES: dict[str, dict[str, str]] = {
    "RATE_LIMITED": {
        "ar": "تجاوزت الحد المسموح من المحاولات، حاول لاحقاً",
        "en": "Too many requests. Please try again later.",
    },
    "UNAUTHORIZED": {
        "ar": "مطلوب Authorization Bearer",
        "en": "Authorization Bearer token required.",
    },
    "FORBIDDEN": {
        "ar": "غير مسموح بالوصول",
        "en": "Access denied.",
    },
    "NOT_FOUND": {
        "ar": "غير موجود",
        "en": "Not found.",
    },
    "INTERNAL_ERROR": {
        "ar": "حدث خطأ داخلي، تم تسجيله",
        "en": "An internal error occurred and has been logged.",
    },
}


def error_message(code: str, locale: str, *, override_ar: str | None = None) -> str:
    if override_ar and locale == "ar":
        return override_ar
    bucket = ERROR_MESSAGES.get(code, {})
    return bucket.get(locale) or bucket.get("ar") or override_ar or code
