import os

import pytest
from fastapi.testclient import TestClient

from app.customer_delivery_services import _map_bounds, _progress_percent
from app.main import app

DEV_USER = "a0000000-0000-4000-8000-000000000001"
BOOKING_ID = "i0000000-0000-4000-8000-000000000001"
USER_HEADERS = {"X-User-Id": DEV_USER}
HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"

client = TestClient(app)


def test_progress_percent_unit():
    assert _progress_percent(0.2, 1.0, "en_route") == 80.0
    assert _progress_percent(None, 1.0, "en_route") is None
    assert _progress_percent(0.5, 1.0, "completed") == 100.0
    assert _progress_percent(0.5, 1.0, "in_progress") == 95.0


def test_map_bounds_unit():
    bounds = _map_bounds([(24.77, 46.735), (24.774, 46.738)])
    assert bounds is not None
    assert bounds["min_lat"] < 24.77
    assert bounds["max_lat"] > 24.774


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_booking_delivery_map_seed():
    response = client.get(
        f"/api/v1/bookings/{BOOKING_ID}/delivery-map",
        headers=USER_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["booking"]["reference"] == "RST-2026-001"
    assert data["delivery_phase"] == "en_route"
    assert data["is_live"] is True
    assert data["customer_location"] is not None
    assert len(data["trail"]) >= 2
    assert data["map_bounds"] is not None
    assert data["progress_percent"] is not None


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_active_delivery_map():
    response = client.get(
        "/api/v1/bookings/active/delivery-map",
        headers=USER_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data is not None
    assert data["booking"]["id"] == BOOKING_ID
    assert data["refresh_interval_seconds"] == 20


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_delivery_map_requires_auth():
    response = client.get(f"/api/v1/bookings/{BOOKING_ID}/delivery-map")
    assert response.status_code == 401
