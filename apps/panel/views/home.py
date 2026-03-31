from django.views.generic import TemplateView

from apps.panel.navigation import build_panel_navigation
from apps.panel.permissions import PanelAccessMixin
from apps.panel.services.dashboard_service import build_dashboard_cards, build_dashboard_highlights


class PanelHomeView(PanelAccessMixin, TemplateView):
    template_name = "panel/home/dashboard.html"
    page_title = "Dashboard"
    page_heading = "Control Panel"
    active_nav_key = "dashboard"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav_items"] = build_panel_navigation(self.request.user)
        context["cards"] = build_dashboard_cards(self.request.user, self.selected_client)
        context.update(build_dashboard_highlights(self.request.user, self.selected_client))
        context["show_client_selection_warning"] = False
        return context
