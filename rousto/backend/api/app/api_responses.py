"""Unified JSON envelope for Rousto API responses."""

from __future__ import annotations

from typing import Any


def success(
    data: Any,
    *,
    message: str | None = None,
    meta: dict | None = None,
) -> dict:
    body: dict = {"success": True, "data": data}
    if message:
        body["message"] = message
    if meta:
        body["meta"] = meta
    return body


def success_list(
    items: list,
    *,
    total: int | None = None,
    message: str | None = None,
) -> dict:
    meta: dict = {"total": total if total is not None else len(items)}
    return success(items, message=message, meta=meta)
