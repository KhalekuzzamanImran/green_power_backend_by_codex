from django.urls import path

from .api.views import TelemetryEventListView

urlpatterns = [
    path("events/", TelemetryEventListView.as_view(), name="telemetry-events"),
]
