from django.views.generic import TemplateView

from apps.access_control.models import OMClientAccess, UserClientAccess
from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import get_action_label
from apps.panel.forms import OMClientAccessPanelForm, UserClientAccessPanelForm
from apps.panel.navigation import build_panel_navigation
from apps.panel.permissions import AdminOnlyMixin
from apps.panel.views.common import PanelCreateView, PanelDeleteView, PanelUpdateView


class UserClientAccessListView(AdminOnlyMixin, TemplateView):
    template_name = "panel/access/user_client_access.html"
    page_title = "Client Access"
    active_nav_key = "user_client_access"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav_items"] = build_panel_navigation(self.request.user)
        context["assignments"] = UserClientAccess.objects.select_related("user", "client").order_by("user__username", "client__site_name")
        return context


class OMClientAccessListView(AdminOnlyMixin, TemplateView):
    template_name = "panel/access/om_client_access.html"
    page_title = "O&M Access"
    active_nav_key = "om_client_access"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav_items"] = build_panel_navigation(self.request.user)
        context["assignments"] = OMClientAccess.objects.select_related("om_user", "client").order_by("om_user__username", "client__site_name")
        return context


class UserClientAccessCreateView(PanelCreateView):
    model = UserClientAccess
    form_class = UserClientAccessPanelForm
    page_title = "Assign Client Access"
    active_nav_key = "user_client_access"
    success_url_name = "panel:user-client-access"
    success_message = "Client access assigned successfully."
    audit_action_create = AuditAction.ASSIGN

    def get_audit_description(self, action, instance):
        return f"{get_action_label(action)} user-client access {instance.user.username} -> {instance.client.site_name}"


class UserClientAccessUpdateView(PanelUpdateView):
    model = UserClientAccess
    form_class = UserClientAccessPanelForm
    page_title = "Edit Client Access"
    active_nav_key = "user_client_access"
    success_url_name = "panel:user-client-access"
    success_message = "Client access updated successfully."

    def get_audit_description(self, action, instance):
        return f"{get_action_label(action)} user-client access {instance.user.username} -> {instance.client.site_name}"


class UserClientAccessDeleteView(PanelDeleteView):
    model = UserClientAccess
    page_title = "Delete Client Access"
    active_nav_key = "user_client_access"
    success_url_name = "panel:user-client-access"
    success_message = "Client access removed successfully."

    def get_audit_description(self, action, instance):
        return f"{get_action_label(action)} user-client access {instance.user.username} -> {instance.client.site_name}"


class OMClientAccessCreateView(PanelCreateView):
    model = OMClientAccess
    form_class = OMClientAccessPanelForm
    page_title = "Assign O&M Access"
    active_nav_key = "om_client_access"
    success_url_name = "panel:om-client-access"
    success_message = "O&M access assigned successfully."
    audit_action_create = AuditAction.ASSIGN

    def get_audit_description(self, action, instance):
        return f"{get_action_label(action)} O&M access {instance.om_user.username} -> {instance.client.site_name}"


class OMClientAccessUpdateView(PanelUpdateView):
    model = OMClientAccess
    form_class = OMClientAccessPanelForm
    page_title = "Edit O&M Access"
    active_nav_key = "om_client_access"
    success_url_name = "panel:om-client-access"
    success_message = "O&M access updated successfully."

    def get_audit_description(self, action, instance):
        return f"{get_action_label(action)} O&M access {instance.om_user.username} -> {instance.client.site_name}"


class OMClientAccessDeleteView(PanelDeleteView):
    model = OMClientAccess
    page_title = "Delete O&M Access"
    active_nav_key = "om_client_access"
    success_url_name = "panel:om-client-access"
    success_message = "O&M access removed successfully."

    def get_audit_description(self, action, instance):
        return f"{get_action_label(action)} O&M access {instance.om_user.username} -> {instance.client.site_name}"
