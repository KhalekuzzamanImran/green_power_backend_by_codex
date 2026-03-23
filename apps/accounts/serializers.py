from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

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
            "permissions",
            "allowed_dashboards",
        )

    @extend_schema_field({"type": "object"})
    def get_permissions(self, obj):
        override = getattr(obj, "permission_override", None)
        can_set_threshold = obj.role in {"ADMIN", "OM"}
        can_view_all_clients = obj.role == "ADMIN"
        if override:
            can_set_threshold = can_set_threshold or override.can_set_threshold
            can_view_all_clients = can_view_all_clients or override.can_view_all_clients
        return {
            "can_manage_users": obj.role == "ADMIN",
            "can_set_threshold": can_set_threshold,
            "can_view_all_clients": can_view_all_clients,
        }

    @extend_schema_field({"type": "string", "nullable": True})
    def get_client_id(self, obj):
        profile = getattr(obj, "client_profile", None)
        return str(profile.client_id) if profile else None

    @extend_schema_field({"type": "array", "items": {"type": "string"}})
    def get_allowed_dashboards(self, obj):
        if obj.role == "ADMIN":
            return list(Dashboard.objects.filter(is_active=True).values_list("code", flat=True))
        if obj.role == "OM":
            return list(Dashboard.objects.filter(is_active=True).values_list("code", flat=True))
        return list(obj.dashboard_accesses.select_related("dashboard").values_list("dashboard__code", flat=True))
