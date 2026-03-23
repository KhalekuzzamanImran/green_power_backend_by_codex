from rest_framework.routers import DefaultRouter

from apps.devices.views import DeviceViewSet, TopicDataViewSet, TopicViewSet

router = DefaultRouter()
router.register("devices", DeviceViewSet, basename="device")
router.register("topics", TopicViewSet, basename="topic")
router.register("topic-data", TopicDataViewSet, basename="topic-data")

urlpatterns = router.urls
