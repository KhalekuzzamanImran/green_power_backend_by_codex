from rest_framework.routers import DefaultRouter

from apps.thresholds.views import DeviceThresholdViewSet

router = DefaultRouter()
router.register("thresholds", DeviceThresholdViewSet, basename="threshold")

urlpatterns = router.urls
