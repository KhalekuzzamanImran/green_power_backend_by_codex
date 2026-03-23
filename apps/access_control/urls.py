from rest_framework.routers import DefaultRouter

from apps.access_control.views import (
    OMClientAccessViewSet,
    UserClientAccessViewSet,
)

router = DefaultRouter()
router.register("user-client-accesses", UserClientAccessViewSet, basename="user-client-access")
router.register("assignments/om-client", OMClientAccessViewSet, basename="om-client-access")

urlpatterns = router.urls
