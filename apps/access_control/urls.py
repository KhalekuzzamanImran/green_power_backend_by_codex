from rest_framework.routers import DefaultRouter

from apps.access_control.views import (
    OMClientAccessViewSet,
    UserClientAccessViewSet,
    UserPermissionOverrideViewSet,
)

router = DefaultRouter()
router.register("user-client-accesses", UserClientAccessViewSet, basename="user-client-access")
router.register("assignments/om-client", OMClientAccessViewSet, basename="om-client-access")
router.register("permission-overrides", UserPermissionOverrideViewSet, basename="permission-override")

urlpatterns = router.urls
