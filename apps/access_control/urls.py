from rest_framework.routers import DefaultRouter

from apps.access_control.views import (
    ClientDashboardAccessViewSet,
    ClientProfileViewSet,
    OMClientAccessViewSet,
    UserPermissionOverrideViewSet,
)

router = DefaultRouter()
router.register("client-profiles", ClientProfileViewSet, basename="client-profile")
router.register("assignments/om-client", OMClientAccessViewSet, basename="om-client-access")
router.register("assignments/client-dashboard", ClientDashboardAccessViewSet, basename="client-dashboard-access")
router.register("permission-overrides", UserPermissionOverrideViewSet, basename="permission-override")

urlpatterns = router.urls
