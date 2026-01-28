"""
API tests for session-aware chat endpoints.

Tests POST /api/chat with session_id parameter per FR-3.1 requirements.

Reference: specs/spec-driven-development-pilot/spec.md
"""

import logging
import uuid
from flask import Flask
from unittest.mock import MagicMock

from web.routes.shared_context import APIRouteContext
from web.routes.ai_chat_routes import create_chat_blueprint


# ============================================================================
# TEST FIXTURES
# ============================================================================

def _make_test_app():
    """Create Flask app with chat blueprint for testing."""
    app = Flask("test_chat_routes_memory")
    
    # Create mock agent
    mock_agent = MagicMock()
    mock_agent.process_query.return_value = "RAW RESPONSE"
    mock_agent.process_query_streaming.return_value = iter(["chunk-1", "chunk-2"])
    
    stream_calls = []

    def stream_chat_response(message, provider_override=None, session_id=None):
        stream_calls.append((message, provider_override, session_id))
        yield "data: test-chunk\n\n"

    def extract_meta(raw):
        return ("openai", "gpt-4", False)

    def strip_fallback(raw):
        return "cleaned response"

    def get_timestamp():
        return "2024-01-01T00:00:00Z"

    # Create mock chat_service
    mock_chat_service = MagicMock()
    mock_chat_service.process_chat_query.return_value = {
        "response": "cleaned response",
        "provider": "openai",
        "model": "gpt-4",
        "fallback": False,
        "timestamp": "2024-01-01T00:00:00Z"
    }
    mock_chat_service.stream_chat_response = stream_chat_response
    mock_chat_service.extract_meta = extract_meta
    mock_chat_service.strip_fallback_prefix = strip_fallback
    mock_chat_service.get_timestamp = get_timestamp

    context = APIRouteContext(
        app=app,
        agent=mock_agent,
        config={"model_provider": "openai", "openai": {"model": "gpt-4"}},
        logger=logging.getLogger("test-chat-routes-memory"),
        chat_service=mock_chat_service,
        stream_chat_response=stream_chat_response,
        extract_meta=extract_meta,
        strip_fallback_prefix=strip_fallback,
        get_timestamp=get_timestamp,
    )
    
    blueprint = create_chat_blueprint(context)
    app.register_blueprint(blueprint, url_prefix="/api")
    
    return app, mock_agent, stream_calls, mock_chat_service


def generate_valid_session_id():
    """Generate a valid UUID v4 session_id."""
    return str(uuid.uuid4())


# ============================================================================
# TESTS: VALID SESSION_ID
# ============================================================================

def test_chat_with_valid_session_id_returns_200():
    """Test POST /api/chat with valid session_id returns 200."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()
    session_id = generate_valid_session_id()

    response = client.post("/api/chat", json={
        "message": "Hello",
        "session_id": session_id
    })

    assert response.status_code == 200


def test_chat_response_includes_echoed_session_id():
    """Test response includes echoed session_id when provided."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()
    session_id = generate_valid_session_id()

    response = client.post("/api/chat", json={
        "message": "Hello",
        "session_id": session_id
    })

    payload = response.get_json()
    assert "session_id" in payload
    assert payload["session_id"] == session_id


def test_chat_passes_session_id_to_chat_service():
    """Test chat endpoint passes session_id to chat_service.process_chat_query."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()
    session_id = generate_valid_session_id()

    response = client.post("/api/chat", json={
        "message": "Test message",
        "session_id": session_id
    })

    assert response.status_code == 200
    # Verify session_id passed to chat_service
    mock_chat_service.process_chat_query.assert_called_once_with(
        "Test message",
        provider_override=None,
        session_id=session_id
    )


def test_chat_without_session_id_still_works():
    """Test POST /api/chat works without session_id (backward compatibility)."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={
        "message": "Hello"
    })

    assert response.status_code == 200
    payload = response.get_json()
    # session_id should NOT be in response when not provided
    assert "session_id" not in payload


def test_chat_without_session_id_passes_none_to_service():
    """Test chat passes None for session_id when not provided."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={
        "message": "Test"
    })

    assert response.status_code == 200
    mock_chat_service.process_chat_query.assert_called_once_with(
        "Test",
        provider_override=None,
        session_id=None
    )


# ============================================================================
# TESTS: INVALID SESSION_ID FORMAT
# ============================================================================

def test_chat_with_invalid_session_id_returns_400():
    """Test POST /api/chat with invalid session_id format returns 400."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={
        "message": "Hello",
        "session_id": "not-a-valid-uuid"
    })

    assert response.status_code == 400
    payload = response.get_json()
    assert "error" in payload
    assert "session_id" in payload["error"].lower() or "uuid" in payload["error"].lower()


def test_chat_with_uuid_v1_returns_400():
    """Test POST /api/chat rejects UUID v1 (only v4 allowed)."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()
    # UUID v1 has version bits different from v4
    uuid_v1 = str(uuid.uuid1())

    response = client.post("/api/chat", json={
        "message": "Hello",
        "session_id": uuid_v1
    })

    # UUID v1 should be rejected because we only accept v4
    assert response.status_code == 400


def test_chat_with_empty_session_id_returns_400():
    """Test POST /api/chat with empty string session_id returns 400."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={
        "message": "Hello",
        "session_id": ""
    })

    assert response.status_code == 400


def test_chat_with_numeric_session_id_returns_400():
    """Test POST /api/chat with numeric session_id returns 400."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={
        "message": "Hello",
        "session_id": 12345
    })

    assert response.status_code == 400


def test_chat_with_null_session_id_treated_as_not_provided():
    """Test POST /api/chat with null session_id works (treated as None)."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={
        "message": "Hello",
        "session_id": None
    })

    # null is treated as not provided, should succeed
    assert response.status_code == 200
    payload = response.get_json()
    # session_id should NOT be in response when None
    assert "session_id" not in payload


# ============================================================================
# TESTS: SESSION_ID WITH STREAMING
# ============================================================================

def test_streaming_chat_accepts_session_id():
    """Test streaming mode accepts session_id."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()
    session_id = generate_valid_session_id()

    # Use stream: true parameter to trigger streaming mode
    response = client.post("/api/chat", json={
        "message": "Hello",
        "session_id": session_id,
        "stream": True
    })

    assert response.status_code == 200
    # Verify session_id was passed to stream_chat_response
    assert len(stream_calls) == 1
    assert stream_calls[0][2] == session_id  # Third element is session_id


def test_streaming_chat_with_invalid_session_id_returns_400():
    """Test streaming mode rejects invalid session_id."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={
        "message": "Hello",
        "session_id": "invalid-uuid",
        "stream": True
    })

    assert response.status_code == 400


# ============================================================================
# TESTS: SESSION_ID WITH PROVIDER OVERRIDE
# ============================================================================

def test_chat_with_session_id_and_provider_override():
    """Test POST /api/chat with both session_id and provider works."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()
    session_id = generate_valid_session_id()

    response = client.post("/api/chat", json={
        "message": "Hello",
        "provider": "grok",
        "session_id": session_id
    })

    assert response.status_code == 200
    mock_chat_service.process_chat_query.assert_called_once_with(
        "Hello",
        provider_override="grok",
        session_id=session_id
    )


# ============================================================================
# TESTS: MULTI-TURN CONVERSATION (API LEVEL)
# ============================================================================

def test_multiple_requests_with_same_session_id():
    """Test multiple API requests with same session_id use consistent config."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()
    session_id = generate_valid_session_id()

    # First request
    response1 = client.post("/api/chat", json={
        "message": "My name is Alice",
        "session_id": session_id
    })
    assert response1.status_code == 200

    # Second request with same session_id
    response2 = client.post("/api/chat", json={
        "message": "What is my name?",
        "session_id": session_id
    })
    assert response2.status_code == 200

    # Both should have passed the same session_id
    calls = mock_chat_service.process_chat_query.call_args_list
    assert len(calls) == 2
    assert calls[0][1]['session_id'] == session_id
    assert calls[1][1]['session_id'] == session_id


def test_requests_with_different_session_ids():
    """Test requests with different session_ids use different configs."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()
    session_id_1 = generate_valid_session_id()
    session_id_2 = generate_valid_session_id()

    # Request with session 1
    response1 = client.post("/api/chat", json={
        "message": "Hello from session 1",
        "session_id": session_id_1
    })

    # Request with session 2
    response2 = client.post("/api/chat", json={
        "message": "Hello from session 2",
        "session_id": session_id_2
    })

    assert response1.status_code == 200
    assert response2.status_code == 200

    calls = mock_chat_service.process_chat_query.call_args_list
    assert len(calls) == 2
    assert calls[0][1]['session_id'] == session_id_1
    assert calls[1][1]['session_id'] == session_id_2
    assert session_id_1 != session_id_2
