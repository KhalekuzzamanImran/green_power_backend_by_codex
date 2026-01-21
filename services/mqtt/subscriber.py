from __future__ import annotations

import logging
import os
from datetime import datetime

from services.mqtt.processor import MessageEnvelope, MessageProcessor
from services.mqtt.topics import get_topics

logger = logging.getLogger("mqtt.subscriber")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        topics = get_topics()
        qos = int(os.getenv("MQTT_QOS", "0"))
        for topic in topics:
            client.subscribe(topic, qos=qos)
        logger.info("connected; subscribed to %s topic(s)", len(topics))
    else:
        logger.error("connect failed rc=%s", rc)


def on_disconnect(client, userdata, rc):
    if rc != 0:
        logger.warning("unexpected disconnect rc=%s", rc)
    else:
        logger.info("disconnected")


def on_message(client, userdata, msg):
    timestamp = datetime.utcnow().isoformat() + "Z"
    envelope = MessageEnvelope(
        topic=msg.topic,
        qos=msg.qos,
        retained=msg.retain,
        payload=msg.payload,
        timestamp=timestamp,
    )
    if isinstance(userdata, MessageProcessor):
        userdata.enqueue(envelope)
        return
    logger.info(
        "message timestamp=%s topic=%s qos=%s retained=%s payload=<unprocessed>",
        timestamp,
        msg.topic,
        msg.qos,
        msg.retain,
    )
