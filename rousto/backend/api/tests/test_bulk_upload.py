import os

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.part_condition_services import parse_part_condition
from app.spare_parts_bulk_services import (
    BULK_COLUMNS,
    TEMPLATE_CSV,
    _parse_compatible_vehicles,
    _parse_rows_from_csv,
    _slugify,
    _validate_row,
    parse_upload_file,
)
from app.spare_parts_bulk_services import _CategoryResolver

VENDOR_ID = "v0000000-0000-4000-8000-000000000001"
HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"

client = TestClient(app)
headers = {"X-Vendor-Id": VENDOR_ID}


class _FakeDB:
    pass


def test_bulk_columns_match_template():
    header = TEMPLATE_CSV.splitlines()[0].split(",")
    assert header == BULK_COLUMNS


def test_parse_csv_rows():
    content = TEMPLATE_CSV.encode("utf-8")
    rows = _parse_rows_from_csv(content)
    assert len(rows) == 2
    assert rows[0]["oem_number"] == "TOY-04152-YZZA1"
    assert rows[0]["sub_category"] == "maintenance-filters"
    assert rows[0]["condition"] == "new"
    assert rows[1]["oem_number"] == "BOSCH-USED-001"
    assert parse_part_condition(rows[1]["condition"]) == "used"


def test_parse_upload_file_csv():
    rows = parse_upload_file(TEMPLATE_CSV.encode("utf-8"), "parts.csv")
    assert len(rows) == 2


def test_template_includes_condition_column():
    assert "condition" in BULK_COLUMNS
    assert "حالة القطعة" in TEMPLATE_CSV


def test_slugify_oem():
    assert _slugify("TOY-04152-YZZA1").startswith("toy")


def test_compatible_vehicles_parser():
    out = _parse_compatible_vehicles("Toyota Camry 2018-2024, Honda Civic")
    assert len(out) == 2
    assert out[0]["label"] == "Toyota Camry 2018-2024"


def test_validate_row_requires_oem_price_qty():
    resolver = _CategoryResolver.__new__(_CategoryResolver)
    resolver.by_slug = {"maintenance-filters": "c1000000-0000-4000-8000-000000000116"}
    resolver.by_name_ar = {}
    resolver.by_name_en = {}
    resolver.uncategorized_id = "c1000000-0000-4000-8000-000000000122"

    parsed, errors, _ = _validate_row(
        {"name_ar": "قطعة"},
        2,
        seen_oem=set(),
        seen_slugs=set(),
        existing_parts=set(),
        existing_slugs=set(),
        category_resolver=resolver,
    )
    assert parsed is None
    fields = {e.field for e in errors}
    assert "oem_number" in fields
    assert "price" in fields
    assert "quantity" in fields


def test_bulk_template_endpoint_requires_vendor():
    response = client.get("/api/v1/vendor/parts/bulk-upload/template")
    assert response.status_code == 401


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_bulk_template_download():
    response = client.get(
        "/api/v1/vendor/parts/bulk-upload/template",
        headers=headers,
    )
    assert response.status_code == 200
    assert "oem_number" in response.text


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_bulk_upload_csv_success():
    csv_body = (
        "oem_number,name_ar,name_en,part_brand,price,quantity,"
        "sub_category,compatible_vehicles,vin_prefixes,description\n"
        "BULK-TEST-001,قطعة اختبار جماعي,Bulk Test Part,TestBrand,99.5,5,"
        "brakes,Toyota Corolla,,وصف تجريبي\n"
    )
    response = client.post(
        "/api/v1/vendor/parts/bulk-upload",
        headers=headers,
        files={"file": ("bulk.csv", csv_body.encode("utf-8"), "text/csv")},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["imported"] == 1
    assert data["failed"] == 0


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_bulk_upload_validation_error_no_db_write():
    csv_body = (
        "oem_number,name_ar,name_en,part_brand,price,quantity,"
        "sub_category,compatible_vehicles,vin_prefixes,description\n"
        ",قطعة بدون OEM,,,10,5,brakes,,,\n"
    )
    response = client.post(
        "/api/v1/vendor/parts/bulk-upload",
        headers=headers,
        files={"file": ("bad.csv", csv_body.encode("utf-8"), "text/csv")},
    )
    assert response.status_code == 422
    err = response.json()["error"]
    assert err["code"] == "BULK_VALIDATION"
    assert err["data"]["imported"] == 0
