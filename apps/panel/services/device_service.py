from apps.accounts.models import RoleChoices
from apps.devices.models import Device, Topic, TopicData
from apps.panel.permissions import resolve_panel_client
from apps.thresholds.models import DeviceThreshold


def get_panel_devices(user, client_id=None):
    queryset = Device.objects.select_related("client", "client__client_type", "client__dashboard_scope").order_by("name")
    if user.role == RoleChoices.ADMIN:
        selected_client = resolve_panel_client(user, client_id=client_id)
        return queryset.filter(client=selected_client) if selected_client else queryset
    if user.role == RoleChoices.OM:
        selected_client = resolve_panel_client(user, client_id=client_id)
        if selected_client:
            return queryset.filter(client=selected_client)
        return queryset.none()
    return queryset.none()


def get_panel_device_states(user, client_id=None, device_id=None):
    queryset = Topic.objects.select_related("device", "device__client").order_by("name")
    queryset = queryset.filter(device__in=get_panel_devices(user, client_id=client_id))
    if device_id:
        queryset = queryset.filter(device_id=device_id)
    return queryset


def get_panel_device_data(user, client_id=None, device_id=None, topic_id=None):
    queryset = TopicData.objects.select_related("topic", "topic__device", "topic__device__client").order_by("-recorded_at")
    queryset = queryset.filter(topic__in=get_panel_device_states(user, client_id=client_id, device_id=device_id))
    if topic_id:
        queryset = queryset.filter(topic_id=topic_id)
    return queryset


def get_panel_thresholds(user, client_id=None):
    queryset = DeviceThreshold.objects.select_related("device", "device__client", "updated_by").order_by("device__name", "key")
    return queryset.filter(device__in=get_panel_devices(user, client_id=client_id))
