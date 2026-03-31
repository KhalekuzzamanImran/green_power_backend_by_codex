from django.views.generic import TemplateView

from apps.audit_logs.models import AuditAction
from apps.panel.forms import DeviceThresholdPanelForm
from apps.panel.navigation import build_panel_navigation
from apps.panel.permissions import AdminOrOMMixin
from apps.panel.services.device_service import get_panel_thresholds
from apps.panel.views.common import PanelCreateView, PanelDeleteView, PanelUpdateView
from apps.thresholds.models import DeviceThreshold


class ThresholdListView(AdminOrOMMixin, TemplateView):
    template_name = "panel/thresholds/list.html"
    page_title = "Thresholds"
    active_nav_key = "thresholds"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav_items"] = build_panel_navigation(self.request.user)
        context["thresholds"] = get_panel_thresholds(self.request.user, client_id=self.client_id)
        return context


class ThresholdCreateView(PanelCreateView):
    model = DeviceThreshold
    form_class = DeviceThresholdPanelForm
    page_title = "Create Threshold"
    active_nav_key = "thresholds"
    success_url_name = "panel:thresholds"
    success_message = "Threshold created successfully."
    audit_action_create = AuditAction.THRESHOLD_UPDATE

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def get_audit_description(self, action, instance):
        return f"Updated threshold {instance.key} for {instance.device.serial_number}"


class ThresholdUpdateView(PanelUpdateView):
    model = DeviceThreshold
    form_class = DeviceThresholdPanelForm
    page_title = "Edit Threshold"
    active_nav_key = "thresholds"
    success_url_name = "panel:thresholds"
    success_message = "Threshold updated successfully."
    audit_action_update = AuditAction.THRESHOLD_UPDATE

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def get_audit_description(self, action, instance):
        return f"Updated threshold {instance.key} for {instance.device.serial_number}"


class ThresholdDeleteView(PanelDeleteView):
    model = DeviceThreshold
    page_title = "Delete Threshold"
    active_nav_key = "thresholds"
    success_url_name = "panel:thresholds"
    success_message = "Threshold deleted successfully."
