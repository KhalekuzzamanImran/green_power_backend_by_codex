from __future__ import annotations

import os
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from common.mongo import get_mongo_database


def store_event_mongo(message: dict) -> None:
    collection = os.getenv("MONGO_TELEMETRY_COLLECTION", "telemetry_events")
    db = get_mongo_database()
    db[collection].insert_one(dict(message))


def broadcast_realtime(message: dict) -> None:
    group = os.getenv("TELEMETRY_WS_GROUP", "telemetry")
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        group,
        {"type": "telemetry.message", "message": message},
    )
