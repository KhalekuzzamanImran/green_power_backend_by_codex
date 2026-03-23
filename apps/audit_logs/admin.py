from django.contrib import admin

from apps.audit_logs.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "target_type", "target_id", "actor", "created_at")
    search_fields = ("target_type", "target_id", "description", "actor__username")

# Register your models here.
