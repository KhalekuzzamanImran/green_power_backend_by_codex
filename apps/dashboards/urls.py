from rest_framework.routers import DefaultRouter

from apps.dashboards.views import DashboardScopeViewSet, DashboardViewSet

router = DefaultRouter()
router.register("dashboard-scopes", DashboardScopeViewSet, basename="dashboard-scope")
router.register("dashboards", DashboardViewSet, basename="dashboard")

urlpatterns = router.urls
