from rest_framework import serializers

from apps.telemetry.models import TelemetryEvent


class TelemetryEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelemetryEvent
        fields = ("id", "topic", "payload", "created_at")


class TelemetryEventMongoSerializer(serializers.Serializer):
    id = serializers.CharField()
    topic = serializers.CharField()
    device_id = serializers.CharField(required=False, allow_null=True)
    timestamp = serializers.DateTimeField(required=False, allow_null=True)
    payload = serializers.JSONField()


class RTDataSerializer(serializers.Serializer):
    id = serializers.CharField()
    topic = serializers.CharField()
    device_id = serializers.CharField(required=False, allow_null=True)
    timestamp = serializers.DateTimeField()
    payload = serializers.JSONField()


class EnyNowDataSerializer(serializers.Serializer):
    id = serializers.CharField()
    topic = serializers.CharField()
    device_id = serializers.CharField(required=False, allow_null=True)
    timestamp = serializers.DateTimeField()
    payload = serializers.JSONField()


class EnvironmentDataSerializer(serializers.Serializer):
    id = serializers.CharField()
    topic = serializers.CharField()
    device_id = serializers.CharField(required=False, allow_null=True)
    timestamp = serializers.DateTimeField()
    payload = serializers.JSONField()


class SolarDataSerializer(serializers.Serializer):
    id = serializers.CharField()
    device_id = serializers.CharField(required=False, allow_null=True)
    timestamp = serializers.DateTimeField()
    payload = serializers.JSONField()


class GeneratorDataSerializer(serializers.Serializer):
    id = serializers.CharField()
    topic = serializers.CharField()
    device_id = serializers.CharField(required=False, allow_null=True)
    timestamp = serializers.DateTimeField()
    payload = serializers.JSONField()
