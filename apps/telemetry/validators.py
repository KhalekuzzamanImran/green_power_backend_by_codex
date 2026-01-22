from __future__ import annotations

from pydantic import ValidationError

from apps.telemetry.schemas import validate_message


def validate_packet(message: dict) -> None:
    try:
        validate_message(message)
    except ValidationError as exc:
        raise ValueError(_format_validation_error(exc)) from exc


def _format_validation_error(exc: ValidationError) -> str:
    parts = []
    for error in exc.errors():
        location = ".".join(str(item) for item in error.get("loc", []))
        msg = error.get("msg", "invalid")
        error_type = error.get("type", "error")
        parts.append(f"{location}: {msg} ({error_type})")
    return "; ".join(parts) if parts else "invalid payload"
