import os
import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.tier_services import (
    UNLIMITED_PRODUCTS,
    is_unlimited_products,
    products_limit_label,
    resolve_vendor_tier,
    update_tier,
)
from app.models import Tier, Vendor

HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"
STARTER_ID = "a1000000-0000-4000-8000-000000000001"
GOLD_ID = "a1000000-0000-4000-8000-000000000003"
VENDOR_ID = "v0000000-0000-4000-8000-000000000001"
PENDING_VENDOR_ID = "v0000000-0000-4000-8000-000000000002"

client = TestClient(app)
headers = {"X-Admin-Key": "rousto_admin_dev"}


def test_unlimited_products_flag():
    assert is_unlimited_products(-1) is True
    assert is_unlimited_products(3000) is False
    assert products_limit_label(-1) == "غير محدود"
    assert products_limit_label(50) == "50"


def test_update_tier_rejects_invalid_products_limit():
    tier = Tier(
        id=uuid.uuid4(),
        slug="test",
        name_ar="اختبار",
        name_en="Test",
        price=0,
        products_limit=50,
        allow_excel_upload=False,
        allow_vin_decoder=False,
        allow_unlimited_chat=False,
        has_gold_badge=False,
        sort_order=0,
        is_active=True,
        created_at=None,
        updated_at=None,
    )

    class FakeDB:
        def flush(self):
            pass

    with pytest.raises(ValueError, match="-1"):
        update_tier(FakeDB(), tier, products_limit=-5)


def test_admin_tiers_list_requires_key():
    res = client.get("/api/v1/admin/tiers")
    assert res.status_code == 401


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with migrated PostgreSQL")
def test_admin_tiers_list_with_key():
    res = client.get("/api/v1/admin/tiers", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert "data" in body


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with migrated PostgreSQL")
def test_admin_update_tier_validation():
    res = client.put(
        f"/api/v1/admin/tiers/{STARTER_ID}",
        headers=headers,
        json={"products_limit": -5},
    )
    assert res.status_code in (400, 404, 422)


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with migrated PostgreSQL")
def test_admin_update_tier_unlimited_products():
    res = client.put(
        f"/api/v1/admin/tiers/{STARTER_ID}",
        headers=headers,
        json={"products_limit": UNLIMITED_PRODUCTS},
    )
    if res.status_code == 404:
        pytest.skip("Seed tiers not loaded")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["products_limit"] == -1
    assert data["is_unlimited_products"] is True
    client.put(
        f"/api/v1/admin/tiers/{STARTER_ID}",
        headers=headers,
        json={"products_limit": 50},
    )


@pytest.mark.skipif(not HAS_DB, reason="ROUSTO_TEST_DB=1 required")
def test_vendor_tier_resolution_from_db():
    from sqlalchemy import select

    from app.db import SessionLocal

    db = SessionLocal()
    try:
        vendor = db.scalar(
            select(Vendor).where(Vendor.email == "ahmad.vendor@example.com")
        )
        assert vendor is not None
        tier = resolve_vendor_tier(db, vendor)
        assert str(tier.id) == GOLD_ID
        assert tier.has_gold_badge is True
    finally:
        db.close()


@pytest.mark.skipif(not HAS_DB, reason="ROUSTO_TEST_DB=1 required")
def test_starter_tier_blocks_excel_upload():
    from sqlalchemy import select

    from app.db import SessionLocal
    from app.tier_services import require_excel_upload

    db = SessionLocal()
    try:
        vendor = db.scalar(
            select(Vendor).where(Vendor.email == "khalid.vendor@example.com")
        )
        assert vendor is not None
        with pytest.raises(ValueError, match="Excel"):
            require_excel_upload(db, vendor)
    finally:
        db.close()


@pytest.mark.skipif(not HAS_DB, reason="ROUSTO_TEST_DB=1 required")
def test_vendor_tier_api_endpoint():
    res = client.get("/api/v1/vendor/parts/tier", headers={"X-Vendor-Id": VENDOR_ID})
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["tier"]["slug"] == "gold"
    assert data["usage"]["products_count"] >= 0
