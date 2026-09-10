"""Simple in-memory rate-limiting middleware."""

import time
from collections import defaultdict, deque

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    _requests: dict[str, deque[float]] = defaultdict(deque)
    _limit = 100
    _window_seconds = 60.0

    async def dispatch(self, request, call_next):
        client_host = request.client.host if request.client else "unknown"
        now = time.monotonic()
        bucket = self._requests[client_host]

        while bucket and (now - bucket[0]) > self._window_seconds:
            bucket.popleft()

        if len(bucket) >= self._limit:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

        bucket.append(now)
        return await call_next(request)
