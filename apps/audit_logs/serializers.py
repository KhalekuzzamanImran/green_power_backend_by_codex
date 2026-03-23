from rest_framework import serializers

from apps.audit_logs.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source="actor.username", read_only=True)

    class Meta:
        model = AuditLog
        fields = (
            "id",
            "actor",
            "actor_username",
            "action",
            "target_type",
            "target_id",
            "description",
            "metadata",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
