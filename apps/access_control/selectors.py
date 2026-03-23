from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.access_control.models import UserClientAccess
from apps.clients.models import Client


def get_client_accesses(user):
    return UserClientAccess.objects.filter(user=user, is_active=True).select_related(
        "client",
        "client__client_type",
        "client__dashboard_scope",
    )


def get_selected_client(user, client_id=None, require_selection=False):
    accesses = get_client_accesses(user)
    if client_id:
        access = accesses.filter(client_id=client_id).first()
        if not access:
            raise PermissionDenied("You do not have access to the requested client.")
        return access.client

    if accesses.count() == 1:
        return accesses.first().client

    default_access = accesses.filter(is_default=True).first()
    if default_access and not require_selection:
        return default_access.client

    if require_selection and accesses.exists():
        raise ValidationError({"client_id": "client_id is required when the user has access to multiple clients."})

    return None


def get_accessible_clients_for_client_user(user):
    client_ids = get_client_accesses(user).values_list("client_id", flat=True)
    return Client.objects.filter(id__in=client_ids).order_by("name")
