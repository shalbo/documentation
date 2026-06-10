import os

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.support_services import CATEGORY_LABELS, STATUS_LABELS

DEV_USER = "a0000000-0000-4000-8000-000000000001"
TICKET_ID = "st000000-0000-4000-8000-000000000001"
USER_HEADERS = {"X-User-Id": DEV_USER}
ADMIN_HEADERS = {"X-Admin-Key": "rousto_admin_dev"}
HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"

client = TestClient(app)


def test_support_labels_unit():
    assert CATEGORY_LABELS["booking"] == "الحجوزات"
    assert STATUS_LABELS["open"] == "مفتوحة"


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_faq_public():
    response = client.get("/api/v1/support/faq")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) >= 5


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_get_ticket_seed():
    response = client.get(
        f"/api/v1/support/tickets/{TICKET_ID}",
        headers=USER_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["reference"] == "SUP-2026-001"
    assert len(data["messages"]) >= 2


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_security_summary():
    response = client.get("/api/v1/me/security", headers=USER_HEADERS)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["login_alerts_enabled"] is True
    assert data["open_tickets_count"] >= 1
    assert len(data["recent_events"]) >= 1


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_create_ticket():
    response = client.post(
        "/api/v1/support/tickets",
        headers=USER_HEADERS,
        json={
            "category": "technical",
            "subject": "مشكلة في التطبيق",
            "message": "التطبيق يتوقف عند فتح شاشة التتبّع",
            "priority": "normal",
        },
    )
    assert response.status_code == 201
    assert response.json()["data"]["reference"].startswith("SUP-")


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_admin_security_events():
    response = client.get("/api/v1/admin/security/events", headers=ADMIN_HEADERS)
    assert response.status_code == 200
    assert response.json()["meta"]["total"] >= 1


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_admin_reply_ticket():
    response = client.post(
        f"/api/v1/admin/support/tickets/{TICKET_ID}/reply",
        headers=ADMIN_HEADERS,
        json={"message": "شكراً لصبرك، تم حل المشكلة.", "status": "resolved"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "resolved"
