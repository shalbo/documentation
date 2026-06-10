import pytest

from app.driver_network_services import compute_towing_fare
from app.technician_domain import (
    SERVICE_DRIVER_TYPE,
    TOW_DRIVER_TYPE,
    assert_service_technician,
    assert_tow_driver,
)


class FakeTech:
    def __init__(self, driver_type: str):
        self.driver_type = driver_type


def test_assert_service_technician_unit():
    assert_service_technician(FakeTech(SERVICE_DRIVER_TYPE))


def test_assert_service_technician_rejects_tow_unit():
    with pytest.raises(ValueError, match="فني خدمة"):
        assert_service_technician(FakeTech(TOW_DRIVER_TYPE))


def test_assert_tow_driver_unit():
    assert_tow_driver(FakeTech(TOW_DRIVER_TYPE))


def test_assert_tow_driver_rejects_service_unit():
    with pytest.raises(ValueError, match="سائق سطحة"):
        assert_tow_driver(FakeTech(SERVICE_DRIVER_TYPE))


def test_vehicle_compat_wildcard_unit():
    from app.parts_services import _matches_vehicle

    compat = [{"make": "Toyota", "model": "*", "years": "2018-2024"}]
    assert _matches_vehicle(compat, "Toyota", "Camry") is True
    assert _matches_vehicle(compat, "Honda", "Civic") is False


def test_fare_formula_unchanged_unit():
    fare = compute_towing_fare(10.0, base_fare=75.0, per_km=8.0)
    assert fare["total_fare_sar"] == 155.0
