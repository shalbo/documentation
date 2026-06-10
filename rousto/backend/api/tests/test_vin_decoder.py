import os
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import VinDecoder
from app.vin_decoder_services import decode_vin

HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"
client = TestClient(app)


class _FakeScalars:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class _FakeDB:
    def __init__(self, rows):
        self._rows = rows

    def scalars(self, _):
        return _FakeScalars(self._rows)


def _decoder_row(prefix: str, make: str, model: str) -> VinDecoder:
    now = datetime.now(timezone.utc)
    return VinDecoder(
        id=uuid.uuid4(),
        vin_prefix=prefix,
        make=make,
        model=model,
        year_range="2016-2020",
        engine="1.6L MPI",
        market="libya",
        created_at=now,
        updated_at=now,
    )


def test_decode_vin_longest_prefix_match():
    # SQL orders by prefix length descending — longest match first.
    rows = [
        _decoder_row("KMHCT41M", "Hyundai", "Elantra"),
        _decoder_row("KMH", "Hyundai", "Generic"),
    ]
    result = decode_vin(_FakeDB(rows), "KMHCT41M0GU123456")
    assert result is not None
    assert result["make"] == "Hyundai"
    assert result["model"] == "Elantra"
    assert result["vin_prefix"] == "KMHCT41M"


def test_decode_vin_no_match():
    rows = [_decoder_row("JTMCE90E", "Toyota", "Corolla")]
    assert decode_vin(_FakeDB(rows), "XXXXXXXXXXXX12345") is None


def test_decode_vin_rejects_short_input():
    with pytest.raises(ValueError, match="قصير"):
        decode_vin(_FakeDB([]), "SHORT")


def test_decode_vin_rejects_invalid_chars():
    with pytest.raises(ValueError, match="غير صالحة"):
        decode_vin(_FakeDB([]), "KMHCT41M0!U123456")


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_vin_decode_endpoint_toyota_corolla():
    response = client.get("/api/v1/vin/decode", params={"vin": "JTMCE90E123456789"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["make"] == "Toyota"
    assert data["model"] == "Corolla"
    assert data["vin_prefix"] == "JTMCE90E"


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_vin_decode_endpoint_not_found():
    response = client.get("/api/v1/vin/decode", params={"vin": "ZZZZZZZZ123456789"})
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "VIN_NOT_FOUND"


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_parts_search_includes_decoded_vehicle_meta():
    response = client.get(
        "/api/v1/parts/search",
        params={"vin": "KMHCT41M0GU123456"},
    )
    assert response.status_code == 200
    meta = response.json()["meta"]
    assert meta["strict_vin_match"] is True
    decoded = meta["decoded_vehicle"]
    assert decoded is not None
    assert decoded["make"] == "Hyundai"
    assert decoded["model"] == "Elantra"


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_admin_vin_decoders_list():
    response = client.get(
        "/api/v1/admin/vin-decoders",
        headers={"X-Admin-Key": "rousto_admin_dev"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["total"] >= 17
    assert body["meta"]["market"] == "libya"
    prefixes = {row["vin_prefix"] for row in body["data"]}
    assert "JTMCE90E" in prefixes
    assert "KMHCT41M" in prefixes
