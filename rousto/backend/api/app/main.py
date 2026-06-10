import logging
import sys

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.config import settings
from app.error_reporting import capture_exception, init_error_reporting
from app.security_middleware import SecurityHeadersMiddleware
from app.routers import (
    admin_catalog,
    admin_cities,
    admin_fitment,
    admin_marketing,
    admin_marketplace,
    admin_notifications,
    admin_parts,
    admin_shipping,
    admin_tiers,
    admin_subscriptions,
    admin_payments,
    auth,
    bookings,
    catalog,
    cities,
    devices,
    driver_network,
    fitment,
    health,
    landing,
    logistics,
    marketplace,
    marketing,
    monetization,
    notifications,
    part_categories,
    parts,
    profile,
    promotions,
    scans,
    shipping,
    split_payments,
    support,
    testimonials,
    towing_dispatch,
    vendor_map,
    vendor_parts,
    vendor_subscription,
    vendor_wallet,
    libyan_payments,
    payment_webhooks,
    payment_otp,
    registration,
    driver_registration_auth,
    vin_decoder,
    vendors,
)

logger = logging.getLogger("rousto")

app = FastAPI(
    title="Rousto API",
    description="REST API لمنصة روستو — عناية ذكية بالسيارات",
    version="1.0.0",
    docs_url=None if settings.disable_openapi else "/docs",
    redoc_url=None if settings.disable_openapi else "/redoc",
)

if settings.cors_origins == "*":
    origins = ["*"]
    allow_credentials = False
else:
    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.trusted_host_list:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_host_list)

app.add_middleware(SecurityHeadersMiddleware)

prefix = settings.api_prefix
app.include_router(health.router, prefix=prefix)
app.include_router(auth.router, prefix=prefix)
app.include_router(catalog.router, prefix=prefix)
app.include_router(cities.router, prefix=prefix)
app.include_router(admin_catalog.router, prefix=prefix)
app.include_router(admin_cities.router, prefix=prefix)
app.include_router(admin_marketing.router, prefix=prefix)
app.include_router(admin_notifications.router, prefix=prefix)
app.include_router(admin_parts.router, prefix=prefix)
app.include_router(admin_marketplace.router, prefix=prefix)
app.include_router(admin_fitment.router, prefix=prefix)
app.include_router(admin_shipping.router, prefix=prefix)
app.include_router(admin_tiers.router, prefix=prefix)
app.include_router(admin_subscriptions.router, prefix=prefix)
app.include_router(admin_payments.router, prefix=prefix)
app.include_router(profile.router, prefix=prefix)
app.include_router(devices.router, prefix=prefix)
app.include_router(driver_network.router, prefix=prefix)
app.include_router(notifications.router, prefix=prefix)
app.include_router(part_categories.router, prefix=prefix)
app.include_router(parts.router, prefix=prefix)
app.include_router(marketplace.router, prefix=prefix)
app.include_router(fitment.router, prefix=prefix)
app.include_router(shipping.router, prefix=prefix)
app.include_router(scans.router, prefix=prefix)
app.include_router(bookings.router, prefix=prefix)
app.include_router(logistics.router, prefix=prefix)
app.include_router(promotions.router, prefix=prefix)
app.include_router(testimonials.router, prefix=prefix)
app.include_router(monetization.router, prefix=prefix)
app.include_router(split_payments.router, prefix=prefix)
app.include_router(vendors.router, prefix=prefix)
app.include_router(vendor_parts.router, prefix=prefix)
app.include_router(vendor_subscription.router, prefix=prefix)
app.include_router(vendor_wallet.router, prefix=prefix)
app.include_router(libyan_payments.router, prefix=prefix)
app.include_router(payment_otp.router, prefix=prefix)
app.include_router(payment_webhooks.router, prefix=prefix)
app.include_router(payment_webhooks.legacy_router, prefix=prefix)
app.include_router(registration.router, prefix=prefix)
app.include_router(driver_registration_auth.router, prefix=prefix)
app.include_router(vin_decoder.router, prefix=prefix)
app.include_router(vendor_map.router, prefix=prefix)
app.include_router(towing_dispatch.router, prefix=prefix)
app.include_router(support.router, prefix=prefix)
app.include_router(landing.router, prefix=prefix)
app.include_router(marketing.router, prefix=prefix)
app.include_router(marketing.me_router, prefix=prefix)


@app.on_event("startup")
def on_startup() -> None:
    init_error_reporting()
    warnings = settings.validate_production()
    for warning in warnings:
        logger.warning("Production config: %s", warning)
    if settings.is_production and settings.production_strict and warnings:
        logger.error("Production strict mode: refusing to start with %d config issues", len(warnings))
        sys.exit(1)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": exc.detail},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": {"code": "ERROR", "message": str(exc.detail)}},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    capture_exception(
        exc,
        context={"path": request.url.path, "method": request.method},
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "حدث خطأ داخلي، تم تسجيله",
            }
        },
    )


@app.get("/")
def root():
    return {
        "name": "Rousto API",
        "environment": settings.environment,
        "health": f"{prefix}/health",
        "docs": "/docs" if not settings.disable_openapi else None,
    }
