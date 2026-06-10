"""Libyan-only payment gateway registry — international gateways blocked."""

from __future__ import annotations

from app.gateways.edfali import EdfaliGateway
from app.gateways.muamalat import MuamalatGateway
from app.gateways.sadad import SadadGateway

LIBYAN_GATEWAY_SLUGS = frozenset({"cod", "wallet", "muamalat", "sadad", "edfali"})
BLOCKED_GATEWAYS = frozenset(
    {"stripe", "paypal", "hyperpay", "mada", "apple_pay", "visa", "mastercard"}
)

_ADAPTERS = {
    "muamalat": MuamalatGateway(),
    "sadad": SadadGateway(),
    "edfali": EdfaliGateway(),
}


def validate_gateway(gateway: str) -> str:
    slug = gateway.strip().lower()
    if slug in BLOCKED_GATEWAYS:
        raise ValueError("بوابات الدفع الدولية غير مدعومة في السوق الليبي")
    if slug not in LIBYAN_GATEWAY_SLUGS:
        raise ValueError("بوابة دفع غير معتمدة — الخيارات المحلية فقط")
    return slug


def get_gateway(slug: str):
    validate_gateway(slug)
    if slug in ("cod", "wallet"):
        return None
    return _ADAPTERS.get(slug)


def list_libyan_gateways() -> list[dict]:
    return [
        {
            "slug": "cod",
            "name_ar": "كاش عند الاستلام",
            "requires_redirect": False,
            "icon": "cash",
        },
        {
            "slug": "wallet",
            "name_ar": "رصيد محفظة Rousto",
            "requires_redirect": False,
            "icon": "wallet",
        },
        {
            "slug": "muamalat",
            "name_ar": "معاملات — مصرف الجمهورية",
            "requires_redirect": True,
            "icon": "card",
        },
        {
            "slug": "sadad",
            "name_ar": "سداد — المدار الجديد",
            "requires_redirect": True,
            "icon": "mobile",
        },
        {
            "slug": "edfali",
            "name_ar": "إدفع لي / تداول كاش",
            "requires_redirect": True,
            "icon": "bank",
        },
    ]
