from django.contrib import admin
from drf_yasg import openapi
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.views.generic import RedirectView
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from chat.views import chatPage
from .views import TokenViewWithUserId, privacy_policy, terms_condition



schema_view = get_schema_view(
    openapi.Info(
        title="E-Tugal API",
        default_version='v1',
        description="Testing API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=False,
    permission_classes=(permissions.AllowAny,),
)
router = DefaultRouter()
router.register('devices', FCMDeviceAuthorizedViewSet)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('api-auth/', include('rest_framework.urls')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('o/login/', TokenViewWithUserId.as_view(), name='token'),
    path('admin/', admin.site.urls),
    path('chat/', chatPage, name="chat-page"),
    path('', RedirectView.as_view(url='/admin/', permanent=True)),
    path('api/', include('api.urls', namespace='api')),
    path('privacy_policy/', privacy_policy, name='privacy_policy'),
    path('terms_condition/', terms_condition, name='terms_condtion'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password_reset_complete.html'),
         name='password_reset_complete'),
]

urlpatterns += router.urls
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)