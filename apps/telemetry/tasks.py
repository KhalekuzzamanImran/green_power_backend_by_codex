from __future__ import annotations

from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from common.mongo import get_mongo_database


def _coerce_number(value):
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _aggregate_window(
    db,
    *,
    source_collection: str,
    target_collection: str,
    window_start,
    window_end,
    default_topic: str,
):
    cursor = db[source_collection].find(
        {"timestamp": {"$gte": window_start, "$lt": window_end}},
        projection={"payload": 1, "topic": 1, "device_id": 1},
    )

    groups = {}
    for doc in cursor:
        device_id = doc.get("device_id")
        topic = doc.get("topic", default_topic)
        payload = doc.get("payload") or {}
        key = (device_id, topic)
        if key not in groups:
            groups[key] = {"sums": {}, "counts": {}}
        sums = groups[key]["sums"]
        counts = groups[key]["counts"]
        for field, value in payload.items():
            numeric_value = _coerce_number(value)
            if numeric_value is None:
                continue
            sums[field] = sums.get(field, 0.0) + numeric_value
            counts[field] = counts.get(field, 0) + 1

    if not groups:
        return

    for (device_id, topic), agg in groups.items():
        if db[target_collection].find_one(
            {"timestamp": window_end, "device_id": device_id, "topic": topic},
            projection={"_id": 1},
        ):
            continue

        averaged_payload = {}
        for field, total in agg["sums"].items():
            count = agg["counts"].get(field)
            if not count:
                continue
            averaged_payload[field] = round(total / count, 3)

        db[target_collection].insert_one(
            {
                "topic": topic,
                "device_id": device_id,
                "timestamp": window_end,
                "payload": averaged_payload,
            }
        )




@shared_task
def aggregate_rt_data_minutely() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return

    now = timezone.now()
    window_end = now.replace(second=0, microsecond=0)
    window_start = window_end - timedelta(minutes=1)

    db = get_mongo_database()
    _aggregate_window(
        db,
        source_collection="grid_rt_data",
        target_collection="today_grid_rt_data",
        window_start=window_start,
        window_end=window_end,
        default_topic="MQTT_RT_DATA",
    )


@shared_task
def aggregate_rt_data_ten_minutes() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return

    now = timezone.now()
    window_end = now.replace(second=0, microsecond=0)
    window_start = window_end - timedelta(minutes=10)
    db = get_mongo_database()
    _aggregate_window(
        db,
        source_collection="today_grid_rt_data",
        target_collection="last_7_days_grid_rt_data",
        window_start=window_start,
        window_end=window_end,
        default_topic="MQTT_RT_DATA",
    )


@shared_task
def aggregate_rt_data_thirty_minutes() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return

    now = timezone.now()
    window_end = now.replace(second=0, microsecond=0)
    window_start = window_end - timedelta(minutes=30)

    db = get_mongo_database()
    _aggregate_window(
        db,
        source_collection="last_7_days_grid_rt_data",
        target_collection="last_30_days_grid_rt_data",
        window_start=window_start,
        window_end=window_end,
        default_topic="MQTT_RT_DATA",
    )


@shared_task
def aggregate_rt_data_three_hours() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return

    now = timezone.now()
    window_end = now.replace(minute=0, second=0, microsecond=0)
    window_start = window_end - timedelta(hours=3)

    db = get_mongo_database()
    _aggregate_window(
        db,
        source_collection="last_30_days_grid_rt_data",
        target_collection="last_6_months_grid_rt_data",
        window_start=window_start,
        window_end=window_end,
        default_topic="MQTT_RT_DATA",
    )


@shared_task
def aggregate_rt_data_six_hours() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return

    now = timezone.now()
    window_end = now.replace(minute=0, second=0, microsecond=0)
    window_start = window_end - timedelta(hours=6)

    db = get_mongo_database()
    _aggregate_window(
        db,
        source_collection="last_6_months_grid_rt_data",
        target_collection="this_year_grid_rt_data",
        window_start=window_start,
        window_end=window_end,
        default_topic="MQTT_RT_DATA",
    )


@shared_task
def aggregate_env_data_minutely() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return

    now = timezone.now()
    window_end = now.replace(second=0, microsecond=0)
    window_start = window_end - timedelta(minutes=1)

    db = get_mongo_database()
    _aggregate_window(
        db,
        source_collection="environment_data",
        target_collection="today_environment_data",
        window_start=window_start,
        window_end=window_end,
        default_topic="CCCL/PURBACHAL/ENV_01",
    )


@shared_task
def aggregate_env_data_ten_minutes() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return

    now = timezone.now()
    window_end = now.replace(second=0, microsecond=0)
    window_start = window_end - timedelta(minutes=10)

    db = get_mongo_database()
    _aggregate_window(
        db,
        source_collection="today_environment_data",
        target_collection="last_7_days_environment_data",
        window_start=window_start,
        window_end=window_end,
        default_topic="CCCL/PURBACHAL/ENV_01",
    )


@shared_task
def aggregate_env_data_thirty_minutes() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return

    now = timezone.now()
    window_end = now.replace(second=0, microsecond=0)
    window_start = window_end - timedelta(minutes=30)

    db = get_mongo_database()
    _aggregate_window(
        db,
        source_collection="last_7_days_environment_data",
        target_collection="last_30_days_environment_data",
        window_start=window_start,
        window_end=window_end,
        default_topic="CCCL/PURBACHAL/ENV_01",
    )


@shared_task
def aggregate_env_data_three_hours() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return

    now = timezone.now()
    window_end = now.replace(minute=0, second=0, microsecond=0)
    window_start = window_end - timedelta(hours=3)

    db = get_mongo_database()
    _aggregate_window(
        db,
        source_collection="last_30_days_environment_data",
        target_collection="last_6_months_environment_data",
        window_start=window_start,
        window_end=window_end,
        default_topic="CCCL/PURBACHAL/ENV_01",
    )


@shared_task
def aggregate_env_data_six_hours() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return

    now = timezone.now()
    window_end = now.replace(minute=0, second=0, microsecond=0)
    window_start = window_end - timedelta(hours=6)

    db = get_mongo_database()
    _aggregate_window(
        db,
        source_collection="last_6_months_environment_data",
        target_collection="this_year_environment_data",
        window_start=window_start,
        window_end=window_end,
        default_topic="CCCL/PURBACHAL/ENV_01",
    )


@shared_task
def aggregate_eny_now_data_thirty_minutes() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return

    now = timezone.now()
    window_end = now.replace(second=0, microsecond=0)
    window_start = window_end - timedelta(minutes=30)

    db = get_mongo_database()
    _aggregate_window(
        db,
        source_collection="today_grid_eny_now_data",
        target_collection="last_30_days_grid_eny_now_data",
        window_start=window_start,
        window_end=window_end,
        default_topic="MQTT_ENY_NOW",
    )


@shared_task
def aggregate_eny_now_data_three_hours() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return

    now = timezone.now()
    window_end = now.replace(minute=0, second=0, microsecond=0)
    window_start = window_end - timedelta(hours=3)

    db = get_mongo_database()
    _aggregate_window(
        db,
        source_collection="last_30_days_grid_eny_now_data",
        target_collection="last_6_months_grid_eny_now_data",
        window_start=window_start,
        window_end=window_end,
        default_topic="MQTT_ENY_NOW",
    )


@shared_task
def aggregate_eny_now_data_six_hours() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return

    now = timezone.now()
    window_end = now.replace(minute=0, second=0, microsecond=0)
    window_start = window_end - timedelta(hours=6)

    db = get_mongo_database()
    _aggregate_window(
        db,
        source_collection="last_6_months_grid_eny_now_data",
        target_collection="this_year_grid_eny_now_data",
        window_start=window_start,
        window_end=window_end,
        default_topic="MQTT_ENY_NOW",
    )
