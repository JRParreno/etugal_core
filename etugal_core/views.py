import json
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from oauth2_provider.models import get_access_token_model
from oauth2_provider.signals import app_authorized
from oauth2_provider.views.base import TokenView
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render


def privacy_policy(request):
    
    return render(request, 'privacy_policy.html')

def terms_condition(request):
    
    return render(request, 'terms_condition.html')

def safety_guide(request):
    
    return render(request, 'safety_guide.html')

class TokenViewWithUserId(TokenView):
    @method_decorator(sensitive_post_parameters("password"))
    def post(self, request, *args, **kwargs):
        url, headers, body, status = self.create_token_response(request)

        if status == 200:
            body = json.loads(body)
            access_token = body.get("access_token")
            if access_token is not None:
                try:
                    token = get_access_token_model().objects.get(
                        token=access_token)
                    
                    # Check if the user has a profile
                    profile = token.user.profile
                    
                    profile.is_active()
                    
                    if profile is None:
                        raise ObjectDoesNotExist("User profile does not exist")

                    app_authorized.send(
                        sender=self, request=request,
                        token=token)
                    
                    # Add user ID to the response body
                    data = {
                        "pk": str(token.user.pk),
                        "profilePk": str(profile.pk),
                        "username": token.user.username,
                        "firstName": token.user.first_name,
                        "lastName": token.user.last_name,
                        "email": token.user.email,
                        "contactNumber": profile.contact_number,
                        "birthdate": str(profile.birthdate),
                        "profilePhoto": request.build_absolute_uri(profile.profile_photo.url) if profile.profile_photo else None,
                        "address": profile.address,
                        "gender": profile.gender,
                        "verificationStatus": profile.verification_status,
                        "verificationRemarks": profile.verification_remarks,
                        "access_token": access_token,
                        "refresh_token": body.get("refresh_token"),
                        "is_suspended": profile.is_suspended,
                        "suspension_reason": profile.suspension_reason,
                        "suspended_until": profile.suspended_until.isoformat() if profile.suspended_until else None,
                        "is_terminated": profile.is_terminated,
                        "termination_reason": profile.termination_reason,
                    }
                    
                    body = json.dumps(data)
                    
                except ObjectDoesNotExist:
                    # Handle case where user profile doesn't exist
                    return JsonResponse({'error_description': 'User profile does not exist'}, status=400)
   
        response = HttpResponse(content=body, status=status)
        for k, v in headers.items():
            response[k] = v
        return response