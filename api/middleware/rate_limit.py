"""Minimal rate-limit middleware placeholder."""

from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-RateLimit-Limit", "60")
        return response
