import uuid

import pytest

from app.tier_services import (
    BULK_UPLOAD_TIER_SLUGS,
    DEFAULT_TIER_SLUG,
    PRODUCTS_LIMIT_EXCEEDED_MSG,
    _tier_allows_bulk_upload,
    ensure_products_capacity,
    is_unlimited_products,
)
from app.models import Tier


def test_default_tier_slug_is_standard():
    assert DEFAULT_TIER_SLUG == "standard"


def test_bulk_upload_allowed_slugs():
    assert BULK_UPLOAD_TIER_SLUGS == frozenset({"professional", "enterprise"})


def test_tier_allows_bulk_upload():
    pro = Tier(
        id=uuid.uuid4(),
        slug="professional",
        name_ar="احترافية",
        name_en="Pro",
        price=99,
        products_limit=500,
        allow_excel_upload=True,
        allow_vin_decoder=True,
        allow_unlimited_chat=False,
        has_gold_badge=False,
        search_priority=200,
        sort_order=2,
        is_active=True,
        created_at=None,
        updated_at=None,
    )
    std = Tier(
        id=uuid.uuid4(),
        slug="standard",
        name_ar="قياسية",
        name_en="Std",
        price=0,
        products_limit=100,
        allow_excel_upload=False,
        allow_vin_decoder=False,
        allow_unlimited_chat=False,
        has_gold_badge=False,
        search_priority=100,
        sort_order=1,
        is_active=True,
        created_at=None,
        updated_at=None,
    )
    assert _tier_allows_bulk_upload(pro) is True
    assert _tier_allows_bulk_upload(std) is False


def test_standard_limit_message_constant():
    assert "الترقية" in PRODUCTS_LIMIT_EXCEEDED_MSG


def test_ensure_products_capacity_standard_message():
    class FakeVendor:
        id = uuid.uuid4()
        tier_id = None
        tier = None

    tier = Tier(
        id=uuid.uuid4(),
        slug="standard",
        name_ar="قياسية",
        name_en="Standard",
        price=0,
        products_limit=100,
        allow_excel_upload=False,
        allow_vin_decoder=False,
        allow_unlimited_chat=False,
        has_gold_badge=False,
        search_priority=100,
        sort_order=1,
        is_active=True,
        created_at=None,
        updated_at=None,
    )

    class FakeDB:
        def get(self, _model, _id):
            return tier

        def scalar(self, _stmt):
            return 100

    vendor = FakeVendor()

    def fake_resolve(_db, _vendor):
        return tier

    import app.tier_services as ts

    original = ts.resolve_vendor_tier
    ts.resolve_vendor_tier = fake_resolve
    try:
        with pytest.raises(ValueError, match="الترقية"):
            ensure_products_capacity(FakeDB(), vendor)
    finally:
        ts.resolve_vendor_tier = original


def test_unlimited_flag():
    assert is_unlimited_products(-1) is True
