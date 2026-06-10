import os
import uuid
from datetime import datetime, timezone

import pytest

from app.registration_services import (
    DRIVER_REGISTRATION_FEE_ORDER_TYPE,
    approve_registration,
    driver_profile_out,
    initiate_driver_registration_payment,
)

HAS_DB = os.getenv("ROUSTO_TEST_DB", "0") == "1"


class _FakeUser:
    def __init__(self):
        self.id = uuid.uuid4()
        self.full_name = "أحمد السائق"
        self.phone = "+218912345678"
        self.email = "driver@rousto.app"
        self.city = "طرابلس"


class _FakeDriverProfile:
    def __init__(self, *, service_type="tow", fee_status="unpaid"):
        self.id = uuid.uuid4()
        self.user_id = uuid.uuid4()
        self.service_type = service_type
        self.vehicle_type = "tow_truck" if service_type == "tow" else None
        self.plate_number = "ABC-123"
        self.city = "طرابلس"
        self.license_doc_path = "registrations/x/license.jpg"
        self.id_doc_path = "registrations/x/id.jpg"
        self.vehicle_doc_path = "registrations/x/vehicle.jpg"
        self.is_approved = False
        self.verification_status = "pending"
        self.registration_fee_status = fee_status
        self.payment_reference_id = None
        self.registration_fee_gateway = None
        self.rejection_reason = None
        self.technician_id = None


class _FakeDB:
    def __init__(self, profile):
        self.profile = profile
        self.user = _FakeUser()

    def get(self, model, pk):
        name = getattr(model, "__name__", str(model))
        if name == "DriverProfile" and pk == self.profile.id:
            return self.profile
        if name == "User":
            return self.user
        return None

    def add(self, _):
        pass

    def flush(self):
        pass


def test_driver_registration_fee_order_type():
    assert DRIVER_REGISTRATION_FEE_ORDER_TYPE == "driver_registration_fee"


def test_driver_profile_out_includes_fee_fields():
    user = _FakeUser()
    profile = _FakeDriverProfile(fee_status="unpaid")
    profile.id = uuid.uuid4()
    out = driver_profile_out(profile, user)  # type: ignore[arg-type]
    assert out["is_verified"] is False
    assert out["registration_fee_status"] == "unpaid"
    assert out["registration_fee_lyd"] == 150.0
    assert out["vehicle_type"] == "tow_truck"


def test_approve_tow_driver_blocks_unpaid_fee():
    profile = _FakeDriverProfile(service_type="tow", fee_status="unpaid")
    db = _FakeDB(profile)
    with pytest.raises(ValueError, match="رسوم التفعيل"):
        approve_registration(db, role="driver", profile_id=profile.id)  # type: ignore[arg-type]


@pytest.mark.skipif(not HAS_DB, reason="Set ROUSTO_TEST_DB=1 with running PostgreSQL")
def test_initiate_payment_endpoint_requires_documents():
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    fake_id = str(uuid.uuid4())
    res = client.post(
        "/api/v1/auth/register/driver/initiate-payment",
        json={
            "profile_id": fake_id,
            "phone": "+218912345678",
            "gateway": "muamalat",
        },
    )
    assert res.status_code == 400
