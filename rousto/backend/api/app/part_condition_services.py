"""Parse and validate spare part condition (new / used)."""

from __future__ import annotations

import re

VALID_CONDITIONS = frozenset({"new", "used"})
USED_TOKENS = (
    "used_part",
    "used",
    "مستعملة",
    "مستعمل",
    "ربش",
)


def parse_part_condition(raw: str | None) -> str:
    if not raw or not str(raw).strip():
        return "new"
    val = str(raw).strip().lower()
    if val in VALID_CONDITIONS:
        return val
    compact = re.sub(r"\s+", "", val)
    for token in USED_TOKENS:
        if token in val or token in compact:
            return "used"
    return "new"


def normalize_condition_filter(value: str | None) -> str | None:
    if not value or not value.strip():
        return None
    val = value.strip().lower()
    if val not in VALID_CONDITIONS:
        raise ValueError("حالة القطعة يجب أن تكون new أو used")
    return val
