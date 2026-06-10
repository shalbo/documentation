import time
from threading import Lock
from typing import Any, Callable

_lock = Lock()
_store: dict[str, tuple[float, Any]] = {}


def cached(ttl_seconds: int, key: str, loader: Callable[[], Any]) -> Any:
    now = time.time()
    with _lock:
        entry = _store.get(key)
        if entry and now - entry[0] < ttl_seconds:
            return entry[1]
    value = loader()
    with _lock:
        _store[key] = (now, value)
    return value


def invalidate(key: str) -> None:
    with _lock:
        _store.pop(key, None)


def invalidate_prefix(prefix: str) -> None:
    with _lock:
        for k in list(_store.keys()):
            if k.startswith(prefix):
                _store.pop(k, None)
