import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.logger import logger

# Routes that don't require an API key
PUBLIC_ROUTES = {"/", "/health", "/docs", "/openapi.json", "/redoc"}


class RequestTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start) * 1000
        logger.info(f"{request.method} {request.url.path} {duration_ms:.2f} ms")
        return response


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip auth for public routes
        if request.url.path in PUBLIC_ROUTES:
            return await call_next(request)

        # Skip auth if no API key is configured (local dev)
        if not settings.API_KEY:
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")

        if api_key != settings.API_KEY:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or missing API key"},
            )

        return await call_next(request)
