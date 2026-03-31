import uuid
from decimal import Decimal

from django.db import models

from apps.audit_logs.models import AuditLog


SENSITIVE_FIELD_NAMES = {"password", "last_login"}


def _serialize_field_value(value):
    if value is None:
        return None
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except TypeError:
            return str(value)
    if isinstance(value, models.Model):
        return str(value.pk)
    return value


def get_action_label(action):
    action_map = {
        "CREATE": "Created",
        "UPDATE": "Updated",
        "DELETE": "Deleted",
        "ASSIGN": "Assigned",
        "THRESHOLD_UPDATE": "Updated",
        "LOGIN": "Logged in",
        "LOGOUT": "Logged out",
    }
    return action_map.get(str(action), str(action).replace("_", " ").title())


def serialize_instance(instance):
    payload = {}
    for field in instance._meta.concrete_fields:
        if field.name in SENSITIVE_FIELD_NAMES:
            continue
        value = getattr(instance, field.name)
        if field.is_relation:
            payload[field.name] = str(value.pk) if value is not None else None
        else:
            payload[field.name] = _serialize_field_value(value)

    if hasattr(instance, "groups"):
        payload["groups"] = list(instance.groups.values_list("name", flat=True))
    if hasattr(instance, "user_permissions"):
        payload["user_permissions"] = list(
            instance.user_permissions.values_list("codename", flat=True)
        )

    return payload


def build_request_metadata(request=None, source=None):
    metadata = {}
    if source:
        metadata["source"] = source
    if request is None:
        return metadata

    metadata.update(
        {
            "path": request.path,
            "method": request.method,
            "query_params": request.GET.dict(),
        }
    )
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    remote_addr = forwarded_for.split(",")[0].strip() if forwarded_for else request.META.get("REMOTE_ADDR")
    if remote_addr:
        metadata["remote_addr"] = remote_addr
    return metadata


def write_audit_log(
    *,
    actor,
    action,
    target_type,
    target_id,
    description="",
    metadata=None,
):
    return AuditLog.objects.create(
        actor=actor,
        action=action,
        target_type=target_type,
        target_id=str(target_id),
        description=description,
        metadata=metadata or {},
    )


def audit_model_event(
    *,
    actor,
    action,
    instance,
    description="",
    request=None,
    source=None,
    changed_fields=None,
    extra_metadata=None,
):
    metadata = build_request_metadata(request=request, source=source)
    metadata["snapshot"] = serialize_instance(instance)
    if changed_fields:
        metadata["changed_fields"] = list(changed_fields)
    if extra_metadata:
        metadata.update(extra_metadata)

    return write_audit_log(
        actor=actor,
        action=action,
        target_type=instance.__class__.__name__,
        target_id=instance.pk,
        description=description,
        metadata=metadata,
    )
