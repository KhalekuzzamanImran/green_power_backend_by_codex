from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.access_control.models import OMClientAccess
from apps.access_control.selectors import get_accessible_clients_for_client_user, get_selected_client
from apps.accounts.models import RoleChoices
from apps.audit_logs.models import AuditAction, AuditLog
from apps.clients.models import Client, ClientType
from apps.clients.serializers import ClientSerializer, ClientTypeSerializer
from apps.core.permissions import IsAdminOrReadOnly


class ClientTypeViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = ClientType.objects.filter(is_active=True).order_by("name")
    serializer_class = ClientTypeSerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = Client.objects.all().order_by("site_name")
        if user.role == RoleChoices.ADMIN:
            return queryset
        if user.role == RoleChoices.OM:
            client_ids = OMClientAccess.objects.filter(om_user=user).values_list("client_id", flat=True)
            return queryset.filter(id__in=client_ids)
        if user.role == RoleChoices.CLIENT:
            return get_accessible_clients_for_client_user(user)
        return queryset.none()

    def perform_create(self, serializer):
        client = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            action=AuditAction.CREATE,
            target_type="Client",
            target_id=str(client.id),
            description=f"Created client {client.site_name}",
        )

    def perform_update(self, serializer):
        client = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            action=AuditAction.UPDATE,
            target_type="Client",
            target_id=str(client.id),
            description=f"Updated client {client.site_name}",
        )

    def perform_destroy(self, instance):
        AuditLog.objects.create(
            actor=self.request.user,
            action=AuditAction.DELETE,
            target_type="Client",
            target_id=str(instance.id),
            description=f"Deleted client {instance.site_name}",
        )
        instance.delete()

    @action(detail=False, methods=["get"], url_path="my")
    def my_client(self, request):
        if request.user.role != RoleChoices.CLIENT:
            return Response({"detail": "Client access not available."}, status=404)
        client = get_selected_client(request.user, request.query_params.get("client_id"), require_selection=True)
        serializer = self.get_serializer(client)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="my-clients")
    def my_clients(self, request):
        if request.user.role != RoleChoices.CLIENT:
            return Response({"detail": "Client access not available."}, status=404)
        serializer = self.get_serializer(get_accessible_clients_for_client_user(request.user), many=True)
        return Response(serializer.data)
