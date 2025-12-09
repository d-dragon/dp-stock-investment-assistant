"""
Flask API server for Stock Investment Assistant.
Provides REST API endpoints for the React frontend.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Callable, Optional, Sequence, Tuple, TYPE_CHECKING

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

# Add the src directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.agent import StockAgent
from core.data_manager import DataManager
from core.model_factory import ModelClientFactory
from core.model_registry import OpenAIModelRegistry
from data.repositories.factory import RepositoryFactory
from utils.config_loader import ConfigLoader
from services.factory import ServiceFactory
from web.routes.shared_context import APIRouteContext
from web.routes.service_health_routes import create_health_blueprint
from web.routes.ai_chat_routes import create_chat_blueprint
from web.sockets.chat_events import SocketIOContext, register_chat_events
from web.routes.models_routes import create_models_blueprint
from web.routes.user_routes import create_user_blueprint

if TYPE_CHECKING:
    from flask import Blueprint

RouteFactory = Callable[[APIRouteContext], "Blueprint"]
SocketRegistrar = Callable[[SocketIOContext], None]

DEFAULT_HTTP_ROUTE_FACTORIES: Tuple[RouteFactory, ...] = (
    create_health_blueprint,
    create_chat_blueprint,
    create_models_blueprint,
    create_user_blueprint,
)
DEFAULT_SOCKETIO_REGISTRARS: Tuple[SocketRegistrar, ...] = (register_chat_events,)


class APIServer:
    """Flask API server for the Stock Investment Assistant."""

    def __init__(
        self,
        app: Optional[Flask] = None,
        *,
        cors_origins: Optional[Sequence[str]] = None,
        socketio_kwargs: Optional[dict] = None,
        config: Optional[dict] = None,
        data_manager: Optional[DataManager] = None,
        agent: Optional[StockAgent] = None,
        http_route_factories: Optional[Sequence[RouteFactory]] = None,
        socketio_registrars: Optional[Sequence[SocketRegistrar]] = None,
    ):
        """Initialize the API server."""
        self.app = app or Flask(__name__)
        self.app.config.setdefault('SECRET_KEY', 'your-secret-key-here')

        if cors_origins is None:
            origins = ["http://localhost:3000"]
        elif isinstance(cors_origins, str):
            origins = [cors_origins]
        else:
            origins = list(cors_origins)
        CORS(self.app, origins=origins)

        socketio_config = {"cors_allowed_origins": origins}
        if socketio_kwargs:
            socketio_config.update(socketio_kwargs)
        self.socketio = SocketIO(self.app, **socketio_config)

        self.logger = logging.getLogger(__name__)

        self.config = config or ConfigLoader.load_config()
        self.data_manager = data_manager or DataManager(self.config)
        self.agent = agent or StockAgent(self.config, self.data_manager)
        self.repository_factory = RepositoryFactory(self.config)
        self.cache_repository = self.repository_factory.get_cache_repository() or RepositoryFactory.create_cache_repository(self.config)
        self.model_registry = OpenAIModelRegistry(self.config, self.cache_repository)
        self.service_factory = ServiceFactory(
            self.config,
            repository_factory=self.repository_factory,
            cache_backend=None,
            logger=self.logger.getChild("services"),
        )

        self.http_route_factories: Tuple[RouteFactory, ...] = tuple(
            http_route_factories or DEFAULT_HTTP_ROUTE_FACTORIES
        )
        self.socketio_registrars: Tuple[SocketRegistrar, ...] = tuple(
            socketio_registrars or DEFAULT_SOCKETIO_REGISTRARS
        )

        self._register_routes()
        self._register_socketio_events()

    def _set_active_model(self, provider: str, model_name: str) -> dict:
        """Update the server's default model client."""
        result = self.agent.set_default_model(provider, model_name)
        if provider == "openai" and getattr(self, "model_registry", None):
            try:
                self.model_registry.record_active_model(model_name)
            except Exception as exc:  # pragma: no cover - defensive logging
                self.logger.warning(f"Failed to record active model selection: {exc}")
        return result

    def _register_routes(self) -> None:
        """Register API blueprints."""
        context = APIRouteContext(
            app=self.app,
            agent=self.agent,
            config=self.config,
            logger=self.logger,
            stream_chat_response=self._stream_chat_response,
            extract_meta=self._extract_meta,
            strip_fallback_prefix=self._strip_fallback_prefix,
            get_timestamp=self._get_timestamp,
            model_registry=self.model_registry,
            set_active_model=self._set_active_model,
            service_factory=self.service_factory,
        )

        for factory in self.http_route_factories:
            blueprint = factory(context)
            if blueprint is None:
                continue
            self.app.register_blueprint(blueprint, url_prefix="/api")

    def _register_socketio_events(self) -> None:
        """Register Socket.IO event handlers."""
        context = SocketIOContext(
            socketio=self.socketio,
            agent=self.agent,
            config=self.config,
            logger=self.logger,
            extract_meta=self._extract_meta,
            strip_fallback_prefix=self._strip_fallback_prefix,
            get_timestamp=self._get_timestamp,
        )

        for registrar in self.socketio_registrars:
            registrar(context)

    def _stream_chat_response(self, user_message, provider_override=None):
        """Stream chat response in real-time (SSE)."""
        try:
            self.logger.info(f"Starting streaming response for: {user_message}")
            client = ModelClientFactory.get_client(self.config, provider=provider_override) if provider_override else self.agent._select_client(None)
            meta = {
                'event': 'meta',
                'provider': client.provider,
                'model': client.model_name
            }
            yield f"data: {json.dumps(meta)}\n\n"

            chunk_count = 0
            full_text_parts = []
            for chunk in self.agent.process_query_streaming(user_message, provider=provider_override):
                if chunk:
                    chunk_count += 1
                    full_text_parts.append(chunk)
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            full_text = "".join(full_text_parts)
            provider_used, model_used, fallback_flag = self._extract_meta(full_text)
            completion_payload = {
                'event': 'done',
                'fallback': fallback_flag,
                'provider': provider_used,
                'model': model_used
            }
            yield f"data: {json.dumps(completion_payload)}\n\n"
            yield "data: [DONE]\n\n"
            self.logger.info(f"Streaming complete chunks={chunk_count}")
        except Exception as e:
            self.logger.error(f"Error in streaming response: {e}")
            error_data = json.dumps({'error': str(e)})
            yield f"data: {error_data}\n\n"

    def _extract_meta(self, raw: str):
        """
        Inspect response for fallback prefix pattern: [fallback:provider]
        Returns (provider, model, fallback_flag)
        """
        fallback_flag = False
        provider = self.config.get('model', {}).get('provider', 'openai')
        model = self.config.get('model', {}).get('name') or self.config.get('openai', {}).get('model', 'gpt-4')

        if raw.startswith("[fallback:"):
            fallback_flag = True
            try:
                closing = raw.find("]")
                tag = raw[1:closing]
                provider = tag.split(":", 1)[1]
            except Exception:
                pass
        return provider, model, fallback_flag

    def _strip_fallback_prefix(self, raw: str) -> str:
        if raw.startswith("[fallback:"):
            closing = raw.find("]")
            if closing != -1:
                return raw[closing + 1:].lstrip()
        return raw

    def _get_timestamp(self) -> str:
        """Return current UTC timestamp as ISO 8601 string (Z suffix)."""
        return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    def run(self, host: str = "0.0.0.0", port: int = 5000, debug: bool = False, **kwargs):
        """
        Run the underlying server. Use SocketIO's runner so WebSocket support works locally.
        """
        self.logger.info(f"Starting API server on {host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=debug)


def main():
    """Main function to run the API server."""
    logging.basicConfig(level=logging.INFO)

    server = APIServer()
    print("Starting Stock Investment Assistant API Server...")
    print("API available at: http://localhost:5000")
    print("React app should connect to: http://localhost:5000")
    print("WebSocket endpoint: ws://localhost:5000")

    server.run()


if __name__ == '__main__':
    main()
