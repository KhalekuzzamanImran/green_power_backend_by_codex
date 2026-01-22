from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView

from apps.telemetry.models import TelemetryEvent
from common.api.time_range import TIME_RANGE_PARAMETERS, TimeRangeFilterMixin

from .serializers import TelemetryEventSerializer


@extend_schema(parameters=TIME_RANGE_PARAMETERS, responses={200: TelemetryEventSerializer})
class TelemetryEventListView(TimeRangeFilterMixin, ListAPIView):
    queryset = TelemetryEvent.objects.all().order_by("-created_at")
    serializer_class = TelemetryEventSerializer
