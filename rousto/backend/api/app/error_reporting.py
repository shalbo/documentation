import logging
from typing import Any

from app.config import settings

logger = logging.getLogger("rousto")

_sentry_initialized = False


def init_error_reporting() -> None:
    global _sentry_initialized
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

    if not settings.sentry_dsn:
        return
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            integrations=[FastApiIntegration()],
            traces_sample_rate=0.1 if settings.is_production else 0.0,
        )
        _sentry_initialized = True
        logger.info("Sentry error reporting enabled")
    except ImportError:
        logger.warning("sentry-sdk not installed; skipping Sentry init")


def capture_exception(exc: BaseException, *, context: dict[str, Any] | None = None) -> None:
    logger.exception("Unhandled error", extra={"context": context or {}})
    if _sentry_initialized:
        import sentry_sdk

        if context:
            with sentry_sdk.push_scope() as scope:
                for k, v in context.items():
                    scope.set_extra(k, v)
                sentry_sdk.capture_exception(exc)
        else:
            sentry_sdk.capture_exception(exc)
