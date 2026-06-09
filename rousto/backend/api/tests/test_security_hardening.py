import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.rate_limit import check_rate_limit

client = TestClient(app)


class FakeRequest:
    def __init__(self, ip: str = "10.0.0.1"):
        self.client = type("C", (), {"host": ip})()
        self.headers = {}


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
