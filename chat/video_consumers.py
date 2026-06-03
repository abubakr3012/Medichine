import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Call


class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.call_id = self.scope["url_route"]["kwargs"]["call_id"]
        self.call_group_name = f"call_{self.call_id}"

        await self.channel_layer.group_add(self.call_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.call_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get("type")

        if message_type == "offer":
            await self.channel_layer.group_send(
                self.call_group_name,
                {
                    "type": "call.offer",
                    "offer": data.get("offer"),
                    "sender": self.scope["user"].id,
                },
            )
        elif message_type == "answer":
            await self.channel_layer.group_send(
                self.call_group_name,
                {
                    "type": "call.answer",
                    "answer": data.get("answer"),
                    "sender": self.scope["user"].id,
                },
            )
        elif message_type == "ice_candidate":
            await self.channel_layer.group_send(
                self.call_group_name,
                {
                    "type": "call.ice_candidate",
                    "candidate": data.get("candidate"),
                    "sender": self.scope["user"].id,
                },
            )
        elif message_type == "end_call":
            await self.channel_layer.group_send(
                self.call_group_name,
                {
                    "type": "call.end",
                    "sender": self.scope["user"].id,
                },
            )

    async def call_offer(self, event):
        if event["sender"] != self.scope["user"].id:
            await self.send(text_data=json.dumps({
                "type": "offer",
                "offer": event["offer"],
            }))

    async def call_answer(self, event):
        if event["sender"] != self.scope["user"].id:
            await self.send(text_data=json.dumps({
                "type": "answer",
                "answer": event["answer"],
            }))

    async def call_ice_candidate(self, event):
        if event["sender"] != self.scope["user"].id:
            await self.send(text_data=json.dumps({
                "type": "ice_candidate",
                "candidate": event["candidate"],
            }))

    async def call_end(self, event):
        await self.send(text_data=json.dumps({
            "type": "end_call",
        }))
