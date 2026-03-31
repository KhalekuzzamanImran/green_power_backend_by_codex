from rest_framework import viewsets

from apps.access_control.models import OMClientAccess, UserClientAccess
from apps.access_control.serializers import (
    OMClientAccessSerializer,
    UserClientAccessSerializer,
)
from apps.audit_logs.mixins import AuditModelViewSetMixin
from apps.audit_logs.models import AuditAction
from apps.core.permissions import CanManageUsers


class UserClientAccessViewSet(AuditModelViewSetMixin, viewsets.ModelViewSet):
    queryset = UserClientAccess.objects.select_related("user", "client").all()
    serializer_class = UserClientAccessSerializer
    permission_classes = [CanManageUsers]
    audit_action_create = AuditAction.ASSIGN

    def get_audit_description(self, action, instance):
        return f"{action.title()}d user-client access {instance.user.username} -> {instance.client.site_name}"


class OMClientAccessViewSet(AuditModelViewSetMixin, viewsets.ModelViewSet):
    queryset = OMClientAccess.objects.select_related("om_user", "client").all()
    serializer_class = OMClientAccessSerializer
    permission_classes = [CanManageUsers]
    audit_action_create = AuditAction.ASSIGN

    def get_audit_description(self, action, instance):
        return f"{action.title()}d O&M access {instance.om_user.username} -> {instance.client.site_name}"
