from __future__ import annotations

import json
import logging
import os
import queue
import time
import threading
from concurrent.futures import ThreadPoolExecutor, wait
from dataclasses import dataclass

from apps.telemetry.services import broadcast_realtime, store_event_mongo
from apps.telemetry.schemas import GeneratorDataModel
from apps.telemetry.validators import validate_packet

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
        maxsize = int(os.getenv("MQTT_MESSAGE_QUEUE", "10000"))
        self._queue: queue.Queue[MessageEnvelope] = queue.Queue(maxsize=maxsize)
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, name="mqtt-message-worker", daemon=True)
        self._buffers: dict[tuple[str, str | None], dict[str, object]] = {}
        self._buffer_timestamps: dict[tuple[str, str | None], float] = {}
        self._buffer_ttl_seconds = int(os.getenv("MQTT_BUFFER_TTL_SECONDS", "300"))
        self._executor = ThreadPoolExecutor(
            max_workers=int(os.getenv("MQTT_FANOUT_WORKERS", "4"))
        )
        self._drop_on_full = _parse_bool(os.getenv("MQTT_DROP_ON_FULL", "true"))
        self._fanout_timeout = float(os.getenv("MQTT_FANOUT_TIMEOUT_SECONDS", "0.2"))
        self._metrics = {"dropped": 0, "fanout_errors": 0}
        self._metrics_lock = threading.Lock()

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self._queue.join()
        self._thread.join(timeout=10)
        self._executor.shutdown(wait=True)

    def metrics(self) -> dict:
        with self._metrics_lock:
            return dict(self._metrics)

    def enqueue(self, envelope: MessageEnvelope) -> None:
        try:
            self._queue.put_nowait(envelope)
        except queue.Full:
            if self._drop_on_full:
                with self._metrics_lock:
                    self._metrics["dropped"] += 1
                logger.warning("message queue full; dropping topic=%s", envelope.topic)
            else:
                self._queue.put(envelope)

    def _run(self) -> None:
        while not self._stop_event.is_set() or not self._queue.empty():
            try:
                envelope = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue
            self._cleanup_stale_buffers()
            payload = _parse_payload(envelope.payload, pretty_json=self._pretty_json)
            if isinstance(payload, str):
                payload = " ".join(payload.splitlines())
            assembled = self._assemble_packet(envelope.topic, payload)
            if assembled is None:
                self._queue.task_done()
                continue
            message = _build_message(envelope, _normalize_keys(assembled))
            if message.get("topic") == "CCCL/PURBACHAL/ENM_01":
                try:
                    message = _normalize_generator_message(message)
                except Exception as exc:
                    logger.warning("generator normalization failed: %s", exc)
            try:
                validate_packet(message)
            except ValueError as exc:
                logger.warning("invalid packet dropped: %s", exc)
                self._queue.task_done()
                continue
            futures = [
                self._executor.submit(store_event_mongo, message),
                self._executor.submit(broadcast_realtime, message),
            ]
            done, not_done = wait(futures, timeout=self._fanout_timeout)
            for future in done:
                try:
                    future.result()
                except Exception as exc:
                    with self._metrics_lock:
                        self._metrics["fanout_errors"] += 1
                    logger.exception("fanout error: %s", exc)
            if not_done:
                with self._metrics_lock:
                    self._metrics["fanout_errors"] += len(not_done)
                logger.warning("fanout timeout: %s pending task(s)", len(not_done))
            logger.info("mqtt message", extra={"mqtt_message": message})
            self._queue.task_done()

    def _assemble_packet(self, topic: str, payload):
        if not isinstance(payload, dict):
            return payload
        is_end = payload.get("isend")
        if is_end is None:
            return payload
        buffer_key = self._buffer_key(topic, payload)
        buffer = self._buffers.get(buffer_key)
        if buffer is None:
            buffer = {}
            self._buffers[buffer_key] = buffer
        self._buffer_timestamps[buffer_key] = time.monotonic()
        buffer.update(payload)
        if str(is_end) == "1":
            self._buffers.pop(buffer_key, None)
            self._buffer_timestamps.pop(buffer_key, None)
            return buffer
        return None

    def _buffer_key(self, topic: str, payload: dict) -> tuple[str, str | None]:
        time_key = payload.get("time")
        return (topic, str(time_key) if time_key is not None else None)

    def _cleanup_stale_buffers(self) -> None:
        if not self._buffer_timestamps:
            return
        now = time.monotonic()
        expired = [
            key for key, ts in self._buffer_timestamps.items() if now - ts > self._buffer_ttl_seconds
        ]
        for key in expired:
            self._buffers.pop(key, None)
            self._buffer_timestamps.pop(key, None)


def _build_message(envelope: MessageEnvelope, payload):
    if not isinstance(payload, dict):
        return {
            "device_id": None,
            "topic": envelope.topic,
            "timestamp": envelope.timestamp,
            "payload": payload,
        }
    device_id = payload.get("id") or payload.get("device_id")
    trimmed = {k: v for k, v in payload.items() if k != "id"}
    return {
        "device_id": device_id,
        "topic": envelope.topic,
        "timestamp": envelope.timestamp,
        "payload": trimmed,
    }


def _normalize_keys(payload):
    if not isinstance(payload, dict):
        return payload
    normalized = {}
    for key, value in payload.items():
        new_key = (
            str(key)
            .strip()
            .replace("(", "_")
            .replace(")", "")
            .replace("/", "_")
            .replace("%", "percent")
            .replace("*", "")
            .replace("+", "plus")
            .replace("-", "minus")
            .replace(" ", "_")
            .lower()
        )
        while "__" in new_key:
            new_key = new_key.replace("__", "_")
        normalized[new_key] = value
    return normalized


def _normalize_generator_message(message: dict) -> dict:
    payload = message.get("payload")
    if not isinstance(payload, dict):
        return message
    data_point = payload.get("data", [{}])[0]
    if not data_point:
        return message
    timestamp = data_point.get("tp")
    points = {str(p.get("id")): p.get("val") for p in data_point.get("point", []) if p.get("id") is not None}
    flattened = {"timestamp": timestamp, **points}
    model = GeneratorDataModel.from_flat_dict(flattened)
    normalized = dict(message)
    normalized["payload"] = model.model_dump()
    return normalized


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
