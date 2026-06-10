"""Service layer import smoke tests."""

from app.service_layer.bookings import ACTIVE_STATUSES, create_booking
from app.service_layer.notifications import NOTIFICATION_CATEGORIES, list_notifications
from app.service_layer.parts import search_parts, list_part_categories
from app.service_layer.support import create_support_ticket, faq_out
from app.service_layer.vendors import vendor_create_product


def test_parts_service_layer_exports():
    assert callable(search_parts)
    assert callable(list_part_categories)


def test_bookings_service_layer_exports():
    assert "pending" in ACTIVE_STATUSES or len(ACTIVE_STATUSES) > 0
    assert callable(create_booking)


def test_support_service_layer_exports():
    assert callable(create_support_ticket)
    assert callable(faq_out)


def test_notifications_service_layer_exports():
    assert len(NOTIFICATION_CATEGORIES) > 0
    assert callable(list_notifications)


def test_vendors_service_layer_exports():
    assert callable(vendor_create_product)
