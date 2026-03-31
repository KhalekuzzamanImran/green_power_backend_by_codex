from django.http import Http404
from django.views.generic import TemplateView

from apps.devices.models import Topic
from apps.panel.forms import TopicPanelForm
from apps.panel.navigation import build_panel_navigation
from apps.panel.permissions import PanelAccessMixin
from apps.panel.services.device_service import get_panel_device_data, get_panel_device_states
from apps.panel.views.common import PanelCreateView, PanelDeleteView, PanelUpdateView


class DeviceStateListView(PanelAccessMixin, TemplateView):
    template_name = "panel/device_states/list.html"
    page_title = "Device States"
    active_nav_key = "device_states"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        device_id = self.request.GET.get("device_id")
        context["nav_items"] = build_panel_navigation(self.request.user)
        context["device_states"] = get_panel_device_states(self.request.user, client_id=self.client_id, device_id=device_id)
        context["selected_device_id"] = device_id or ""
        return context


class DeviceStateDetailView(PanelAccessMixin, TemplateView):
    template_name = "panel/device_states/detail.html"
    page_title = "Device State Detail"
    active_nav_key = "device_states"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        state = get_panel_device_states(self.request.user, client_id=self.client_id).filter(pk=self.kwargs["state_id"]).first()
        if not state:
            raise Http404("Device state not found.")
        context["nav_items"] = build_panel_navigation(self.request.user)
        context["device_state"] = state
        context["device_data_rows"] = get_panel_device_data(self.request.user, client_id=str(state.device.client_id), device_id=str(state.device_id), topic_id=str(state.id))[:25]
        return context


class DeviceStateCreateView(PanelCreateView):
    model = Topic
    form_class = TopicPanelForm
    page_title = "Create Device State"
    active_nav_key = "device_states"
    success_url_name = "panel:device-states"
    success_message = "Device state created successfully."


class DeviceStateUpdateView(PanelUpdateView):
    model = Topic
    form_class = TopicPanelForm
    page_title = "Edit Device State"
    active_nav_key = "device_states"
    success_url_name = "panel:device-states"
    success_message = "Device state updated successfully."


class DeviceStateDeleteView(PanelDeleteView):
    model = Topic
    page_title = "Delete Device State"
    active_nav_key = "device_states"
    success_url_name = "panel:device-states"
    success_message = "Device state deleted successfully."
