from __future__ import annotations

from apps.telemetry.services import store_event
from apps.telemetry.validators import validate_payload


def handle_message(topic: str, payload: str) -> None:
    """Domain-level handler for inbound MQTT messages."""
    validate_payload(topic, payload)
    store_event(topic, payload)
