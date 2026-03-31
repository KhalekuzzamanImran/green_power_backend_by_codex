from django.http import Http404
from django.views.generic import TemplateView

from apps.devices.models import Device
from apps.panel.forms import DevicePanelForm
from apps.panel.navigation import build_panel_navigation
from apps.panel.permissions import PanelAccessMixin
from apps.panel.services.device_service import get_panel_devices, get_panel_device_states, get_panel_thresholds
from apps.panel.views.common import PanelCreateView, PanelDeleteView, PanelUpdateView


class DeviceListView(PanelAccessMixin, TemplateView):
    template_name = "panel/devices/list.html"
    page_title = "Devices"
    active_nav_key = "devices"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        device_type = self.request.GET.get("device_type")
        devices = get_panel_devices(self.request.user, client_id=self.client_id)
        if device_type:
            devices = devices.filter(device_type=device_type)
        context["nav_items"] = build_panel_navigation(self.request.user)
        context["devices"] = devices
        context["selected_device_type"] = device_type or ""
        return context


class DeviceDetailView(PanelAccessMixin, TemplateView):
    template_name = "panel/devices/detail.html"
    page_title = "Device Detail"
    active_nav_key = "devices"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        device = get_panel_devices(self.request.user, client_id=self.client_id).filter(pk=self.kwargs["device_id"]).first()
        if not device:
            raise Http404("Device not found.")
        context["nav_items"] = build_panel_navigation(self.request.user)
        context["device"] = device
        context["states"] = get_panel_device_states(self.request.user, client_id=str(device.client_id), device_id=str(device.id))
        context["thresholds"] = get_panel_thresholds(self.request.user, client_id=str(device.client_id)).filter(device=device)
        return context


class DeviceCreateView(PanelCreateView):
    model = Device
    form_class = DevicePanelForm
    page_title = "Create Device"
    active_nav_key = "devices"
    success_url_name = "panel:devices"
    success_message = "Device created successfully."


class DeviceUpdateView(PanelUpdateView):
    model = Device
    form_class = DevicePanelForm
    page_title = "Edit Device"
    active_nav_key = "devices"
    success_url_name = "panel:devices"
    success_message = "Device updated successfully."


class DeviceDeleteView(PanelDeleteView):
    model = Device
    page_title = "Delete Device"
    active_nav_key = "devices"
    success_url_name = "panel:devices"
    success_message = "Device deleted successfully."
