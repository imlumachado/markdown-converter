from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Limita requisições por IP usando janela deslizante em memória."""

    def __init__(self, app, max_requests: int = 10, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method == "POST" and request.url.path.startswith("/api/convert"):
            client_ip = request.client.host if request.client else "unknown"
            now = time.time()

            recent = [t for t in self._hits.get(client_ip, []) if now - t < self.window_seconds]
            if len(recent) >= self.max_requests:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Muitas requisições. Aguarde alguns instantes e tente novamente."},
                    headers={"Retry-After": str(self.window_seconds)},
                )
            recent.append(now)
            self._hits[client_ip] = recent

        return await call_next(request)
