from rest_framework import generics, permissions, response, filters, viewsets, status

from core.paginate import ExtraSmallResultsSetPagination
from task.notification import notifyTask
from user_profile.models import UserProfile
from .models import TaskCategory, Task, TaskReview, TaskApplicant
from .serializers import (TaskCategorySerializers, TaskListSerializers, TaskSerializer, 
                          TaskReviewSerializers, CreateTaskApplicantSerializer, TaskListApplicantSerializer)
from rest_framework.decorators import action
from firebase_admin.messaging import Message, Notification

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
        serializer.save(provider=self.request.user)
    
    @action(detail=True, methods=['patch'])
    def patch_performer(self, request, pk=None):
        task = self.get_object()
        performer_id = request.data.get('performer_id')

        # Validate that the performer exists
        # TODO notify performer
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
                return response.Response({"error": "Performer does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return response.Response({"error": "Performer ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def patch_status(self, request, pk=None):
        task = self.get_object()
        new_status = request.data.get('status')
        
        # Ensure the new status is valid
        if new_status in dict(Task.STATUSES).keys():
            serializer = TaskSerializer(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data)
            return response.Response(serializer.errors, status=400)
        else:
            return response.Response({"error": f"Invalid status. Allowed statuses: {list(dict(Task.STATUSES).keys())}"}, status=400)


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




class TaskReviewListView(generics.ListAPIView):
    serializer_class = TaskReviewSerializers
    permission_classes = [permissions.IsAuthenticated]
    queryset = TaskReview.objects.filter(task__status=Task.COMPLETED).order_by('-created_at')
    pagination_class = ExtraSmallResultsSetPagination

    def get_queryset(self):
        performer_id = self.request.query_params.get('performer', None)
        provider_id = self.request.query_params.get('provider', None)

        if performer_id:
            return TaskReview.objects.filter(task__performer__id=performer_id)
        elif provider_id:
            return TaskReview.objects.filter(task__provider__id=provider_id)
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
        task_applicant = serializer.save()

        # Notify user logic
        user = self.request.user
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
    