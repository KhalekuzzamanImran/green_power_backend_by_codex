from django.contrib import admin

from apps.clients.models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "contact_person", "is_active")
    search_fields = ("name", "code", "contact_person")
    list_filter = ("is_active",)

# Register your models here.
