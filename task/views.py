from rest_framework import generics, permissions, response, status, filters

from core.paginate import ExtraSmallResultsSetPagination
from .models import TaskCategory, Task
from .serializers import TaskCategorySerializers, TaskSerializers

class TaskCategoryListView(generics.ListAPIView):
    serializer_class = TaskCategorySerializers
    queryset = TaskCategory.objects.all()
    permission_classes = [permissions.IsAuthenticated,]
    pagination_class = ExtraSmallResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title',]
    

class TaskListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = TaskSerializers
    queryset = Task.objects.all().order_by('-created_at')
    pagination_class = ExtraSmallResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title',]
    
    def get_queryset(self):
        task_category_id = self.request.GET.get('task_category', None)
        
        if task_category_id:
            return super().get_queryset().filter(task_category=task_category_id)
        
        return super().get_queryset()