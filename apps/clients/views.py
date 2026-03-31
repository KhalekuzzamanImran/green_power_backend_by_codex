from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.access_control.selectors import (
    get_accessible_clients_for_client_user,
    get_accessible_clients_for_om_user,
    get_selected_client,
)
from apps.accounts.models import RoleChoices
from apps.audit_logs.mixins import AuditModelViewSetMixin
from apps.audit_logs.services import get_action_label
from apps.clients.models import Client, ClientType
from apps.clients.serializers import ClientSerializer, ClientTypeSerializer
from apps.core.permissions import IsAdminOrReadOnly


class ClientTypeViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = ClientType.objects.filter(is_active=True).order_by("name")
    serializer_class = ClientTypeSerializer


class ClientViewSet(AuditModelViewSetMixin, viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = Client.objects.all().order_by("site_name")
        if user.role == RoleChoices.ADMIN:
            return queryset
        if user.role == RoleChoices.OM:
            return get_accessible_clients_for_om_user(user)
        if user.role == RoleChoices.CLIENT:
            return get_accessible_clients_for_client_user(user)
        return queryset.none()

    def get_audit_description(self, action, instance):
        return f"{get_action_label(action)} client {instance.site_name}"

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
