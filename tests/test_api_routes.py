"""Unit tests for the HTTP API blueprint.

DEPRECATED: This test file is deprecated as api_routes.py has been split into:
- service_health_routes.py (tested in test_health_routes.py)
- ai_chat_routes.py (tested in test_chat_routes.py)

Keeping this file temporarily for reference, but tests now live in the new files.
"""

import logging
from flask import Flask

from web.routes.shared_context import APIRouteContext
from web.routes.service_health_routes import create_health_blueprint
from web.routes.ai_chat_routes import create_chat_blueprint


class DummyAgent:
    """Record-only agent stub used in route tests."""

    def __init__(self):
        self.calls = []

    def process_query(self, message, provider=None):
        """Public method that matches actual agent interface."""
        self.calls.append((message, provider))
        return "RAW RESPONSE"

    def process_query_streaming(self, message, provider=None):
        yield from ["chunk-1", "chunk-2"]


class DummyRegistry:
    def __init__(self):
        self.models = [
            {"id": "gpt-4", "created": 1},
            {"id": "gpt-4o", "created": 2},
        ]
        self.get_calls = []
        self.refreshed = False
        self.active_model = "gpt-4"

    @property
    def is_configured(self):  # pragma: no cover - compatibility
        return True

    def get_supported_models(self, force_refresh=False):
        self.get_calls.append(force_refresh)
        source = "live" if force_refresh else "cache"
        return {
            "models": self.models,
            "refreshed_at": "2024-01-01T00:00:00Z",
            "source": source,
            "active_model": self.active_model,
        }

    def refresh_supported_models(self):
        self.refreshed = True
        return {
            "models": self.models,
            "refreshed_at": "2024-01-01T00:00:01Z",
            "active_model": self.active_model,
        }

    def is_supported_model(self, model_name: str) -> bool:
        return any(item["id"] == model_name for item in self.models)

    def record_active_model(self, model_name: str) -> None:
        self.active_model = model_name

    def get_active_model(self):
        return self.active_model


def _make_test_app(registry=None):
    app = Flask("test_api_routes")
    agent = DummyAgent()
    stream_calls = []
    registry = registry or DummyRegistry()
    active_calls = []

    def stream_chat_response(message, provider_override, conversation_id=None):
        stream_calls.append((message, provider_override, conversation_id))
        yield "data: test-chunk\n\n"

    def extract_meta(raw):
        return ("provider", "model", False)

    def strip_fallback(raw):
        return "cleaned"

    def get_timestamp():
        return "2024-01-01T00:00:00Z"

    def set_active(provider, model):
        active_calls.append((provider, model))
        return {"provider": provider, "model": model}

    # Create mock chat_service for non-streaming tests
    from unittest.mock import MagicMock
    mock_chat_service = MagicMock()
    mock_chat_service.process_chat_query.return_value = {
        "response": "cleaned",
        "provider": "provider",
        "model": "model",
        "fallback": False,
        "timestamp": "2024-01-01T00:00:00Z"
    }
    mock_chat_service.stream_chat_response = stream_chat_response
    mock_chat_service.extract_meta = extract_meta
    mock_chat_service.strip_fallback_prefix = strip_fallback
    mock_chat_service.get_timestamp = get_timestamp

    context = APIRouteContext(
        app=app,
        agent=agent,
        config={},
        logger=logging.getLogger("test-api-routes"),
        chat_service=mock_chat_service,
        stream_chat_response=stream_chat_response,
        extract_meta=extract_meta,
        strip_fallback_prefix=strip_fallback,
        get_timestamp=get_timestamp,
        model_registry=registry,
        set_active_model=set_active,
    )
    # Register new split blueprints
    health_blueprint = create_health_blueprint(context)
    chat_blueprint = create_chat_blueprint(context)
    app.register_blueprint(health_blueprint, url_prefix="/api")
    app.register_blueprint(chat_blueprint, url_prefix="/api")
    return app, agent, stream_calls, registry, active_calls, mock_chat_service


def test_health_check_returns_healthy_status():
    app, _, _, _, _, _ = _make_test_app()
    client = app.test_client()

    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "healthy"


def test_chat_endpoint_returns_processed_payload():
    app, agent, stream_calls, _, _, mock_chat_service = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={"message": "Hello world"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["response"] == "cleaned"
    assert payload["provider"] == "provider"
    assert payload["model"] == "model"
    assert payload["fallback"] is False
    assert payload["timestamp"] == "2024-01-01T00:00:00Z"
    mock_chat_service.process_chat_query.assert_called_once_with("Hello world", provider_override=None, conversation_id=None)
    assert stream_calls == []


def test_chat_endpoint_streaming_branch():
    app, agent, stream_calls, _, _, _ = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={"message": "Stream this", "stream": True})

    assert response.status_code == 200
    response.direct_passthrough = False
    body = response.get_data(as_text=True)
    assert "data: test-chunk" in body
    assert response.mimetype == "text/event-stream"
    assert response.headers["Cache-Control"] == "no-cache"
    assert response.headers["Connection"] == "keep-alive"
    assert response.headers["Access-Control-Allow-Origin"] == "*"
    assert stream_calls == [("Stream this", None, None)]
    assert agent.calls == []


# ---------------------------------------------------------------------------
# Management blueprint registration (T047)
# ---------------------------------------------------------------------------


def test_default_route_factories_include_management_blueprints():
    """DEFAULT_HTTP_ROUTE_FACTORIES includes workspace, session, conversation blueprints."""
    from web.api_server import DEFAULT_HTTP_ROUTE_FACTORIES
    from web.routes.workspace_routes import create_workspace_blueprint
    from web.routes.session_routes import create_session_blueprint
    from web.routes.conversation_routes import create_conversation_blueprint

    factory_set = set(DEFAULT_HTTP_ROUTE_FACTORIES)
    assert create_workspace_blueprint in factory_set
    assert create_session_blueprint in factory_set
    assert create_conversation_blueprint in factory_set


def test_management_blueprints_register_without_error():
    """Management blueprints can be registered alongside health/chat."""
    from unittest.mock import MagicMock

    app = Flask("test_blueprint_reg")
    app.config["TESTING"] = True

    service_factory = MagicMock()
    service_factory.get_workspace_service.return_value = MagicMock()
    service_factory.get_session_service.return_value = MagicMock()
    service_factory.get_conversation_service.return_value = MagicMock()

    context = APIRouteContext(
        app=app,
        agent=DummyAgent(),
        config={},
        logger=logging.getLogger("test-reg"),
        service_factory=service_factory,
    )

    from web.routes.workspace_routes import create_workspace_blueprint
    from web.routes.session_routes import create_session_blueprint
    from web.routes.conversation_routes import create_conversation_blueprint

    # All three register without raising
    app.register_blueprint(create_health_blueprint(context), url_prefix="/api")
    app.register_blueprint(create_workspace_blueprint(context), url_prefix="/api")
    app.register_blueprint(create_session_blueprint(context), url_prefix="/api")
    app.register_blueprint(create_conversation_blueprint(context), url_prefix="/api")

    # Verify key management routes exist in the url map
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/api/workspaces" in rules
    assert "/api/workspaces/<workspace_id>" in rules
    assert "/api/sessions/<session_id>" in rules
    assert "/api/conversations/<conversation_id>" in rules


def test_management_endpoint_returns_503_without_service_factory(management_headers):
    """Management endpoints return 503 when service_factory is None."""
    from web.routes.workspace_routes import create_workspace_blueprint

    app = Flask("test_no_factory")
    app.config["TESTING"] = True

    context = APIRouteContext(
        app=app,
        agent=DummyAgent(),
        config={},
        logger=logging.getLogger("test-no-factory"),
        service_factory=None,
    )

    app.register_blueprint(create_workspace_blueprint(context), url_prefix="/api")
    client = app.test_client()

    resp = client.get("/api/workspaces", headers=management_headers)
    assert resp.status_code == 503


# Model management tests have been moved to their own test file since
# model endpoints are now handled by models_routes.py to avoid duplication

