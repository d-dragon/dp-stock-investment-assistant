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


# =============================================================================
# US5 — Archived Conversation Rejection at Route Level (T031)
# =============================================================================


def _make_test_app_with_archive_rejection():
    """Create Flask app whose chat_service raises ArchivedConversationError."""
    from services.exceptions import ArchivedConversationError

    app = Flask("test_chat_routes_archive")
    agent = DummyAgent()

    mock_chat_service = MagicMock()
    mock_chat_service.process_chat_query.side_effect = ArchivedConversationError(
        "550e8400-e29b-41d4-a716-446655440000"
    )
    mock_chat_service.stream_chat_response.side_effect = ArchivedConversationError(
        "550e8400-e29b-41d4-a716-446655440000"
    )
    mock_chat_service.extract_meta = lambda raw: ("provider", "model", False)
    mock_chat_service.strip_fallback_prefix = lambda raw: raw
    mock_chat_service.get_timestamp = lambda: "2024-01-01T00:00:00Z"

    context = APIRouteContext(
        app=app,
        agent=agent,
        config={"model_provider": "openai", "openai": {"model": "gpt-4"}},
        logger=logging.getLogger("test-archive-routes"),
        chat_service=mock_chat_service,
        stream_chat_response=mock_chat_service.stream_chat_response,
        extract_meta=mock_chat_service.extract_meta,
        strip_fallback_prefix=mock_chat_service.strip_fallback_prefix,
        get_timestamp=mock_chat_service.get_timestamp,
    )

    blueprint = create_chat_blueprint(context)
    app.register_blueprint(blueprint, url_prefix="/api")
    return app


class TestChatRouteArchivedConversationRejection:
    """Route-level tests for archived conversation 409 CONFLICT response."""

    def test_chat_endpoint_rejects_archived_conversation_with_409(self):
        """POST /api/chat with archived conversation_id returns 409."""
        app = _make_test_app_with_archive_rejection()
        client = app.test_client()

        response = client.post("/api/chat", json={
            "message": "Hello",
            "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
        })

        assert response.status_code == 409
        payload = response.get_json()
        assert "error" in payload
        assert payload.get("code") == "CONVERSATION_ARCHIVED"
        assert payload.get("conversation_id") == "550e8400-e29b-41d4-a716-446655440000"

    def test_chat_endpoint_409_has_correct_error_envelope(self):
        """Verify the 409 error response matches the standard error envelope."""
        app = _make_test_app_with_archive_rejection()
        client = app.test_client()

        response = client.post("/api/chat", json={
            "message": "Hello",
            "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
        })

        assert response.status_code == 409
        payload = response.get_json()
        assert "error" in payload
        assert isinstance(payload["error"], str)
        assert len(payload["error"]) > 0


# =============================================================================
# STM Conversation Isolation at Route Level (T046 / US8)
# Verifies conversation_id propagation and isolation through the chat API
# =============================================================================


class TestChatRouteSTMIsolation:
    """Route-level tests for conversation_id == thread_id STM isolation model.

    Verifies that the chat API properly propagates conversation_id to
    underlying services and maintains isolation between conversations.
    """

    def test_conversation_id_propagated_to_chat_service(self):
        """POST /api/chat with conversation_id passes it to chat_service."""
        app, agent, _, mock_chat_service = _make_test_app()
        client = app.test_client()

        cid = "550e8400-e29b-41d4-a716-446655440000"
        response = client.post("/api/chat", json={
            "message": "Hello",
            "conversation_id": cid,
        })

        assert response.status_code == 200
        mock_chat_service.process_chat_query.assert_called_once_with(
            "Hello", provider_override=None, conversation_id=cid
        )

    def test_different_conversation_ids_isolated_in_service_calls(self):
        """Two requests with different conversation_ids produce separate service calls."""
        app, agent, _, mock_chat_service = _make_test_app()
        client = app.test_client()

        cid_a = "550e8400-e29b-41d4-a716-446655440000"
        cid_b = "660f9500-f39c-41e5-a827-557766551111"

        resp_a = client.post("/api/chat", json={"message": "Q1", "conversation_id": cid_a})
        assert resp_a.status_code == 200

        resp_b = client.post("/api/chat", json={"message": "Q2", "conversation_id": cid_b})
        assert resp_b.status_code == 200

        calls = mock_chat_service.process_chat_query.call_args_list
        assert len(calls) == 2
        # First call with cid_a
        assert calls[0] == (("Q1",), {"provider_override": None, "conversation_id": cid_a})
        # Second call with cid_b (cross-conversation isolation)
        assert calls[1] == (("Q2",), {"provider_override": None, "conversation_id": cid_b})

    def test_streaming_propagates_conversation_id(self):
        """Streaming chat with conversation_id passes it through to stream function."""
        app, agent, stream_calls, _ = _make_test_app()
        client = app.test_client()

        cid = "550e8400-e29b-41d4-a716-446655440000"
        response = client.post("/api/chat", json={
            "message": "Stream this",
            "stream": True,
            "conversation_id": cid,
        })

        assert response.status_code == 200
        # stream_calls records (message, provider_override, conversation_id)
        assert len(stream_calls) == 1
        assert stream_calls[0] == ("Stream this", None, cid)

    def test_stateless_mode_no_conversation_id_in_service(self):
        """POST /api/chat without conversation_id passes None (stateless mode)."""
        app, agent, _, mock_chat_service = _make_test_app()
        client = app.test_client()

        response = client.post("/api/chat", json={"message": "Stateless query"})

        assert response.status_code == 200
        mock_chat_service.process_chat_query.assert_called_once_with(
            "Stateless query", provider_override=None, conversation_id=None
        )

    def test_same_conversation_id_across_turns_preserves_binding(self):
        """Two sequential requests with same conversation_id maintain checkpoint binding."""
        app, agent, _, mock_chat_service = _make_test_app()
        client = app.test_client()

        cid = "550e8400-e29b-41d4-a716-446655440000"

        client.post("/api/chat", json={"message": "Turn 1", "conversation_id": cid})
        client.post("/api/chat", json={"message": "Turn 2", "conversation_id": cid})

        calls = mock_chat_service.process_chat_query.call_args_list
        assert len(calls) == 2
        # Both turns use the same conversation_id
        call_1_cid = calls[0][1].get('conversation_id') if len(calls[0]) > 1 else calls[0].kwargs.get('conversation_id')
        call_2_cid = calls[1][1].get('conversation_id') if len(calls[1]) > 1 else calls[1].kwargs.get('conversation_id')
        assert call_1_cid == call_2_cid == cid
