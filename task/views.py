from rest_framework import generics, permissions, response, filters, viewsets, status

from core.paginate import ExtraSmallResultsSetPagination
from user_profile.models import UserProfile
from .models import TaskCategory, Task
from .serializers import TaskCategorySerializers, TaskListSerializers, TaskSerializer
from rest_framework.decorators import action

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
    queryset = Task.objects.all().order_by('-created_at')
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
        performer_id = request.data.get('performer')

        # Validate that the performer exists
        if performer_id:
            try:
                performer = UserProfile.objects.get(pk=performer_id)
                task.performer = performer
                task.status = Task.IN_PROGRESS
                task.save()
                serializer = TaskSerializer(task)
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