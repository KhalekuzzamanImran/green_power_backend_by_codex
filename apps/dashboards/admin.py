from django.contrib import admin

from apps.dashboards.models import Dashboard


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "dashboard_type", "is_active")
    search_fields = ("name", "code")
    list_filter = ("dashboard_type", "is_active")

# Register your models here.
