"""Route registration helpers for the web server."""

from .shared_context import APIRouteContext
from .service_health_routes import create_health_blueprint
from .ai_chat_routes import create_chat_blueprint
from .models_routes import create_models_blueprint
from .user_routes import create_user_blueprint

__all__ = [
    "APIRouteContext",
    "create_health_blueprint",
    "create_chat_blueprint",
    "create_models_blueprint",
    "create_user_blueprint",
]
