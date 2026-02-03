import time
import uuid

from django.conf import settings

from .services import log_audit_event


class RequestMetricsMiddleware:
    """Agrega headers de observabilidad y registra requests lentos."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        request_id = request.META.get("HTTP_X_REQUEST_ID") or uuid.uuid4().hex
        request.request_id = request_id

        response = self.get_response(request)

        duration_ms = int((time.monotonic() - start) * 1000)
        response["X-Request-ID"] = request_id
        response["X-Response-Time-ms"] = str(duration_ms)

        if self._should_log(request, response, duration_ms):
            log_audit_event(
                request,
                "request_metrics",
                None,
                extra_data={
                    "path": request.path,
                    "method": request.method,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "request_id": request_id,
                },
            )

        return response

    def _should_log(self, request, response, duration_ms):
        if not request.path.startswith("/api/"):
            return False
        if request.path.startswith("/api/performance/metrics/"):
            return False
        if request.path.startswith("/api/wizard/analytics/"):
            return False
        threshold = int(getattr(settings, "OBS_SLOW_REQUEST_MS", 800))
        return duration_ms >= threshold or response.status_code >= 500
