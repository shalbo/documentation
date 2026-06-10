import uuid

import pytest

from app.notification_inbox_services import (
    NOTIFICATION_CATEGORIES,
    category_label,
    get_category_prefs,
    render_template,
    update_user_preferences,
)


class FakeScalarResult:
    def __init__(self, value):
        self._value = value

    def all(self):
        return self._value if isinstance(self._value, list) else []


class FakeSession:
    def __init__(self, scalar_value=None):
        self.scalar_value = scalar_value
        self.added = []

    def scalar(self, _):
        return self.scalar_value

    def scalars(self, _):
        return FakeScalarResult(self.scalar_value or [])

    def add(self, obj):
        self.added.append(obj)

    def flush(self):
        pass


def test_render_template_unit():
    text = render_template(
        "تحديث حجز {{reference}} — {{label}}",
        {"reference": "RST-001", "label": "تم التأكيد"},
    )
    assert text == "تحديث حجز RST-001 — تم التأكيد"


def test_render_template_missing_key_unit():
    assert render_template("مرحباً {{name}}", {}) == "مرحباً {{name}}"


def test_categories_defined_unit():
    assert "booking" in NOTIFICATION_CATEGORIES
    assert category_label("support", "ar") == "الدعم"
    assert category_label("support", "en") == "Support"


def test_default_prefs_when_missing_unit():
    push, in_app = get_category_prefs(
        FakeSession(scalar_value=None),
        uuid.uuid4(),
        "booking",
    )
    assert push is True
    assert in_app is True


def test_update_preferences_invalid_category_unit():
    db = FakeSession()
    with pytest.raises(ValueError, match="فئة غير مدعومة"):
        update_user_preferences(
            db,
            uuid.uuid4(),
            [{"category": "invalid", "push_enabled": False}],
        )


def test_notify_booking_wrapper_unit():
    from app.notifications import notify_booking_status_change

    class NoCommitDb:
        def commit(self):
            pass

        def rollback(self):
            pass

    # Should not raise when templates/table unavailable
    notify_booking_status_change(
        NoCommitDb(),
        user_id=uuid.uuid4(),
        booking_ref="RST-TEST",
        status="confirmed",
        label_ar="تم التأكيد",
    )
