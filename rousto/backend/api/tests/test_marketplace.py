import os

import pytest
from fastapi.testclient import TestClient

from app.logistics_services import haversine_km
from app.main import app

HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"
client = TestClient(app)


def test_haversine_for_vendor_sorting():
    dist = haversine_km(24.7136, 46.6753, 24.77, 46.735)
    assert 5 < dist < 15


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_marketplace_home_endpoint_shape():
    response = client.get("/api/v1/marketplace/home")
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    data = body["data"]
    assert "categories" in data
    assert "featured_parts" in data
    assert "featured_vendors" in data
    assert "promotions" in data
    assert "default_location" in data


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_marketplace_home_has_parts_categories():
    response = client.get("/api/v1/marketplace/home")
    assert response.status_code == 200
    categories = response.json()["data"]["categories"]
    slugs = {c["slug"] for c in categories}
    assert "filters" in slugs or len(categories) >= 1


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_admin_marketplace_analytics():
    response = client.get(
        "/api/v1/admin/marketplace/analytics",
        headers={"X-Admin-Key": "rousto_admin_dev"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "active_parts" in data
    assert "inventory_units" in data
