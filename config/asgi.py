import os

import logging

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

from common.redis_client import close_async_redis
from apps.telemetry.routing import websocket_urlpatterns

_django_app = get_asgi_application()
_router = ProtocolTypeRouter(
    {
        "http": _django_app,
        "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)
_logger = logging.getLogger(__name__)
_lifespan_warned = False


async def application(scope, receive, send):
    # Ensure ASGI lifespan support is enabled in production (e.g., Uvicorn/Gunicorn with lifespan on),
    # so Redis client cleanup executes on shutdown. Safe no-op if lifespan is unsupported.
    if scope["type"] == "lifespan":
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                try:
                    await close_async_redis()
                except Exception:
                    pass
                await send({"type": "lifespan.shutdown.complete"})
                return
    else:
        global _lifespan_warned
        if not _lifespan_warned:
            _logger.warning(
                "ASGI lifespan events not observed; enable lifespan support to guarantee Redis cleanup."
            )
            _lifespan_warned = True
        await _router(scope, receive, send)
