import io
import os
import zipfile

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.part_image_services import (
    is_valid_image_url,
    resize_image_bytes,
    _oem_from_filename,
)
from app.spare_parts_bulk_services import BULK_COLUMNS, TEMPLATE_CSV

VENDOR_ID = "v0000000-0000-4000-8000-000000000001"
HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"

client = TestClient(app)
headers = {"X-Vendor-Id": VENDOR_ID}


def test_template_includes_image_url():
    header = TEMPLATE_CSV.splitlines()[0].split(",")
    assert "image_url" in header
    assert header == BULK_COLUMNS


def test_is_valid_image_url():
    assert is_valid_image_url("")
    assert is_valid_image_url("https://cdn.example.com/part.jpg")
    assert not is_valid_image_url("ftp://bad.com/x.jpg")
    assert not is_valid_image_url("not-a-url")


def test_resize_image_bytes():
    img = Image.new("RGB", (2400, 1800), color=(200, 30, 30))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    out = resize_image_bytes(buf.getvalue())
    assert len(out) < len(buf.getvalue())
    with Image.open(io.BytesIO(out)) as resized:
        assert max(resized.size) <= 1200


def test_oem_from_filename():
    assert _oem_from_filename("58101-H5A10.png") == "58101-H5A10"


def test_bulk_images_zip_requires_vendor():
    response = client.post("/api/v1/vendor/parts/bulk-images-zip")
    assert response.status_code == 401


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_bulk_images_zip_rejects_bad_zip():
    response = client.post(
        "/api/v1/vendor/parts/bulk-images-zip",
        headers=headers,
        files={"file": ("bad.zip", b"not-a-zip", "application/zip")},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "ZIP_ERROR"


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_bulk_images_zip_links_by_oem():
    oem = "BULK-IMG-001"
    csv_body = (
        "oem_number,name_ar,name_en,part_brand,price,quantity,"
        "sub_category,compatible_vehicles,vin_prefixes,description,image_url\n"
        f"{oem},قطعة صورة,Image Part,Brand,50,3,brakes,,,\n"
    )
    up = client.post(
        "/api/v1/vendor/parts/bulk-upload",
        headers=headers,
        files={"file": ("p.csv", csv_body.encode("utf-8"), "text/csv")},
    )
    assert up.status_code == 200

    img = Image.new("RGB", (400, 300), color=(0, 48, 73))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w") as zf:
        zf.writestr(f"{oem}.png", buf.getvalue())
    zbuf.seek(0)

    response = client.post(
        "/api/v1/vendor/parts/bulk-images-zip",
        headers=headers,
        files={"file": ("images.zip", zbuf.read(), "application/zip")},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["linked"] >= 1
