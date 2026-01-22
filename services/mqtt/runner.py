from __future__ import annotations

import json
import logging
import os
import signal
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

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

    status = {"connected": False, "last_message": None, "dropped": 0, "fanout_errors": 0}
    status_lock = threading.Lock()

    def _on_connect(client, userdata, flags, rc):
        on_connect(client, userdata, flags, rc)
        with status_lock:
            status["connected"] = rc == 0

    def _on_disconnect(client, userdata, rc):
        on_disconnect(client, userdata, rc)
        with status_lock:
            status["connected"] = False

    def _on_message(client, userdata, msg):
        on_message(client, userdata, msg)
        with status_lock:
            status["last_message"] = _utc_now()

    _start_health_server(status, status_lock)

    client = build_client()
    client.on_connect = _on_connect
    client.on_message = _on_message
    client.on_disconnect = _on_disconnect
    processor = MessageProcessor()
    client.user_data_set(processor)
    processor.start()

    def _sync_metrics():
        while True:
            with status_lock:
                status.update(processor.metrics())
            time.sleep(1.0)

    threading.Thread(target=_sync_metrics, name="mqtt-metrics-sync", daemon=True).start()

    stop_event = threading.Event()

    def _shutdown(signum, frame):
        stop_event.set()
        client.disconnect()

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    try:
        client.connect_async(host, port, keepalive)
        client.loop_start()
        stop_event.wait()
    finally:
        client.loop_stop()
        processor.stop()


def _configure_logging() -> None:
    level = os.getenv("MQTT_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def _utc_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def _start_health_server(status: dict, lock: threading.Lock) -> None:
    port = int(os.getenv("MQTT_HEALTH_PORT", "7002"))
    if port <= 0:
        return

    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != "/health":
                self.send_response(404)
                self.end_headers()
                return
            with lock:
                payload = dict(status)
            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            try:
                self.wfile.write(body)
            except BrokenPipeError:
                return

        def log_message(self, format, *args):
            return

    def _run():
        try:
            httpd = HTTPServer(("0.0.0.0", port), HealthHandler)
            logging.getLogger("mqtt.health").info(
                "mqtt health server listening on 0.0.0.0:%s", port
            )
            httpd.serve_forever()
        except Exception as exc:
            logging.getLogger("mqtt.health").warning("health server error: %s", exc)

    threading.Thread(target=_run, name="mqtt-health-server", daemon=True).start()


if __name__ == "__main__":
    run()
