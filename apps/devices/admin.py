from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from apps.devices.models import Device, Topic, TopicData


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    class TopicInline(admin.TabularInline):
        model = Topic
        fields = ("name", "code", "description", "is_active")
        readonly_fields = fields
        extra = 0
        can_delete = False
        show_change_link = True
        verbose_name_plural = "Device states"

        def has_add_permission(self, request, obj=None):
            return False

    list_display = ("name", "serial_number", "device_type", "client_display", "is_active")
    search_fields = ("name", "serial_number", "client__site_name")
    list_filter = ("device_type", "is_active")
    inlines = (TopicInline,)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "client" and formfield is not None:
            formfield.label_from_instance = lambda client: f"{client.site_name} ({client.code})"
        return formfield

    @admin.display(description="Client")
    def client_display(self, obj):
        return f"{obj.client.site_name} ({obj.client.code})"


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "device", "is_active", "view_device_data_link")
    search_fields = ("name", "code", "device__serial_number", "device__client__site_name")
    list_filter = ("is_active",)
    readonly_fields = ("view_device_data_link",)
    fields = ("device", "name", "code", "description", "is_active", "view_device_data_link")

    @admin.display(description="Device data")
    def view_device_data_link(self, obj):
        if not obj or not obj.pk:
            return "-"

        url = reverse("hardened_admin:devices_topicdata_changelist")
        return format_html(
            '<a class="button" href="{}?topic__id__exact={}">View Device data</a>',
            url,
            obj.pk,
        )


@admin.register(TopicData)
class TopicDataAdmin(admin.ModelAdmin):
    list_display = ("topic", "payload", "recorded_at", "created_at")
    search_fields = ("topic__code", "topic__device__serial_number")
    list_filter = ("recorded_at",)
