from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, reverse

from apps.clients.forms import ClientAdminForm, get_dashboard_scope_queryset
from apps.clients.models import Client, ClientType
from apps.devices.models import Device


@admin.register(ClientType)
class ClientTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    search_fields = ("name", "code")
    list_filter = ("is_active",)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    form = ClientAdminForm
    list_display = ("site_name", "code", "client_type", "dashboard_scope", "is_active")
    search_fields = ("site_name", "code", "client_type__name", "dashboard_scope__name")
    list_filter = ("client_type", "dashboard_scope", "is_active")

    class Media:
        js = ("clients/js/client_admin.js",)

    class DeviceInline(admin.TabularInline):
        model = Device
        fields = ("name", "serial_number", "device_type", "installed_at", "is_active")
        readonly_fields = fields
        extra = 0
        can_delete = False
        show_change_link = True
        verbose_name_plural = "Installed devices"

        def has_add_permission(self, request, obj=None):
            return False

    inlines = (DeviceInline,)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["dashboard_scope"].widget.attrs["data-scope-options-url"] = reverse(
            f"{self.admin_site.name}:clients_client_dashboard_scope_options"
        )
        return form

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "dashboard-scope-options/",
                self.admin_site.admin_view(self.dashboard_scope_options_view),
                name="clients_client_dashboard_scope_options",
            ),
        ]
        return custom_urls + urls

    def dashboard_scope_options_view(self, request):
        client_type_id = request.GET.get("client_type_id")
        results = [
            {"id": str(scope.id), "name": scope.name}
            for scope in get_dashboard_scope_queryset(client_type_id)
        ]
        return JsonResponse({"results": results})
