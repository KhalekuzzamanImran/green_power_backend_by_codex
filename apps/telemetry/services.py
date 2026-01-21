from __future__ import annotations

import os
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from common.mongo import get_mongo_database


def store_event_mongo(message: dict) -> None:
    collection = _collection_for_topic(message.get("topic"))
    db = get_mongo_database()
    db[collection].insert_one(dict(message))


def _collection_for_topic(topic: str | None) -> str:
    if topic == "MQTT_RT_DATA":
        return "grid_rt_data"
    if topic == "MQTT_ENY_NOW":
        return "grid_eny_now_data"
    if topic == "MQTT_DAY_DATA":
        return "grid_day_data"
    if topic == "MQTT_ENY_FRZ":
        return "grid_eny_frz_data"
    if topic == "CCCL/PURBACHAL/ENV_01":
        return "environment"
    if topic == "CCCL/PURBACHAL/ENM_01":
        return "generator"
    return os.getenv("MONGO_TELEMETRY_COLLECTION", "telemetry_events")


def broadcast_realtime(message: dict) -> None:
    group = os.getenv("TELEMETRY_WS_GROUP", "telemetry")
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        group,
        {"type": "telemetry.message", "message": message},
    )
