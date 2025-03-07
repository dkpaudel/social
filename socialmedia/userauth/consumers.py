import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from .models import ChatMessage, ChatRoom

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        sender_username = data["sender"]

        sender = await sync_to_async(User.objects.get)(username=sender_username)
        room = await sync_to_async(ChatRoom.objects.get)(id=self.room_id)

        # Save message to database
        chat_message = await sync_to_async(ChatMessage.objects.create)(
            room=room, sender=sender, message=message
        )

        # Send message to WebSocket group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": sender.username,
            },
        )

    async def chat_message(self, event):
        message = event["message"]
        sender = event["sender"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message, "sender": sender}))
