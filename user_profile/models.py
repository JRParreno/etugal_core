from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from etugal_core import settings
from django.utils import timezone


class UserProfile(models.Model):
    class ProfileManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().select_related('user')
    NA = 'N/A'
    MALE = 'M'
    FEMALE = 'F'

    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    ]
    
    SUBMITTED = 'SUBMITTED'
    PROCESSING_APPLICATION = 'PROCESSING_APPLICATION'
    VERIFIED = 'VERIFIED'
    UNVERIFIED = 'UNVERIFIED'
    REJECTED = 'REJECTED'
    
    VERIFICATION_CHOICES = [
        (PROCESSING_APPLICATION, 'PROCESSING APPLICATION'),
        (VERIFIED, 'VERIFIED'),
        (REJECTED, 'REJECTED'),
        (UNVERIFIED, 'UNVERIFIED'),
    ]
    
    SUSPENSION_DURATIONS = {
        '1_day': timedelta(days=1),
        '3_days': timedelta(days=3),
        '1_week': timedelta(weeks=1),
        '1_month': timedelta(days=30),  # Approximate month
    }

    user = models.OneToOneField(
        User, related_name='profile', on_delete=models.CASCADE)
    birthdate = models.DateField(null=True)
    address = models.TextField(blank=False, null=False)
    contact_number = models.CharField(max_length=25)
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, default=MALE)
    profile_photo = models.ImageField(
        upload_to='images/profiles/', blank=True, null=True)
    verification_status = models.CharField(
        max_length=100, choices=VERIFICATION_CHOICES, default=UNVERIFIED, null=False, blank=False,)
    verification_remarks = models.TextField(null=True, blank=True)
    id_photo = models.ImageField(
        upload_to='images/ids/', blank=True, null=True)
    face_photo = models.ImageField(
        upload_to='images/faces/', blank=True, null=True)
    is_suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(blank=True, null=True)
    suspended_until = models.DateTimeField(blank=True, null=True)
    is_terminated = models.BooleanField(default=False)
    termination_reason = models.TextField(blank=True, null=True)
    
    
    
    def __str__(self):
        return str(f'{self.user.last_name} - {self.user.first_name}')
    
    def suspend(self, reason, duration_key=None):
        self.is_suspended = True
        self.suspension_reason = reason
        if duration_key in self.SUSPENSION_DURATIONS:
            self.suspended_until = timezone.now() + self.SUSPENSION_DURATIONS[duration_key]
        else:
            self.suspended_until = None  # Indefinite suspension
            # Log an error or raise an exception if needed
        self.save()

    def terminate(self, reason):
        self.is_terminated = True
        self.termination_reason = reason
        self.save()

    def is_active(self):
        # Check suspension expiry and termination
        if self.is_terminated:
            return False
        if self.is_suspended and self.suspended_until and self.suspended_until < timezone.now():
            self.is_suspended = False
            self.suspension_reason = ""
            self.suspended_until = None
            self.save()
        return not self.is_suspended


class UserReport(models.Model):
    REPORT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]
    
    REPORT_ACTION_CHOICES = [
        ('none', 'No Action'),
        ('suspend', 'Suspend User'),
        ('terminate', 'Terminate User'),
    ]
    
    SUSPENSION_DURATIONS = {
        '1_day': timedelta(days=1),
        '3_days': timedelta(days=3),
        '1_week': timedelta(weeks=1),
        '1_month': timedelta(days=30),  # Approximate month
    }

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received')
    reason = models.TextField()
    additional_info = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=REPORT_STATUS_CHOICES, default='pending')
    action_taken = models.CharField(max_length=10, choices=REPORT_ACTION_CHOICES, default='none')
    suspension_duration = models.CharField(max_length=10, blank=True, null=True, choices=[
        ('1_day', '1 Day'),
        ('3_days', '3 Days'),
        ('1_week', '1 Week'),
        ('1_month', '1 Month'),
    ], help_text="Duration of suspension if applicable.")
    resolution_notes = models.TextField(blank=True, null=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    def resolve_report(self, action_taken, resolution_notes=""):
        self.status = 'resolved'
        self.action_taken = action_taken
        self.resolution_notes = resolution_notes
        self.resolved_at = timezone.now()

        # Perform the chosen action: suspend or terminate
        user_profile = self.reported_user.profile
        
        if action_taken == 'suspend' and self.suspension_duration:
            # Suspend the user for the specified duration
            user_profile.suspend(reason=self.reason, duration_key=self.suspension_duration)
        elif action_taken == 'terminate':
            # Terminate the user account
            user_profile.terminate(reason=self.reason)
        
        self.save()

    def __str__(self):
        return f"Report by {self.reporter.username} against {self.reported_user.username} (Status: {self.status})"
    


class ReportImage(models.Model):
    report = models.ForeignKey(UserReport, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='report_images/')  # You can customize the upload path

    def __str__(self):
        return f'Image for report {self.report.id}'