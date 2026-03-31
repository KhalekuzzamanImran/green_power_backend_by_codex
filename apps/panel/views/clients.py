from django.db.models import Q
from django.http import Http404, JsonResponse
from django.views.generic import TemplateView

from apps.clients.forms import get_dashboard_scope_queryset
from apps.clients.models import Client, ClientType
from apps.clients.utils import generate_unique_client_code, normalize_client_code
from apps.dashboards.models import DashboardScope
from apps.panel.forms import ClientPanelForm, ClientTypePanelForm
from apps.panel.navigation import build_panel_navigation
from apps.panel.permissions import AdminOnlyMixin, PanelAccessMixin, get_accessible_clients_for_panel
from apps.panel.services.device_service import get_panel_devices
from apps.panel.views.common import PanelCreateView, PanelDeleteView, PanelUpdateView


class ClientTypeListView(PanelAccessMixin, TemplateView):
    template_name = "panel/clients/client_types_list.html"
    page_title = "Client Types"
    active_nav_key = "client_types"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav_items"] = build_panel_navigation(self.request.user)
        context["client_types"] = ClientType.objects.order_by("name")
        return context


class ClientListView(PanelAccessMixin, TemplateView):
    template_name = "panel/clients/list.html"
    page_title = "Clients"
    active_nav_key = "clients"

    def get_template_names(self):
        if self.request.headers.get("X-Panel-Partial") == "clients-results":
            return ["panel/clients/partials/results.html"]
        return [self.template_name]

    def get_filtered_clients(self):
        client_type_id = self.request.GET.get("client_type")
        scope_id = self.request.GET.get("scope")
        search_query = self.request.GET.get("q", "").strip()
        legacy_code = self.request.GET.get("code", "").strip()
        legacy_site_name = self.request.GET.get("site_name", "").strip()

        clients = get_accessible_clients_for_panel(self.request.user).select_related(
            "client_type",
            "dashboard_scope",
        )
        if client_type_id:
            clients = clients.filter(client_type_id=client_type_id)
        if scope_id:
            clients = clients.filter(dashboard_scope_id=scope_id)

        search_terms = [term for term in search_query.split() if term][:3]
        if search_terms:
            for term in search_terms:
                clients = clients.filter(Q(site_name__icontains=term) | Q(code__icontains=term))
        else:
            if legacy_code:
                clients = clients.filter(code__icontains=legacy_code)
            if legacy_site_name:
                clients = clients.filter(site_name__icontains=legacy_site_name)

        return clients, client_type_id or "", scope_id or "", search_query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clients, selected_client_type, selected_scope, search_query = self.get_filtered_clients()
        context["nav_items"] = build_panel_navigation(self.request.user)
        context["clients"] = clients
        context["client_types"] = ClientType.objects.filter(is_active=True).order_by("name")
        context["dashboard_scopes"] = DashboardScope.objects.filter(is_active=True).order_by("name")
        context["selected_client_type"] = selected_client_type
        context["selected_scope"] = selected_scope
        context["search_query"] = search_query
        return context


class ClientDetailView(PanelAccessMixin, TemplateView):
    template_name = "panel/clients/detail.html"
    page_title = "Client Detail"
    active_nav_key = "clients"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav_items"] = build_panel_navigation(self.request.user)
        client = get_accessible_clients_for_panel(self.request.user).filter(pk=self.kwargs["client_id"]).first()
        if not client:
            raise Http404("Client not found.")
        context["client"] = client
        context["devices"] = get_panel_devices(self.request.user, client_id=str(client.id))
        return context


class ClientCreateView(PanelCreateView):
    model = Client
    form_class = ClientPanelForm
    page_title = "Create Client"
    active_nav_key = "clients"
    success_url_name = "panel:clients"
    success_message = "Client created successfully."


class ClientUpdateView(PanelUpdateView):
    model = Client
    form_class = ClientPanelForm
    page_title = "Edit Client"
    active_nav_key = "clients"
    success_url_name = "panel:clients"
    success_message = "Client updated successfully."


class ClientDeleteView(PanelDeleteView):
    model = Client
    page_title = "Delete Client"
    active_nav_key = "clients"
    success_url_name = "panel:clients"
    success_message = "Client deleted successfully."


class ClientTypeCreateView(PanelCreateView):
    model = ClientType
    form_class = ClientTypePanelForm
    page_title = "Create Client Type"
    active_nav_key = "client_types"
    success_url_name = "panel:client-types"
    success_message = "Client type created successfully."


class ClientTypeUpdateView(PanelUpdateView):
    model = ClientType
    form_class = ClientTypePanelForm
    page_title = "Edit Client Type"
    active_nav_key = "client_types"
    success_url_name = "panel:client-types"
    success_message = "Client type updated successfully."


class ClientTypeDeleteView(PanelDeleteView):
    model = ClientType
    page_title = "Delete Client Type"
    active_nav_key = "client_types"
    success_url_name = "panel:client-types"
    success_message = "Client type deleted successfully."


class ClientScopeOptionsView(AdminOnlyMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        results = [
            {"id": str(scope.id), "name": scope.name}
            for scope in get_dashboard_scope_queryset(request.GET.get("client_type_id"))
        ]
        return JsonResponse({"results": results})


class ClientCodeSuggestionView(AdminOnlyMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        code = generate_unique_client_code(
            request.GET.get("site_name", ""),
            model=Client,
            exclude_client_id=request.GET.get("client_id"),
        )
        return JsonResponse({"code": code})


class ClientCodeValidationView(AdminOnlyMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        normalized_code = normalize_client_code(request.GET.get("code", ""))
        is_available = True
        message = ""
        if normalized_code:
            qs = Client.objects.filter(code=normalized_code)
            client_id = request.GET.get("client_id")
            if client_id:
                qs = qs.exclude(pk=client_id)
            if qs.exists():
                is_available = False
                message = "This code is already in use."
        return JsonResponse(
            {
                "normalized_code": normalized_code,
                "is_available": is_available,
                "message": message,
            }
        )
