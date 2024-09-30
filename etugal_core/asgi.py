import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'etugal_core.settings')
django.setup()


from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from chat import routing
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(
                routing.websocket_urlpatterns
            )
        )
    }
)

ASGI_APPLICATION = 'etugal_core.asgi.application'