import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import userauth.routing  # Import the new routing file

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "socialmedia.settings")  # Change to your project name

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            userauth.routing.websocket_urlpatterns  # Add WebSocket routes
        )
    ),
})
