import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

from chat.models import ChatMessage, ChatSession
from asgiref.sync import sync_to_async
from user_profile.models import UserProfile

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route'].get(
            'kwargs', {}).get('room_name')
        if self.room_name:
            self.room_group_name = f"chat_{self.room_name}"

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        username = text_data_json["username"]
        session_id = text_data_json["id"]

        if message and hasattr(self, 'room_group_name'):
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "sendMessage",
                    "message": message,
                    "username": username,
                    "session_id": session_id,
                })

    async def sendMessage(self, event):
        # TODO handle save messages
        message = event["message"]
        username = event["username"]
        session_id = event["session_id"]
        time_stamp = timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
        chat_session = await sync_to_async(ChatSession.objects.get)(pk=session_id)
        user = await sync_to_async(UserProfile.objects.get)(user__username=username)
        
        await sync_to_async(ChatMessage.objects.create)(chat_session=chat_session, user_profile=user, message=message)
        
        await self.send(text_data=json.dumps({"message": message, "username": username, "time_stamp": time_stamp}))
   