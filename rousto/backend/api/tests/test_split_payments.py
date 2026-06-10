import os
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.split_payments import calculate_split_legs

DEV_USER = "a0000000-0000-4000-8000-000000000001"
BOOKING_ID = "i0000000-0000-4000-8000-000000000001"
ADMIN_HEADERS = {"X-Admin-Key": "rousto_admin_dev"}
USER_HEADERS = {"X-User-Id": DEV_USER}
HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"

client = TestClient(app)


def test_calculate_split_legs_unit():
    rule = MagicMock()
    rule.platform_rate = 0.15
    rule.technician_rate = 0.75
    rule.reserve_rate = 0.10
    legs = {l["recipient_type"]: l for l in calculate_split_legs(90, rule)}
    assert legs["platform"]["amount_sar"] == 13.5
    assert legs["technician"]["amount_sar"] == 67.5
    assert legs["reserve"]["amount_sar"] == 9.0


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_split_rules_public():
    response = client.get("/api/v1/payments/split-rules")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) >= 1
    default = next(r for r in data if r["is_default"])
    assert default["platform_rate"] == 0.15
    assert default["technician_rate"] == 0.75


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_split_preview():
    response = client.post(
        "/api/v1/payments/split/preview",
        json={"amount_sar": 90},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["amount_sar"] == 90.0
    legs = {leg["recipient_type"]: leg for leg in data["legs"]}
    assert legs["platform"]["amount_sar"] == 13.5
    assert legs["technician"]["amount_sar"] == 67.5
    assert legs["reserve"]["amount_sar"] == 9.0


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_booking_payment_split_seed():
    response = client.get(
        f"/api/v1/bookings/{BOOKING_ID}/payment-split",
        headers=USER_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["net_sar"] == 90.0
    assert len(data["legs"]) == 3
    tech = next(l for l in data["legs"] if l["recipient_type"] == "technician")
    assert tech["amount_sar"] == 67.5
    assert tech["status"] == "held"


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_admin_release_technician_split():
    response = client.post(
        "/api/v1/payments/splits/release",
        headers=ADMIN_HEADERS,
        json={"booking_id": BOOKING_ID, "recipient_type": "technician"},
    )
    assert response.status_code == 200
    tech = next(
        l
        for l in response.json()["data"]["legs"]
        if l["recipient_type"] == "technician"
    )
    assert tech["status"] == "released"
