import uuid

import pytest

from app.device_services import register_device_token, list_active_tokens


class FakeSession:
    def __init__(self):
        self.added = []
        self.committed = False

    def scalar(self, _):
        return None

    def add(self, obj):
        self.added.append(obj)

    def flush(self):
        pass


def test_register_device_token_unit():
    db = FakeSession()
    user_id = uuid.UUID("a0000000-0000-4000-8000-000000000001")
    entry = register_device_token(
        db, user_id=user_id, fcm_token="a" * 40, platform="android"
    )
    assert entry.user_id == user_id
    assert entry.platform == "android"
    assert len(db.added) == 1


def test_list_active_tokens_empty_unit():
    class EmptyDb:
        def scalars(self, _):
            return type("R", (), {"all": lambda self: []})()

    assert list_active_tokens(EmptyDb(), uuid.uuid4()) == []


def test_send_push_disabled_unit():
    from app.notifications import send_push

    assert send_push(token="x" * 40, title="t", body="b") is False
