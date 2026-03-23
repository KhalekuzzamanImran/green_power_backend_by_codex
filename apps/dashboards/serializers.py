from rest_framework import serializers

from apps.dashboards.models import Dashboard


class DashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dashboard
        fields = (
            "id",
            "name",
            "code",
            "dashboard_type",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
