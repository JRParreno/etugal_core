from django.contrib import admin
from .models import Task, TaskCategory, TaskApplicant, TaskReview
from django_admin_geomap import ModelAdmin


@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title',)
    ordering = ('title',)
    search_fields = ('title',)
    

@admin.register(Task)
class TaskAdmin(ModelAdmin):
    geomap_field_longitude = "id_longitude"
    geomap_field_latitude = "id_latitude"
    geomap_zoom = 30
    geomap_show_map_on_list = False
    geomap_autozoom = "15"
    geomap_default_longitude = 123.50606531769205
    geomap_default_latitude = 13.332045364707417
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