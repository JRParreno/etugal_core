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


class TaskSerializers(serializers.ModelSerializer):
    task_category = TaskCategorySerializers()
    provider = TaskProfileSerializer()
    
    class Meta:
        model = Task
        fields = '__all__'