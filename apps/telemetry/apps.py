import logging

from django.apps import AppConfig


class TelemetryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.telemetry"

    def ready(self) -> None:
        from .services import ensure_today_collection_ttl_indexes

        try:
            ensure_today_collection_ttl_indexes()
        except Exception:  # pragma: no cover - defensive startup guard
            logging.getLogger(__name__).exception("Failed to ensure Mongo TTL indexes")
