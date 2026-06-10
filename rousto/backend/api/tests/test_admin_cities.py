import os

import pytest
from fastapi.testclient import TestClient

from app.city_services import VALID_REGIONS
from app.main import app

ADMIN_KEY = "rousto_admin_dev"
HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"

client = TestClient(app)
headers = {"X-Admin-Key": ADMIN_KEY}


def test_valid_regions_match_spec():
    assert VALID_REGIONS == {"West", "East", "South"}


def test_admin_cities_unauthorized_without_key():
    response = client.get("/api/v1/admin/cities")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_admin_create_city_validation():
    response = client.post(
        "/api/v1/admin/cities",
        headers=headers,
        json={"name_ar": "ا", "name_en": "X", "region": "West"},
    )
    assert response.status_code == 422


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_admin_list_cities_includes_seeded():
    response = client.get("/api/v1/admin/cities", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) >= 28
    assert any(c["name_ar"] == "طرابلس" for c in data)


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_admin_create_update_deactivate_city():
    create = client.post(
        "/api/v1/admin/cities",
        headers=headers,
        json={
            "name_ar": "مدينة اختبار",
            "name_en": "Test Admin City",
            "region": "West",
        },
    )
    assert create.status_code == 201
    city_id = create.json()["data"]["id"]

    public = client.get("/api/v1/cities")
    assert any(c["name_en"] == "Test Admin City" for c in public.json()["data"])

    update = client.patch(
        f"/api/v1/admin/cities/{city_id}",
        headers=headers,
        json={"name_ar": "مدينة اختبار محدّثة"},
    )
    assert update.status_code == 200
    assert update.json()["data"]["name_ar"] == "مدينة اختبار محدّثة"

    deactivate = client.patch(
        f"/api/v1/admin/cities/{city_id}",
        headers=headers,
        json={"is_active": False},
    )
    assert deactivate.status_code == 200
    assert deactivate.json()["data"]["is_active"] is False

    public_after = client.get("/api/v1/cities")
    assert not any(c["name_en"] == "Test Admin City" for c in public_after.json()["data"])

    admin_all = client.get("/api/v1/admin/cities?active=false", headers=headers)
    assert any(c["name_en"] == "Test Admin City" for c in admin_all.json()["data"])


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_admin_cities_region_filter():
    response = client.get("/api/v1/admin/cities?region=South", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert all(c["region"] == "South" for c in data)
    assert len(data) >= 6
