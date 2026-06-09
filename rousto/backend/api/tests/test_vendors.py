import os

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.vendor_services import mask_iban, validate_iban

DEV_VENDOR_APPROVED = "v0000000-0000-4000-8000-000000000001"
DEV_VENDOR_PENDING = "v0000000-0000-4000-8000-000000000002"
ADMIN_HEADERS = {"X-Admin-Key": "rousto_admin_dev"}
VENDOR_HEADERS = {"X-Vendor-Id": DEV_VENDOR_APPROVED}
HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"

client = TestClient(app)


def test_validate_iban_unit():
    assert validate_iban("SA0380000000608010167519") == "SA0380000000608010167519"
    assert validate_iban("sa0380000000608010167519") == "SA0380000000608010167519"
    assert validate_iban("  SA0380000000608010167519  ") == "SA0380000000608010167519"


def test_validate_iban_invalid_unit():
    with pytest.raises(ValueError):
        validate_iban("SA123")


def test_mask_iban_unit():
    assert mask_iban("SA0380000000608010167519") == "SA03****7519"


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_admin_list_pending_vendors():
    response = client.get(
        "/api/v1/admin/vendors?status=pending",
        headers=ADMIN_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert any(v["id"] == DEV_VENDOR_PENDING for v in data)


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_vendor_me_approved():
    response = client.get("/api/v1/vendor/me", headers=VENDOR_HEADERS)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "approved"
    assert data["technician_id"] == "g0000000-0000-4000-8000-000000000001"
    assert data["bank_account"]["iban_masked"] == "SA03****7519"
    assert data["payout_summary"]["total_earned_sar"] == 67.5
    assert data["payout_summary"]["pending_sar"] == 67.5


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_vendor_payouts():
    response = client.get("/api/v1/vendor/me/payouts", headers=VENDOR_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["total"] >= 1
    assert body["meta"]["summary"]["legs_count"] >= 1


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_submit_vendor_application():
    response = client.post(
        "/api/v1/vendors/applications",
        json={
            "business_name": "ورشة الاختبار",
            "contact_name": "فهد السبيعي",
            "email": "fahd.test.vendor@example.com",
            "phone": "+966559998877",
            "city": "الرياض",
            "bank_name": "بنك الرياض",
            "account_holder": "فهد السبيعي",
            "iban": "SA442000000000001234567890",
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "pending"
    assert data["bank_account"]["iban_masked"].startswith("SA44")


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_admin_approve_pending_vendor():
    create = client.post(
        "/api/v1/vendors/applications",
        json={
            "business_name": "ورشة الموافقة",
            "contact_name": "سعد القحطاني",
            "email": "saad.approve.vendor@example.com",
            "phone": "+966558887766",
            "city": "الرياض",
            "bank_name": "البنك السعودي الفرنسي",
            "account_holder": "سعد القحطاني",
            "iban": "SA442000000000001234567891",
        },
    )
    assert create.status_code == 200
    vendor_id = create.json()["data"]["id"]

    response = client.post(
        f"/api/v1/admin/vendors/{vendor_id}/approve",
        headers=ADMIN_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "approved"
    assert data["technician_id"] is not None
