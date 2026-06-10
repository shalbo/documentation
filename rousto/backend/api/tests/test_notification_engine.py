import uuid

import pytest

from app.notification_engine_services import (
    BROADCAST_SEGMENTS,
    EVENT_SOURCES,
    next_broadcast_reference,
    record_dispatch_log,
)


class FakeSession:
    def __init__(self, scalar_value=0):
        self.scalar_value = scalar_value
        self.added = []

    def scalar(self, _):
        return self.scalar_value

    def add(self, obj):
        self.added.append(obj)


def test_event_sources_defined_unit():
    assert "admin_broadcast" in EVENT_SOURCES
    assert "booking_hook" in EVENT_SOURCES


def test_broadcast_segments_unit():
    assert "all_users" in BROADCAST_SEGMENTS
    assert "customers" in BROADCAST_SEGMENTS


def test_next_broadcast_reference_unit():
    ref = next_broadcast_reference(FakeSession(scalar_value=5))
    assert ref == "BCAST-2026-006"


def test_record_dispatch_log_unit():
    db = FakeSession()
    user_id = uuid.uuid4()
    entry = record_dispatch_log(
        db,
        event_source="admin_send",
        user_id=user_id,
        category="system",
        title="Test",
        push_sent=True,
        in_app_created=True,
    )
    assert entry.event_source == "admin_send"
    assert entry.channel == "both"
    assert len(db.added) == 1


def test_record_dispatch_skipped_unit():
    db = FakeSession()
    entry = record_dispatch_log(
        db,
        event_source="admin_send",
        user_id=uuid.uuid4(),
        category="promo",
        title="Skipped",
        status="skipped_prefs",
    )
    assert entry.status == "skipped_prefs"
    assert entry.channel == "both"


def test_render_template_reexport_unit():
    from app.notification_inbox_services import render_template as rt

    assert rt("Hi {{name}}", {"name": "Ali"}) == "Hi Ali"
