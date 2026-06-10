import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import settings

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "X-XSS-Protection": "0",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        request.state.request_id = request_id

        if settings.max_request_body_bytes > 0:
            content_length = request.headers.get("content-length")
            if content_length:
                try:
                    if int(content_length) > settings.max_request_body_bytes:
                        from fastapi.responses import JSONResponse

                        return JSONResponse(
                            status_code=413,
                            content={
                                "error": {
                                    "code": "PAYLOAD_TOO_LARGE",
                                    "message": "حجم الطلب يتجاوز الحد المسموح",
                                }
                            },
                            headers={"X-Request-Id": request_id},
                        )
                except ValueError:
                    pass

        response = await call_next(request)

        if settings.security_headers_enabled:
            for key, value in SECURITY_HEADERS.items():
                response.headers.setdefault(key, value)
            if settings.is_production:
                response.headers.setdefault(
                    "Strict-Transport-Security",
                    f"max-age={settings.hsts_max_age}; includeSubDomains",
                )

        response.headers["X-Request-Id"] = request_id
        return response
