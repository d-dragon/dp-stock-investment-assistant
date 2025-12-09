"""Unit tests for AI chat routes."""

import logging
from flask import Flask

from web.routes.shared_context import APIRouteContext
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


def _make_test_app():
    """Create Flask app with chat blueprint for testing."""
    app = Flask("test_chat_routes")
    agent = DummyAgent()
    stream_calls = []

    def stream_chat_response(message, provider_override):
        stream_calls.append((message, provider_override))
        yield "data: test-chunk\n\n"

    def extract_meta(raw):
        return ("provider", "model", False)

    def strip_fallback(raw):
        return "cleaned"

    def get_timestamp():
        return "2024-01-01T00:00:00Z"

    context = APIRouteContext(
        app=app,
        agent=agent,
        config={"model_provider": "openai", "openai": {"model": "gpt-4"}},
        logger=logging.getLogger("test-chat-routes"),
        stream_chat_response=stream_chat_response,
        extract_meta=extract_meta,
        strip_fallback_prefix=strip_fallback,
        get_timestamp=get_timestamp,
    )
    
    blueprint = create_chat_blueprint(context)
    app.register_blueprint(blueprint, url_prefix="/api")
    
    return app, agent, stream_calls


def test_chat_endpoint_returns_200_for_valid_message():
    """Test chat endpoint returns 200 with valid payload."""
    app, agent, _ = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={"message": "Hello world"})

    assert response.status_code == 200


def test_chat_endpoint_returns_processed_payload():
    """Test chat endpoint processes message and returns expected fields."""
    app, agent, stream_calls = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={"message": "Hello world"})

    payload = response.get_json()
    assert payload["response"] == "cleaned"
    assert payload["provider"] == "provider"
    assert payload["model"] == "model"
    assert payload["fallback"] is False
    assert payload["timestamp"] == "2024-01-01T00:00:00Z"
    assert agent.calls == [("Hello world", None)]
    assert stream_calls == []


def test_chat_endpoint_passes_provider_override():
    """Test chat endpoint respects provider parameter."""
    app, agent, _ = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={"message": "Test", "provider": "grok"})

    assert response.status_code == 200
    assert agent.calls == [("Test", "grok")]


def test_chat_endpoint_streaming_branch():
    """Test chat endpoint supports streaming responses via SSE."""
    app, agent, stream_calls = _make_test_app()
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


def test_chat_endpoint_returns_400_on_missing_message():
    """Test chat endpoint validates required message field."""
    app, _, _ = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={})

    assert response.status_code == 400
    payload = response.get_json()
    assert "error" in payload


def test_config_endpoint_returns_safe_config():
    """Test config endpoint returns configuration without secrets."""
    app, _, _ = _make_test_app()
    client = app.test_client()

    response = client.get("/api/config")

    assert response.status_code == 200
    payload = response.get_json()
    assert "model" in payload
    assert "features" in payload


def test_config_endpoint_returns_correct_defaults():
    """Test config endpoint extracts correct default values from config."""
    app, _, _ = _make_test_app()
    client = app.test_client()

    response = client.get("/api/config")
    payload = response.get_json()

    assert payload["model"]["provider"] == "openai"
    assert payload["model"]["name"] == "gpt-4"


def test_config_endpoint_content_type_is_json():
    """Test config endpoint returns JSON content type."""
    app, _, _ = _make_test_app()
    client = app.test_client()

    response = client.get("/api/config")

    assert response.content_type == "application/json"
