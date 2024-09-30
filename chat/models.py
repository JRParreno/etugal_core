import json
from django.db import models
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message, Notification

from core.base_models import BaseModel
from task.models import Task
from user_profile.models import UserProfile


class ChatSession(BaseModel):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name='chat_task')
    room_name = models.CharField(max_length=255)
    provider = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='chat_sessions_provider')
    performer = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='chat_sessions_performer')

    class Meta:
        unique_together = ['task', 'provider', 'performer']
        ordering = ["-updated_at"]


class ChatMessage(BaseModel):
    chat_session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name='messages')
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.timestamp}: {self.message}"
    
    def save(self, *args, **kwargs) -> None:
        receiver = self.user_profile
        sender = self.chat_session.provider if self.chat_session.provider.user.username != receiver.user.username else self.chat_session.performer


        for device in FCMDevice.objects.all().filter(user=receiver.user):
            data = {
                "title": "ETugal",
                "body": self.message,
                "full_name": sender.user.get_full_name(),
            }
            device.send_message(
                Message(
                    notification=Notification(
                        title="New Message", body=self.message
                    ),
                    data={
                        "json": json.dumps(data)
                    },
                )
            )

        
        super(ChatMessage, self).save(*args, **kwargs)

