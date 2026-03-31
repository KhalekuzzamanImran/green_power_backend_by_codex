from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import audit_model_event, get_action_label


class AuditModelViewSetMixin:
    audit_action_create = AuditAction.CREATE
    audit_action_update = AuditAction.UPDATE
    audit_action_delete = AuditAction.DELETE
    audit_source = "api"

    def get_audit_description(self, action, instance):
        return f"{get_action_label(action)} {instance.__class__.__name__} {instance}"

    def get_audit_extra_metadata(self, action, instance, serializer=None):
        metadata = {}
        if serializer is not None:
            metadata["validated_fields"] = sorted(serializer.validated_data.keys())
        return metadata

    def write_audit(self, *, action, instance, serializer=None, changed_fields=None):
        return audit_model_event(
            actor=self.request.user,
            action=action,
            instance=instance,
            description=self.get_audit_description(action, instance),
            request=self.request,
            source=self.audit_source,
            changed_fields=changed_fields,
            extra_metadata=self.get_audit_extra_metadata(action, instance, serializer=serializer),
        )

    def perform_create(self, serializer):
        instance = serializer.save()
        self.write_audit(action=self.audit_action_create, instance=instance, serializer=serializer)

    def perform_update(self, serializer):
        changed_fields = list(serializer.validated_data.keys())
        instance = serializer.save()
        self.write_audit(
            action=self.audit_action_update,
            instance=instance,
            serializer=serializer,
            changed_fields=changed_fields,
        )

    def perform_destroy(self, instance):
        self.write_audit(action=self.audit_action_delete, instance=instance)
        instance.delete()
