from django.contrib import admin

from apps.clients.models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "client_type", "dashboard_scope", "contact_person", "is_active")
    search_fields = ("name", "code", "contact_person", "client_type__name", "dashboard_scope__name")
    list_filter = ("client_type", "dashboard_scope", "is_active")
