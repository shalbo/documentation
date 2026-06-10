import os

import pytest
from fastapi.testclient import TestClient

from app.category_seed_data import MAIN_CATEGORIES, SUB_CATEGORIES
from app.main import app

HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"
client = TestClient(app)


def test_category_seed_data_counts():
    assert len(MAIN_CATEGORIES) == 9
    assert len(SUB_CATEGORIES) == 22


def test_sub_categories_reference_valid_parents():
    for _slug, _name_ar, _name_en, parent_slug, _icon in SUB_CATEGORIES:
        assert parent_slug in MAIN_CATEGORIES


def test_main_category_slugs_match_user_spec():
    expected = {
        "engine",
        "suspension",
        "electrical",
        "fuel",
        "ac",
        "fluids",
        "body",
        "interior",
        "general",
    }
    assert set(MAIN_CATEGORIES.keys()) == expected


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_category_tree_has_eight_roots():
    response = client.get("/api/v1/parts/categories/roots")
    assert response.status_code == 200
    roots = response.json()["data"]
    root_slugs = {r["slug"] for r in roots if r["is_root"]}
    for slug in MAIN_CATEGORIES:
        assert slug in root_slugs


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_engine_subcategories():
    roots = client.get("/api/v1/parts/categories/roots").json()["data"]
    engine = next(r for r in roots if r["slug"] == "engine")
    children = client.get(
        f"/api/v1/parts/categories/{engine['id']}/children"
    ).json()["data"]
    child_names = {c["name_ar"] for c in children}
    assert "أجزاء المحرك الداخلية" in child_names
    assert "السيور والكاتينات" in child_names
    assert len(children) >= 4
