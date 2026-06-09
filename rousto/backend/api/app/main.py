from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import (
    admin_catalog,
    bookings,
    catalog,
    health,
    monetization,
    profile,
    promotions,
    testimonials,
)

app = FastAPI(
    title="Rousto API",
    description="REST API لمنصة روستو — عناية ذكية بالسيارات",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

origins = (
    [o.strip() for o in settings.cors_origins.split(",")]
    if settings.cors_origins != "*"
    else ["*"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prefix = settings.api_prefix
app.include_router(health.router, prefix=prefix)
app.include_router(catalog.router, prefix=prefix)
app.include_router(admin_catalog.router, prefix=prefix)
app.include_router(profile.router, prefix=prefix)
app.include_router(bookings.router, prefix=prefix)
app.include_router(promotions.router, prefix=prefix)
app.include_router(testimonials.router, prefix=prefix)
app.include_router(monetization.router, prefix=prefix)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "ERROR", "message": str(exc.detail)}},
    )


@app.get("/")
def root():
    return {"name": "Rousto API", "docs": "/docs", "health": f"{prefix}/health"}
