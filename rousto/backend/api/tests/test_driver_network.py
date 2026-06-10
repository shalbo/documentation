import pytest

from app.driver_network_services import (
    DRIVER_TYPES,
    compute_towing_fare,
    dispatch_job_summary,
)


class FakeDispatch:
    def __init__(self):
        self.id = "td000000-0000-4000-8000-000000000002"
        self.reference = "TOW-2026-002"
        self.status = "pending"
        self.pickup_label = "موقع العطل"
        self.pickup_lat = 24.77
        self.pickup_lng = 46.73
        self.dropoff_label = "ورشة"
        self.dropoff_lat = 24.71
        self.dropoff_lng = 46.67
        self.total_route_km = 8.2
        self.total_fare_sar = 140.6
        self.created_at = None


def test_driver_types_defined_unit():
    assert "tow" in DRIVER_TYPES
    assert "service" in DRIVER_TYPES


def test_compute_towing_fare_unit():
    fare = compute_towing_fare(10.0)
    assert fare["base_fare_sar"] == 75.0
    assert fare["per_km_rate_sar"] == 8.0
    assert fare["total_fare_sar"] == 155.0


def test_dispatch_job_summary_unit():
    summary = dispatch_job_summary(FakeDispatch(), distance_km=2.5)
    assert summary["reference"] == "TOW-2026-002"
    assert summary["distance_km"] == 2.5
    assert summary["total_fare_sar"] == 140.6


def test_cancellable_statuses_unit():
    from app.driver_network_services import CANCELLABLE_STATUSES

    assert "pending" in CANCELLABLE_STATUSES
    assert "completed" not in CANCELLABLE_STATUSES
