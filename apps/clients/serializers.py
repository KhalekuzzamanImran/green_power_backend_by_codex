from rest_framework import serializers

from apps.clients.models import Client, ClientType
from apps.clients.utils import generate_unique_client_code, normalize_client_code
from apps.dashboards.models import Dashboard


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


class ClientSerializer(serializers.ModelSerializer):
    client_type_code = serializers.CharField(source="client_type.code", read_only=True)
    client_type_name = serializers.CharField(source="client_type.name", read_only=True)
    dashboard_scope_code = serializers.CharField(source="dashboard_scope.code", read_only=True)
    dashboard_scope_name = serializers.CharField(source="dashboard_scope.name", read_only=True)

    class Meta:
        model = Client
        fields = (
            "id",
            "site_name",
            "code",
            "client_type",
            "client_type_code",
            "client_type_name",
            "dashboard_scope",
            "dashboard_scope_code",
            "dashboard_scope_name",
            "address",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
        extra_kwargs = {
            "code": {"required": False, "allow_blank": True},
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        client_type = attrs.get("client_type") or getattr(self.instance, "client_type", None)
        dashboard_scope = attrs.get("dashboard_scope") or getattr(self.instance, "dashboard_scope", None)
        code = attrs.get("code")
        site_name = attrs.get("site_name") or getattr(self.instance, "site_name", "")

        if code:
            normalized_code = normalize_client_code(code)
            duplicate_qs = Client.objects.filter(code=normalized_code)
            if self.instance:
                duplicate_qs = duplicate_qs.exclude(pk=self.instance.pk)
            if duplicate_qs.exists():
                raise serializers.ValidationError({"code": "Client code must be unique."})
            attrs["code"] = normalized_code
        else:
            attrs["code"] = generate_unique_client_code(
                site_name,
                model=Client,
                exclude_client_id=getattr(self.instance, "pk", None),
            )

        if client_type and dashboard_scope and not Dashboard.objects.filter(
            client_type=client_type,
            scope=dashboard_scope,
            is_active=True,
        ).exists():
            raise serializers.ValidationError(
                {"dashboard_scope": "Selected dashboard scope is not available for this client type."}
            )

        return attrs
