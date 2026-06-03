import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_authenticated:
            self.user_group_name = f"notifications_{user.id}"
            await self.channel_layer.group_add(self.user_group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        user = self.scope["user"]
        if user.is_authenticated:
            await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

    async def receive(self, text_data):
        pass  # Клиент только получает уведомления

    async def call_notification(self, event):
        await self.send(text_data=json.dumps({
            "type": "incoming_call",
            "call_id": event["call_id"],
            "caller_id": event["caller_id"],
            "caller_name": event["caller_name"],
        }))
