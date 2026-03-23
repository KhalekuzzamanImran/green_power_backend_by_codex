from rest_framework import serializers

from apps.access_control.models import OMClientAccess, UserClientAccess, UserPermissionOverride
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


class UserClientAccessSerializer(RoleBoundUserValidatorMixin, serializers.ModelSerializer):
    role_required = RoleChoices.CLIENT

    class Meta:
        model = UserClientAccess
        fields = ("id", "user", "client", "is_default", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        client = attrs.get("client")
        instance = getattr(self, "instance", None)
        existing_access = UserClientAccess.objects.filter(client=client)
        if instance:
            existing_access = existing_access.exclude(pk=instance.pk)
        if client and existing_access.exists():
            raise serializers.ValidationError({"client": "This client is already linked to another user."})
        return attrs


class OMClientAccessSerializer(RoleBoundUserValidatorMixin, serializers.ModelSerializer):
    role_required = RoleChoices.OM
    user_field_name = "om_user"

    class Meta:
        model = OMClientAccess
        fields = ("id", "om_user", "client", "created_at", "updated_at")
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
