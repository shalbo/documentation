import pytest

from app.city_seed_data import LIBYAN_CITIES
from app.registration_services import normalize_phone, register_customer


def test_normalize_phone_libya():
    assert normalize_phone("0912345678") == "+218912345678"


def test_normalize_phone_saudi():
    assert normalize_phone("0501234567") == "+966501234567"


def test_normalize_phone_invalid():
    with pytest.raises(ValueError, match="صيغة"):
        normalize_phone("123")


def test_libyan_cities_has_tripoli():
    names_ar = {name_ar for _, name_ar, _, _ in LIBYAN_CITIES}
    assert "طرابلس" in names_ar


def test_register_customer_validation_city():
    class DB:
        def scalar(self, _):
            return None

        def add(self, _):
            pass

        def flush(self):
            pass

    with pytest.raises(ValueError, match="مدينة"):
        register_customer(DB(), full_name="أحمد", phone="+218912345678", city="مدينة غير معتمدة")
