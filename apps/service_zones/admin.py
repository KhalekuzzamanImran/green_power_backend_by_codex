from django.contrib import admin

from .models import Device, DeviceStat, ServiceZone


@admin.register(ServiceZone)
class ServiceZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "status", "network_status", "user")
    search_fields = ("name", "code", "address")
    list_filter = ("status", "network_status")


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("device_name", "device_code", "status", "service_zone")
    search_fields = ("device_name", "device_code")
    list_filter = ("status",)


@admin.register(DeviceStat)
class DeviceStatAdmin(admin.ModelAdmin):
    list_display = ("device", "state")
    search_fields = ("device__device_code", "state")
