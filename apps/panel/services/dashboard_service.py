from apps.accounts.models import RoleChoices, User
from apps.audit_logs.models import AuditLog
from apps.devices.models import Device, Topic, TopicData
from apps.panel.services.device_service import get_panel_devices, get_panel_device_data, get_panel_device_states, get_panel_thresholds
from apps.clients.models import Client


def build_dashboard_cards(user, selected_client=None):
    client_id = str(selected_client.id) if selected_client else None
    devices = get_panel_devices(user, client_id=client_id)
    states = get_panel_device_states(user, client_id=client_id)
    data_points = get_panel_device_data(user, client_id=client_id)

    cards = []

    if user.role == RoleChoices.ADMIN:
        cards.append({"label": "Clients", "value": _client_count(user, selected_client)})

    cards.extend(
        [
            {"label": "Devices", "value": devices.count()},
            {"label": "Device States", "value": states.count()},
            {"label": "Device Data Rows", "value": data_points.count()},
        ]
    )

    if user.role == RoleChoices.ADMIN:
        cards.append({"label": "Users", "value": User.objects.count()})

    return cards


def _client_count(user, selected_client):
    if selected_client:
        return 1
    if user.role == RoleChoices.ADMIN:
        return Client.objects.count()
    return user.assigned_clients.count()


def build_dashboard_highlights(user, selected_client=None):
    client_id = str(selected_client.id) if selected_client else None
    return {
        "recent_devices": list(get_panel_devices(user, client_id=client_id)[:5]),
        "recent_states": list(get_panel_device_states(user, client_id=client_id)[:5]),
        "latest_data": list(get_panel_device_data(user, client_id=client_id)[:10]),
        "recent_audit_logs": list(AuditLog.objects.select_related("actor")[:10]) if user.role == RoleChoices.ADMIN else [],
    }
