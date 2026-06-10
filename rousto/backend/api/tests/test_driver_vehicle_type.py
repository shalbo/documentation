import pytest
from pydantic import ValidationError

from app.registration_services import VEHICLE_TYPES, _validate_vehicle_type
from app.routers.registration import DriverRegisterIn


def test_vehicle_types_constants():
    assert VEHICLE_TYPES == frozenset({"tow_truck", "flatbed"})


def test_validate_vehicle_type_required_for_tow():
    with pytest.raises(ValueError, match="نوع الآلية"):
        _validate_vehicle_type("tow", None)
    assert _validate_vehicle_type("tow", "flatbed") == "flatbed"
    assert _validate_vehicle_type("tow", "tow_truck") == "tow_truck"


def test_validate_vehicle_type_rejected_for_courier():
    assert _validate_vehicle_type("courier", None) is None
    with pytest.raises(ValueError, match="سائقي الساحبات"):
        _validate_vehicle_type("courier", "flatbed")


def test_driver_register_schema_requires_vehicle_type_for_tow():
    with pytest.raises(ValidationError):
        DriverRegisterIn(
            full_name="أحمد",
            phone="+218912345678",
            city="طرابلس",
            service_type="tow",
            plate_number="ABC-123",
        )
    model = DriverRegisterIn(
        full_name="أحمد",
        phone="+218912345678",
        city="طرابلس",
        service_type="tow",
        plate_number="ABC-123",
        vehicle_type="tow_truck",
    )
    assert model.vehicle_type == "tow_truck"


def test_driver_register_schema_allows_courier_without_vehicle_type():
    model = DriverRegisterIn(
        full_name="سالم",
        phone="+218912345678",
        city="طرابلس",
        service_type="courier",
        plate_number="XYZ-99",
    )
    assert model.vehicle_type is None
