from __future__ import annotations

from apps.telemetry.models import TelemetryEvent


def store_event(topic: str, payload: str) -> TelemetryEvent:
    """Persist inbound MQTT data; keep small and synchronous."""
    return TelemetryEvent.objects.create(topic=topic, payload=payload)
