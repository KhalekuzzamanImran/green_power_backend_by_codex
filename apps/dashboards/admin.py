from django.contrib import admin

from apps.dashboards.models import Dashboard, DashboardScope


@admin.register(DashboardScope)
class DashboardScopeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    search_fields = ("name", "code")
    list_filter = ("is_active",)


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "client_type", "scope", "is_active")
    search_fields = ("name", "code")
    list_filter = ("client_type", "scope", "is_active")
