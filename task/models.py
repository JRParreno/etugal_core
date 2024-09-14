from django.db import models
from django.forms import ValidationError

from core.base_models import BaseModel
from user_profile.models import UserProfile
from django_admin_geomap import GeoItem

class TaskCategory(BaseModel):
    title = models.CharField(max_length=25, unique=True)
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['title',]
    
    def __str__(self):
        return self.title


class Task(BaseModel, GeoItem):
    IN_PERSON = 'IN_PERSON'
    ONLINE = 'ONLINE'

    WORK_TYPE = [
        (IN_PERSON, 'In Person'),
        (ONLINE, 'Online'),
    ]
    
    PENDING = 'PENDING'
    IN_PROGRESS = 'IN_PROGRESS'
    ACCEPTED = 'ACCEPTED'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'
    REJECTED = 'REJECTED'

    STATUSES = [
        (PENDING, 'Pending'),
        (IN_PROGRESS, 'In Progress'),
        (ACCEPTED, 'Accepted'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
        (REJECTED, 'Rejected'),
    ]
    
    title = models.CharField(max_length=25)
    task_category = models.ForeignKey(TaskCategory, on_delete=models.CASCADE)
    provider = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='task_provider')
    performer = models.ForeignKey(UserProfile, null=True, blank=True, on_delete=models.CASCADE, related_name='task_performer')
    description = models.TextField()
    work_type = models.CharField(
        max_length=10, choices=WORK_TYPE, default=ONLINE, verbose_name="Work Type")
    reward = models.FloatField(default=0.0)
    address = models.CharField(max_length=150)
    longitude = models.FloatField()
    latitude = models.FloatField()
    done_date = models.DateField(null=True, blank=False)
    schedule_time = models.TimeField(null=True, blank=True)
    is_done_perform = models.BooleanField(default=False)
    status = models.CharField(
        max_length=15, choices=STATUSES, default=PENDING, verbose_name="Task Status")
    rejection_reason = models.TextField(blank=True, null=True)
    
    @property
    def geomap_longitude(self):
        return '' if self.longitude is None else str(self.longitude)

    @property
    def geomap_latitude(self):
        return '' if self.latitude is None else str(self.latitude)

    @property
    def geomap_popup_view(self):
        return "<strong>{}</strong>".format(str(self))

    @property
    def geomap_popup_edit(self):
        return self.geomap_popup_view

    @property
    def geomap_popup_common(self):
        return self.geomap_popup_view

    class Meta:
        managed = True
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ['-updated_at',]
    
    def __str__(self):
        return f"{self.title} - {self.status}"
    
    def clean(self):
        # Ensure that is_done_perform is True before marking the task as completed
        if self.status == self.COMPLETED and not self.is_done_perform:
            raise ValidationError("The task cannot be marked as completed unless 'is_done_perform' is True.")
    
    def save(self, *args, **kwargs):
        # Call the clean method to perform validation
        self.clean()
        super().save(*args, **kwargs)


class TaskApplicant(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_applicant')
    performer = models.ForeignKey(UserProfile, null=True, blank=True, on_delete=models.CASCADE, related_name='task_applicant_performer')
    description = models.TextField(null=True, blank=True)
    
    class Meta:
        unique_together = ['task', 'performer',]
        verbose_name = "Applicant"
        verbose_name_plural = "Applicants"
    
    def __str__(self):
        return f"{self.task.title} - {self.performer.user.get_full_name}"


class TaskReview(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_review')
    provider_rate = models.IntegerField(default=0, choices=((i,i) for i in range(1, 6)))
    provider_feedback = models.TextField(null=True, blank=True)
    performer_rate = models.IntegerField(default=0, choices=((i,i) for i in range(1, 6)))
    performer_feedback = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Review"
    
    def __str__(self):
        return self.task.title
    