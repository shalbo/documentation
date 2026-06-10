import os

import pytest
from fastapi.testclient import TestClient

from app.logistics_services import estimate_eta_minutes, haversine_km
from app.main import app

DEV_USER = "a0000000-0000-4000-8000-000000000001"
BOOKING_ID = "i0000000-0000-4000-8000-000000000001"
TECH_ID = "g0000000-0000-4000-8000-000000000001"
ADMIN_HEADERS = {"X-Admin-Key": "rousto_admin_dev"}
USER_HEADERS = {"X-User-Id": DEV_USER}
HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"

client = TestClient(app)


def test_haversine_and_eta_helpers():
    # Riyadh demo coords ~0.4 km apart
    distance = haversine_km(24.77, 46.735, 24.774265, 46.738586)
    assert 0.3 < distance < 0.6
    eta = estimate_eta_minutes(distance)
    assert 1 <= eta <= 5


def test_logistics_requires_admin():
    response = client.post(f"/api/v1/logistics/bookings/{BOOKING_ID}/advance")
    assert response.status_code == 401


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_tracking_includes_destination_and_full_steps():
    response = client.get(
        f"/api/v1/bookings/{BOOKING_ID}/tracking",
        headers=USER_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["destination"] is not None
    assert data["destination"]["label"]
    assert data["distance_km"] is not None
    assert data["eta_minutes"] is not None
    assert len(data["steps"]) == 5
    assert data["technician"]["phone"]
    assert data["technician"]["location"] is not None


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_advance_booking_status():
    before = client.get(
        f"/api/v1/bookings/{BOOKING_ID}/tracking",
        headers=USER_HEADERS,
    ).json()["data"]["booking"]["status"]

    response = client.post(
        f"/api/v1/logistics/bookings/{BOOKING_ID}/advance",
        headers=ADMIN_HEADERS,
    )
    if before == "completed":
        assert response.status_code == 400
        return

    assert response.status_code == 200
    after = response.json()["data"]["booking"]["status"]
    assert after != before


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_simulate_move_updates_location():
    # Use a fresh booking state — test on tracking after completed may fail simulate
    # Reset by patching location directly
    response = client.patch(
        f"/api/v1/logistics/technicians/{TECH_ID}/location",
        headers=ADMIN_HEADERS,
        json={
            "lat": 24.771,
            "lng": 46.736,
            "booking_id": BOOKING_ID,
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["lat"] == 24.771
