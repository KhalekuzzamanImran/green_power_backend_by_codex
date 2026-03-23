from rest_framework import viewsets

from apps.access_control.models import ClientProfile, OMClientAccess, UserPermissionOverride
from apps.access_control.serializers import (
    ClientProfileSerializer,
    OMClientAccessSerializer,
    UserPermissionOverrideSerializer,
)
from apps.audit_logs.models import AuditAction, AuditLog
from apps.core.permissions import CanManageUsers


class AuditMixin:
    audit_target_type = None

    def write_audit(self, action, instance, description):
        AuditLog.objects.create(
            actor=self.request.user,
            action=action,
            target_type=self.audit_target_type,
            target_id=str(instance.id),
            description=description,
        )

    def perform_create(self, serializer):
        instance = serializer.save()
        self.write_audit(AuditAction.ASSIGN, instance, f"Created {self.audit_target_type} assignment")

    def perform_update(self, serializer):
        instance = serializer.save()
        self.write_audit(AuditAction.UPDATE, instance, f"Updated {self.audit_target_type} assignment")

    def perform_destroy(self, instance):
        self.write_audit(AuditAction.DELETE, instance, f"Deleted {self.audit_target_type} assignment")
        instance.delete()


class ClientProfileViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = ClientProfile.objects.select_related("user", "client").all()
    serializer_class = ClientProfileSerializer
    permission_classes = [CanManageUsers]
    audit_target_type = "ClientProfile"


class OMClientAccessViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = OMClientAccess.objects.select_related("om_user", "client").all()
    serializer_class = OMClientAccessSerializer
    permission_classes = [CanManageUsers]
    audit_target_type = "OMClientAccess"

class UserPermissionOverrideViewSet(AuditMixin, viewsets.ModelViewSet):
    queryset = UserPermissionOverride.objects.select_related("user").all()
    serializer_class = UserPermissionOverrideSerializer
    permission_classes = [CanManageUsers]
    audit_target_type = "UserPermissionOverride"
