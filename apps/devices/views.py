from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.access_control.models import OMClientAccess
from apps.accounts.models import RoleChoices
from apps.audit_logs.models import AuditAction, AuditLog
from apps.core.permissions import IsAdminOrReadOnly
from apps.devices.models import Device, DeviceData
from apps.devices.serializers import DeviceDataSerializer, DeviceSerializer


def get_accessible_devices(user):
    queryset = Device.objects.select_related("client").all()
    if user.role == RoleChoices.ADMIN:
        return queryset
    if user.role == RoleChoices.OM:
        if getattr(user, "permission_override", None) and user.permission_override.can_view_all_clients:
            return queryset
        client_ids = OMClientAccess.objects.filter(om_user=user).values_list("client_id", flat=True)
        return queryset.filter(client_id__in=client_ids)
    if user.role == RoleChoices.CLIENT and hasattr(user, "client_profile"):
        return queryset.filter(client_id=user.client_profile.client_id)
    return queryset.none()


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = get_accessible_devices(self.request.user)
        client_id = self.request.query_params.get("client_id")
        device_type = self.request.query_params.get("device_type")
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        if device_type:
            queryset = queryset.filter(device_type=device_type)
        return queryset.order_by("name")

    def perform_create(self, serializer):
        device = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            action=AuditAction.CREATE,
            target_type="Device",
            target_id=str(device.id),
            description=f"Created device {device.serial_number}",
        )

    def perform_update(self, serializer):
        device = serializer.save()
        AuditLog.objects.create(
            actor=self.request.user,
            action=AuditAction.UPDATE,
            target_type="Device",
            target_id=str(device.id),
            description=f"Updated device {device.serial_number}",
        )

    def perform_destroy(self, instance):
        AuditLog.objects.create(
            actor=self.request.user,
            action=AuditAction.DELETE,
            target_type="Device",
            target_id=str(instance.id),
            description=f"Deleted device {instance.serial_number}",
        )
        instance.delete()

    @action(detail=True, methods=["get"], url_path="data")
    def data(self, request, pk=None):
        device = get_object_or_404(self.get_queryset(), pk=pk)
        queryset = device.data_points.all()
        recorded_from = request.query_params.get("from")
        recorded_to = request.query_params.get("to")
        limit = request.query_params.get("limit")
        if recorded_from:
            queryset = queryset.filter(recorded_at__gte=recorded_from)
        if recorded_to:
            queryset = queryset.filter(recorded_at__lte=recorded_to)
        if limit:
            queryset = queryset[: int(limit)]
        serializer = DeviceDataSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="data/latest")
    def latest_data(self, request, pk=None):
        device = get_object_or_404(self.get_queryset(), pk=pk)
        data = device.data_points.order_by("-recorded_at").first()
        serializer = DeviceDataSerializer(data)
        return Response(serializer.data if data else None)


class DeviceDataViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = DeviceData.objects.all()
    serializer_class = DeviceDataSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return DeviceData.objects.filter(device__in=get_accessible_devices(self.request.user)).select_related("device")
