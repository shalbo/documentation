import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.rate_limit import check_rate_limit

client = TestClient(app)


class FakeRequest:
    def __init__(self, ip: str = "10.0.0.1"):
        self.client = type("C", (), {"host": ip})()
        self.headers = {"Accept-Language": "ar"}


def test_rate_limit_blocks_after_threshold():
    req = FakeRequest()
    for _ in range(settings.rate_limit_per_minute):
        check_rate_limit(req, suffix="test")
    with pytest.raises(Exception) as exc:
        check_rate_limit(req, suffix="test")
    assert exc.value.status_code == 429


def test_production_warnings_unit():
    original = settings.environment
    try:
        settings.environment = "production"
        settings.allow_legacy_headers = True
        warnings = settings.validate_production()
        assert any("LEGACY" in w.upper() for w in warnings)
    finally:
        settings.environment = original


def test_health_public():
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_security_headers_on_health():
    response = client.get("/api/v1/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Request-Id")


def test_admin_security_status():
    response = client.get(
        "/api/v1/admin/security/status",
        headers={"X-Admin-Key": settings.admin_api_key},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "security_headers_enabled" in data
    assert "admin_rate_limit_per_minute" in data


def test_admin_key_failure_audited():
    response = client.get(
        "/api/v1/admin/security/events",
        headers={"X-Admin-Key": "wrong-key"},
    )
    assert response.status_code == 401


def test_trusted_host_list_unit():
    original = settings.trusted_hosts
    try:
        settings.trusted_hosts = "rousto.com, api.rousto.com"
        assert settings.trusted_host_list == ["rousto.com", "api.rousto.com"]
    finally:
        settings.trusted_hosts = original
