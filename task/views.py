from rest_framework import generics, permissions, response, filters, viewsets, status, exceptions

from core.paginate import ExtraSmallResultsSetPagination
from task.notification import notifyTask
from user_profile.models import UserProfile
from .models import TaskCategory, Task, TaskReview, TaskApplicant
from .serializers import (TaskCategorySerializers, TaskListSerializers, TaskSerializer, 
                          TaskReviewSerializers, CreateTaskApplicantSerializer, TaskListApplicantSerializer)
from rest_framework.decorators import action
from firebase_admin.messaging import Message, Notification
from django.db.models import Q

class TaskCategoryListView(generics.ListAPIView):
    serializer_class = TaskCategorySerializers
    queryset = TaskCategory.objects.all()
    permission_classes = [permissions.IsAuthenticated,]
    pagination_class = ExtraSmallResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title',]
    

class TaskListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = TaskListSerializers
    queryset = Task.objects.all()
    pagination_class = ExtraSmallResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title',]
    
    def get_queryset(self):
        task_category_id = self.request.GET.get('task_category', None)
        queryset = super().get_queryset().filter(performer=None, status=Task.PENDING).exclude(provider=self.request.user.profile)
        if task_category_id:
            return queryset.filter(task_category=task_category_id)
        
        return queryset
    


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset().filter(provider=self.request.user.profile)
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user.profile
        
        user.is_active()
        
        if user.is_suspended or user.is_terminated:
            raise exceptions.ValidationError({"error_message": "Your account is suspended."})
    
        serializer.save(provider=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        """Handles PATCH requests to update any or all fields of the Task."""
        # Get the task object
        task = self.get_object()

        # Use serializer to partially update the task
        serializer = self.get_serializer(task, data=request.data, partial=True)

        # Validate and save the serializer
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Return the updated data
        return response.Response(serializer.data, status=status.HTTP_200_OK)
        
    @action(detail=True, methods=['patch'])
    def patch_performer(self, request, pk=None):
        task = self.get_object()
        performer_id = request.data.get('performer_id')

        if performer_id:
            try:
                performer = UserProfile.objects.get(pk=performer_id)
                task.performer = performer
                task.status = Task.IN_PROGRESS
                task.save()
                serializer = TaskSerializer(task)
                
                body = f"Congratulations! Your application for the task {task.title} has been approved. You can now communicate with the Task Provider to finalize the details."
                data = {
                    "title": "E-Tugal",
                    "body": body,
                }
                notification = {
                    "title": "E-Tugal", "body": body
                }

                notifyTask(performer.user, notification, data)
                return response.Response(serializer.data, status=status.HTTP_200_OK)
            except UserProfile.DoesNotExist:
                return response.Response({"error_message": "Performer does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return response.Response({"error_message": "Performer ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def patch_status(self, request, pk=None):
        task = self.get_object()
        new_status = request.data.get('status')
        
        if new_status in dict(Task.STATUSES).keys():
            serializer = TaskSerializer(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data)
            return response.Response(serializer.errors, status=400)
        else:
            return response.Response({"error_message": f"Invalid status. Allowed statuses: {list(dict(Task.STATUSES).keys())}"}, status=400)


    
class PerformerTaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset().filter(performer=self.request.user.profile)
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        return queryset


    @action(detail=True, methods=['patch'])
    def patch_is_done_perform(self, request, pk=None):
        task = self.get_object()
        is_done_perform = request.data.get('is_done_perform')

        # Check if performer exists
        if task.performer is None:
            return response.Response({"error_message": "No performer assigned to this task."}, status=status.HTTP_400_BAD_REQUEST)

        if is_done_perform is not None:
            if isinstance(is_done_perform, bool):  # Ensure the value is a boolean
                task.is_done_perform = is_done_perform
                task.save()

                # Notify the performer about the status update, if needed
                if is_done_perform:  # For example, only notify if the task is marked as done
                    notification = {
                        "title": "Task Update",
                        "body": f"The task '{task.title}' has been marked as completed by the performer."
                    }
                    data = {
                        "title": "Task Update",
                        "body": f"The task '{task.title}' is done."
                    }
                    notifyTask(task.provider.user, notification, data)

                serializer = TaskSerializer(task)
                return response.Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return response.Response({"error_message": "Invalid value for is_done_perform. Must be true or false."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return response.Response({"error_message": "is_done_perform is required."}, status=status.HTTP_400_BAD_REQUEST)


class TaskReviewListView(generics.ListAPIView):
    serializer_class = TaskReviewSerializers
    permission_classes = [permissions.IsAuthenticated]
    queryset = TaskReview.objects.filter(task__status=Task.COMPLETED).order_by('-created_at')
    pagination_class = ExtraSmallResultsSetPagination

    def get_queryset(self):
        performer_id = self.request.query_params.get('performer', None)
        provider_id = self.request.query_params.get('provider', None)

        if performer_id:
            return TaskReview.objects.filter(task__performer__id=performer_id, performer_rate__gt=0)
        elif provider_id:
            return TaskReview.objects.filter(task__provider__id=provider_id, provider_rate__gt=0)
        else:
            return None

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if queryset is None:
            return response.Response(
                {"error_message": "Please provide either a performer or provider ID."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # If pagination is not applied, return a normal response
        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)



class TaskApplicantCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = TaskApplicant.objects.all()
    serializer_class = CreateTaskApplicantSerializer

    def perform_create(self, serializer):

        # Notify user logic
        user = self.request.user.profile
        
        # Validate user's status before creating TaskApplicant
        if user.is_suspended:
            raise exceptions.ValidationError({"error_message": "Your account is suspended."})
    
        if user.is_terminated:
            raise exceptions.ValidationError({"error_message": "Your account is terminated."})
   
        
        task_applicant = serializer.save()
        task = task_applicant.task  # Assuming Task is related to TaskApplicant
        
        body = f"A new performer has applied for your task: {task.title}. Review their profile and approve if suitable."
        data = {
            "title": "E-Tugal",
            "body": body,
        }
        notification = {
            "title": "E-Tugal", "body": body
        }

        notifyTask(task.provider.user, notification, data)


class TaskListApplicantView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = TaskApplicant.objects.all()
    serializer_class = TaskListApplicantSerializer
    pagination_class = ExtraSmallResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset().filter(performer=self.request.user.profile)
        status = self.request.query_params.get('status', None)
        if status:
            if status == Task.PENDING:
                queryset = queryset.filter(task__status=status, task__performer=None)
            else:
                queryset = queryset.filter(task__status=status, task__performer=self.request.user.profile)
        return queryset




class TaskReviewViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create_or_update(self, request, task_id=None):
        try:
            # Get the task based on the provided task_id
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return response.Response({"error_message": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if a review for this task already exists
        try:
            task_review = TaskReview.objects.get(task=task)
            # If a review exists, update it
            serializer = TaskReviewSerializers(task_review, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data, status=status.HTTP_200_OK)
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except TaskReview.DoesNotExist:
            # If no review exists, create one
            serializer = TaskReviewSerializers(data=request.data, partial=True)
            if serializer.is_valid():
                # Manually assign the task to the review
                serializer.save(task=task)
                return response.Response(serializer.data, status=status.HTTP_201_CREATED)
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, task_id=None):
        try:
            # Get the task based on the provided task_id
            task = Task.objects.get(id=task_id)
            task_review = TaskReview.objects.get(task=task)
            serializer = TaskReviewSerializers(task_review)
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return response.Response({"error_message": "Task not found."}, status=status.HTTP_404_NOT_FOUND)
        except TaskReview.DoesNotExist:
            return response.Response({"error_message": "Review not found for this task."}, status=status.HTTP_404_NOT_FOUND)