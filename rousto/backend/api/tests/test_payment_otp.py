import uuid

import pytest

from app.auth_services import authenticate_user, hash_password, verify_password
from app.payment_otp_services import (
    PAYMENT_OTP_TTL_SECONDS,
    create_payment_intent,
    generate_payment_otp,
    verify_payment_otp_and_execute,
)


def test_hash_and_verify_password():
    hashed = hash_password("Rousto@123")
    assert verify_password("Rousto@123", hashed)
    assert not verify_password("wrong", hashed)


def test_payment_otp_length_constant():
    assert PAYMENT_OTP_TTL_SECONDS == 60


def test_auth_otp_login_disabled():
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    res = client.post("/api/v1/auth/otp/send", json={"phone": "+218912345678"})
    assert res.status_code == 410


class _User:
    id = uuid.uuid4()
    phone = "+218912345678"


class _FakeDB:
    def __init__(self):
        self.intents = []
        self.otps = []
        self.payments = []

    def add(self, obj):
        if hasattr(obj, "order_type"):
            self.intents.append(obj)
        else:
            self.otps.append(obj)

    def flush(self):
        pass

    def get(self, model, pk):
        name = getattr(model, "__name__", "")
        if name == "PaymentIntent":
            return next((i for i in self.intents if i.id == pk), None)
        return None

    def scalar(self, _):
        return None


def test_create_payment_intent_rejects_zero():
    with pytest.raises(ValueError, match="المبلغ"):
        create_payment_intent(
            _FakeDB(),  # type: ignore[arg-type]
            _User(),  # type: ignore[arg-type]
            amount_lyd=0,
            gateway="wallet",
            order_type="part_order",
            order_ref_id=None,
            return_url="rousto://payment/return",
        )
