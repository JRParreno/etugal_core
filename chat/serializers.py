from rest_framework import serializers

from .models import ChatSession, ChatMessage
from task.serializers import TaskSerializer, TaskProfileSerializer

class ChatMessageSerializers(serializers.ModelSerializer):
    user = TaskProfileSerializer()
    class Meta:
        model = ChatMessage
        fields = '__all__'


class ChatSessionSerializers(serializers.ModelSerializer):
    provider = TaskProfileSerializer()
    performer = TaskProfileSerializer()
    task = TaskSerializer()
    
    class Meta:
        model = ChatSession
        fields = ['task', 'provider', 'performer', 'room_name', 'id', 'created_at', 'updated_at']
    