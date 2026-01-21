from __future__ import annotations

import logging
import os
import signal

import django

from services.mqtt.client import build_client
from services.mqtt.processor import MessageProcessor
from services.mqtt.subscriber import on_connect, on_disconnect, on_message


def run() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    django.setup()

    _configure_logging()

    host = os.getenv("MQTT_BROKER") or os.getenv("MQTT_HOST", "localhost")
    port = int(os.getenv("MQTT_PORT", "1883"))
    keepalive = int(os.getenv("MQTT_KEEPALIVE", "60"))
    connect_timeout = int(os.getenv("MQTT_CONNECT_TIMEOUT", "10"))

    client = build_client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    processor = MessageProcessor()
    client.user_data_set(processor)
    processor.start()

    def _shutdown(signum, frame):
        client.disconnect()

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    try:
        client.connect_async(host, port, keepalive)
        client.loop_forever(timeout=connect_timeout, retry_first_connection=True)
    finally:
        processor.stop()


def _configure_logging() -> None:
    level = os.getenv("MQTT_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


if __name__ == "__main__":
    run()
