from __future__ import annotations

import json
import logging
import os
import queue
import threading
from dataclasses import dataclass

logger = logging.getLogger("mqtt.processor")


@dataclass(frozen=True)
class MessageEnvelope:
    topic: str
    qos: int
    retained: bool
    payload: bytes
    timestamp: str


class MessageProcessor:
    def __init__(self) -> None:
        self._pretty_json = _parse_bool(os.getenv("MQTT_PRETTY_JSON", "false"))
        maxsize = int(os.getenv("MQTT_MESSAGE_QUEUE", "0"))
        self._queue: queue.Queue[MessageEnvelope] = queue.Queue(maxsize=maxsize)
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, name="mqtt-message-worker", daemon=True)
        self._buffers: dict[tuple[str, str], dict[str, object]] = {}

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self._queue.join()
        self._thread.join(timeout=10)

    def enqueue(self, envelope: MessageEnvelope) -> None:
        self._queue.put(envelope)

    def _run(self) -> None:
        while not self._stop_event.is_set() or not self._queue.empty():
            try:
                envelope = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue
            payload = _parse_payload(envelope.payload, pretty_json=self._pretty_json)
            if isinstance(payload, str):
                payload = " ".join(payload.splitlines())
            assembled = self._assemble_packet(envelope.topic, payload)
            if assembled is None:
                self._queue.task_done()
                continue
            message = _build_message(envelope, assembled)
            logger.info("mqtt message", extra={"mqtt_message": message})
            self._queue.task_done()

    def _assemble_packet(self, topic: str, payload):
        if not isinstance(payload, dict):
            return payload
        time_value = payload.get("time")
        is_end = payload.get("isend")
        if not time_value or is_end is None:
            return payload
        key = (topic, str(time_value))
        buffer = self._buffers.get(key)
        if buffer is None:
            buffer = {}
            self._buffers[key] = buffer
        buffer.update(payload)
        if str(is_end) == "1":
            self._buffers.pop(key, None)
            return buffer
        return None


def _build_message(envelope: MessageEnvelope, payload):
    if not isinstance(payload, dict):
        return {
            "device_id": None,
            "topic": envelope.topic,
            "timestamp": envelope.timestamp,
            "payload": payload,
        }
    device_id = payload.get("id")
    trimmed = {k: v for k, v in payload.items() if k != "id"}
    return {
        "device_id": device_id,
        "topic": envelope.topic,
        "timestamp": envelope.timestamp,
        "payload": trimmed,
    }


def _parse_payload(raw: bytes, *, pretty_json: bool):
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.hex()

    try:
        payload = json.loads(text)
        if pretty_json and isinstance(payload, (dict, list)):
            return payload
        return payload
    except json.JSONDecodeError:
        return text


def _parse_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}
