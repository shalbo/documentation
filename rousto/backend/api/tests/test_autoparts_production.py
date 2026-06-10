import pytest

from app.shipping_services import classify_shipping, calculate_settlements
from app.parts_services import _matches_vehicle


def test_classify_local_delivery():
    assert classify_shipping("الرياض", "الرياض") == "local_delivery"


def test_classify_intercity():
    assert classify_shipping("طرابلس", "مصراتة") == "intercity_shipping"


def test_part_order_settlements_include_shipping():
    import uuid

    vendor_id = uuid.uuid4()
    courier_id = uuid.uuid4()
    legs = calculate_settlements(
        subtotal_sar=100.0,
        shipping_fee_sar=30.0,
        shipping_type="local_delivery",
        vendor_id=vendor_id,
        courier_id=courier_id,
    )
    types = {l["recipient_type"] for l in legs}
    assert "vendor" in types
    assert "platform" in types
    assert "courier" in types
    total = sum(l["amount_sar"] for l in legs)
    assert total == pytest.approx(130.0, abs=0.05)


def test_intercity_settlements_carrier_share():
    import uuid

    legs = calculate_settlements(
        subtotal_sar=200.0,
        shipping_fee_sar=45.0,
        shipping_type="intercity_shipping",
        vendor_id=uuid.uuid4(),
    )
    types = {l["recipient_type"] for l in legs}
    assert "carrier" in types


def test_vehicle_compat_unchanged():
    compat = [{"make": "Toyota", "model": "Camry"}]
    assert _matches_vehicle(compat, "Toyota", "Camry") is True
