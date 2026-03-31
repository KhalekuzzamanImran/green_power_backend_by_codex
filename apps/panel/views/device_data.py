from django.views.generic import TemplateView

from apps.devices.models import TopicData
from apps.panel.forms import TopicDataPanelForm
from apps.panel.navigation import build_panel_navigation
from apps.panel.permissions import PanelAccessMixin
from apps.panel.services.device_service import get_panel_device_data, get_panel_device_states
from apps.panel.views.common import PanelCreateView, PanelDeleteView, PanelUpdateView


class DeviceDataListView(PanelAccessMixin, TemplateView):
    template_name = "panel/device_data/list.html"
    page_title = "Device Data"
    active_nav_key = "device_data"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        device_id = self.request.GET.get("device_id")
        topic_id = self.request.GET.get("topic_id")
        context["nav_items"] = build_panel_navigation(self.request.user)
        context["device_states"] = get_panel_device_states(self.request.user, client_id=self.client_id, device_id=device_id)
        context["rows"] = get_panel_device_data(self.request.user, client_id=self.client_id, device_id=device_id, topic_id=topic_id)[:100]
        context["selected_device_id"] = device_id or ""
        context["selected_topic_id"] = topic_id or ""
        return context


class DeviceDataCreateView(PanelCreateView):
    model = TopicData
    form_class = TopicDataPanelForm
    page_title = "Create Device Data"
    active_nav_key = "device_data"
    success_url_name = "panel:device-data"
    success_message = "Device data created successfully."


class DeviceDataUpdateView(PanelUpdateView):
    model = TopicData
    form_class = TopicDataPanelForm
    page_title = "Edit Device Data"
    active_nav_key = "device_data"
    success_url_name = "panel:device-data"
    success_message = "Device data updated successfully."


class DeviceDataDeleteView(PanelDeleteView):
    model = TopicData
    page_title = "Delete Device Data"
    active_nav_key = "device_data"
    success_url_name = "panel:device-data"
    success_message = "Device data deleted successfully."
