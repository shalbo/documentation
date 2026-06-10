import os

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.vendor_map_services import _location_point, require_approved_vendor
from unittest.mock import MagicMock

DEV_VENDOR_APPROVED = "v0000000-0000-4000-8000-000000000001"
DEV_VENDOR_PENDING = "v0000000-0000-4000-8000-000000000002"
BOOKING_ID = "i0000000-0000-4000-8000-000000000001"
ADMIN_HEADERS = {"X-Admin-Key": "rousto_admin_dev"}
VENDOR_HEADERS = {"X-Vendor-Id": DEV_VENDOR_APPROVED}
HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"

client = TestClient(app)


def test_location_point_unit():
    assert _location_point(24.77, 46.735) == {"lat": 24.77, "lng": 46.735}
    assert _location_point(None, 46.735) is None


def test_require_approved_vendor_unit():
    pending = MagicMock(status="pending", technician_id=None)
    with pytest.raises(ValueError):
        require_approved_vendor(pending)


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_vendor_map_seed():
    response = client.get("/api/v1/vendor/me/map", headers=VENDOR_HEADERS)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["business_name"] == "خدمات أحمد للسيارات"
    assert data["base_location"]["lat"] == 24.77
    assert data["live_location"] is not None
    assert data["active_job"]["reference"] == "RST-2026-001"
    assert data["active_job"]["destination"] is not None


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_vendor_active_job():
    response = client.get("/api/v1/vendor/me/jobs/active", headers=VENDOR_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["has_active_job"] is True
    assert body["data"]["booking_id"] == BOOKING_ID


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_vendor_update_live_location():
    response = client.patch(
        "/api/v1/vendor/me/location/live",
        headers=VENDOR_HEADERS,
        json={"lat": 24.771, "lng": 46.736, "booking_id": BOOKING_ID},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["live_location"]["lat"] == 24.771


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_admin_vendors_map():
    response = client.get("/api/v1/admin/vendors/map", headers=ADMIN_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["total"] >= 1
    assert any(v["vendor_id"] == DEV_VENDOR_APPROVED for v in body["data"])


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_pending_vendor_map_forbidden():
    response = client.get(
        "/api/v1/vendor/me/map",
        headers={"X-Vendor-Id": DEV_VENDOR_PENDING},
    )
    assert response.status_code == 400
