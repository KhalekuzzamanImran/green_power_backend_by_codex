import json
import logging
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": getattr(record, "mqtt_message", record.getMessage()),
            "request_id": getattr(record, "request_id", "-"),
        }
        mqtt_payload = getattr(record, "mqtt_payload", None)
        if mqtt_payload is not None:
            payload["mqtt_payload"] = mqtt_payload
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=True)
