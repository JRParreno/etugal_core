from django.contrib import admin
from .models import UserProfile, UserReport, ReportImage
from django.core.mail import send_mail
from etugal_core import settings
from django.contrib import messages
from .email import Util

class ReportImageInline(admin.TabularInline):
    model = ReportImage
    extra = 1  # Number of extra empty image fields

from django.contrib import admin
from .models import UserProfile

from django.contrib import admin
from .models import UserProfile

from django.contrib import admin
from django import forms
from .models import UserProfile
from django.utils.translation import gettext_lazy as _

class CustomVerificationStatusListFilter(admin.SimpleListFilter):
    # The title to be displayed in the filter sidebar
    title = _('Verification Status')  # You can customize this title

    # Parameter for the filter, which is what you will use in the query parameters
    parameter_name = 'verification_status'

    def lookups(self, request, model_admin):
        # Custom labels for the filter options
        return (
            (UserProfile.VERIFIED, _('Verified')),
            (UserProfile.PROCESSING_APPLICATION, _('Processing Application')),
            (UserProfile.UNVERIFIED, _('Unverified')),
            (UserProfile.REJECTED, _('Disapproved')),  # Changed REJECTED to Disapproved here
        )

    def queryset(self, request, queryset):
        # Filter the queryset based on the selected value
        if self.value():
            return queryset.filter(verification_status=self.value())
        return queryset

@admin.register(UserProfile)
class UserProfileAdminView(admin.ModelAdmin):
    # Custom method to change 'REJECTED' to 'DISAPPROVED' in the admin list view
    def get_verification_status_display_admin(self, obj):
        if obj.verification_status == UserProfile.REJECTED:
            return 'DISAPPROVED'  # Change display of REJECTED to DISAPPROVED
        return obj.get_verification_status_display()  # Default display method for other statuses

    get_verification_status_display_admin.short_description = 'Verification Status'  # Column name

    # Customize list display to use the custom method
    list_display = ('id', 'user', 'get_verification_status_display_admin', 'is_suspended', 'is_terminated', 'suspended_until')
    
    ordering = ('user',)
    search_fields = ('user__first_name', 'user__last_name',)
    list_filter = (CustomVerificationStatusListFilter, 'is_suspended', 'is_terminated')
    
    actions = ['suspend_1_day', 'suspend_3_days', 'suspend_1_week', 'suspend_1_month', 'terminate_user']

    # Action methods for suspending and terminating users
    def suspend_1_day(self, request, queryset):
        for profile in queryset:
            profile.suspend(reason="Admin Suspension", duration_key='1_day')
    suspend_1_day.short_description = 'Suspend for 1 Day'

    def suspend_3_days(self, request, queryset):
        for profile in queryset:
            profile.suspend(reason="Admin Suspension", duration_key='3_days')
    suspend_3_days.short_description = 'Suspend for 3 Days'

    def suspend_1_week(self, request, queryset):
        for profile in queryset:
            profile.suspend(reason="Admin Suspension", duration_key='1_week')
    suspend_1_week.short_description = 'Suspend for 1 Week'

    def suspend_1_month(self, request, queryset):
        for profile in queryset:
            profile.suspend(reason="Admin Suspension", duration_key='1_month')
    suspend_1_month.short_description = 'Suspend for 1 Month'

    def terminate_user(self, request, queryset):
        for profile in queryset:
            profile.terminate(reason="Admin Termination")
    terminate_user.short_description = 'Terminate selected users'

    # Override save_model to send email when the verification status changes
    def save_model(self, request, obj, form, change):
        prev_profile = UserProfile.objects.get(pk=obj.pk)
        if obj.verification_status == UserProfile.VERIFIED and not prev_profile.verification_status == UserProfile.VERIFIED: 
            message = f'Your account was verified by our team. Kindly ignore this message if you did not initiate this request.'
            Util.send_email_with_certifi(
                subject='Registration',
                from_email='settings.EMAIL_HOST_USER',
                message=message,
                recipient_list=[obj.user.email],
            )
        if obj.verification_status == UserProfile.REJECTED and not prev_profile.verification_status == UserProfile.REJECTED:
            message = f'Your account was rejected by our team. \n{obj.verification_remarks}'
            Util.send_email_with_certifi(
                subject='Registration',
                from_email='settings.EMAIL_HOST_USER',
                message=message,
                recipient_list=[obj.user.email],
            )
        super(UserProfileAdminView, self).save_model(request, obj, form, change)

    # Customize the form field for verification_status in the admin form
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "verification_status":
            choices = list(UserProfile.VERIFICATION_CHOICES)
            # Replace 'REJECTED' with 'DISAPPROVED' in the form choices
            for i, choice in enumerate(choices):
                if choice[0] == UserProfile.REJECTED:
                    choices[i] = (UserProfile.REJECTED, 'DISAPPROVED')
            kwargs['choices'] = choices
        return super().formfield_for_choice_field(db_field, request, **kwargs)

        
    
@admin.register(UserReport)
class UserReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'reported_user', 'status', 'action_taken', 'resolved_at')
    list_filter = ('status', 'action_taken')
    search_fields = ('reporter__username', 'reported_user__username')
    inlines = [ReportImageInline]  # Add inline for report images
    actions = ['resolve_as_suspension', 'resolve_as_termination']

    def save_model(self, request, obj, form, change):
        # Call the original save_model to save the report
        super().save_model(request, obj, form, change)

        # Get the user profile of the reported user
        profile = obj.reported_user.profile
        
        # Perform the chosen action based on 'action_taken'
        if obj.action_taken == 'suspend' and obj.suspension_duration:
            message = f"{obj.reported_user} suspended for {obj.suspension_duration}."
            profile.suspend(reason=obj.reason, duration_key=obj.suspension_duration)
            self.message_user(request, message, level=messages.SUCCESS)
            Util.send_email_with_certifi(
                subject='Account Suspension',
                from_email='settings.EMAIL_HOST_USER',
                message=obj.resolution_notes,
                recipient_list=[obj.reported_user.email],
            )
        elif obj.action_taken == 'terminate':
            message = f"{obj.reported_user} terminated."
            profile.terminate(reason=obj.reason)
            self.message_user(request, message, level=messages.SUCCESS)
            Util.send_email_with_certifi(
                subject='Account Termination',
                from_email='settings.EMAIL_HOST_USER',
                message=obj.resolution_notes,
                recipient_list=[obj.reported_user.email],
            )
        else:
            self.message_user(request, f"No action taken on {obj.reported_user}.", level=messages.INFO)

    def resolve_as_suspension(self, request, queryset):
        for report in queryset.filter(status='pending'):
            report.resolve_report(action_taken='suspend', resolution_notes="Resolved by admin action")
            profile = report.reported_user.profile
            profile.suspend(reason=f"Suspended due to report: {report.reason}", duration_key=report.suspension_duration)
        self.message_user(request, f"{queryset.count()} users suspended.", level=messages.SUCCESS)

    resolve_as_suspension.short_description = 'Suspend User for 1 Week'

    def resolve_as_termination(self, request, queryset):
        for report in queryset.filter(status='pending'):
            report.resolve_report(action_taken='terminate', resolution_notes="Resolved by admin action")
            profile = report.reported_user.profile
            profile.terminate(reason=f"Terminated due to report: {report.reason}")
        self.message_user(request, f"{queryset.count()} users terminated.", level=messages.SUCCESS)

    resolve_as_termination.short_description = 'Terminate User'