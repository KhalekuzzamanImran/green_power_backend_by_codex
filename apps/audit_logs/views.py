from rest_framework import mixins, viewsets

from apps.audit_logs.models import AuditLog
from apps.audit_logs.serializers import AuditLogSerializer
from apps.core.permissions import IsAdminRole


class AuditLogViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = AuditLog.objects.select_related("actor").all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminRole]
