"""Simple API key middleware used by the ECO-IA API."""

import os

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = request.url.path
        if not path.startswith("/api/v1/services"):
            return await call_next(request)

        expected_key = os.getenv("ECO_IA_API_KEY", "")
        provided_key = request.headers.get("X-API-Key")
        if not expected_key or provided_key != expected_key:
            return JSONResponse(status_code=401, content={"detail": "Invalid or missing API key"})

        return await call_next(request)
