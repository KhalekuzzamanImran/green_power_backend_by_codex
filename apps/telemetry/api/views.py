from datetime import timedelta

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.utils.urls import replace_query_param

from apps.telemetry.models import TelemetryEvent
from common.api.time_range import TIME_RANGE_PARAMETERS, TimeRangeFilterMixin, get_time_range
from common.mongo import get_mongo_database

from .serializers import (
    EnyNowDataSerializer,
    RTDataSerializer,
    TelemetryEventMongoSerializer,
    TelemetryEventSerializer,
)


@extend_schema(
    parameters=[
        *TIME_RANGE_PARAMETERS,
        OpenApiParameter(
            name="topic",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Filter by topic",
        ),
    ],
    responses={200: TelemetryEventMongoSerializer},
)
class TelemetryEventListView(APIView):
    pagination_class = MongoPageNumberPagination

    def get(self, request, *args, **kwargs):
        start_time, end_time = get_time_range(request)
        if (start_time is None) != (end_time is None):
            raise ValidationError({"detail": "start_time and end_time must be provided together"})

        query = {}
        topic = request.query_params.get("topic")
        if topic:
            query["topic"] = topic
        if start_time and end_time:
            query["timestamp"] = {"$gte": start_time, "$lte": end_time}

        db = get_mongo_database()
        paginator = self.pagination_class()
        page_size = paginator.get_page_size(request)
        page_number = paginator.get_page_number(request, None)
        offset = (page_number - 1) * page_size

        cursor = (
            db["telemetry_events"]
            .find(query)
            .sort("timestamp", 1)
            .skip(offset)
            .limit(page_size)
        )
        items = [self._serialize_doc(doc) for doc in cursor]
        total_count = db["telemetry_events"].count_documents(query)
        paginator.paginate_mongo(request, total_count=total_count, items=items)
        return paginator.get_paginated_response(items)

    def _serialize_doc(self, doc):
        return {
            "id": str(doc.get("_id")),
            "topic": doc.get("topic"),
            "device_id": doc.get("device_id"),
            "timestamp": doc.get("timestamp"),
            "payload": doc.get("payload"),
        }


class MongoPageNumberPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 1000

    def paginate_mongo(self, request, *, total_count, items):
        self.request = request
        self.count = total_count
        self.page_size = self.get_page_size(request)
        self.page_number = self.get_page_number(request, None)
        return items

    def get_next_link(self):
        if self.page_size is None:
            return None
        if self.page_number * self.page_size >= self.count:
            return None
        url = self.request.build_absolute_uri()
        return replace_query_param(url, self.page_query_param, self.page_number + 1)

    def get_previous_link(self):
        if self.page_number <= 1:
            return None
        url = self.request.build_absolute_uri()
        return replace_query_param(url, self.page_query_param, self.page_number - 1)

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )


@extend_schema(parameters=TIME_RANGE_PARAMETERS, responses={200: RTDataSerializer})
class RTDataListView(APIView):
    pagination_class = MongoPageNumberPagination

    def get(self, request, *args, **kwargs):
        start_time, end_time = get_time_range(request)
        if (start_time is None) != (end_time is None):
            raise ValidationError({"detail": "start_time and end_time must be provided together"})

        collection = self._select_collection(start_time, end_time)
        query = {}
        if start_time and end_time:
            query["timestamp"] = {"$gte": start_time, "$lte": end_time}

        db = get_mongo_database()
        paginator = self.pagination_class()
        page_size = paginator.get_page_size(request)
        page_number = paginator.get_page_number(request, None)
        offset = (page_number - 1) * page_size

        cursor = (
            db[collection]
            .find(query)
            .sort("timestamp", 1)
            .skip(offset)
            .limit(page_size)
        )
        items = [self._serialize_doc(doc) for doc in cursor]
        total_count = db[collection].count_documents(query)
        paginator.paginate_mongo(request, total_count=total_count, items=items)
        return paginator.get_paginated_response(items)

    def _select_collection(self, start_time, end_time):
        if start_time is None or end_time is None:
            return "grid_rt_data"

        delta = end_time - start_time
        if delta <= timedelta(hours=24):
            return "today_grid_rt_data"
        if delta <= timedelta(days=7):
            return "last_7_days_grid_rt_data"
        if delta <= timedelta(days=30):
            return "last_30_days_grid_rt_data"
        if delta <= timedelta(days=180):
            return "last_6_months_grid_rt_data"
        return "this_year_grid_rt_data"

    def _serialize_doc(self, doc):
        return {
            "id": str(doc.get("_id")),
            "topic": doc.get("topic"),
            "device_id": doc.get("device_id"),
            "timestamp": doc.get("timestamp"),
            "payload": doc.get("payload"),
        }


@extend_schema(parameters=TIME_RANGE_PARAMETERS, responses={200: EnyNowDataSerializer})
class EnyNowDataListView(APIView):
    pagination_class = MongoPageNumberPagination

    def get(self, request, *args, **kwargs):
        start_time, end_time = get_time_range(request)
        if (start_time is None) != (end_time is None):
            raise ValidationError({"detail": "start_time and end_time must be provided together"})

        collection = self._select_collection(start_time, end_time)
        query = {}
        if start_time and end_time:
            query["timestamp"] = {"$gte": start_time, "$lte": end_time}

        db = get_mongo_database()
        paginator = self.pagination_class()
        page_size = paginator.get_page_size(request)
        page_number = paginator.get_page_number(request, None)
        offset = (page_number - 1) * page_size

        cursor = (
            db[collection]
            .find(query)
            .sort("timestamp", 1)
            .skip(offset)
            .limit(page_size)
        )
        items = [self._serialize_doc(doc) for doc in cursor]
        total_count = db[collection].count_documents(query)
        paginator.paginate_mongo(request, total_count=total_count, items=items)
        return paginator.get_paginated_response(items)

    def _select_collection(self, start_time, end_time):
        if start_time is None or end_time is None:
            return "grid_eny_now_data"

        delta = end_time - start_time
        if delta <= timedelta(hours=24):
            return "today_grid_eny_now_data"
        if delta <= timedelta(days=7):
            return "last_7_days_grid_eny_now_data"
        if delta <= timedelta(days=30):
            return "last_30_days_grid_eny_now_data"
        if delta <= timedelta(days=180):
            return "last_6_months_grid_eny_now_data"
        return "this_year_grid_eny_now_data"

    def _serialize_doc(self, doc):
        return {
            "id": str(doc.get("_id")),
            "topic": doc.get("topic"),
            "device_id": doc.get("device_id"),
            "timestamp": doc.get("timestamp"),
            "payload": doc.get("payload"),
        }
