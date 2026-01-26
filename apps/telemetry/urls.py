from django.urls import path

from .api.views import (
    EnyNowDataListView,
    EnvironmentDataListView,
    GeneratorDataListView,
    RTDataListView,
    SolarDataListView,
    TelemetryEventListView,
)

urlpatterns = [
    path("events/", TelemetryEventListView.as_view(), name="telemetry-events"),
    path("rt-data/", RTDataListView.as_view(), name="rt-data"),
    path("eny-now-data/", EnyNowDataListView.as_view(), name="eny-now-data"),
    path("environment-data/", EnvironmentDataListView.as_view(), name="environment-data"),
    path("solar-data/", SolarDataListView.as_view(), name="solar-data"),
    path("generator-data/", GeneratorDataListView.as_view(), name="generator-data"),
]
