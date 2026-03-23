from rest_framework import viewsets

from apps.access_control.models import OMClientAccess
from apps.accounts.models import RoleChoices
from apps.audit_logs.models import AuditAction, AuditLog
from apps.clients.models import Client
from apps.clients.serializers import ClientSerializer
from apps.core.permissions import IsAdminOrReadOnly


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = Client.objects.all().order_by("name")
        if user.role == RoleChoices.ADMIN:
            return queryset
        if user.role == RoleChoices.OM:
            if getattr(user, "permission_override", None) and user.permission_override.can_view_all_clients:
                return queryset
            client_ids = OMClientAccess.objects.filter(om_user=user).values_list("client_id", flat=True)
            return queryset.filter(id__in=client_ids)
        if user.role == RoleChoices.CLIENT and hasattr(user, "client_profile"):
            return queryset.filter(id=user.client_profile.client_id)
        return queryset.none()

    def perform_create(self, serializer):
        client = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            action=AuditAction.CREATE,
            target_type="Client",
            target_id=str(client.id),
            description=f"Created client {client.name}",
        )

    def perform_update(self, serializer):
        client = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            action=AuditAction.UPDATE,
            target_type="Client",
            target_id=str(client.id),
            description=f"Updated client {client.name}",
        )

    def perform_destroy(self, instance):
        AuditLog.objects.create(
            actor=self.request.user,
            action=AuditAction.DELETE,
            target_type="Client",
            target_id=str(instance.id),
            description=f"Deleted client {instance.name}",
        )
        instance.delete()
