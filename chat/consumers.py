import json
import time

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import ChatRoom, GlobalMessage, Message

RATE_LIMIT_COUNT = 5
RATE_LIMIT_WINDOW_SECONDS = 10
GLOBAL_GROUP_NAME = "global_chat"


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.group_name = f"chat_{self.room_id}"
        self.message_times = []
        user = self.scope["user"]

        if not user.is_authenticated or not await self.is_participant(user.id):
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        content = str(data.get("message", "")).strip()[:1000]
        if not content:
            return

        now = time.monotonic()
        self.message_times = [t for t in self.message_times if now - t < RATE_LIMIT_WINDOW_SECONDS]
        if len(self.message_times) >= RATE_LIMIT_COUNT:
            await self.send(text_data=json.dumps({"error": "메시지를 너무 빠르게 보내고 있습니다. 잠시 후 다시 시도해주세요."}))
            return
        self.message_times.append(now)

        user = self.scope["user"]
        await self.save_message(user.id, content)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "message": content,
                "username": user.username,
                "display_name": user.nickname or user.username,
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "username": event["username"],
            "display_name": event["display_name"],
        }))

    @database_sync_to_async
    def is_participant(self, user_id):
        try:
            room = ChatRoom.objects.select_related("product").get(pk=self.room_id)
        except ChatRoom.DoesNotExist:
            return False
        return room.is_participant(user_id)

    @database_sync_to_async
    def save_message(self, user_id, content):
        Message.objects.create(room_id=self.room_id, sender_id=user_id, content=content)


class GlobalChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.message_times = []
        user = self.scope["user"]
        if not user.is_authenticated or user.is_banned or user.is_dormant:
            await self.close()
            return
        await self.channel_layer.group_add(GLOBAL_GROUP_NAME, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(GLOBAL_GROUP_NAME, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        content = str(data.get("message", "")).strip()[:1000]
        if not content:
            return

        now = time.monotonic()
        self.message_times = [t for t in self.message_times if now - t < RATE_LIMIT_WINDOW_SECONDS]
        if len(self.message_times) >= RATE_LIMIT_COUNT:
            await self.send(text_data=json.dumps({"error": "메시지를 너무 빠르게 보내고 있습니다. 잠시 후 다시 시도해주세요."}))
            return
        self.message_times.append(now)

        user = self.scope["user"]
        await self.save_message(user.id, content)
        await self.channel_layer.group_send(
            GLOBAL_GROUP_NAME,
            {
                "type": "chat.message",
                "message": content,
                "username": user.username,
                "display_name": user.nickname or user.username,
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "username": event["username"],
            "display_name": event["display_name"],
        }))

    @database_sync_to_async
    def save_message(self, user_id, content):
        GlobalMessage.objects.create(sender_id=user_id, content=content)
