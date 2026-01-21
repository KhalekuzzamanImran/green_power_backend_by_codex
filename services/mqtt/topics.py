from __future__ import annotations

import json
import os


def get_topics() -> list[str]:
    raw = os.getenv("MQTT_TOPICS")
    if not raw:
        return ["telemetry/#"]
    try:
        topics = json.loads(raw)
    except json.JSONDecodeError:
        topics = [topic.strip() for topic in raw.split(",") if topic.strip()]
    if isinstance(topics, str):
        topics = [topics]
    return [str(topic) for topic in topics if str(topic)]
