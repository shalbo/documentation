import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException, Request

from app.config import settings
from app.i18n import error_message, resolve_locale

_lock = Lock()
_buckets: dict[str, list[float]] = defaultdict(list)


def _client_key(request: Request, suffix: str = "") -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "unknown")
    return f"{ip}:{suffix}" if suffix else ip


def check_rate_limit(
    request: Request,
    *,
    suffix: str = "",
    limit: int | None = None,
    locale: str | None = None,
) -> None:
    max_requests = limit or settings.rate_limit_per_minute
    window_sec = 60
    key = _client_key(request, suffix)
    now = time.time()
    lang = locale or resolve_locale(request.headers.get("Accept-Language"))

    with _lock:
        hits = [t for t in _buckets[key] if now - t < window_sec]
        if len(hits) >= max_requests:
            raise HTTPException(
                status_code=429,
                detail={
                    "code": "RATE_LIMITED",
                    "message": error_message("RATE_LIMITED", lang),
                },
            )
        hits.append(now)
        _buckets[key] = hits


def rate_limit_dependency(suffix: str, limit: int | None = None):
    def checker(request: Request) -> None:
        check_rate_limit(request, suffix=suffix, limit=limit)

    return checker
