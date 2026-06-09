import os

import pytest
from fastapi.testclient import TestClient

from app.main import app

DEV_USER = "a0000000-0000-4000-8000-000000000001"
HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "Rousto API"


def test_health_endpoint_shape():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert "status" in body["data"]
    assert "database" in body["data"]


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_categories_tree():
    response = client.get("/api/v1/categories/tree")
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert "meta" in body
    assert body["meta"]["total_categories"] == 6
    assert body["meta"]["total_services"] == 6

    all_node = next(n for n in body["data"] if n["slug"] == "all")
    assert all_node["services_count"] == 6
    assert len(all_node["services"]) == 6

    oil_node = next(n for n in body["data"] if n["slug"] == "oil")
    assert oil_node["services_count"] == 1
    assert oil_node["services"][0]["slug"] == "oil-change"


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_services_public():
    response = client.get("/api/v1/services")
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert "meta" in body
    assert body["meta"]["total"] == 6


def test_unauthorized_without_header():
    response = client.get("/api/v1/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_me_with_seed_user():
    response = client.get("/api/v1/me", headers={"X-User-Id": DEV_USER})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["full_name"] == "سعود العتيبي"
    assert data["loyalty_points"] == 320


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_active_booking():
    response = client.get(
        "/api/v1/bookings/active", headers={"X-User-Id": DEV_USER}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data is not None
    assert data["reference"] == "RST-2026-001"
    assert data["status"] == "en_route"


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_monetization_plans():
    response = client.get("/api/v1/monetization/plans")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 3
    assert data[0]["slug"] == "free"
    assert data[1]["slug"] == "gold"


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_me_monetization():
    response = client.get(
        "/api/v1/me/monetization", headers={"X-User-Id": DEV_USER}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["loyalty"]["balance"] == 320
    assert data["membership"]["plan_slug"] == "free"


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_promotion_validate():
    response = client.post(
        "/api/v1/promotions/validate",
        headers={"X-User-Id": DEV_USER},
        json={"code": "ROUSTO", "service_price_sar": 120.0},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["valid"] is True
    assert data["discount_sar"] == 30.0
    assert data["total_sar"] == 90.0
