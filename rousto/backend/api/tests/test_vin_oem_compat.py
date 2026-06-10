import uuid

import pytest

from app.vin_compat_services import (
    normalize_vin_prefix,
    parse_vin_prefixes,
    part_ids_compatible_with_vin,
)


def test_normalize_vin_prefix_11_chars():
    assert normalize_vin_prefix("KMHCT41M0GU123456") == "KMHCT41M0GU"


def test_normalize_vin_rejects_short():
    with pytest.raises(ValueError, match="11"):
        normalize_vin_prefix("SHORT")


def test_parse_multiple_prefixes():
    raw = "4T1B11HK5JK\n2T1BURHE0JC12345"
    prefixes = parse_vin_prefixes(raw)
    assert len(prefixes) == 2
    assert prefixes[0] == "4T1B11HK5JK"
    assert prefixes[1] == "2T1BURHE0JC"


def test_part_ids_compatible_empty_db():
    class DB:
        def scalars(self, _):
            class R:
                def all(self_inner):
                    return []

            return R()

    ids = part_ids_compatible_with_vin(DB(), "KMHCT41M0GU123456")
    assert ids == set()
