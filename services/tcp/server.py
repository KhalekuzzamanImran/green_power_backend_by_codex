from __future__ import annotations

import itertools
import json
import logging
import os
import queue
import socket
import struct
import threading
import time
import concurrent.futures
from datetime import datetime, timezone
from typing import Dict, List, Tuple
from http.server import BaseHTTPRequestHandler, HTTPServer

import pymongo

from common.mongo import get_mongo_database
from apps.telemetry.services import broadcast_realtime
from services.tcp.schemas import SolarDataPayload

logger = logging.getLogger("tcp.server")
if not logging.getLogger().handlers:
    logging.basicConfig(level=os.getenv("TCP_LOG_LEVEL", "INFO"))

HEARTBEAT_PACKET = b"GWCCCL0001"
DEFAULT_RESPONSE_PACKETS = [
    bytes.fromhex("01 26 00 00 00 06 01 03 0B B7 00 0A"),
    bytes.fromhex("01 6E 00 00 00 06 01 03 0B ED 00 06"),
    bytes.fromhex("01 B6 00 00 00 06 01 03 0C 83 00 08"),
]


class TCPSocketServer:
    def __init__(
        self,
        host: str,
        port: int,
        heartbeat_packet: bytes = HEARTBEAT_PACKET,
        response_packets: List[bytes] | None = None,
        recv_buffer_size: int = 1024,
        client_timeout: int = 120,
        backlog: int = 50,
        batch_size: int = 200,
        batch_flush_ms: int = 500,
    ) -> None:
        self.host = host
        self.port = port
        self.heartbeat_packet = heartbeat_packet
        self.response_packets = response_packets or DEFAULT_RESPONSE_PACKETS
        self.response_cycle = itertools.cycle(enumerate(self.response_packets))
        self.cycle_lock = threading.Lock()
        self.recv_buffer_size = recv_buffer_size
        self.client_timeout = client_timeout
        self.backlog = backlog
        self.batch_size = batch_size
        self.batch_flush_ms = batch_flush_ms
        self.timeout_max_retries = int(os.getenv("TCP_TIMEOUT_MAX_RETRIES", "3"))
        self.timeout_backoff_base = float(os.getenv("TCP_TIMEOUT_BACKOFF_BASE", "1.0"))
        self.timeout_backoff_max = float(os.getenv("TCP_TIMEOUT_BACKOFF_MAX", "10.0"))
        self.mongo_lock = threading.Lock()
        self._queue: queue.Queue[dict] = queue.Queue(maxsize=int(os.getenv("TCP_QUEUE_SIZE", "5000")))
        self._stop_event = threading.Event()
        self._health_server: HTTPServer | None = None
        self._health_thread: threading.Thread | None = None
        self._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=int(os.getenv("TCP_MAX_CLIENTS", "100"))
        )
        self._metrics_lock = threading.Lock()
        self._metrics = {
            "connections_total": 0,
            "active_connections": 0,
            "timeouts_total": 0,
            "messages_queued": 0,
            "batches_flushed": 0,
            "parse_errors_total": 0,
            "mongo_errors_total": 0,
        }
        self._init_mongo()
        self._start_worker()
        self._start_health_server()

    def _init_mongo(self) -> None:
        db = get_mongo_database()
        self.collections = {
            "solar_data": self._ensure_timeseries(
                db,
                "solar_data",
                expire_after_seconds=None,
            ),
            "today_solar_data": self._ensure_timeseries(
                db,
                "today_solar_data",
                expire_after_seconds=86400,
            ),
            "current_month_solar_data": self._ensure_timeseries(
                db,
                "current_month_solar_data",
                expire_after_seconds=2592000,
            ),
        }
        self._create_indexes()

    def _ensure_timeseries(
        self,
        db,
        name: str,
        expire_after_seconds: int | None,
    ):
        try:
            options = {"timeField": "timestamp", "metaField": "client_id", "granularity": "minutes"}
            if expire_after_seconds is not None:
                db.create_collection(
                    name,
                    timeseries=options,
                    expireAfterSeconds=expire_after_seconds,
                )
            else:
                db.create_collection(name, timeseries=options)
            return db[name]
        except pymongo.errors.CollectionInvalid:
            return db[name]
        except pymongo.errors.OperationFailure as exc:
            logger.warning("timeseries creation failed for %s: %s", name, exc)
            return db[name]

    def _create_indexes(self) -> None:
        try:
            self.collections["solar_data"].create_index(
                [("client_id", pymongo.ASCENDING), ("timestamp", pymongo.DESCENDING)]
            )
        except pymongo.errors.OperationFailure as exc:
            logger.warning("index creation error: %s", exc)

    def _store_data(self, data: Dict[str, List[float]], client_id: str) -> None:
        if len(data) != 3:
            return

        now = datetime.now(timezone.utc)
        document = {
            "timestamp": now,
            "client_id": client_id,
            "current": data.get("response_0", []),
            "power": data.get("response_1", []),
            "energy_consumption": data.get("response_2", []),
        }
        try:
            SolarDataPayload.model_validate(document)
        except Exception as exc:
            logger.warning("invalid payload for %s: %s", client_id, exc)
            return
        message = {
            "device_id": client_id,
            "topic": "TCP_SOLAR_DATA",
            "timestamp": now.isoformat(),
            "payload": {
                "current": document["current"],
                "power": document["power"],
                "energy_consumption": document["energy_consumption"],
            },
        }
        try:
            self._queue.put_nowait(document)
        except queue.Full:
            logger.warning("tcp queue full; dropping payload for %s", client_id)
            return
        with self._metrics_lock:
            self._metrics["messages_queued"] += 1
        try:
            broadcast_realtime(message, group=os.getenv("TCP_WS_GROUP", "tcp_telemetry"), event="tcp.message")
        except Exception as exc:
            logger.warning("tcp websocket broadcast failed: %s", exc)

    def _process_response(self, index: int, hex_response: str) -> List[float]:
        if "0103" not in hex_response:
            return []

        try:
            _, payload = hex_response.split("0103", 1)
            payload = payload[2:]

            chunk_size = 16 if index == 2 else 8
            if len(payload) % chunk_size != 0:
                logger.warning("invalid payload length %s", len(payload))
                return []

            chunks = [payload[i : i + chunk_size] for i in range(0, len(payload), chunk_size)]
            converted_values: List[float] = []
            for chunk in chunks:
                try:
                    fmt = "!f" if chunk_size == 8 else "!q"
                    value = struct.unpack(fmt, bytes.fromhex(chunk))[0]
                    converted_values.append(float(value))
                except (struct.error, ValueError) as exc:
                    logger.warning("data unpacking error: %s", exc)
                    with self._metrics_lock:
                        self._metrics["parse_errors_total"] += 1
            return converted_values
        except Exception as exc:
            logger.warning("processing error: %s", exc)
            with self._metrics_lock:
                self._metrics["parse_errors_total"] += 1
            return []

    def _start_worker(self) -> None:
        threading.Thread(target=self._worker_loop, name="tcp-store-worker", daemon=True).start()

    def _worker_loop(self) -> None:
        batch: List[dict] = []
        last_flush = time.monotonic()
        while not self._stop_event.is_set():
            timeout = max(self.batch_flush_ms / 1000 - (time.monotonic() - last_flush), 0.1)
            try:
                item = self._queue.get(timeout=timeout)
                batch.append(item)
                self._queue.task_done()
            except queue.Empty:
                pass

            should_flush = len(batch) >= self.batch_size or (
                batch and (time.monotonic() - last_flush) * 1000 >= self.batch_flush_ms
            )
            if should_flush:
                self._flush_batch(batch)
                batch = []
                last_flush = time.monotonic()

        if batch:
            self._flush_batch(batch)

    def _flush_batch(self, batch: List[dict]) -> None:
        if not batch:
            return
        try:
            with self.mongo_lock:
                self.collections["solar_data"].insert_many(batch, ordered=False)
                self.collections["today_solar_data"].insert_many(batch, ordered=False)
                self.collections["current_month_solar_data"].insert_many(batch, ordered=False)
            logger.info("stored %s tcp records", len(batch))
            with self._metrics_lock:
                self._metrics["batches_flushed"] += 1
        except pymongo.errors.PyMongoError as exc:
            logger.error("mongo batch insert error: %s", exc)
            with self._metrics_lock:
                self._metrics["mongo_errors_total"] += 1

    def handle_client(self, client_socket: socket.socket, addr: Tuple[str, int]) -> None:
        client_id = f"{addr[0]}:{addr[1]}"
        accumulated_data: Dict[str, List[float]] = {}
        timeout_retries = 0

        with client_socket:
            client_socket.settimeout(self.client_timeout)
            with self._metrics_lock:
                self._metrics["connections_total"] += 1
                self._metrics["active_connections"] += 1

            try:
                while True:
                    data = client_socket.recv(self.recv_buffer_size)
                    if not data:
                        logger.info("client disconnected: %s", client_id)
                        break
                    timeout_retries = 0

                    logger.info("heartbeat from %s: %s", client_id, data)

                    if data == self.heartbeat_packet:
                        with self.cycle_lock:
                            index, response_packet = next(self.response_cycle)

                        logger.info("sending response #%s to %s", index, client_id)
                        client_socket.sendall(response_packet)

                        try:
                            response = client_socket.recv(self.recv_buffer_size)
                            if not response:
                                logger.warning("client %s disconnected after response", client_id)
                                break

                            if len(response) < 6:
                                logger.warning("short response from %s", client_id)
                                with self._metrics_lock:
                                    self._metrics["parse_errors_total"] += 1
                                continue
                            hex_response = response.hex().upper()
                            logger.info("response from %s: %s", client_id, hex_response)
                            values = self._process_response(index, hex_response)
                            if values:
                                accumulated_data[f"response_{index}"] = values
                                if len(accumulated_data) == 3:
                                    self._store_data(accumulated_data, client_id)
                                    accumulated_data = {}

                        except (socket.timeout, socket.error):
                            logger.warning("timeout waiting for response from %s", client_id)
                            with self._metrics_lock:
                                self._metrics["timeouts_total"] += 1
                            timeout_retries += 1
                            if timeout_retries >= self.timeout_max_retries:
                                logger.warning("max timeouts reached for %s; closing", client_id)
                                break
                            delay = min(
                                self.timeout_backoff_base * (2 ** (timeout_retries - 1)),
                                self.timeout_backoff_max,
                            )
                            time.sleep(delay)
                            continue
                    else:
                        logger.warning("unrecognized packet from %s: %s", client_id, data)

            except socket.timeout:
                logger.warning("connection timeout with %s", client_id)
                with self._metrics_lock:
                    self._metrics["timeouts_total"] += 1
            except (socket.error, ConnectionResetError, BrokenPipeError):
                logger.warning("connection lost with %s", client_id)
            except Exception as exc:
                logger.exception("error handling %s: %s", client_id, exc)
            finally:
                with self._metrics_lock:
                    self._metrics["active_connections"] -= 1

    def start_server(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(self.backlog)
            logger.info("server listening on %s:%s", self.host, self.port)

            try:
                while True:
                    client_socket, addr = server_socket.accept()
                    logger.info("new connection from %s:%s", addr[0], addr[1])
                    self._executor.submit(self.handle_client, client_socket, addr)
            except KeyboardInterrupt:
                logger.info("server shutdown requested")
            except Exception as exc:
                logger.exception("server error: %s", exc)
            finally:
                self._stop_event.set()
                self._queue.join()
                self._executor.shutdown(wait=True)
                if self._health_server:
                    self._health_server.shutdown()
                    self._health_server.server_close()

    def _start_health_server(self) -> None:
        port = int(os.getenv("TCP_HEALTH_PORT", "7001"))
        if port <= 0:
            return

        server = self

        class HealthHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path != "/health":
                    self.send_response(404)
                    self.end_headers()
                    return
                with server._metrics_lock:
                    payload = dict(server._metrics)
                payload["queue_size"] = server._queue.qsize()
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

        self._health_thread = threading.Thread(
            target=self._run_health_server,
            args=(port, HealthHandler),
            daemon=True,
            name="tcp-health-server",
        )
        self._health_thread.start()

    def _run_health_server(self, port: int, handler) -> None:
        try:
            httpd = HTTPServer((self.host, port), handler)
            self._health_server = httpd
            logger.info("tcp health server listening on %s:%s", self.host, port)
            httpd.serve_forever()
        except Exception as exc:
            logger.warning("health server error: %s", exc)


def run() -> None:
    host = os.getenv("TCP_HOST", "0.0.0.0")
    port = int(os.getenv("TCP_PORT", "6000"))
    recv_buffer = int(os.getenv("TCP_RECV_BUFFER", "1024"))
    timeout = int(os.getenv("TCP_CLIENT_TIMEOUT", "120"))
    backlog = int(os.getenv("TCP_BACKLOG", "50"))

    server = TCPSocketServer(
        host=host,
        port=port,
        recv_buffer_size=recv_buffer,
        client_timeout=timeout,
        backlog=backlog,
        batch_size=int(os.getenv("TCP_BATCH_SIZE", "200")),
        batch_flush_ms=int(os.getenv("TCP_BATCH_FLUSH_MS", "500")),
    )
    server.start_server()
