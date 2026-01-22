from rest_framework import serializers

from apps.telemetry.models import TelemetryEvent


class TelemetryEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelemetryEvent
        fields = ("id", "topic", "payload", "created_at")
