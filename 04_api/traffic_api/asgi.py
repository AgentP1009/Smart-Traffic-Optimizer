import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import traffic_api.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traffic_api.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            traffic_api.routing.websocket_urlpatterns
        )
    ),
})