import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Direct


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # ws/chat/<room_name>/ — room_name это id получателя (из шаблона)
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        """
        WebSocket принимает ТОЛЬКО текстовые сообщения в формате JSON:
            { "message": "...", "sender": <user_id>, "receiver": <user_id> }

        Фото и голосовые сообщения отправляются через обычный HTTP POST (multipart/form-data)
        и НЕ проходят через WebSocket. Это правильная архитектура — WebSocket не
        предназначен для передачи бинарных файлов в данной реализации.
        """
        if not text_data:
            return

        try:
            text_data_json = json.loads(text_data)
        except json.JSONDecodeError:
            return

        message_text = (text_data_json.get("message") or "").strip()
        sender_id = text_data_json.get("sender")
        receiver_id = text_data_json.get("receiver")

        user = self.scope.get("user")
        if not (user and user.is_authenticated):
            return

        if not message_text:
            return

        # receiver берём из тела сообщения, иначе из room_name
        receiver_id = receiver_id if receiver_id is not None else self.room_name

        if receiver_id is None:
            return

        # Защита от подмены sender
        if sender_id is not None and str(user.id) != str(sender_id):
            return

        # Сохраняем в БД
        saved = await self.save_direct_message(user, receiver_id, message_text)
        if not saved:
            return

        # Рассылаем в группу (оба участника получат сообщение)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "direct.message",
                "sender": user.username,
                "sender_id": user.id,
                "message": message_text,
            },
        )

        # Также отправляем в группу получателя, чтобы он увидел сообщение
        # если у него открыт чат с отправителем
        receiver_group = f"chat_{user.id}"
        await self.channel_layer.group_send(
            receiver_group,
            {
                "type": "direct.message",
                "sender": user.username,
                "sender_id": user.id,
                "message": message_text,
            },
        )

    async def direct_message(self, event):
        await self.send(text_data=json.dumps({
            "sender": event.get("sender"),
            "sender_id": event.get("sender_id"),
            "message": event.get("message"),
        }))

    @database_sync_to_async
    def save_direct_message(self, sender, receiver_id, text):
        try:
            receiver = sender.__class__.objects.get(id=receiver_id)
            return Direct.objects.create(
                sender=sender,
                receiner=receiver,
                text=text,
            )
        except sender.__class__.DoesNotExist:
            return None