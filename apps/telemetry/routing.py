from __future__ import annotations

from django.urls import path

from apps.telemetry.consumers import TCPConsumer, TelemetryConsumer

websocket_urlpatterns = [
    path("ws/telemetry/", TelemetryConsumer.as_asgi()),
    path("ws/tcp/", TCPConsumer.as_asgi()),
]
