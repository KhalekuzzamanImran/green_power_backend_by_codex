from rest_framework import serializers

from apps.service_zones.models import Device, DeviceStat, ServiceZone


class ServiceZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceZone
        fields = "__all__"


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = "__all__"


class DeviceStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceStat
        fields = "__all__"
