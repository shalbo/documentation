import json
import uuid

import pytest
from fastapi.testclient import TestClient

from app.gateways.registry import BLOCKED_GATEWAYS, LIBYAN_GATEWAY_SLUGS, validate_gateway
from app.main import app
from app.wallet_services import _d, get_or_create_wallet

client = TestClient(app)


def test_libyan_gateways_only():
    assert "stripe" in BLOCKED_GATEWAYS
    assert "paypal" in BLOCKED_GATEWAYS
    assert "muamalat" in LIBYAN_GATEWAY_SLUGS
    assert "sadad" in LIBYAN_GATEWAY_SLUGS
    assert "edfali" in LIBYAN_GATEWAY_SLUGS
    assert "cod" in LIBYAN_GATEWAY_SLUGS
    assert "wallet" in LIBYAN_GATEWAY_SLUGS


def test_validate_gateway_blocks_international():
    with pytest.raises(ValueError, match="الدولية"):
        validate_gateway("stripe")


def test_validate_gateway_accepts_muamalat():
    assert validate_gateway("muamalat") == "muamalat"


def test_checkout_options_requires_auth():
    res = client.get("/api/v1/payments/libyan/options")
    assert res.status_code == 401


def test_webhook_rejects_bad_gateway():
    res = client.post("/api/v1/webhooks/payments/stripe", json={})
    assert res.status_code == 400


def test_muamalat_adapter_creates_redirect():
    from app.gateways.muamalat import MuamalatGateway

    gw = MuamalatGateway()
    result = gw.create_payment(
        amount_lyd=50.0,
        user_id=uuid.uuid4(),
        order_type="part_order",
        order_id=None,
        return_url="rousto://payment/return",
    )
    assert result.redirect_url is not None
    assert result.gateway_ref.startswith("MML-")


def test_wallet_decimal_precision():
    assert _d(10.556) == _d("10.56")


def test_get_or_create_wallet_in_memory():
    class FakeDB:
        def __init__(self):
            self.wallet = None

        def scalar(self, _):
            return self.wallet

        def add(self, w):
            self.wallet = w

        def flush(self):
            pass

    db = FakeDB()
    wid = uuid.uuid4()
    w1 = get_or_create_wallet(db, owner_type="customer", owner_id=wid)
    assert w1.currency == "LYD"
    w2 = get_or_create_wallet(db, owner_type="customer", owner_id=wid)
    assert w1 is w2
