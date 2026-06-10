import os

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.parts_services import _part_has_only_inactive_vendor_stock, _vendor_store_visible

DEV_VENDOR = "v0000000-0000-4000-8000-000000000001"
HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"

client = TestClient(app)
headers = {"X-Vendor-Id": DEV_VENDOR}


def test_vendor_store_visible_tuple():
    assert len(_vendor_store_visible()) == 2


def test_toggle_requires_vendor_auth():
    response = client.patch("/api/v1/vendor/status/toggle")
    assert response.status_code == 401


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_vendor_me_includes_is_active():
    response = client.get("/api/v1/vendor/me", headers=headers)
    assert response.status_code == 200
    assert "is_active" in response.json()["data"]


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_vendor_status_toggle_flips_and_restores():
    me = client.get("/api/v1/vendor/me", headers=headers).json()["data"]
    original = me["is_active"]

    toggled = client.patch("/api/v1/vendor/status/toggle", headers=headers)
    assert toggled.status_code == 200
    data = toggled.json()["data"]
    assert data["is_active"] is not original
    assert "message_ar" in data

    restored = client.patch("/api/v1/vendor/status/toggle", headers=headers)
    assert restored.status_code == 200
    assert restored.json()["data"]["is_active"] is original


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_inactive_vendor_parts_hidden_from_search():
    from app.db import SessionLocal

    client.patch("/api/v1/vendor/status/toggle", headers=headers)
    try:
        search = client.get("/api/v1/parts/search?in_stock_only=true&limit=100")
        assert search.status_code == 200
        db = SessionLocal()
        try:
            from app.models import Part, PartInventory
            from sqlalchemy import select

            inv = db.scalar(
                select(PartInventory).where(PartInventory.vendor_id == DEV_VENDOR).limit(1)
            )
            if inv:
                part = db.get(Part, inv.part_id)
                if part:
                    ids = {p["id"] for p in search.json()["data"]}
                    assert str(part.id) not in ids or _part_has_only_inactive_vendor_stock(
                        db, part.id
                    )
        finally:
            db.close()
    finally:
        client.patch("/api/v1/vendor/status/toggle", headers=headers)
