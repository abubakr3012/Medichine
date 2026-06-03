import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.files.base import ContentFile
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
        WebSocket принимает сообщения в формате JSON:
            { "message": "...", "sender": <user_id>, "receiver": <user_id>, 
              "photo": "<base64>", "voice": "<base64>" }
        
        Фото и голосовые сообщения теперь также отправляются через WebSocket в формате base64.
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
        photo_base64 = text_data_json.get("photo")
        voice_base64 = text_data_json.get("voice")

        user = self.scope.get("user")
        if not (user and user.is_authenticated):
            return

        if not message_text and not photo_base64 and not voice_base64:
            return

        # receiver берём из тела сообщения, иначе из room_name
        receiver_id = receiver_id if receiver_id is not None else self.room_name

        if receiver_id is None:
            return

        # Защита от подмены sender
        if sender_id is not None and str(user.id) != str(sender_id):
            return

        # Декодируем файлы из base64
        photo_file = None
        voice_file = None
        
        if photo_base64:
            photo_file = await self.decode_base64_file(photo_base64, "photo")
        
        if voice_base64:
            voice_file = await self.decode_base64_file(voice_base64, "voice")

        # Сохраняем в БД
        saved = await self.save_direct_message(user, receiver_id, message_text, photo_file, voice_file)
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
                "photo_url": saved.photo.url if saved.photo else None,
                "voice_url": saved.voice.url if saved.voice else None,
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
                "photo_url": saved.photo.url if saved.photo else None,
                "voice_url": saved.voice.url if saved.voice else None,
            },
        )

    async def direct_message(self, event):
        await self.send(text_data=json.dumps({
            "sender": event.get("sender"),
            "sender_id": event.get("sender_id"),
            "message": event.get("message"),
            "photo_url": event.get("photo_url"),
            "voice_url": event.get("voice_url"),
        }))

    async def decode_base64_file(self, base64_data, file_type):
        """Декодирует base64 строку в Django ContentFile"""
        try:
            # Убираем префикс data:image/...;base64, если есть
            if "," in base64_data:
                base64_data = base64_data.split(",")[1]
            
            file_data = base64.b64decode(base64_data)
            
            # Определяем расширение файла
            if file_type == "photo":
                ext = "jpg"
            elif file_type == "voice":
                ext = "webm"
            else:
                ext = "bin"
            
            filename = f"{file_type}_{self.scope['user'].id}_{self.room_name}.{ext}"
            return ContentFile(file_data, name=filename)
        except Exception:
            return None

    @database_sync_to_async
    def save_direct_message(self, sender, receiver_id, text, photo_file=None, voice_file=None):
        try:
            receiver = sender.__class__.objects.get(id=receiver_id)
            return Direct.objects.create(
                sender=sender,
                receiner=receiver,
                text=text,
                photo=photo_file,
                voice=voice_file,
            )
        except sender.__class__.DoesNotExist:
            return None