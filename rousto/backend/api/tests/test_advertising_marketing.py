import os
import re

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.marketing_services import validate_referral_code

HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"

client = TestClient(app)


def test_email_regex_unit():
    assert re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", "demo@rousto.sa")
    assert not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", "invalid")


def test_validate_referral_invalid_unit():
    class FakeDb:
        def scalar(self, _):
            return None

    result = validate_referral_code(FakeDb(), "BADCODE")
    assert result["valid"] is False


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_marketing_partners():
    response = client.get("/api/v1/marketing/partners")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) >= 7
    slugs = {p["slug"] for p in data}
    assert "toyota" in slugs


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_marketing_banners_home_hero():
    response = client.get("/api/v1/marketing/banners?placement=home_hero")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) >= 1
    assert data[0]["placement"] == "home_hero"


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_referral_validate_saud():
    response = client.get("/api/v1/marketing/referrals/validate?code=SAUD100")
    assert response.status_code == 200
    assert response.json()["data"]["valid"] is True
    assert response.json()["data"]["reward_points"] == 100


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_newsletter_subscribe():
    response = client.post(
        "/api/v1/marketing/newsletter/subscribe",
        json={"email": "new@rousto.sa", "source": "landing"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["subscribed"] is True


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_landing_page_includes_marketing():
    response = client.get("/api/v1/landing/page")
    assert response.status_code == 200
    marketing = response.json()["data"]["marketing"]
    assert len(marketing["partners"]) >= 7
    assert len(marketing["banners"]) >= 1


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_admin_marketing_analytics():
    response = client.get(
        "/api/v1/admin/marketing/analytics",
        headers={"X-Admin-Key": "rousto_admin_dev"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["campaigns_total"] >= 2
    assert data["partners_active"] >= 7
