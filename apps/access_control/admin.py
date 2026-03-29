from django.contrib import admin

from apps.accounts.models import RoleChoices, User
from apps.access_control.models import OMClientAccess, UserClientAccess
from apps.clients.models import Client


@admin.register(UserClientAccess)
class UserClientAccessAdmin(admin.ModelAdmin):
    list_display = ("user", "client", "is_default", "is_active")
    search_fields = ("user__username", "client__site_name")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(role=RoleChoices.CLIENT).order_by("username")
        elif db_field.name == "client":
            linked_client_ids = UserClientAccess.objects.values_list("client_id", flat=True)
            kwargs["queryset"] = Client.objects.exclude(id__in=linked_client_ids).order_by("site_name")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(OMClientAccess)
class OMClientAccessAdmin(admin.ModelAdmin):
    list_display = ("om_user", "client")
    search_fields = ("om_user__username", "client__site_name")
