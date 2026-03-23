from rest_framework import serializers

from apps.thresholds.models import DeviceThreshold


class DeviceThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceThreshold
        fields = (
            "id",
            "device",
            "key",
            "value",
            "unit",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "updated_by", "created_at", "updated_at")
