import os

import pytest
from fastapi.testclient import TestClient

from app.landing_pricing_services import CURRENCY_AR, ICON_EMOJI, _service_icon
from app.main import app

HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"

client = TestClient(app)


def test_service_icon_unit():
    assert _service_icon("oil_barrel") == ICON_EMOJI["oil_barrel"]
    assert _service_icon(None) == "🔧"
    assert CURRENCY_AR == "دينار"


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_landing_pricing():
    response = client.get("/api/v1/landing/pricing")
    assert response.status_code == 200
    body = response.json()
    data = body["data"]
    assert body["meta"]["currency"] == "دينار"
    assert len(data["services"]) >= 6
    assert len(data["marketing_plans"]) >= 3
    assert len(data["membership_plans"]) >= 3
    assert len(data["packages"]) >= 2
    family = next(p for p in data["marketing_plans"] if p["slug"] == "family")
    assert family["is_featured"] is True
    assert family["badge_ar"] == "الأكثر شعبية"


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_landing_page():
    response = client.get("/api/v1/landing/page")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["hero"]["stats"]) >= 4
    assert len(data["features"]) >= 4
    assert len(data["pricing"]["services"]) >= 6
    slugs = {s["slug"] for s in data["hero"]["stats"]}
    assert "happy_customers" in slugs
    assert "rating" in slugs
