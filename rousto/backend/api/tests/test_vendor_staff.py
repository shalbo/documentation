import os
import uuid

import pytest

from app.auth_services import hash_password
from app.vendor_staff_rbac import PRICE_EDIT_BLOCKED_ROLES, WALLET_BLOCKED_ROLES
from app.vendor_staff_services import (
    authenticate_vendor_staff,
    normalize_staff_phone,
    revoke_staff_tokens,
    staff_out,
)

HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"


def test_normalize_staff_phone_libya():
    assert normalize_staff_phone("0912345678") == "+218912345678"


def test_sales_blocked_from_wallet_and_prices():
    assert "sales" in WALLET_BLOCKED_ROLES
    assert "sales" in PRICE_EDIT_BLOCKED_ROLES


def test_manager_blocked_from_wallet():
    assert "manager" in WALLET_BLOCKED_ROLES
    assert "manager" not in PRICE_EDIT_BLOCKED_ROLES


class _Staff:
    id = uuid.uuid4()
    vendor_id = uuid.uuid4()
    name = "موظف"
    phone = "+218912345678"
    role = "sales"
    is_active = True
    created_at = None
    updated_at = None


def test_staff_out_shape():
    out = staff_out(_Staff())  # type: ignore[arg-type]
    assert out["role"] == "sales"
    assert out["is_active"] is True


class _ActiveStaff:
    def __init__(self, *, active: bool = True, password: str = "secret12"):
        self.id = uuid.uuid4()
        self.vendor_id = uuid.uuid4()
        self.phone = "+218912345678"
        self.is_active = active
        self.password_hash = hash_password(password)


class _FakeDB:
    def __init__(self, staff):
        self.staff = staff
        self.revoked = 0

    def scalar(self, _):
        return self.staff

    def scalars(self, _):
        class _R:
            def __init__(self, items):
                self._items = items

            def all(self):
                return self._items

        return _R([])


def test_authenticate_vendor_staff_rejects_inactive():
    staff = _ActiveStaff(active=False)
    with pytest.raises(ValueError, match="معطّل"):
        authenticate_vendor_staff(_FakeDB(staff), "0912345678", "secret12")  # type: ignore[arg-type]


def test_authenticate_vendor_staff_rejects_wrong_password():
    staff = _ActiveStaff(password="secret12")
    with pytest.raises(ValueError, match="غير صحيحة"):
        authenticate_vendor_staff(_FakeDB(staff), "0912345678", "wrongpass")  # type: ignore[arg-type]


def test_authenticate_vendor_staff_success():
    staff = _ActiveStaff(password="secret12")
    result = authenticate_vendor_staff(_FakeDB(staff), "0912345678", "secret12")  # type: ignore[arg-type]
    assert result is staff


def test_revoke_staff_tokens_marks_rows():
    now_holder = []

    class _Token:
        def __init__(self):
            self.revoked_at = None

    tokens = [_Token(), _Token()]
    db = type(
        "DB",
        (),
        {
            "scalars": staticmethod(lambda _: type("R", (), {"all": staticmethod(lambda: tokens)})()),
        },
    )()
    count = revoke_staff_tokens(db, uuid.uuid4())  # type: ignore[arg-type]
    assert count == 2
    assert all(t.revoked_at is not None for t in tokens)


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_auth_login_falls_through_to_staff_auth():
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    res = client.post(
        "/api/v1/auth/login",
        json={"phone": "+218912345678", "password": "wrongpass"},
    )
    assert res.status_code == 401
