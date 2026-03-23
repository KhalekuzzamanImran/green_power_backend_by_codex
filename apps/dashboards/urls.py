from rest_framework.routers import DefaultRouter

from apps.dashboards.views import ClientTypeViewSet, DashboardScopeViewSet, DashboardViewSet

router = DefaultRouter()
router.register("client-types", ClientTypeViewSet, basename="client-type")
router.register("dashboard-scopes", DashboardScopeViewSet, basename="dashboard-scope")
router.register("dashboards", DashboardViewSet, basename="dashboard")

urlpatterns = router.urls
