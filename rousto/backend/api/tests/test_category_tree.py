import uuid

import pytest

from app.category_services import (
    category_out,
    collect_filter_category_ids,
    is_leaf_category,
)


class FakeCategory:
    def __init__(self, *, id=None, parent_id=None, is_active=True, sort_order=0):
        self.id = id or uuid.uuid4()
        self.slug = "test"
        self.name_ar = "اختبار"
        self.name_en = "Test"
        self.parent_id = parent_id
        self.icon_key = None
        self.sort_order = sort_order
        self.is_active = is_active
        self.children = []


def test_category_out_root_flag():
    root = FakeCategory(parent_id=None)
    out = category_out(root, "ar")
    assert out["is_root"] is True
    assert out["is_leaf"] is False


def test_category_out_leaf_flag():
    leaf = FakeCategory(parent_id=uuid.uuid4())
    out = category_out(leaf, "ar")
    assert out["is_root"] is False
    assert out["is_leaf"] is True


def test_is_leaf_category_unit():
    class DB:
        def get(self, _, cid):
            return FakeCategory(id=cid, parent_id=uuid.uuid4())

    assert is_leaf_category(DB(), uuid.uuid4()) is True


def test_collect_filter_leaf_returns_single():
    leaf_id = uuid.uuid4()

    class DB:
        def get(self, _, cid):
            return FakeCategory(id=cid, parent_id=uuid.uuid4())

    ids = collect_filter_category_ids(DB(), leaf_id)
    assert ids == {leaf_id}
