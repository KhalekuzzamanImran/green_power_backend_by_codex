from django.views.generic import TemplateView

from apps.audit_logs.models import AuditLog
from apps.panel.navigation import build_panel_navigation
from apps.panel.permissions import AdminOnlyMixin


class AuditLogListView(AdminOnlyMixin, TemplateView):
    template_name = "panel/audit_logs/list.html"
    page_title = "Audit Logs"
    active_nav_key = "audit_logs"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav_items"] = build_panel_navigation(self.request.user)
        context["audit_logs"] = AuditLog.objects.select_related("actor").all()[:200]
        return context

