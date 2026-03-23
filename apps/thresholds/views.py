from rest_framework import mixins, viewsets
from rest_framework.exceptions import ValidationError

from apps.audit_logs.models import AuditAction, AuditLog
from apps.core.permissions import CanSetThreshold
from apps.devices.views import get_accessible_devices
from apps.thresholds.models import DeviceThreshold
from apps.thresholds.serializers import DeviceThresholdSerializer


class DeviceThresholdViewSet(viewsets.ModelViewSet):
    queryset = DeviceThreshold.objects.all()
    serializer_class = DeviceThresholdSerializer
    permission_classes = [CanSetThreshold]

    def get_queryset(self):
        return DeviceThreshold.objects.filter(device__in=get_accessible_devices(self.request.user)).select_related(
            "device",
            "updated_by",
        )

    def perform_create(self, serializer):
        device = serializer.validated_data["device"]
        if not get_accessible_devices(self.request.user).filter(pk=device.pk).exists():
            raise ValidationError("You do not have access to this device.")
        threshold = serializer.save(updated_by=self.request.user)
        AuditLog.objects.create(
            actor=self.request.user,
            action=AuditAction.THRESHOLD_UPDATE,
            target_type="DeviceThreshold",
            target_id=str(threshold.id),
            description=f"Created threshold {threshold.key}",
        )

    def perform_update(self, serializer):
        device = serializer.instance.device
        if not get_accessible_devices(self.request.user).filter(pk=device.pk).exists():
            raise ValidationError("You do not have access to this device.")
        threshold = serializer.save(updated_by=self.request.user)
        AuditLog.objects.create(
            actor=self.request.user,
            action=AuditAction.THRESHOLD_UPDATE,
            target_type="DeviceThreshold",
            target_id=str(threshold.id),
            description=f"Updated threshold {threshold.key}",
        )
