from django.db import models
from django.contrib.auth.models import User
from etugal_core import settings


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
    
    
    def __str__(self):
        return str(f'{self.user.last_name} - {self.user.first_name}')