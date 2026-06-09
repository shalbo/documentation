import io
import os

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.ai_diagnosis import analyze, get_scan_type_catalog, is_valid_scan_type
from app.main import app

DEV_USER = "a0000000-0000-4000-8000-000000000001"
VEHICLE_ID = "b0000000-0000-4000-8000-000000000001"
SEED_SCAN_ID = "s0000000-0000-4000-8000-000000000001"
HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"

client = TestClient(app)
headers = {"X-User-Id": DEV_USER}


def _jpeg_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (64, 64), color=(200, 40, 40)).save(buf, format="JPEG")
    return buf.getvalue()


def test_scan_types_public():
    response = client.get("/api/v1/scans/types")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 5
    assert data[0]["id"] == "dashboard_warning"


def test_analyze_stub_profiles():
    assert is_valid_scan_type("tire_tread")
    findings = analyze("tire_tread", image_count=1)
    assert findings[0].service_slug == "tires"
    assert get_scan_type_catalog()


def test_create_scan_requires_auth():
    response = client.post(
        "/api/v1/scans",
        data={"vehicle_id": VEHICLE_ID, "scan_type": "dashboard_warning"},
        files={"images": ("test.jpg", _jpeg_bytes(), "image/jpeg")},
    )
    assert response.status_code == 401


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_create_scan_and_list():
    response = client.post(
        "/api/v1/scans",
        headers=headers,
        data={"vehicle_id": VEHICLE_ID, "scan_type": "battery_corrosion"},
        files={"images": ("battery.jpg", _jpeg_bytes(), "image/jpeg")},
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["status"] == "completed"
    assert len(data["findings"]) == 1
    assert data["findings"][0]["suggested_service"]["slug"] == "battery"

    listing = client.get("/api/v1/me/scans", headers=headers)
    assert listing.status_code == 200
    assert listing.json()["meta"]["total"] >= 2


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_get_seed_scan():
    response = client.get(f"/api/v1/scans/{SEED_SCAN_ID}", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["scan_type"] == "dashboard_warning"
    assert data["findings"][0]["code"] == "check_engine"
