import time

from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logger import logger


class RequestTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()

        response = await call_next(request)

        elapsed = (time.time() - start) * 1000

        logger.info(f"{request.method} {request.url.path} {elapsed:.2f} ms")

        response.headers["X-Response-Time"] = f"{elapsed:.2f} ms"

        return response
