from rest_framework import serializers

from apps.clients.models import Client


class ClientSerializer(serializers.ModelSerializer):
    client_type_code = serializers.CharField(source="client_type.code", read_only=True)
    client_type_name = serializers.CharField(source="client_type.name", read_only=True)
    dashboard_scope_code = serializers.CharField(source="dashboard_scope.code", read_only=True)
    dashboard_scope_name = serializers.CharField(source="dashboard_scope.name", read_only=True)

    class Meta:
        model = Client
        fields = (
            "id",
            "name",
            "code",
            "client_type",
            "client_type_code",
            "client_type_name",
            "dashboard_scope",
            "dashboard_scope_code",
            "dashboard_scope_name",
            "contact_person",
            "email",
            "phone",
            "address",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
