import os
import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.permissions import AuthPrincipal, ROLE_ADMIN, ROLE_CUSTOMER

DEV_USER = uuid.UUID("a0000000-0000-4000-8000-000000000001")
TECH_USER_PHONE = "+966509876543"
HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"

client = TestClient(app)


def test_role_constants_unit():
    assert ROLE_CUSTOMER == "customer"
    assert ROLE_ADMIN == "admin"


def test_principal_permissions_unit():
    from app.models import User

    user = User(
        id=DEV_USER,
        full_name="test",
        email="t@example.com",
        phone="+966500000000",
    )
    principal = AuthPrincipal(
        user=user,
        roles=["customer", "admin"],
        permissions=["bookings:read", "catalog:manage"],
    )
    assert principal.has_role("admin")
    assert principal.has_permission("catalog:manage")
    assert not principal.has_permission("missing:perm")


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_otp_send_and_verify():
    send = client.post("/api/v1/auth/otp/send", json={"phone": "+966501234567"})
    assert send.status_code == 200
    dev_otp = send.json()["meta"]["dev_otp"]
    request_id = send.json()["data"]["request_id"]

    verify = client.post(
        "/api/v1/auth/otp/verify",
        json={
            "phone": "+966501234567",
            "code": dev_otp,
            "request_id": request_id,
        },
    )
    assert verify.status_code == 200
    data = verify.json()["data"]
    assert "access_token" in data
    assert "refresh_token" in data
    assert "admin" in data["principal"]["roles"]


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_jwt_auth_me():
    send = client.post("/api/v1/auth/otp/send", json={"phone": "+966501234567"})
    dev_otp = send.json()["meta"]["dev_otp"]
    verify = client.post(
        "/api/v1/auth/otp/verify",
        json={"phone": "+966501234567", "code": dev_otp},
    )
    token = verify.json()["data"]["access_token"]

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["data"]["user"]["full_name"] == "سعود العتيبي"
    assert "bookings:create" in me.json()["data"]["permissions"]


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_jwt_admin_catalog_access():
    send = client.post("/api/v1/auth/otp/send", json={"phone": "+966501234567"})
    token = client.post(
        "/api/v1/auth/otp/verify",
        json={"phone": "+966501234567", "code": send.json()["meta"]["dev_otp"]},
    ).json()["data"]["access_token"]

    response = client.get(
        "/api/v1/admin/categories",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_list_roles_and_permissions():
    response = client.get(
        "/api/v1/auth/permissions",
        headers={"X-Admin-Key": "rousto_admin_dev"},
    )
    assert response.status_code == 200
    assert response.json()["meta"]["total"] >= 10

    roles = client.get("/api/v1/auth/roles")
    assert roles.status_code == 200
    slugs = {r["slug"] for r in roles.json()["data"]}
    assert "customer" in slugs
    assert "admin" in slugs
