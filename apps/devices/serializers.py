from rest_framework import serializers

from apps.devices.models import Device, DeviceData


class DeviceSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.name", read_only=True)

    class Meta:
        model = Device
        fields = (
            "id",
            "client",
            "client_name",
            "name",
            "serial_number",
            "device_type",
            "is_active",
            "installed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class DeviceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceData
        fields = ("id", "device", "payload", "recorded_at", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")
