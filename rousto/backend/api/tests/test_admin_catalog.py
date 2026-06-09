import os

import pytest
from fastapi.testclient import TestClient

from app.main import app

ADMIN_KEY = "rousto_admin_dev"
OIL_CATEGORY = "e0000000-0000-4000-8000-000000000002"
ALL_CATEGORY = "e0000000-0000-4000-8000-000000000001"
OIL_SERVICE = "f0000000-0000-4000-8000-000000000001"
HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"

client = TestClient(app)
headers = {"X-Admin-Key": ADMIN_KEY}


def test_admin_unauthorized_without_key():
    response = client.get("/api/v1/admin/categories")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_admin_list_categories_includes_inactive():
    response = client.get("/api/v1/admin/categories", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 6
    assert any(c["slug"] == "all" for c in data)


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_admin_create_and_deactivate_service():
    create = client.post(
        "/api/v1/admin/services",
        headers=headers,
        json={
            "category_id": OIL_CATEGORY,
            "slug": "test-admin-service",
            "name_ar": "خدمة اختبار",
            "price_sar": 99,
            "duration_minutes": 20,
        },
    )
    assert create.status_code == 201
    service_id = create.json()["data"]["id"]

    public = client.get("/api/v1/services")
    assert any(s["slug"] == "test-admin-service" for s in public.json()["data"])

    deactivate = client.patch(
        f"/api/v1/admin/services/{service_id}",
        headers=headers,
        json={"is_active": False},
    )
    assert deactivate.status_code == 200

    public_after = client.get("/api/v1/services")
    assert not any(s["slug"] == "test-admin-service" for s in public_after.json()["data"])


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_admin_cannot_deactivate_all_category():
    response = client.patch(
        f"/api/v1/admin/categories/{ALL_CATEGORY}",
        headers=headers,
        json={"is_active": False},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PROTECTED_CATEGORY"


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_admin_cannot_assign_service_to_all_category():
    response = client.post(
        "/api/v1/admin/services",
        headers=headers,
        json={
            "category_id": ALL_CATEGORY,
            "slug": "bad-service",
            "name_ar": "خدمة خاطئة",
            "price_sar": 50,
            "duration_minutes": 10,
        },
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_CATEGORY"


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_admin_update_service_price():
    response = client.patch(
        f"/api/v1/admin/services/{OIL_SERVICE}",
        headers=headers,
        json={"price_sar": 125},
    )
    assert response.status_code == 200
    assert response.json()["data"]["price_sar"] == 125.0

    client.patch(
        f"/api/v1/admin/services/{OIL_SERVICE}",
        headers=headers,
        json={"price_sar": 120},
    )
