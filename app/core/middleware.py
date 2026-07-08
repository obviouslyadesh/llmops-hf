import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.logger import logger

from app.monitoring.metrics import (
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_IN_PROGRESS,
    HTTP_REQUESTS_TOTAL,
    HTTP_RESPONSES_TOTAL,
)

PUBLIC_ROUTES = {"/", "/health", "/docs", "/openapi.json", "/redoc"}


class RequestTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        method = request.method
        endpoint = request.url.path

        HTTP_REQUESTS_IN_PROGRESS.inc()
        HTTP_REQUESTS_TOTAL.labels(
            method=method,
            endpoint=endpoint,
        ).inc()

        start = time.perf_counter()

        try:
            response = await call_next(request)

            return response

        finally:
            duration = time.perf_counter() - start

            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method,
                endpoint=endpoint,
            ).observe(duration)

            status = (
                str(response.status_code)
                if "response" in locals()
                else "500"
            )

            HTTP_RESPONSES_TOTAL.labels(
                method=method,
                endpoint=endpoint,
                status=status,
            ).inc()

            HTTP_REQUESTS_IN_PROGRESS.dec()

            logger.info(
                "%s %s %.2f ms",
                method,
                endpoint,
                duration * 1000,
            )

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in PUBLIC_ROUTES:
            return await call_next(request)

        if not settings.API_KEY:
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")

        if api_key != settings.API_KEY:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or missing API key"},
            )

        return await call_next(request)
