from __future__ import annotations

from datetime import datetime, time

from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from drf_spectacular.utils import OpenApiParameter
from rest_framework.exceptions import ValidationError

TIME_RANGE_PARAMETERS = [
    OpenApiParameter(
        name="start_time",
        type=str,
        location=OpenApiParameter.QUERY,
        description="ISO 8601 datetime or date (inclusive).",
    ),
    OpenApiParameter(
        name="end_time",
        type=str,
        location=OpenApiParameter.QUERY,
        description="ISO 8601 datetime or date (inclusive).",
    ),
]


def _parse_datetime_param(value: str | None, param_name: str, *, bound: str) -> datetime | None:
    if not value:
        return None

    parsed = parse_datetime(value)
    if parsed is None:
        parsed_date = parse_date(value)
        if parsed_date is None:
            raise ValidationError({param_name: "Invalid datetime. Use ISO 8601."})
        parsed = datetime.combine(parsed_date, time.max if bound == "end" else time.min)

    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def get_time_range(request) -> tuple[datetime | None, datetime | None]:
    start_time = _parse_datetime_param(request.query_params.get("start_time"), "start_time", bound="start")
    end_time = _parse_datetime_param(request.query_params.get("end_time"), "end_time", bound="end")

    if start_time and end_time and start_time > end_time:
        raise ValidationError({"detail": "start_time must be before end_time"})

    return start_time, end_time


class TimeRangeFilterMixin:
    time_field = "created_at"

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        start_time, end_time = get_time_range(self.request)
        if start_time:
            queryset = queryset.filter(**{f"{self.time_field}__gte": start_time})
        if end_time:
            queryset = queryset.filter(**{f"{self.time_field}__lte": end_time})
        return queryset
