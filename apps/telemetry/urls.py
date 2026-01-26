from django.urls import path

from .api.views import EnyNowDataListView, RTDataListView, TelemetryEventListView

urlpatterns = [
    path("events/", TelemetryEventListView.as_view(), name="telemetry-events"),
    path("rt-data/", RTDataListView.as_view(), name="rt-data"),
    path("eny-now-data/", EnyNowDataListView.as_view(), name="eny-now-data"),
]
