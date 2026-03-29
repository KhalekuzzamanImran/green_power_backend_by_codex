from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import RoleChoices
from apps.access_control.selectors import get_selected_client
from apps.dashboards.models import Dashboard, DashboardScope
from apps.dashboards.serializers import DashboardScopeSerializer, DashboardSerializer


class DashboardScopeViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = DashboardScope.objects.filter(is_active=True).order_by("name")
    serializer_class = DashboardScopeSerializer


class DashboardViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Dashboard.objects.filter(is_active=True).order_by("name")
        if user.role == RoleChoices.ADMIN:
            return self.apply_filters(queryset)
        if user.role == RoleChoices.OM:
            return self.apply_filters(queryset)
        if user.role == RoleChoices.CLIENT:
            client = get_selected_client(user, self.request.query_params.get("client_id"), require_selection=False)
            if not client:
                return queryset.none()
            queryset = queryset.filter(
                client_type=client.client_type,
                scope=client.dashboard_scope,
            ).distinct()
            return self.apply_filters(queryset)
        return queryset.none()

    def apply_filters(self, queryset):
        client_type_code = self.request.query_params.get("client_type")
        scope_code = self.request.query_params.get("scope")

        if client_type_code:
            queryset = queryset.filter(client_type__code=client_type_code)
        if scope_code:
            queryset = queryset.filter(scope__code=scope_code)
        return queryset

    @action(detail=False, methods=["get"], url_path="my")
    def my_dashboards(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)
