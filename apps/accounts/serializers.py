from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.access_control.selectors import get_accessible_clients_for_client_user, get_selected_client
from apps.accounts.models import User
from apps.dashboards.models import Dashboard


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "role",
            "is_active",
            "is_staff",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "role",
            "password",
            "is_active",
            "is_staff",
        )
        read_only_fields = ("id",)

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class MeSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    client_id = serializers.SerializerMethodField()
    client_type = serializers.SerializerMethodField()
    dashboard_scope = serializers.SerializerMethodField()
    accessible_clients = serializers.SerializerMethodField()
    requires_client_selection = serializers.SerializerMethodField()
    allowed_dashboards = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "client_id",
            "client_type",
            "dashboard_scope",
            "accessible_clients",
            "requires_client_selection",
            "permissions",
            "allowed_dashboards",
        )

    def _get_selected_client(self, obj):
        request = self.context.get("request")
        client_id = None
        if request:
            client_id = request.query_params.get("client_id")
        if obj.role != "CLIENT":
            return None
        return get_selected_client(obj, client_id=client_id, require_selection=False)

    @extend_schema_field({"type": "object"})
    def get_permissions(self, obj):
        can_set_threshold = obj.role in {"ADMIN", "OM"}
        can_view_all_clients = obj.role == "ADMIN"
        return {
            "can_manage_users": obj.role == "ADMIN",
            "can_set_threshold": can_set_threshold,
            "can_view_all_clients": can_view_all_clients,
        }

    @extend_schema_field({"type": "string", "nullable": True})
    def get_client_id(self, obj):
        client = self._get_selected_client(obj)
        return str(client.id) if client else None

    @extend_schema_field({"type": "string", "nullable": True})
    def get_client_type(self, obj):
        client = self._get_selected_client(obj)
        return client.client_type.code if client else None

    @extend_schema_field({"type": "string", "nullable": True})
    def get_dashboard_scope(self, obj):
        client = self._get_selected_client(obj)
        return client.dashboard_scope.code if client else None

    @extend_schema_field({"type": "array", "items": {"type": "object"}})
    def get_accessible_clients(self, obj):
        if obj.role != "CLIENT":
            return []
        return [
            {
                "id": str(client.id),
                "site_name": client.site_name,
                "code": client.code,
                "client_type": client.client_type.code,
                "dashboard_scope": client.dashboard_scope.code,
            }
            for client in get_accessible_clients_for_client_user(obj)
        ]

    @extend_schema_field({"type": "boolean"})
    def get_requires_client_selection(self, obj):
        if obj.role != "CLIENT":
            return False
        return get_accessible_clients_for_client_user(obj).count() > 1

    @extend_schema_field({"type": "array", "items": {"type": "string"}})
    def get_allowed_dashboards(self, obj):
        if obj.role == "ADMIN":
            return list(Dashboard.objects.filter(is_active=True).values_list("code", flat=True))
        if obj.role == "OM":
            return list(Dashboard.objects.filter(is_active=True).values_list("code", flat=True))
        client = self._get_selected_client(obj)
        if not client:
            return []
        return list(
            Dashboard.objects.filter(
                is_active=True,
                client_type=client.client_type,
                scope=client.dashboard_scope,
            ).values_list("code", flat=True)
        )
