from django.contrib import admin

from apps.devices.models import Device, DeviceData


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "serial_number", "device_type", "client", "is_active")
    search_fields = ("name", "serial_number", "client__name")
    list_filter = ("device_type", "is_active")


@admin.register(DeviceData)
class DeviceDataAdmin(admin.ModelAdmin):
    list_display = ("device", "recorded_at", "created_at")
    search_fields = ("device__serial_number",)
    list_filter = ("recorded_at",)

# Register your models here.
