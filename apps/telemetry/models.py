from django.db import models


class TelemetryEvent(models.Model):
    """Minimal placeholder for MQTT telemetry/event storage."""

    topic = models.CharField(max_length=255)
    payload = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "telemetry_events"
