"""Unit tests for the HTTP API blueprint."""

import logging
from flask import Flask

from web.routes.api_routes import APIRouteContext, create_api_blueprint


class DummyAgent:
    """Record-only agent stub used in route tests."""

    def __init__(self):
        self.calls = []

    def _process_query(self, message, provider=None):
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

    def stream_chat_response(message, provider_override):
        stream_calls.append((message, provider_override))
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

    context = APIRouteContext(
        app=app,
        agent=agent,
        config={},
        logger=logging.getLogger("test-api-routes"),
        stream_chat_response=stream_chat_response,
        extract_meta=extract_meta,
        strip_fallback_prefix=strip_fallback,
        get_timestamp=get_timestamp,
        model_registry=registry,
        set_active_model=set_active,
    )
    blueprint = create_api_blueprint(context)
    app.register_blueprint(blueprint, url_prefix="/api")
    return app, agent, stream_calls, registry, active_calls


def test_health_check_returns_healthy_status():
    app, _, _, _, _ = _make_test_app()
    client = app.test_client()

    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "healthy"


def test_chat_endpoint_returns_processed_payload():
    app, agent, stream_calls, _, _ = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={"message": "Hello world"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["response"] == "cleaned"
    assert payload["provider"] == "provider"
    assert payload["model"] == "model"
    assert payload["fallback"] is False
    assert payload["timestamp"] == "2024-01-01T00:00:00Z"
    assert agent.calls == [("Hello world", None)]
    assert stream_calls == []


def test_chat_endpoint_streaming_branch():
    app, agent, stream_calls, _, _ = _make_test_app()
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
    assert stream_calls == [("Stream this", None)]
    assert agent.calls == []


def test_get_openai_models_returns_cached_list():
    app, _, _, registry, _ = _make_test_app()
    client = app.test_client()

    response = client.get("/api/models/openai")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["source"] == "cache"
    assert payload["models"] == registry.models


def test_get_openai_models_with_refresh_param_forces_live_fetch():
    app, _, _, registry, _ = _make_test_app()
    client = app.test_client()

    response = client.get("/api/models/openai?refresh=true")

    assert response.status_code == 200
    assert registry.get_calls[-1] is True
    payload = response.get_json()
    assert payload["source"] == "live"


def test_set_openai_default_model_updates_registry_and_agent():
    app, _, _, registry, active_calls = _make_test_app()
    client = app.test_client()

    response = client.put("/api/models/openai/default", json={"model": "gpt-4o"})

    assert response.status_code == 200
    assert active_calls == [("openai", "gpt-4o")]
    data = response.get_json()
    assert data["model"] == "gpt-4o"
    assert registry.active_model == "gpt-4o"


def test_set_openai_default_model_rejects_unsupported_model():
    registry = DummyRegistry()
    app, _, _, registry, active_calls = _make_test_app(registry=registry)
    registry.models = [{"id": "gpt-4", "created": 1}]
    client = app.test_client()

    response = client.put("/api/models/openai/default", json={"model": "unknown"})

    assert response.status_code == 400

def test_refresh_openai_models_endpoint_forces_refresh():
    app, _, _, registry, active_calls = _make_test_app()
    client = app.test_client()

    response = client.post("/api/models/openai/refresh")

    assert response.status_code == 200
    assert registry.refreshed is True
    assert active_calls == []

