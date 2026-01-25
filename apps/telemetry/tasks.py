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


@shared_task
def aggregate_rt_data_minutely() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return

    now = timezone.now()
    window_end = now.replace(second=0, microsecond=0)
    window_start = window_end - timedelta(minutes=1)

    db = get_mongo_database()
    if db["today_grid_rt_data"].find_one(
        {"timestamp": window_end},
        projection={"_id": 1},
    ):
        return

    cursor = db["grid_rt_data"].find(
        {"timestamp": {"$gte": window_start, "$lt": window_end}},
        projection={"payload": 1, "topic": 1, "device_id": 1},
    )

    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    device_id = None
    topic = "MQTT_RT_DATA"
    seen = 0

    for doc in cursor:
        seen += 1
        if device_id is None:
            device_id = doc.get("device_id")
        topic = doc.get("topic", topic)
        payload = doc.get("payload") or {}
        for key, value in payload.items():
            numeric_value = _coerce_number(value)
            if numeric_value is None:
                continue
            sums[key] = sums.get(key, 0.0) + numeric_value
            counts[key] = counts.get(key, 0) + 1

    if seen == 0:
        return

    averaged_payload = {}
    for key in sums:
        count = counts.get(key)
        if not count:
            continue
        averaged_value = sums[key] / count
        averaged_payload[key] = round(averaged_value, 3)

    aggregated_doc = {
        "topic": topic,
        "device_id": device_id,
        "timestamp": window_end,
        "payload": averaged_payload,
    }

    db["today_grid_rt_data"].insert_one(aggregated_doc)


@shared_task
def aggregate_rt_data_ten_minutes() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return

    now = timezone.now()
    window_end = now.replace(second=0, microsecond=0)
    window_start = window_end - timedelta(minutes=10)
    db = get_mongo_database()
    if db["last_7_days_grid_rt_data"].find_one(
        {"timestamp": window_end},
        projection={"_id": 1},
    ):
        return

    cursor = db["today_grid_rt_data"].find(
        {
            "timestamp": {
                "$gte": window_start,
                "$lt": window_end,
            }
        },
        projection={"payload": 1, "topic": 1, "device_id": 1},
    )

    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    device_id = None
    topic = "MQTT_RT_DATA"
    seen = 0

    for doc in cursor:
        seen += 1
        if device_id is None:
            device_id = doc.get("device_id")
        topic = doc.get("topic", topic)
        payload = doc.get("payload") or {}
        for key, value in payload.items():
            numeric_value = _coerce_number(value)
            if numeric_value is None:
                continue
            sums[key] = sums.get(key, 0.0) + numeric_value
            counts[key] = counts.get(key, 0) + 1

    if seen == 0:
        return

    averaged_payload = {}
    for key in sums:
        count = counts.get(key)
        if not count:
            continue
        averaged_value = sums[key] / count
        averaged_payload[key] = round(averaged_value, 3)

    aggregated_doc = {
        "topic": topic,
        "device_id": device_id,
        "timestamp": window_end,
        "payload": averaged_payload,
    }

    db["last_7_days_grid_rt_data"].insert_one(aggregated_doc)


@shared_task
def aggregate_rt_data_thirty_minutes() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return

    now = timezone.now()
    window_end = now.replace(second=0, microsecond=0)
    window_start = window_end - timedelta(minutes=30)

    db = get_mongo_database()
    if db["last_30_days_grid_rt_data"].find_one(
        {"timestamp": window_end},
        projection={"_id": 1},
    ):
        return

    cursor = db["last_7_days_grid_rt_data"].find(
        {
            "timestamp": {
                "$gte": window_start,
                "$lt": window_end,
            }
        },
        projection={"payload": 1, "topic": 1, "device_id": 1},
    )

    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    device_id = None
    topic = "MQTT_RT_DATA"
    seen = 0

    for doc in cursor:
        seen += 1
        if device_id is None:
            device_id = doc.get("device_id")
        topic = doc.get("topic", topic)
        payload = doc.get("payload") or {}
        for key, value in payload.items():
            numeric_value = _coerce_number(value)
            if numeric_value is None:
                continue
            sums[key] = sums.get(key, 0.0) + numeric_value
            counts[key] = counts.get(key, 0) + 1

    if seen == 0:
        return

    averaged_payload = {}
    for key in sums:
        count = counts.get(key)
        if not count:
            continue
        averaged_value = sums[key] / count
        averaged_payload[key] = round(averaged_value, 3)

    aggregated_doc = {
        "topic": topic,
        "device_id": device_id,
        "timestamp": window_end,
        "payload": averaged_payload,
    }

    db["last_30_days_grid_rt_data"].insert_one(aggregated_doc)


@shared_task
def aggregate_rt_data_three_hours() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return

    now = timezone.now()
    window_end = now.replace(minute=0, second=0, microsecond=0)
    window_start = window_end - timedelta(hours=3)

    db = get_mongo_database()
    if db["last_6_months_grid_rt_data"].find_one(
        {"timestamp": window_end},
        projection={"_id": 1},
    ):
        return

    cursor = db["last_30_days_grid_rt_data"].find(
        {
            "timestamp": {
                "$gte": window_start,
                "$lt": window_end,
            }
        },
        projection={"payload": 1, "topic": 1, "device_id": 1},
    )

    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    device_id = None
    topic = "MQTT_RT_DATA"
    seen = 0

    for doc in cursor:
        seen += 1
        if device_id is None:
            device_id = doc.get("device_id")
        topic = doc.get("topic", topic)
        payload = doc.get("payload") or {}
        for key, value in payload.items():
            numeric_value = _coerce_number(value)
            if numeric_value is None:
                continue
            sums[key] = sums.get(key, 0.0) + numeric_value
            counts[key] = counts.get(key, 0) + 1

    if seen == 0:
        return

    averaged_payload = {}
    for key in sums:
        count = counts.get(key)
        if not count:
            continue
        averaged_value = sums[key] / count
        averaged_payload[key] = round(averaged_value, 3)

    aggregated_doc = {
        "topic": topic,
        "device_id": device_id,
        "timestamp": window_end,
        "payload": averaged_payload,
    }

    db["last_6_months_grid_rt_data"].insert_one(aggregated_doc)


@shared_task
def aggregate_rt_data_six_hours() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return

    now = timezone.now()
    window_end = now.replace(minute=0, second=0, microsecond=0)
    window_start = window_end - timedelta(hours=6)

    db = get_mongo_database()
    if db["this_year_grid_rt_data"].find_one(
        {"timestamp": window_end},
        projection={"_id": 1},
    ):
        return

    cursor = db["last_6_months_grid_rt_data"].find(
        {
            "timestamp": {
                "$gte": window_start,
                "$lt": window_end,
            }
        },
        projection={"payload": 1, "topic": 1, "device_id": 1},
    )

    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    device_id = None
    topic = "MQTT_RT_DATA"
    seen = 0

    for doc in cursor:
        seen += 1
        if device_id is None:
            device_id = doc.get("device_id")
        topic = doc.get("topic", topic)
        payload = doc.get("payload") or {}
        for key, value in payload.items():
            numeric_value = _coerce_number(value)
            if numeric_value is None:
                continue
            sums[key] = sums.get(key, 0.0) + numeric_value
            counts[key] = counts.get(key, 0) + 1

    if seen == 0:
        return

    averaged_payload = {}
    for key in sums:
        count = counts.get(key)
        if not count:
            continue
        averaged_value = sums[key] / count
        averaged_payload[key] = round(averaged_value, 3)

    expires_at = window_end.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    expires_at = expires_at.replace(year=expires_at.year + 1)

    aggregated_doc = {
        "topic": topic,
        "device_id": device_id,
        "timestamp": window_end,
        "payload": averaged_payload,
        "expires_at": expires_at,
    }

    db["this_year_grid_rt_data"].insert_one(aggregated_doc)


@shared_task
def aggregate_env_data_minutely() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return

    now = timezone.now()
    window_end = now.replace(second=0, microsecond=0)
    window_start = window_end - timedelta(minutes=1)

    db = get_mongo_database()
    if db["today_environment"].find_one(
        {"timestamp": window_end},
        projection={"_id": 1},
    ):
        return

    cursor = db["environment"].find(
        {"timestamp": {"$gte": window_start, "$lt": window_end}},
        projection={"payload": 1, "topic": 1, "device_id": 1},
    )

    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    device_id = None
    topic = "CCCL/PURBACHAL/ENV_01"
    seen = 0

    for doc in cursor:
        seen += 1
        if device_id is None:
            device_id = doc.get("device_id")
        topic = doc.get("topic", topic)
        payload = doc.get("payload") or {}
        for key, value in payload.items():
            numeric_value = _coerce_number(value)
            if numeric_value is None:
                continue
            sums[key] = sums.get(key, 0.0) + numeric_value
            counts[key] = counts.get(key, 0) + 1

    if seen == 0:
        return

    averaged_payload = {}
    for key in sums:
        count = counts.get(key)
        if not count:
            continue
        averaged_value = sums[key] / count
        averaged_payload[key] = round(averaged_value, 3)

    aggregated_doc = {
        "topic": topic,
        "device_id": device_id,
        "timestamp": window_end,
        "payload": averaged_payload,
    }

    db["today_environment"].insert_one(aggregated_doc)


@shared_task
def aggregate_env_data_ten_minutes() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return

    now = timezone.now()
    window_end = now.replace(second=0, microsecond=0)
    window_start = window_end - timedelta(minutes=10)

    db = get_mongo_database()
    if db["last_7_days_environment"].find_one(
        {"timestamp": window_end},
        projection={"_id": 1},
    ):
        return

    cursor = db["today_environment"].find(
        {"timestamp": {"$gte": window_start, "$lt": window_end}},
        projection={"payload": 1, "topic": 1, "device_id": 1},
    )

    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    device_id = None
    topic = "CCCL/PURBACHAL/ENV_01"
    seen = 0

    for doc in cursor:
        seen += 1
        if device_id is None:
            device_id = doc.get("device_id")
        topic = doc.get("topic", topic)
        payload = doc.get("payload") or {}
        for key, value in payload.items():
            numeric_value = _coerce_number(value)
            if numeric_value is None:
                continue
            sums[key] = sums.get(key, 0.0) + numeric_value
            counts[key] = counts.get(key, 0) + 1

    if seen == 0:
        return

    averaged_payload = {}
    for key in sums:
        count = counts.get(key)
        if not count:
            continue
        averaged_value = sums[key] / count
        averaged_payload[key] = round(averaged_value, 3)

    aggregated_doc = {
        "topic": topic,
        "device_id": device_id,
        "timestamp": window_end,
        "payload": averaged_payload,
    }

    db["last_7_days_environment"].insert_one(aggregated_doc)


@shared_task
def aggregate_env_data_thirty_minutes() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return

    now = timezone.now()
    window_end = now.replace(second=0, microsecond=0)
    window_start = window_end - timedelta(minutes=30)

    db = get_mongo_database()
    if db["last_30_days_environment"].find_one(
        {"timestamp": window_end},
        projection={"_id": 1},
    ):
        return

    cursor = db["last_7_days_environment"].find(
        {"timestamp": {"$gte": window_start, "$lt": window_end}},
        projection={"payload": 1, "topic": 1, "device_id": 1},
    )

    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    device_id = None
    topic = "CCCL/PURBACHAL/ENV_01"
    seen = 0

    for doc in cursor:
        seen += 1
        if device_id is None:
            device_id = doc.get("device_id")
        topic = doc.get("topic", topic)
        payload = doc.get("payload") or {}
        for key, value in payload.items():
            numeric_value = _coerce_number(value)
            if numeric_value is None:
                continue
            sums[key] = sums.get(key, 0.0) + numeric_value
            counts[key] = counts.get(key, 0) + 1

    if seen == 0:
        return

    averaged_payload = {}
    for key in sums:
        count = counts.get(key)
        if not count:
            continue
        averaged_value = sums[key] / count
        averaged_payload[key] = round(averaged_value, 3)

    aggregated_doc = {
        "topic": topic,
        "device_id": device_id,
        "timestamp": window_end,
        "payload": averaged_payload,
    }

    db["last_30_days_environment"].insert_one(aggregated_doc)


@shared_task
def aggregate_env_data_three_hours() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return

    now = timezone.now()
    window_end = now.replace(minute=0, second=0, microsecond=0)
    window_start = window_end - timedelta(hours=3)

    db = get_mongo_database()
    if db["last_6_months_environment"].find_one(
        {"timestamp": window_end},
        projection={"_id": 1},
    ):
        return

    cursor = db["last_30_days_environment"].find(
        {"timestamp": {"$gte": window_start, "$lt": window_end}},
        projection={"payload": 1, "topic": 1, "device_id": 1},
    )

    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    device_id = None
    topic = "CCCL/PURBACHAL/ENV_01"
    seen = 0

    for doc in cursor:
        seen += 1
        if device_id is None:
            device_id = doc.get("device_id")
        topic = doc.get("topic", topic)
        payload = doc.get("payload") or {}
        for key, value in payload.items():
            numeric_value = _coerce_number(value)
            if numeric_value is None:
                continue
            sums[key] = sums.get(key, 0.0) + numeric_value
            counts[key] = counts.get(key, 0) + 1

    if seen == 0:
        return

    averaged_payload = {}
    for key in sums:
        count = counts.get(key)
        if not count:
            continue
        averaged_value = sums[key] / count
        averaged_payload[key] = round(averaged_value, 3)

    aggregated_doc = {
        "topic": topic,
        "device_id": device_id,
        "timestamp": window_end,
        "payload": averaged_payload,
    }

    db["last_6_months_environment"].insert_one(aggregated_doc)


@shared_task
def aggregate_env_data_six_hours() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return

    now = timezone.now()
    window_end = now.replace(minute=0, second=0, microsecond=0)
    window_start = window_end - timedelta(hours=6)

    db = get_mongo_database()
    if db["this_year_environment"].find_one(
        {"timestamp": window_end},
        projection={"_id": 1},
    ):
        return

    cursor = db["last_6_months_environment"].find(
        {"timestamp": {"$gte": window_start, "$lt": window_end}},
        projection={"payload": 1, "topic": 1, "device_id": 1},
    )

    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    device_id = None
    topic = "CCCL/PURBACHAL/ENV_01"
    seen = 0

    for doc in cursor:
        seen += 1
        if device_id is None:
            device_id = doc.get("device_id")
        topic = doc.get("topic", topic)
        payload = doc.get("payload") or {}
        for key, value in payload.items():
            numeric_value = _coerce_number(value)
            if numeric_value is None:
                continue
            sums[key] = sums.get(key, 0.0) + numeric_value
            counts[key] = counts.get(key, 0) + 1

    if seen == 0:
        return

    averaged_payload = {}
    for key in sums:
        count = counts.get(key)
        if not count:
            continue
        averaged_value = sums[key] / count
        averaged_payload[key] = round(averaged_value, 3)

    expires_at = window_end.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    expires_at = expires_at.replace(year=expires_at.year + 1)

    aggregated_doc = {
        "topic": topic,
        "device_id": device_id,
        "timestamp": window_end,
        "payload": averaged_payload,
        "expires_at": expires_at,
    }

    db["this_year_environment"].insert_one(aggregated_doc)
