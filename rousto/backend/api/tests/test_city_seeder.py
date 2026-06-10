import os
import uuid

import pytest
from fastapi.testclient import TestClient

from app.city_seed_data import LIBYAN_CITIES
from app.main import app

HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"
client = TestClient(app)


def test_libyan_cities_count():
    assert len(LIBYAN_CITIES) == 28


def test_libyan_cities_regions():
    regions = {r for _, _, _, r in LIBYAN_CITIES}
    assert regions == {"West", "East", "South"}
    west = sum(1 for *_, r in LIBYAN_CITIES if r == "West")
    east = sum(1 for *_, r in LIBYAN_CITIES if r == "East")
    south = sum(1 for *_, r in LIBYAN_CITIES if r == "South")
    assert west == 14
    assert east == 8
    assert south == 6


def test_libyan_cities_has_tripoli():
    names_ar = {name_ar for _, name_ar, _, _ in LIBYAN_CITIES}
    assert "طرابلس" in names_ar


def test_libyan_cities_uuids_valid():
    for cid_str, _, _, _ in LIBYAN_CITIES:
        uuid.UUID(cid_str)


def test_libyan_cities_unique_english_names():
    names_en = [name_en for _, _, name_en, _ in LIBYAN_CITIES]
    assert len(names_en) == len(set(names_en))


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_cities_api_returns_tripoli():
    response = client.get("/api/v1/cities")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) >= 28
    names_ar = {c["name_ar"] for c in data}
    assert "طرابلس" in names_ar


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_cities_api_region_filter():
    response = client.get("/api/v1/cities?region=South")
    assert response.status_code == 200
    data = response.json()["data"]
    assert all(c["region"] == "South" for c in data)
    assert len(data) >= 6
