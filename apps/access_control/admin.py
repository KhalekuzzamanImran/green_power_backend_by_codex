from django.contrib import admin

from apps.access_control.models import ClientProfile, OMClientAccess, UserPermissionOverride


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "client")
    search_fields = ("user__username", "client__name")


@admin.register(OMClientAccess)
class OMClientAccessAdmin(admin.ModelAdmin):
    list_display = ("om_user", "client")
    search_fields = ("om_user__username", "client__name")

@admin.register(UserPermissionOverride)
class UserPermissionOverrideAdmin(admin.ModelAdmin):
    list_display = ("user", "can_set_threshold", "can_view_all_clients")

# Register your models here.
