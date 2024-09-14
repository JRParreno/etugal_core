from rest_framework import serializers

from user_profile.serializers import UserSerializer
from user_profile.models import UserProfile

from .models import TaskApplicant, TaskCategory, Task, TaskReview

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
    performer = TaskProfileSerializer()

    class Meta:
        model = Task
        fields = '__all__'


class TaskReviewSerializers(serializers.ModelSerializer):
    task = TaskListSerializers()

    class Meta:
        model = TaskReview
        fields = '__all__'
        
class TaskApplicantSerializer(serializers.ModelSerializer):
    performer = TaskProfileSerializer(read_only=True)

    class Meta:
        model = TaskApplicant
        fields = ['performer', 'description',]

class TaskSerializer(serializers.ModelSerializer):
    # Use PrimaryKeyRelatedField for write operations, rename to task_category_id
    task_category_id = serializers.PrimaryKeyRelatedField(
        queryset=TaskCategory.objects.all(), write_only=True, source='task_category'
    )
    # Use TaskCategorySerializers for read operations, keeping task_category as a full object
    task_category = TaskCategorySerializers(read_only=True)
    provider = TaskProfileSerializer(read_only=True)
    task_applicants = TaskApplicantSerializer(many=True, read_only=True, source='task_applicant')
    performer = TaskProfileSerializer(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'task_category_id', 'task_category', 'reward', 'done_date', 'schedule_time', 
            'description', 'work_type', 'longitude', 'latitude', 'address', 'provider',
            'performer', 'created_at', 'updated_at', 'status', 'rejection_reason', 'task_applicants', 'done_date',
            'schedule_time', 'is_done_perform'
        ]
        
        extra_kwargs = {
            'rejection_reason': {'read_only': True},
        }
    
    def create(self, validated_data):
        validated_data['provider'] = self.context['request'].user.profile
        return super().create(validated_data)



class CreateTaskApplicantSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskApplicant
        fields = '__all__'