from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import RoleChoices
from apps.dashboards.models import Dashboard
from apps.dashboards.serializers import DashboardSerializer


class DashboardViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Dashboard.objects.filter(is_active=True).order_by("name")
        if user.role == RoleChoices.ADMIN:
            return queryset
        if user.role == RoleChoices.OM:
            return queryset
        if user.role == RoleChoices.CLIENT:
            return queryset.filter(allowed_users__client_user=user).distinct()
        return queryset.none()

    @action(detail=False, methods=["get"], url_path="my")
    def my_dashboards(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)
