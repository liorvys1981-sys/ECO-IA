"""API key authentication middleware."""

import hmac
import os

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

PUBLIC_PATH_PREFIXES = (
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/dashboard",
    "/static",
    "/api/v1/webhooks/",
)


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = request.url.path
        public_paths = {"/", "/health", "/docs", "/redoc", "/openapi.json", "/dashboard"}
        if path in public_paths or path.startswith(("/static", "/api/v1/webhooks/")):
            return await call_next(request)

        api_key = os.getenv("ECO_IA_API_KEY", "change-me-in-production")
        admin_key = os.getenv("ECO_IA_ADMIN_KEY", "change-me-in-production-admin")

        if path.startswith("/api/v1/admin"):
            provided_admin_key = request.headers.get("X-Admin-Key", "")
            if not hmac.compare_digest(provided_admin_key, admin_key):
                return JSONResponse(status_code=403, content={"detail": "Admin access required"})
            return await call_next(request)

        provided_api_key = request.headers.get("X-API-Key", "")
        if not provided_api_key or not hmac.compare_digest(provided_api_key, api_key):
            return JSONResponse(status_code=401, content={"detail": "Invalid or missing API key"})
        return await call_next(request)
