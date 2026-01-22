from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView

from apps.service_zones.models import Device, DeviceStat, ServiceZone
from common.api.time_range import TIME_RANGE_PARAMETERS, TimeRangeFilterMixin

from .serializers import DeviceSerializer, DeviceStatSerializer, ServiceZoneSerializer


@extend_schema(parameters=TIME_RANGE_PARAMETERS, responses={200: ServiceZoneSerializer})
class ServiceZoneListView(TimeRangeFilterMixin, ListAPIView):
    queryset = ServiceZone.objects.all().order_by("-created_at")
    serializer_class = ServiceZoneSerializer


@extend_schema(parameters=TIME_RANGE_PARAMETERS, responses={200: DeviceSerializer})
class DeviceListView(TimeRangeFilterMixin, ListAPIView):
    queryset = Device.objects.all().order_by("-created_at")
    serializer_class = DeviceSerializer


@extend_schema(parameters=TIME_RANGE_PARAMETERS, responses={200: DeviceStatSerializer})
class DeviceStatListView(TimeRangeFilterMixin, ListAPIView):
    queryset = DeviceStat.objects.all().order_by("-created_at")
    serializer_class = DeviceStatSerializer
