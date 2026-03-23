from rest_framework import serializers

from apps.access_control.models import ClientDashboardAccess, ClientProfile, OMClientAccess, UserPermissionOverride
from apps.accounts.models import RoleChoices, User


class RoleBoundUserValidatorMixin:
    role_required = None
    user_field_name = "user"

    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = attrs.get(self.user_field_name)
        if user and self.role_required and user.role != self.role_required:
            raise serializers.ValidationError({self.user_field_name: f"User must have role {self.role_required}."})
        return attrs


class ClientProfileSerializer(RoleBoundUserValidatorMixin, serializers.ModelSerializer):
    role_required = RoleChoices.CLIENT

    class Meta:
        model = ClientProfile
        fields = ("id", "user", "client", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class OMClientAccessSerializer(RoleBoundUserValidatorMixin, serializers.ModelSerializer):
    role_required = RoleChoices.OM
    user_field_name = "om_user"

    class Meta:
        model = OMClientAccess
        fields = ("id", "om_user", "client", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class ClientDashboardAccessSerializer(RoleBoundUserValidatorMixin, serializers.ModelSerializer):
    role_required = RoleChoices.CLIENT
    user_field_name = "client_user"

    class Meta:
        model = ClientDashboardAccess
        fields = ("id", "client_user", "dashboard", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class UserPermissionOverrideSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPermissionOverride
        fields = (
            "id",
            "user",
            "can_set_threshold",
            "can_view_all_clients",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
