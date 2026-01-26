from __future__ import annotations

import os
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from common.mongo import get_mongo_database


def _normalize_timestamp(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            return timezone.datetime.fromtimestamp(value / 1000, tz=timezone.utc)
        except (OSError, OverflowError, ValueError):
            return None
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.isdigit():
            try:
                return timezone.datetime.fromtimestamp(int(stripped) / 1000, tz=timezone.utc)
            except (OSError, OverflowError, ValueError):
                return None
        parsed = parse_datetime(stripped)
        if parsed is None:
            return None
        if timezone.is_naive(parsed):
            return timezone.make_aware(parsed, timezone.get_current_timezone())
        return parsed
    return None


def store_event_mongo(message: dict) -> None:
    db = get_mongo_database()
    payload = dict(message)
    normalized_timestamp = _normalize_timestamp(payload.get("timestamp"))
    if normalized_timestamp is not None:
        payload["timestamp"] = normalized_timestamp
    collections = _collections_for_topic(payload.get("topic"))
    for collection in collections:
        db[collection].insert_one(payload)
    db["telemetry_events"].insert_one(dict(payload))


def _collections_for_topic(topic: str | None) -> list[str]:
    if topic == "MQTT_RT_DATA":
        return ["grid_rt_data"]
    if topic == "MQTT_ENY_NOW":
        return [
            "grid_eny_now_data",
            "today_grid_eny_now_data",
            "last_7_days_grid_eny_now_data",
        ]
    if topic == "MQTT_DAY_DATA":
        return ["grid_day_data"]
    if topic == "MQTT_ENY_FRZ":
        return ["grid_eny_frz_data"]
    if topic == "CCCL/PURBACHAL/ENV_01":
        return ["environment_data"]
    if topic == "CCCL/PURBACHAL/ENM_01":
        return ["generator_data"]
    return [os.getenv("MONGO_TELEMETRY_COLLECTION", "telemetry_events")]


def _ensure_ttl_index(db, collection: str, *, ttl_seconds: int) -> None:
    if ttl_seconds <= 0:
        return
    existing = db[collection].index_information().get("timestamp_1")
    if existing and existing.get("expireAfterSeconds") != ttl_seconds:
        db[collection].drop_index("timestamp_1")
    db[collection].create_index(
        [("timestamp", 1)],
        name="timestamp_1",
        expireAfterSeconds=ttl_seconds,
    )


def ensure_today_collection_ttl_indexes() -> None:
    if not getattr(settings, "MONGO_DB_URI", None):
        return
    ttl_seconds = getattr(settings, "MONGO_TODAY_TTL_SECONDS", 86400)

    db = get_mongo_database()
    base_collections = [
        "grid_rt_data",
        "grid_eny_now_data",
        "grid_day_data",
        "grid_eny_frz_data",
        "environment_data",
        "generator_data",
    ]
    for collection in base_collections:
        db[collection].create_index("timestamp")
    for collection in ("today_grid_rt_data", "today_grid_eny_now_data", "today_environment"):
        _ensure_ttl_index(db, collection, ttl_seconds=ttl_seconds)

    last_7_days_ttl_seconds = getattr(settings, "MONGO_LAST_7_DAYS_TTL_SECONDS", 604800)
    if last_7_days_ttl_seconds > 0:
        _ensure_ttl_index(db, "last_7_days_grid_rt_data", ttl_seconds=last_7_days_ttl_seconds)
        _ensure_ttl_index(db, "last_7_days_environment", ttl_seconds=last_7_days_ttl_seconds)
        _ensure_ttl_index(
            db,
            "last_7_days_grid_eny_now_data",
            ttl_seconds=last_7_days_ttl_seconds,
        )

    last_30_days_ttl_seconds = getattr(settings, "MONGO_LAST_30_DAYS_TTL_SECONDS", 2592000)
    if last_30_days_ttl_seconds > 0:
        _ensure_ttl_index(db, "last_30_days_grid_rt_data", ttl_seconds=last_30_days_ttl_seconds)
        _ensure_ttl_index(db, "last_30_days_environment", ttl_seconds=last_30_days_ttl_seconds)
        _ensure_ttl_index(
            db,
            "last_30_days_grid_eny_now_data",
            ttl_seconds=last_30_days_ttl_seconds,
        )

    last_6_months_ttl_seconds = getattr(settings, "MONGO_LAST_6_MONTHS_TTL_SECONDS", 15552000)
    if last_6_months_ttl_seconds > 0:
        _ensure_ttl_index(db, "last_6_months_grid_rt_data", ttl_seconds=last_6_months_ttl_seconds)
        _ensure_ttl_index(db, "last_6_months_environment", ttl_seconds=last_6_months_ttl_seconds)
        _ensure_ttl_index(
            db,
            "last_6_months_grid_eny_now_data",
            ttl_seconds=last_6_months_ttl_seconds,
        )

    this_year_ttl_seconds = getattr(settings, "MONGO_THIS_YEAR_TTL_SECONDS", 31536000)
    if this_year_ttl_seconds > 0:
        _ensure_ttl_index(db, "this_year_grid_rt_data", ttl_seconds=this_year_ttl_seconds)
        _ensure_ttl_index(db, "this_year_environment", ttl_seconds=this_year_ttl_seconds)
        _ensure_ttl_index(
            db,
            "this_year_grid_eny_now_data",
            ttl_seconds=this_year_ttl_seconds,
        )
    db["telemetry_events"].create_index("timestamp")
    db["telemetry_events"].create_index([("timestamp", 1), ("topic", 1)])


def broadcast_realtime(
    message: dict,
    *,
    group: str | None = None,
    event: str = "telemetry.message",
) -> None:
    group = group or os.getenv("TELEMETRY_WS_GROUP", "telemetry")
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        group,
        {"type": event, "message": message},
    )
