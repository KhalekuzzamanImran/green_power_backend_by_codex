from __future__ import annotations

import os
import ssl
from typing import Any

import paho.mqtt.client as mqtt


def build_client() -> mqtt.Client:
    """Create and configure MQTT client using .env credentials."""
    client_id = os.getenv("MQTT_CLIENT_ID") or "telemetry-subscriber"
    protocol = _resolve_protocol(os.getenv("MQTT_PROTOCOL", "311"))
    clean_session = _parse_bool(os.getenv("MQTT_CLEAN_SESSION", "true"))
    username = os.getenv("MQTT_USERNAME")
    password = os.getenv("MQTT_PASSWORD")

    client = mqtt.Client(client_id=client_id, protocol=protocol, clean_session=clean_session)
    if username:
        client.username_pw_set(username=username, password=password)

    _configure_tls(client)
    _configure_performance(client)
    return client


def _resolve_protocol(value: str) -> int:
    value = (value or "").strip().lower()
    if value in {"5", "v5", "mqttv5"}:
        return mqtt.MQTTv5
    return mqtt.MQTTv311


def _parse_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _configure_tls(client: mqtt.Client) -> None:
    if not _parse_bool(os.getenv("MQTT_TLS", "false")):
        return

    ca_certs = os.getenv("MQTT_CA_CERTS")
    certfile = os.getenv("MQTT_CERTFILE")
    keyfile = os.getenv("MQTT_KEYFILE")
    tls_version = os.getenv("MQTT_TLS_VERSION", "TLSv1_2")
    tls_insecure = _parse_bool(os.getenv("MQTT_TLS_INSECURE", "false"))

    version_map: dict[str, Any] = {
        "TLSv1": ssl.PROTOCOL_TLSv1,
        "TLSv1_1": ssl.PROTOCOL_TLSv1_1,
        "TLSv1_2": ssl.PROTOCOL_TLSv1_2,
        "TLS": ssl.PROTOCOL_TLS_CLIENT,
    }
    client.tls_set(
        ca_certs=ca_certs or None,
        certfile=certfile or None,
        keyfile=keyfile or None,
        tls_version=version_map.get(tls_version, ssl.PROTOCOL_TLS_CLIENT),
    )
    client.tls_insecure_set(tls_insecure)


def _configure_performance(client: mqtt.Client) -> None:
    client.max_inflight_messages_set(int(os.getenv("MQTT_MAX_INFLIGHT", "20")))
    client.max_queued_messages_set(int(os.getenv("MQTT_MAX_QUEUE", "0")))
    client.reconnect_delay_set(
        min_delay=int(os.getenv("MQTT_RECONNECT_MIN", "1")),
        max_delay=int(os.getenv("MQTT_RECONNECT_MAX", "30")),
    )
