from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy

from apps.access_control.selectors import get_accessible_clients_for_om_user
from apps.accounts.models import RoleChoices
from apps.clients.models import Client


def get_accessible_clients_for_panel(user):
    queryset = Client.objects.select_related("client_type", "dashboard_scope").order_by("site_name")
    if not user.is_authenticated:
        return queryset.none()
    if user.role == RoleChoices.ADMIN:
        return queryset
    if user.role == RoleChoices.OM:
        return get_accessible_clients_for_om_user(user)
    return queryset.none()


def resolve_panel_client(user, client_id=None):
    accessible_clients = get_accessible_clients_for_panel(user)
    if not user.is_authenticated:
        return None
    if client_id:
        selected = accessible_clients.filter(id=client_id).first()
        if not selected:
            raise PermissionDenied("You do not have access to the requested client.")
        return selected
    if user.role == RoleChoices.OM and accessible_clients.count() == 1:
        return accessible_clients.first()
    return None


class PanelAccessMixin(LoginRequiredMixin):
    login_url = reverse_lazy("panel:login")
    allowed_roles = (RoleChoices.ADMIN, RoleChoices.OM)
    page_title = ""
    page_heading = ""
    active_nav_key = "dashboard"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in self.allowed_roles:
            raise PermissionDenied("You do not have access to this panel page.")
        self.client_id = request.GET.get("client_id")
        self.accessible_clients = get_accessible_clients_for_panel(request.user)
        self.selected_client = resolve_panel_client(request.user, self.client_id)
        return super().dispatch(request, *args, **kwargs)

    def get_breadcrumbs(self):
        return [{"label": "Panel", "url": reverse_lazy("panel:home")}, {"label": self.page_heading or self.page_title, "url": ""}]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": self.page_title,
                "page_heading": self.page_heading or self.page_title,
                "active_nav_key": self.active_nav_key,
                "accessible_clients": self.accessible_clients,
                "selected_client": self.selected_client,
                "selected_client_id": str(self.selected_client.id) if self.selected_client else "",
                "requires_client_selection": self.request.user.role == RoleChoices.OM and self.accessible_clients.count() > 1 and not self.selected_client,
                "breadcrumbs": self.get_breadcrumbs(),
            }
        )
        return context


class AdminOnlyMixin(PanelAccessMixin):
    allowed_roles = (RoleChoices.ADMIN,)


class AdminOrOMMixin(PanelAccessMixin):
    allowed_roles = (RoleChoices.ADMIN, RoleChoices.OM)
