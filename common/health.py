from django.conf import settings
from django.core.cache import cache
from django.db import connections
from redis import Redis
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

HEALTH_CACHE_KEY = "health:status"
HEALTH_CACHE_TTL_SECONDS = 5
HEALTH_DB_TIMEOUT_MS = 200
HEALTH_REDIS_TIMEOUT_SECONDS = 0.2


class ReadinessCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(responses={200: dict})
    def get(self, request, *args, **kwargs):
        """Lightweight readiness/liveness endpoint for load balancers."""
        return Response({"status": "ready"})


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(responses={200: dict})
    def get(self, request, *args, **kwargs):
        """Deep dependency check; intended for low-frequency probes only."""
        try:
            cached = cache.get(HEALTH_CACHE_KEY)
        except Exception:
            cached = None
        if cached is not None:
            return Response(cached["payload"], status=cached["status_code"])

        db_ok = True
        try:
            with connections["default"].cursor() as cursor:
                if connections["default"].vendor == "postgresql":
                    cursor.execute("SET LOCAL statement_timeout = %s", [HEALTH_DB_TIMEOUT_MS])
                cursor.execute("SELECT 1")
        except Exception:
            db_ok = False

        cache_ok = True
        try:
            redis = Redis.from_url(settings.REDIS_URL, socket_timeout=HEALTH_REDIS_TIMEOUT_SECONDS)
            cache_ok = bool(redis.ping())
        except Exception:
            cache_ok = False

        status_code = 200 if db_ok and cache_ok else 503
        payload = {
            "status": "ok" if status_code == 200 else "degraded",
            "database": db_ok,
            "cache": cache_ok,
            "environment": settings.ENVIRONMENT,
        }
        try:
            cache.set(
                HEALTH_CACHE_KEY,
                {"payload": payload, "status_code": status_code},
                timeout=HEALTH_CACHE_TTL_SECONDS,
            )
        except Exception:
            pass
        return Response(payload, status=status_code)
