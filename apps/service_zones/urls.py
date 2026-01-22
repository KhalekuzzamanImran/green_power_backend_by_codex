from django.urls import path

from .api.views import DeviceListView, DeviceStatListView, ServiceZoneListView

urlpatterns = [
    path("service-zones/", ServiceZoneListView.as_view(), name="service-zones"),
    path("devices/", DeviceListView.as_view(), name="devices"),
    path("device-stats/", DeviceStatListView.as_view(), name="device-stats"),
]
