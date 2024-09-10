from rest_framework import serializers

from user_profile.serializers import UserSerializer
from user_profile.models import UserProfile

from .models import TaskCategory, Task

class TaskCategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = TaskCategory
        fields = '__all__'


class TaskProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = UserProfile
        fields = '__all__'


class TaskListSerializers(serializers.ModelSerializer):
    task_category = TaskCategorySerializers()
    provider = TaskProfileSerializer()
    
    class Meta:
        model = Task
        fields = '__all__'
        

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'task_category', 'reward', 'done_date', 'schedule_time', 
            'description', 'work_type', 'longitude', 'latitude', 'address'
        ]
    
    def create(self, validated_data):
        validated_data['provider'] = self.context['request'].user.profile
        return super().create(validated_data)