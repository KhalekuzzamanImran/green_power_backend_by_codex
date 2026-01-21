from __future__ import annotations


def validate_payload(topic: str, payload: str) -> None:
    """Basic validation stub; expand with schema checks as needed."""
    if not topic:
        raise ValueError("topic is required")
    if payload is None:
        raise ValueError("payload is required")
