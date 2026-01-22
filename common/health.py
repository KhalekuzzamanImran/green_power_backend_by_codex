import logging
from django.conf import settings
from django.core.cache import cache
from django.db import connections
from redis import Redis
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import json

from common.mongo import get_mongo_client

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
        db_ok = True
        try:
            with connections["default"].cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception:
            db_ok = False

        cache_ok = True
        try:
            redis = Redis.from_url(settings.REDIS_URL, socket_timeout=HEALTH_REDIS_TIMEOUT_SECONDS)
            cache_ok = bool(redis.ping())
        except Exception:
            cache_ok = False

        mongo_ok = _check_mongo()
        database_ok = db_ok and mongo_ok
        tcp_ok = _check_tcp()
        mqtt_ok = _check_mqtt_connected()
        status_code = 200 if database_ok and cache_ok and tcp_ok and mqtt_ok else 503
        payload = {
            "status": "ready" if status_code == 200 else "not_ready",
            "database": database_ok,
            "cache": cache_ok,
            "tcp": tcp_ok,
            "mqtt": mqtt_ok,
        }
        return Response(payload, status=status_code)


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

        mongo_ok = _check_mongo()
        database_ok = db_ok and mongo_ok
        tcp_payload = _fetch_tcp_health()
        mqtt_payload = _fetch_mqtt_health()
        tcp_ok = tcp_payload is not None
        mqtt_ok = bool(mqtt_payload and mqtt_payload.get("connected"))
        status_code = 200 if database_ok and cache_ok and tcp_ok and mqtt_ok else 503
        payload = {
            "status": "ok" if status_code == 200 else "degraded",
            "database": database_ok,
            "cache": cache_ok,
            "tcp": tcp_ok,
            "mqtt": mqtt_ok,
            "tcp_details": tcp_payload,
            "mqtt_details": mqtt_payload,
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


class TCPHealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(responses={200: dict, 503: dict})
    def get(self, request, *args, **kwargs):
        url = getattr(settings, "TCP_HEALTH_URL", "http://tcp:7001/health")
        urls = [url]
        if "tcp:7001" in url:
            urls.append(url.replace("tcp:7001", "localhost:7001"))
        last_error = None
        for candidate in urls:
            try:
                with urlopen(candidate, timeout=1.0) as resp:
                    body = resp.read()
                    payload = json.loads(body.decode("utf-8"))
                return Response(payload, status=200)
            except (URLError, HTTPError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc
                continue
        logging.getLogger("django.request").error(
            "TCP health check failed: %s", last_error
        )
        return Response({"status": "down"}, status=503)


class MQTTHealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(responses={200: dict, 503: dict})
    def get(self, request, *args, **kwargs):
        url = getattr(settings, "MQTT_HEALTH_URL", "http://mqtt:7002/health")
        urls = [url]
        if "mqtt:7002" in url:
            urls.append(url.replace("mqtt:7002", "localhost:7002"))
        last_error = None
        for candidate in urls:
            try:
                with urlopen(candidate, timeout=1.0) as resp:
                    body = resp.read()
                    payload = json.loads(body.decode("utf-8"))
                return Response(payload, status=200)
            except (URLError, HTTPError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc
                continue
        logging.getLogger("django.request").error(
            "MQTT health check failed: %s", last_error
        )
        return Response({"status": "down"}, status=503)


def _check_tcp() -> bool:
    tcp_url = getattr(settings, "TCP_HEALTH_URL", "http://tcp:7001/health")
    urls = [tcp_url]
    if "tcp:7001" in tcp_url:
        urls.append(tcp_url.replace("tcp:7001", "localhost:7001"))
    for candidate in urls:
        try:
            with urlopen(candidate, timeout=1.0) as resp:
                body = resp.read()
                json.loads(body.decode("utf-8"))
            return True
        except (URLError, HTTPError, TimeoutError, json.JSONDecodeError):
            continue
    return False


def _check_mqtt_connected() -> bool:
    mqtt_url = getattr(settings, "MQTT_HEALTH_URL", "http://mqtt:7002/health")
    urls = [mqtt_url]
    if "mqtt:7002" in mqtt_url:
        urls.append(mqtt_url.replace("mqtt:7002", "localhost:7002"))
    for candidate in urls:
        try:
            with urlopen(candidate, timeout=1.0) as resp:
                body = resp.read()
                payload = json.loads(body.decode("utf-8"))
            return bool(payload.get("connected"))
        except (URLError, HTTPError, TimeoutError, json.JSONDecodeError):
            continue
    return False


def _check_mongo() -> bool:
    try:
        client = get_mongo_client()
        client.admin.command("ping")
        return True
    except Exception:
        return False


def _fetch_tcp_health() -> dict | None:
    tcp_url = getattr(settings, "TCP_HEALTH_URL", "http://tcp:7001/health")
    urls = [tcp_url]
    if "tcp:7001" in tcp_url:
        urls.append(tcp_url.replace("tcp:7001", "localhost:7001"))
    for candidate in urls:
        try:
            with urlopen(candidate, timeout=1.0) as resp:
                body = resp.read()
                payload = json.loads(body.decode("utf-8"))
            return payload
        except (URLError, HTTPError, TimeoutError, json.JSONDecodeError):
            continue
    return None


def _fetch_mqtt_health() -> dict | None:
    mqtt_url = getattr(settings, "MQTT_HEALTH_URL", "http://mqtt:7002/health")
    urls = [mqtt_url]
    if "mqtt:7002" in mqtt_url:
        urls.append(mqtt_url.replace("mqtt:7002", "localhost:7002"))
    for candidate in urls:
        try:
            with urlopen(candidate, timeout=1.0) as resp:
                body = resp.read()
                payload = json.loads(body.decode("utf-8"))
            return payload
        except (URLError, HTTPError, TimeoutError, json.JSONDecodeError):
            continue
    return None
