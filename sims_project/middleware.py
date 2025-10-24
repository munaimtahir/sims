"""Custom middleware for performance monitoring and optimization."""

import logging
import time

from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger("sims.performance")


class PerformanceTimingMiddleware(MiddlewareMixin):
    """Middleware to track request/response timing for performance monitoring."""

    def process_request(self, request):
        """Mark the start time of the request."""
        request._start_time = time.perf_counter()

    def process_response(self, request, response):
        """Calculate and log request duration."""
        if hasattr(request, "_start_time"):
            duration_ms = int((time.perf_counter() - request._start_time) * 1000)
            response["X-Response-Time"] = f"{duration_ms}ms"
            
            # Log slow requests (> 1000ms)
            if duration_ms > 1000:
                logger.warning(
                    f"Slow request: {request.method} {request.path} took {duration_ms}ms",
                    extra={
                        "method": request.method,
                        "path": request.path,
                        "duration_ms": duration_ms,
                        "user": getattr(request.user, "username", "anonymous"),
                    },
                )
            else:
                logger.debug(
                    f"{request.method} {request.path} - {duration_ms}ms",
                    extra={
                        "method": request.method,
                        "path": request.path,
                        "duration_ms": duration_ms,
                    },
                )
        
        return response
