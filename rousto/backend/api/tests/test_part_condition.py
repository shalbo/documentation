import pytest

from app.part_condition_services import (
    normalize_condition_filter,
    parse_part_condition,
)


@pytest.mark.parametrize(
    "raw,expected",
    [
        (None, "new"),
        ("", "new"),
        ("new", "new"),
        ("NEW", "new"),
        ("used", "used"),
        ("USED", "used"),
        ("used_part", "used"),
        ("مستعمل", "used"),
        ("مستعملة", "used"),
        ("ربش", "used"),
        ("قطعة مستعملة جيدة", "used"),
        ("جديد", "new"),
        ("brand new", "new"),
    ],
)
def test_parse_part_condition(raw, expected):
    assert parse_part_condition(raw) == expected


def test_normalize_condition_filter_accepts_valid():
    assert normalize_condition_filter("new") == "new"
    assert normalize_condition_filter("used") == "used"
    assert normalize_condition_filter("  USED  ") == "used"


def test_normalize_condition_filter_empty_returns_none():
    assert normalize_condition_filter(None) is None
    assert normalize_condition_filter("") is None
    assert normalize_condition_filter("   ") is None


def test_normalize_condition_filter_rejects_invalid():
    with pytest.raises(ValueError, match="new أو used"):
        normalize_condition_filter("refurbished")


def test_search_endpoint_rejects_invalid_condition():
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    response = client.get(
        "/api/v1/parts/search",
        params={"condition": "refurbished", "q": "filter"},
    )
    assert response.status_code == 422


def test_search_endpoint_requires_filter_without_params():
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    response = client.get("/api/v1/parts/search")
    assert response.status_code == 400
    body = response.json()
    code = body.get("detail", body.get("error", {}))
    if isinstance(code, dict):
        assert code.get("code") == "QUERY_REQUIRED"
    else:
        assert "QUERY_REQUIRED" in str(body)
