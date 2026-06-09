import os

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.towing_dispatch_services import _active_leg, _map_bounds

DEV_USER = "a0000000-0000-4000-8000-000000000001"
DISPATCH_ID = "td000000-0000-4000-8000-000000000001"
TOW_DRIVER_ID = "g0000000-0000-4000-8000-000000000002"
ADMIN_HEADERS = {"X-Admin-Key": "rousto_admin_dev"}
USER_HEADERS = {"X-User-Id": DEV_USER}
HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"

client = TestClient(app)


def test_active_leg_unit():
    assert _active_leg("en_route_pickup") == "to_pickup"
    assert _active_leg("en_route_dropoff") == "to_dropoff"
    assert _active_leg("completed") is None


def test_map_bounds_unit():
    bounds = _map_bounds([(24.77, 46.73), (24.71, 46.67)])
    assert bounds["min_lat"] < 24.71


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_towing_dispatch_map_seed():
    response = client.get(
        f"/api/v1/towing/dispatches/{DISPATCH_ID}/map",
        headers=USER_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["dispatch"]["reference"] == "TOW-2026-001"
    assert data["active_leg"] == "to_pickup"
    assert data["pickup"]["label"].startswith("موقع العطل")
    assert data["dropoff"]["label"].startswith("ورشة روستو")
    assert data["tow_truck"]["full_name"] == "سعد السطحة"
    assert data["is_live"] is True
    assert len(data["trail"]) >= 1


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_active_towing_map():
    response = client.get(
        "/api/v1/towing/dispatches/active/map",
        headers=USER_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["dispatch"]["id"] == DISPATCH_ID


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_admin_towing_dispatches_map():
    response = client.get(
        "/api/v1/admin/towing/dispatches/map",
        headers=ADMIN_HEADERS,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["total"] >= 1


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_admin_advance_dispatch():
    response = client.post(
        f"/api/v1/admin/towing/dispatches/{DISPATCH_ID}/advance",
        headers=ADMIN_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["dispatch"]["status"] == "at_pickup"
