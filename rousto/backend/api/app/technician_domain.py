"""Domain guards — enforce technician role separation."""

from app.models import Technician

SERVICE_DRIVER_TYPE = "service"
TOW_DRIVER_TYPE = "tow"
COURIER_DRIVER_TYPE = "courier"


def assert_service_technician(technician: Technician) -> None:
    if technician.driver_type != SERVICE_DRIVER_TYPE:
        raise ValueError(
            f"يجب تعيين فني خدمة (النوع الحالي: {technician.driver_type})"
        )


def assert_tow_driver(technician: Technician) -> None:
    if technician.driver_type != TOW_DRIVER_TYPE:
        raise ValueError(
            f"يجب تعيين سائق سطحة (النوع الحالي: {technician.driver_type})"
        )
