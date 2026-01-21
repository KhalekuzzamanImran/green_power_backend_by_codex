from __future__ import annotations

import os

from channels.generic.websocket import AsyncJsonWebsocketConsumer


class TelemetryConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        group = os.getenv("TELEMETRY_WS_GROUP", "telemetry")
        await self.channel_layer.group_add(group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        group = os.getenv("TELEMETRY_WS_GROUP", "telemetry")
        await self.channel_layer.group_discard(group, self.channel_name)

    async def telemetry_message(self, event):
        await self.send_json(event["message"])
