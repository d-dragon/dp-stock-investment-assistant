"""Route registration helpers for the web server."""

from .api_routes import APIRouteContext, create_api_blueprint
from .user_routes import create_user_blueprint

__all__ = ["APIRouteContext", "create_api_blueprint", "create_user_blueprint"]
