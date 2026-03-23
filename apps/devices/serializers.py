from rest_framework import serializers

from apps.devices.models import Device, Topic, TopicData


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


class TopicSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source="device.name", read_only=True)
    device_serial_number = serializers.CharField(source="device.serial_number", read_only=True)
    client_id = serializers.UUIDField(source="device.client_id", read_only=True)

    class Meta:
        model = Topic
        fields = (
            "id",
            "device",
            "device_name",
            "device_serial_number",
            "client_id",
            "name",
            "code",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

class TopicDataSerializer(serializers.ModelSerializer):
    topic_code = serializers.CharField(source="topic.code", read_only=True)
    device_serial_number = serializers.CharField(source="topic.device.serial_number", read_only=True)

    class Meta:
        model = TopicData
        fields = (
            "id",
            "topic",
            "topic_code",
            "device_serial_number",
            "payload",
            "recorded_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
