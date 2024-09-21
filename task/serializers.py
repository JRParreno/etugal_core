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
        read_only_fields = ['task']

    def create(self, validated_data):
        # Create a review for a task
        return TaskReview.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # Update the review instance
        instance.provider_rate = validated_data.get('provider_rate', instance.provider_rate)
        instance.provider_feedback = validated_data.get('provider_feedback', instance.provider_feedback)
        instance.performer_rate = validated_data.get('performer_rate', instance.performer_rate)
        instance.performer_feedback = validated_data.get('performer_feedback', instance.performer_feedback)
        instance.save()
        return instance

class TaskPrevReviewSerializers(serializers.ModelSerializer):
    class Meta:
        model = TaskReview
        exclude = ['task']
        
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
    review = TaskPrevReviewSerializers(read_only=True, source='task_review')

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'task_category_id', 'task_category', 'reward', 'done_date', 'schedule_time', 
            'description', 'work_type', 'longitude', 'latitude', 'address', 'provider',
            'performer', 'created_at', 'updated_at', 'status', 'rejection_reason', 'task_applicants', 'done_date',
            'schedule_time', 'is_done_perform', 'review',
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


class TaskListApplicantSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)

    class Meta:
        model = TaskApplicant
        fields = ['task',]
    
    
    def to_representation(self, instance):
        # Get the original representation from the parent serializer
        representation = super().to_representation(instance)
        
        # Extract the `task` data from the representation and return it directly
        task_data = representation.pop('task')
        
        # Return the task data without wrapping it in the `task` field
        return task_data