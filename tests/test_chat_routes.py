"""Unit tests for AI chat routes."""

import logging
from flask import Flask
from unittest.mock import MagicMock

from web.routes.shared_context import APIRouteContext
from web.routes.ai_chat_routes import create_chat_blueprint


class DummyAgent:
    """Record-only agent stub used in route tests."""

    def __init__(self):
        self.calls = []

    def process_query(self, message, provider=None, conversation_id=None):
        """Public method that matches actual agent interface."""
        self.calls.append((message, provider))
        return "RAW RESPONSE"

    def process_query_streaming(self, message, provider=None, conversation_id=None):
        yield from ["chunk-1", "chunk-2"]


def _make_test_app():
    """Create Flask app with chat blueprint for testing."""
    app = Flask("test_chat_routes")
    agent = DummyAgent()
    stream_calls = []

    def stream_chat_response(message, provider_override=None, conversation_id=None):
        stream_calls.append((message, provider_override, conversation_id))
        yield "data: test-chunk\n\n"

    def extract_meta(raw):
        return ("provider", "model", False)

    def strip_fallback(raw):
        return "cleaned"

    def get_timestamp():
        return "2024-01-01T00:00:00Z"

    # Create mock chat_service for non-streaming tests
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
        config={"model_provider": "openai", "openai": {"model": "gpt-4"}},
        logger=logging.getLogger("test-chat-routes"),
        chat_service=mock_chat_service,
        stream_chat_response=stream_chat_response,
        extract_meta=extract_meta,
        strip_fallback_prefix=strip_fallback,
        get_timestamp=get_timestamp,
    )
    
    blueprint = create_chat_blueprint(context)
    app.register_blueprint(blueprint, url_prefix="/api")
    
    return app, agent, stream_calls, mock_chat_service


def test_chat_endpoint_returns_200_for_valid_message():
    """Test chat endpoint returns 200 with valid payload."""
    app, agent, _, _ = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={"message": "Hello world"})

    assert response.status_code == 200


def test_chat_endpoint_returns_processed_payload():
    """Test chat endpoint processes message and returns expected fields."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={"message": "Hello world"})

    payload = response.get_json()
    assert payload["response"] == "cleaned"
    assert payload["provider"] == "provider"
    assert payload["model"] == "model"
    assert payload["fallback"] is False
    assert payload["timestamp"] == "2024-01-01T00:00:00Z"
    # Now uses chat_service.process_chat_query instead of direct agent.process_query
    mock_chat_service.process_chat_query.assert_called_once_with("Hello world", provider_override=None, conversation_id=None)
    assert stream_calls == []


def test_chat_endpoint_passes_provider_override():
    """Test chat endpoint respects provider parameter."""
    app, agent, _, mock_chat_service = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={"message": "Test", "provider": "grok"})

    assert response.status_code == 200
    # Now uses chat_service.process_chat_query instead of direct agent.process_query
    mock_chat_service.process_chat_query.assert_called_once_with("Test", provider_override="grok", conversation_id=None)


def test_chat_endpoint_streaming_branch():
    """Test chat endpoint supports streaming responses via SSE."""
    app, agent, stream_calls, _ = _make_test_app()
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
    # stream_calls now includes conversation_id as 3rd element (None when not provided)
    assert stream_calls == [("Stream this", None, None)]
    assert agent.calls == []


def test_chat_endpoint_returns_400_on_missing_message():
    """Test chat endpoint validates required message field."""
    app, _, _, _ = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={})

    assert response.status_code == 400
    payload = response.get_json()
    assert "error" in payload


def test_config_endpoint_returns_safe_config():
    """Test config endpoint returns configuration without secrets."""
    app, _, _, _ = _make_test_app()
    client = app.test_client()

    response = client.get("/api/config")

    assert response.status_code == 200
    payload = response.get_json()
    assert "model" in payload
    assert "features" in payload


def test_config_endpoint_returns_correct_defaults():
    """Test config endpoint extracts correct default values from config."""
    app, _, _, _ = _make_test_app()
    client = app.test_client()

    response = client.get("/api/config")
    payload = response.get_json()

    assert payload["model"]["provider"] == "openai"
    assert payload["model"]["name"] == "gpt-4"


def test_config_endpoint_content_type_is_json():
    """Test config endpoint returns JSON content type."""
    app, _, _, _ = _make_test_app()
    client = app.test_client()

    response = client.get("/api/config")

    assert response.content_type == "application/json"


# =============================================================================
# FR-3.1.6 Backward Compatibility Tests (T025)
# Tests that API works correctly without conversation_id for stateless fallback
# =============================================================================


class TestChatBackwardCompatibility:
    """Tests for backward compatibility when conversation_id is not provided.
    
    Verifies FR-3.1.6: Stateless fallback mode - API continues to work
    without session management for backward compatibility.
    """

    def test_chat_without_conversation_id_returns_200(self):
        """Test: POST /api/chat without conversation_id field returns 200.
        
        Backward compatibility: Existing clients that don't send conversation_id
        should continue to work without any changes.
        """
        app, agent, _, mock_chat_service = _make_test_app()
        client = app.test_client()

        # Request without conversation_id - this is the backward-compatible case
        response = client.post("/api/chat", json={"message": "Test message"})

        assert response.status_code == 200
        payload = response.get_json()
        assert "response" in payload
        assert payload["response"] == "cleaned"

    def test_chat_without_conversation_id_omits_conversation_id_in_response(self):
        """Test: Response omits conversation_id when not provided in request.
        
        When no conversation_id is provided, the response should not include
        the conversation_id field at all (not even as null) for backward
        compatibility with clients not expecting this field.
        """
        app, agent, _, mock_chat_service = _make_test_app()
        client = app.test_client()

        response = client.post("/api/chat", json={"message": "Test message"})

        assert response.status_code == 200
        payload = response.get_json()
        # conversation_id should NOT be in the response when not provided
        assert "conversation_id" not in payload

    def test_chat_with_conversation_id_includes_it_in_response(self):
        """Test: Response includes conversation_id when provided in request.
        
        When conversation_id IS provided, it should be echoed back in response.
        """
        app, agent, _, mock_chat_service = _make_test_app()
        client = app.test_client()

        test_conversation_id = "550e8400-e29b-41d4-a716-446655440000"
        response = client.post("/api/chat", json={
            "message": "Test message",
            "conversation_id": test_conversation_id
        })

        assert response.status_code == 200
        payload = response.get_json()
        assert "conversation_id" in payload
        assert payload["conversation_id"] == test_conversation_id

    def test_chat_validates_conversation_id_format_when_provided(self):
        """Test: Invalid conversation_id format returns 400 error.
        
        If conversation_id is provided but not a valid UUID v4, reject it.
        """
        app, agent, _, mock_chat_service = _make_test_app()
        client = app.test_client()

        # Invalid conversation_id (not a valid UUID)
        response = client.post("/api/chat", json={
            "message": "Test message",
            "conversation_id": "invalid-conversation-id"
        })

        assert response.status_code == 400
        payload = response.get_json()
        assert "error" in payload

    def test_chat_accepts_null_conversation_id_as_stateless(self):
        """Test: Explicit null conversation_id is treated as stateless.
        
        Clients can explicitly send conversation_id: null to indicate
        they want stateless behavior.
        """
        app, agent, _, mock_chat_service = _make_test_app()
        client = app.test_client()

        # Explicit null conversation_id
        response = client.post("/api/chat", json={
            "message": "Test message",
            "conversation_id": None
        })

        assert response.status_code == 200
        payload = response.get_json()
        # conversation_id should NOT be in the response when null
        assert "conversation_id" not in payload
