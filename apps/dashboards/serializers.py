from rest_framework import serializers

from apps.dashboards.models import ClientType, Dashboard, DashboardScope


class ClientTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientType
        fields = (
            "id",
            "code",
            "name",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class DashboardScopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardScope
        fields = (
            "id",
            "code",
            "name",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class DashboardSerializer(serializers.ModelSerializer):
    client_type_code = serializers.CharField(source="client_type.code", read_only=True)
    client_type_name = serializers.CharField(source="client_type.name", read_only=True)
    scope_code = serializers.CharField(source="scope.code", read_only=True)
    scope_name = serializers.CharField(source="scope.name", read_only=True)

    class Meta:
        model = Dashboard
        fields = (
            "id",
            "name",
            "code",
            "client_type",
            "client_type_code",
            "client_type_name",
            "scope",
            "scope_code",
            "scope_name",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
