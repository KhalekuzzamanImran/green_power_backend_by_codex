from django.contrib import admin

from apps.thresholds.models import DeviceThreshold


@admin.register(DeviceThreshold)
class DeviceThresholdAdmin(admin.ModelAdmin):
    list_display = ("device", "key", "value", "unit", "updated_by")
    search_fields = ("device__serial_number", "key")
