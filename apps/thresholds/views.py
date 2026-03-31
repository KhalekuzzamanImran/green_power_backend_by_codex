from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from apps.audit_logs.mixins import AuditModelViewSetMixin
from apps.audit_logs.models import AuditAction
from apps.core.permissions import CanSetThreshold
from apps.devices.views import get_accessible_devices
from apps.thresholds.models import DeviceThreshold
from apps.thresholds.serializers import DeviceThresholdSerializer


class DeviceThresholdViewSet(AuditModelViewSetMixin, viewsets.ModelViewSet):
    queryset = DeviceThreshold.objects.all()
    serializer_class = DeviceThresholdSerializer
    permission_classes = [CanSetThreshold]
    audit_action_create = AuditAction.THRESHOLD_UPDATE
    audit_action_update = AuditAction.THRESHOLD_UPDATE
    audit_action_delete = AuditAction.DELETE

    def get_queryset(self):
        return DeviceThreshold.objects.filter(device__in=get_accessible_devices(self.request.user)).select_related(
            "device",
            "updated_by",
        )

    def get_audit_description(self, action, instance):
        verb = "Updated" if action == AuditAction.THRESHOLD_UPDATE else action.title()
        return f"{verb} threshold {instance.key} for {instance.device.serial_number}"

    def get_audit_extra_metadata(self, action, instance, serializer=None):
        metadata = super().get_audit_extra_metadata(action, instance, serializer=serializer)
        metadata["device_id"] = str(instance.device_id)
        return metadata

    def perform_create(self, serializer):
        device = serializer.validated_data["device"]
        if not get_accessible_devices(self.request.user).filter(pk=device.pk).exists():
            raise ValidationError("You do not have access to this device.")
        serializer.save(updated_by=self.request.user)
        instance = serializer.instance
        self.write_audit(action=self.audit_action_create, instance=instance, serializer=serializer)

    def perform_update(self, serializer):
        device = serializer.instance.device
        if not get_accessible_devices(self.request.user).filter(pk=device.pk).exists():
            raise ValidationError("You do not have access to this device.")
        changed_fields = list(serializer.validated_data.keys())
        serializer.save(updated_by=self.request.user)
        instance = serializer.instance
        self.write_audit(
            action=self.audit_action_update,
            instance=instance,
            serializer=serializer,
            changed_fields=changed_fields,
        )

    def perform_destroy(self, instance):
        if not get_accessible_devices(self.request.user).filter(pk=instance.device.pk).exists():
            raise ValidationError("You do not have access to this device.")
        super().perform_destroy(instance)
