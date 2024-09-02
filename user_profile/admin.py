from django.contrib import admin
from .models import UserProfile
from django.core.mail import send_mail
from etugal_core import settings


@admin.register(UserProfile)
class UserProfileAdminView(admin.ModelAdmin):
    list_display = ('id', 'user', 'verification_status',)
    ordering = ('user',)
    search_fields = ('user__first_name', 'user__last_name',)
    list_filter = ('verification_status',)

    def save_model(self, request, obj, form, change):
        # prev_profile = UserProfile.objects.get(pk=obj.pk)
        # if obj.verified == UserProfile.VERIFIED and not prev_profile.verified == UserProfile.VERIFIED:
        #     send_mail(
        #         subject=f'Registration',
        #         message=f'Your worker application account was approved by our team. '
        #         'Kindly ignore this message if you did not initiate this request.',
        #         from_email=settings.EMAIL_HOST_USER,
        #         recipient_list=[obj.user.email],
        #         html_message=f'Your worker application account was approved by our team. '
        #                      'Kindly ignore this message if you did not initiate this request.',
        #     )
        #     obj.is_worker = True
        # if obj.verified == UserProfile.REJECTED and not prev_profile.verified == UserProfile.REJECTED:
        #     send_mail(
        #         subject=f'Registration',
        #         message=f'Your worker application account was rejected by our team. '
        #         'Kindly ignore this message if you did not initiate this request.',
        #         from_email=settings.EMAIL_HOST_USER,
        #         recipient_list=[obj.user.email],
        #         html_message=f'Your worker application account was rejected by our team. '
        #                      'Kindly ignore this message if you did not initiate this request.',
        #     )
        super(UserProfileAdminView, self).save_model(
            request, obj, form, change)