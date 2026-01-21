from __future__ import annotations

import os


def validate_packet(message: dict) -> None:
    if not isinstance(message, dict):
        raise ValueError("message must be a dict")
    if not message.get("topic"):
        raise ValueError("topic is required")
    if not message.get("timestamp"):
        raise ValueError("timestamp is required")
    payload = message.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")
    topic = message.get("topic")
    strict_topics = _parse_list(os.getenv("TELEMETRY_REQUIRED_TOPICS", ""))
    enforce_strict = not strict_topics or topic in strict_topics

    require_device_topics = _parse_list(os.getenv("TELEMETRY_REQUIRE_DEVICE_ID_TOPICS", ""))
    if not require_device_topics:
        require_device_topics = strict_topics
    if not require_device_topics or topic in require_device_topics:
        if not message.get("device_id"):
            raise ValueError("device_id is required")

    if enforce_strict:
        if "time" not in payload:
            raise ValueError("payload.time is required")
        if "isend" not in payload:
            raise ValueError("payload.isend is required")

        required_fields = _parse_list(os.getenv("TELEMETRY_REQUIRED_PAYLOAD_FIELDS", ""))
        for field in required_fields:
            if field not in payload:
                raise ValueError(f"payload.{field} is required")


def _parse_list(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]
