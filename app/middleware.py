from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

STATIC_MAX_AGE = 3600  # 1 hora


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


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Define políticas de cache por rota.

    - `/static/*`: cache público de 1 hora (assets versionados raramente mudam).
    - demais respostas: `no-cache` (revalida sempre, evita servir conteúdo velho).
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        path = request.url.path
        if path.startswith("/static/"):
            response.headers.setdefault("Cache-Control", f"public, max-age={STATIC_MAX_AGE}")
        elif response.headers.get("Cache-Control") is None:
            response.headers["Cache-Control"] = "no-cache"
        return response
