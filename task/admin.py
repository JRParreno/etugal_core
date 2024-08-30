from django.contrib import admin
from .models import Task, TaskCategory, TaskApplicant, TaskReview


@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title',)
    ordering = ('title',)
    search_fields = ('title',)
    

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'task_category', 'provider', 'performer', 'work_type', 'status',)
    ordering = ('title', 'created_at',)
    search_fields = ('title',)
    list_filter = ('work_type', 'status',)


@admin.register(TaskApplicant)
class TaskApplicantAdmin(admin.ModelAdmin):
    list_display = ('id', 'task',)
    ordering = ('task',)
    search_fields = ('task__title',)


@admin.register(TaskReview)
class TaskReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'provider_rate', 'performer_rate')
    ordering = ('task',)
    search_fields = ('task__title',)