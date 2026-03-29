from rest_framework.routers import DefaultRouter

from apps.clients.views import ClientTypeViewSet, ClientViewSet

router = DefaultRouter()
router.register("client-types", ClientTypeViewSet, basename="client-type")
router.register("clients", ClientViewSet, basename="client")

urlpatterns = router.urls
