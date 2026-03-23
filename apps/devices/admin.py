from django.contrib import admin

from apps.devices.models import Device, Topic, TopicData


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "serial_number", "device_type", "client", "is_active")
    search_fields = ("name", "serial_number", "client__name")
    list_filter = ("device_type", "is_active")


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "device", "is_active")
    search_fields = ("name", "code", "device__serial_number", "device__client__name")
    list_filter = ("is_active",)


@admin.register(TopicData)
class TopicDataAdmin(admin.ModelAdmin):
    list_display = ("topic", "recorded_at", "created_at")
    search_fields = ("topic__code", "topic__device__serial_number")
    list_filter = ("recorded_at",)
