"""Unit tests for the HTTP API blueprint."""

import logging
from flask import Flask

from web.routes.api_routes import APIRouteContext, create_api_blueprint


class DummyAgent:
    """Record-only agent stub used in route tests."""

    def __init__(self):
        self.calls = []

    def process_query(self, message, provider=None):
        self.calls.append((message, provider))
        return "RAW RESPONSE"


def _make_test_app():
    app = Flask("test_api_routes")
    agent = DummyAgent()
    stream_calls = []

    def stream_chat_response(message, provider_override):
        stream_calls.append((message, provider_override))
        yield "data: test-chunk\n\n"

    context = APIRouteContext(
        app=app,
        agent=agent,
        config={},
        logger=logging.getLogger("test-api-routes"),
        stream_chat_response=stream_chat_response,
        extract_meta=lambda raw: ("provider", "model", False),
        strip_fallback_prefix=lambda raw: "cleaned",
        get_timestamp=lambda: "2024-01-01T00:00:00Z",
    )
    blueprint = create_api_blueprint(context)
    app.register_blueprint(blueprint, url_prefix="/api")
    return app, agent, stream_calls


def test_health_check_returns_healthy_status():
    app, _, _ = _make_test_app()
    client = app.test_client()

    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "healthy"


def test_chat_endpoint_returns_processed_payload():
    app, agent, stream_calls = _make_test_app()
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
