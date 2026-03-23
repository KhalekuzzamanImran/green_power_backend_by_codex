from rest_framework.routers import DefaultRouter

from apps.devices.views import DeviceDataViewSet, DeviceViewSet

router = DefaultRouter()
router.register("devices", DeviceViewSet, basename="device")
router.register("device-data", DeviceDataViewSet, basename="device-data")

urlpatterns = router.urls
