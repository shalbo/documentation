from app.i18n import pick_localized, resolve_locale, label_from_map, BOOKING_STATUS_LABELS


class _Obj:
    name_ar = "زيت"
    name_en = "Oil"


def test_pick_localized_ar_unit():
    assert pick_localized(_Obj(), "name", "ar") == "زيت"


def test_pick_localized_en_unit():
    assert pick_localized(_Obj(), "name", "en") == "Oil"


def test_pick_localized_en_fallback_unit():
    class Partial:
        name_ar = "فرامل"

    assert pick_localized(Partial(), "name", "en") == "فرامل"


def test_label_from_map_unit():
    assert label_from_map(BOOKING_STATUS_LABELS, "confirmed", "en") == "Confirmed"


def test_resolve_locale_query_unit():
    assert resolve_locale(accept_language=None, lang="en") == "en"


def test_resolve_locale_header_unit():
    assert resolve_locale(accept_language="en-US,en;q=0.9", lang=None) == "en"
