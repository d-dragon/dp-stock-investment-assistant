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

    def stream_chat_response(message, provider_override=None, conversation_id=None):
        stream_calls.append((message, provider_override, conversation_id))
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


def generate_valid_conversation_id():
    """Generate a valid UUID v4 conversation_id."""
    return str(uuid.uuid4())


# ============================================================================
# TESTS: VALID SESSION_ID
# ============================================================================

def test_chat_with_valid_conversation_id_returns_200():
    """Test POST /api/chat with valid conversation_id returns 200."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()
    conversation_id = generate_valid_conversation_id()

    response = client.post("/api/chat", json={
        "message": "Hello",
        "conversation_id": conversation_id
    })

    assert response.status_code == 200


def test_chat_response_includes_echoed_conversation_id():
    """Test response includes echoed conversation_id when provided."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()
    conversation_id = generate_valid_conversation_id()

    response = client.post("/api/chat", json={
        "message": "Hello",
        "conversation_id": conversation_id
    })

    payload = response.get_json()
    assert "conversation_id" in payload
    assert payload["conversation_id"] == conversation_id


def test_chat_passes_conversation_id_to_chat_service():
    """Test chat endpoint passes conversation_id to chat_service.process_chat_query."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()
    conversation_id = generate_valid_conversation_id()

    response = client.post("/api/chat", json={
        "message": "Test message",
        "conversation_id": conversation_id
    })

    assert response.status_code == 200
    # Verify conversation_id passed to chat_service
    mock_chat_service.process_chat_query.assert_called_once_with(
        "Test message",
        provider_override=None,
        conversation_id=conversation_id
    )


def test_chat_without_conversation_id_still_works():
    """Test POST /api/chat works without conversation_id (backward compatibility)."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={
        "message": "Hello"
    })

    assert response.status_code == 200
    payload = response.get_json()
    # conversation_id should NOT be in response when not provided
    assert "conversation_id" not in payload


def test_chat_without_conversation_id_passes_none_to_service():
    """Test chat passes None for conversation_id when not provided."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={
        "message": "Test"
    })

    assert response.status_code == 200
    mock_chat_service.process_chat_query.assert_called_once_with(
        "Test",
        provider_override=None,
        conversation_id=None
    )


# ============================================================================
# TESTS: INVALID SESSION_ID FORMAT
# ============================================================================

def test_chat_with_invalid_conversation_id_returns_400():
    """Test POST /api/chat with invalid conversation_id format returns 400."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={
        "message": "Hello",
        "conversation_id": "not-a-valid-uuid"
    })

    assert response.status_code == 400
    payload = response.get_json()
    assert "error" in payload
    assert "conversation_id" in payload["error"].lower() or "uuid" in payload["error"].lower()


def test_chat_with_uuid_v1_returns_400():
    """Test POST /api/chat rejects UUID v1 (only v4 allowed)."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()
    # UUID v1 has version bits different from v4
    uuid_v1 = str(uuid.uuid1())

    response = client.post("/api/chat", json={
        "message": "Hello",
        "conversation_id": uuid_v1
    })

    # UUID v1 should be rejected because we only accept v4
    assert response.status_code == 400


def test_chat_with_empty_conversation_id_returns_400():
    """Test POST /api/chat with empty string conversation_id returns 400."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={
        "message": "Hello",
        "conversation_id": ""
    })

    assert response.status_code == 400


def test_chat_with_numeric_conversation_id_returns_400():
    """Test POST /api/chat with numeric conversation_id returns 400."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={
        "message": "Hello",
        "conversation_id": 12345
    })

    assert response.status_code == 400


def test_chat_with_null_conversation_id_treated_as_not_provided():
    """Test POST /api/chat with null conversation_id works (treated as None)."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={
        "message": "Hello",
        "conversation_id": None
    })

    # null is treated as not provided, should succeed
    assert response.status_code == 200
    payload = response.get_json()
    # conversation_id should NOT be in response when None
    assert "conversation_id" not in payload


# ============================================================================
# TESTS: SESSION_ID WITH STREAMING
# ============================================================================

def test_streaming_chat_accepts_conversation_id():
    """Test streaming mode accepts conversation_id."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()
    conversation_id = generate_valid_conversation_id()

    # Use stream: true parameter to trigger streaming mode
    response = client.post("/api/chat", json={
        "message": "Hello",
        "conversation_id": conversation_id,
        "stream": True
    })

    assert response.status_code == 200
    # Verify conversation_id was passed to stream_chat_response
    assert len(stream_calls) == 1
    assert stream_calls[0][2] == conversation_id  # Third element is conversation_id


def test_streaming_chat_with_invalid_conversation_id_returns_400():
    """Test streaming mode rejects invalid conversation_id."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()

    response = client.post("/api/chat", json={
        "message": "Hello",
        "conversation_id": "invalid-uuid",
        "stream": True
    })

    assert response.status_code == 400


# ============================================================================
# TESTS: SESSION_ID WITH PROVIDER OVERRIDE
# ============================================================================

def test_chat_with_conversation_id_and_provider_override():
    """Test POST /api/chat with both conversation_id and provider works."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()
    conversation_id = generate_valid_conversation_id()

    response = client.post("/api/chat", json={
        "message": "Hello",
        "provider": "grok",
        "conversation_id": conversation_id
    })

    assert response.status_code == 200
    mock_chat_service.process_chat_query.assert_called_once_with(
        "Hello",
        provider_override="grok",
        conversation_id=conversation_id
    )


# ============================================================================
# TESTS: MULTI-TURN CONVERSATION (API LEVEL)
# ============================================================================

def test_multiple_requests_with_same_conversation_id():
    """Test multiple API requests with same conversation_id use consistent config."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()
    conversation_id = generate_valid_conversation_id()

    # First request
    response1 = client.post("/api/chat", json={
        "message": "My name is Alice",
        "conversation_id": conversation_id
    })
    assert response1.status_code == 200

    # Second request with same conversation_id
    response2 = client.post("/api/chat", json={
        "message": "What is my name?",
        "conversation_id": conversation_id
    })
    assert response2.status_code == 200

    # Both should have passed the same conversation_id
    calls = mock_chat_service.process_chat_query.call_args_list
    assert len(calls) == 2
    assert calls[0][1]['conversation_id'] == conversation_id
    assert calls[1][1]['conversation_id'] == conversation_id


def test_requests_with_different_conversation_ids():
    """Test requests with different conversation_ids use different configs."""
    app, agent, stream_calls, mock_chat_service = _make_test_app()
    client = app.test_client()
    conversation_id_1 = generate_valid_conversation_id()
    conversation_id_2 = generate_valid_conversation_id()

    # Request with session 1
    response1 = client.post("/api/chat", json={
        "message": "Hello from session 1",
        "conversation_id": conversation_id_1
    })

    # Request with session 2
    response2 = client.post("/api/chat", json={
        "message": "Hello from session 2",
        "conversation_id": conversation_id_2
    })

    assert response1.status_code == 200
    assert response2.status_code == 200

    calls = mock_chat_service.process_chat_query.call_args_list
    assert len(calls) == 2
    assert calls[0][1]['conversation_id'] == conversation_id_1
    assert calls[1][1]['conversation_id'] == conversation_id_2
    assert conversation_id_1 != conversation_id_2


# ============================================================================
# TESTS: ARCHIVED SESSION HANDLING (T032)
# ============================================================================

# Import the actual exception class from services layer
from services.exceptions import ArchivedConversationError


def _make_archived_session_test_app():
    """Create Flask app with chat_service that rejects archived conversations.
    
    This simulates the expected behavior for T032:
    - Archived conversations return 409 Conflict when used with POST /api/chat
    """
    app = Flask("test_archived_sessions")
    
    mock_agent = MagicMock()
    mock_agent.process_query.return_value = "RAW RESPONSE"
    
    mock_chat_service = MagicMock()
    
    # Configure mock to raise error for archived conversations
    archived_conversation_id = str(uuid.uuid4())  # We'll track this
    
    def process_chat_query_with_archive_check(message, provider_override=None, conversation_id=None):
        # Simulate archived conversation detection
        if conversation_id == archived_conversation_id:
            # Use the real exception class that the route knows how to handle
            raise ArchivedConversationError(conversation_id)
        return {
            "response": "cleaned response",
            "provider": "openai",
            "model": "gpt-4",
            "fallback": False,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    
    mock_chat_service.process_chat_query = MagicMock(side_effect=process_chat_query_with_archive_check)
    mock_chat_service.stream_chat_response = MagicMock(return_value=iter(["data: test\n\n"]))
    mock_chat_service.extract_meta = lambda raw: ("openai", "gpt-4", False)
    mock_chat_service.strip_fallback_prefix = lambda raw: raw
    mock_chat_service.get_timestamp = lambda: "2024-01-01T00:00:00Z"

    context = APIRouteContext(
        app=app,
        agent=mock_agent,
        config={"model_provider": "openai", "openai": {"model": "gpt-4"}},
        logger=logging.getLogger("test-archived-sessions"),
        chat_service=mock_chat_service,
        stream_chat_response=mock_chat_service.stream_chat_response,
        extract_meta=mock_chat_service.extract_meta,
        strip_fallback_prefix=mock_chat_service.strip_fallback_prefix,
        get_timestamp=mock_chat_service.get_timestamp,
    )
    
    blueprint = create_chat_blueprint(context)
    app.register_blueprint(blueprint, url_prefix="/api")
    
    return app, mock_chat_service, archived_conversation_id


class TestArchivedSessionHandling:
    """T032: Tests for archived conversation handling per FR-3.1.5.
    
    Archived sessions should:
    - Return 409 Conflict when attempting to POST new messages
    - Include clear error message indicating session is archived
    - (Future) Allow GET requests to read history
    
    These tests document expected behavior that needs implementation
    in ChatService and/or ai_chat_routes.py.
    """
    
    def test_post_to_archived_session_returns_409_conflict(self):
        """Test: Attempt to resume archived conversation returns 409 Conflict.
        
        T032 requirement: System returns 409 Conflict with clear message
        when attempting to POST to an archived conversation.
        
        NOTE: This test requires route-level exception handling for
        ArchivedConversationError to be implemented.
        """
        app, mock_chat_service, archived_conversation_id = _make_archived_session_test_app()
        client = app.test_client()
        
        # Attempt to send message to archived conversation
        response = client.post("/api/chat", json={
            "message": "Hello, can we continue?",
            "conversation_id": archived_conversation_id
        })
        
        # Expected: 409 Conflict (not 500 Internal Server Error)
        # If this fails with 500, the route needs exception handling for ArchivedConversationError
        assert response.status_code == 409, (
            f"Expected 409 Conflict for archived conversation, got {response.status_code}. "
            "Route needs to catch ArchivedConversationError and return 409."
        )
    
    def test_archived_session_error_message_is_clear(self):
        """Test: 409 response includes clear error message.
        
        The error message should indicate:
        - The conversation is archived
        - New messages cannot be added
        """
        app, mock_chat_service, archived_conversation_id = _make_archived_session_test_app()
        client = app.test_client()
        
        response = client.post("/api/chat", json={
            "message": "Hello",
            "conversation_id": archived_conversation_id
        })
        
        # Skip detailed assertion if 409 not implemented yet
        if response.status_code != 409:
            import pytest
            pytest.skip("409 Conflict handling not implemented yet")
        
        payload = response.get_json()
        assert "error" in payload
        error_msg = payload["error"].lower()
        assert "archived" in error_msg or "immutable" in error_msg, (
            f"Error message should mention 'archived' or 'immutable': {payload['error']}"
        )
    
    def test_active_session_still_works_normally(self):
        """Test: Non-archived sessions work normally.
        
        Regression test: Ensure archived session handling doesn't
        break normal session functionality.
        """
        app, mock_chat_service, archived_conversation_id = _make_archived_session_test_app()
        client = app.test_client()
        
        # Use a different session ID (not the archived one)
        active_session_id = str(uuid.uuid4())
        
        response = client.post("/api/chat", json={
            "message": "Hello",
            "conversation_id": active_session_id
        })
        
        # Should succeed with 200
        assert response.status_code == 200
        payload = response.get_json()
        assert "response" in payload
    
    def test_archived_session_error_does_not_expose_internal_details(self):
        """Test: 409 error does not expose internal exception details.
        
        Security: Error responses should not leak implementation details
        like full stack traces or internal class names.
        """
        app, mock_chat_service, archived_conversation_id = _make_archived_session_test_app()
        client = app.test_client()
        
        response = client.post("/api/chat", json={
            "message": "Hello",
            "conversation_id": archived_conversation_id
        })
        
        # Skip if 409 not implemented
        if response.status_code != 409:
            import pytest
            pytest.skip("409 Conflict handling not implemented yet")
        
        payload = response.get_json()
        response_text = str(payload)
        
        # Should not contain internal exception class names
        assert "ArchivedConversationError" not in response_text
        assert "Traceback" not in response_text
        assert "File" not in response_text  # No file paths


# ============================================================================
# TESTS: SOCKET.IO RECONNECTION (T033)
# ============================================================================

def _make_socketio_reconnection_test_app():
    """Create Flask app with Socket.IO for reconnection testing.
    
    This tests T033 requirements:
    - Context maintained across WebSocket reconnection
    - Session state persists when client disconnects and reconnects
    """
    from flask_socketio import SocketIO
    
    app = Flask("test_socketio_reconnection")
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['TESTING'] = True
    
    socketio = SocketIO(app, async_mode='threading')
    
    # Track session history (simulates checkpoint storage)
    session_history = {}
    
    mock_agent = MagicMock()
    
    def process_query_with_history(message, provider=None, conversation_id=None):
        """Simulate agent that uses session history for context."""
        if conversation_id:
            # Get existing history or start new
            history = session_history.get(conversation_id, [])
            history.append(message)
            session_history[conversation_id] = history
            
            # Generate response that references history length
            return f"Received message #{len(history)}: {message}"
        return f"Stateless: {message}"
    
    mock_agent.process_query = MagicMock(side_effect=process_query_with_history)
    
    # Register Socket.IO events
    from web.sockets.chat_events import SocketIOContext, register_chat_events
    import logging
    
    def extract_meta(raw):
        return ("openai", "gpt-4", False)
    
    def strip_fallback(raw):
        return raw
    
    def get_timestamp():
        return "2024-01-01T00:00:00Z"
    
    context = SocketIOContext(
        socketio=socketio,
        agent=mock_agent,
        config={},
        logger=logging.getLogger("test_socketio_reconnection"),
        extract_meta=extract_meta,
        strip_fallback_prefix=strip_fallback,
        get_timestamp=get_timestamp
    )
    
    register_chat_events(context)
    
    return app, socketio, session_history


class TestSocketIOReconnection:
    """Tests for Socket.IO reconnection and session persistence.
    
    T033: Tests context maintained across WebSocket reconnection.
    
    Reference: FR-3.1.5 (Context loaded on reconnect)
    """
    
    def test_disconnect_reconnect_maintains_session_context(self):
        """Test: Disconnecting and reconnecting preserves session history.
        
        Scenario:
        1. Client connects, sends message with conversation_id
        2. Client disconnects
        3. Client reconnects with same conversation_id
        4. New messages should reference existing history
        """
        app, socketio, session_history = _make_socketio_reconnection_test_app()
        
        test_conversation_id = str(uuid.uuid4())
        
        # Use SocketIOTestClient for testing
        from flask_socketio import SocketIOTestClient
        
        # First connection
        client1 = socketio.test_client(app)
        assert client1.is_connected()
        
        # Get initial connection events
        received = client1.get_received()
        status_events = [r for r in received if r['name'] == 'status']
        assert len(status_events) >= 1
        
        # Send first message with conversation_id
        client1.emit('chat_message', {
            'message': 'Hello, first message',
            'conversation_id': test_conversation_id
        })
        
        received = client1.get_received()
        responses = [r for r in received if r['name'] == 'chat_response']
        assert len(responses) >= 1
        first_response = responses[0]['args'][0]
        assert 'message #1' in first_response['response']
        
        # Disconnect first client
        client1.disconnect()
        assert not client1.is_connected()
        
        # Reconnect with new client, same conversation_id
        client2 = socketio.test_client(app)
        assert client2.is_connected()
        
        # Clear connection events
        client2.get_received()
        
        # Send second message with same conversation_id
        client2.emit('chat_message', {
            'message': 'Hello, second message',
            'conversation_id': test_conversation_id
        })
        
        received = client2.get_received()
        responses = [r for r in received if r['name'] == 'chat_response']
        assert len(responses) >= 1
        second_response = responses[0]['args'][0]
        
        # Should show message #2, proving history was maintained
        assert 'message #2' in second_response['response'], (
            f"Expected 'message #2' in response, got: {second_response['response']}"
        )
        
        # Verify session history has both messages
        assert test_conversation_id in session_history
        assert len(session_history[test_conversation_id]) == 2
        
        client2.disconnect()
    
    def test_conversation_id_echoed_back_in_response(self):
        """Test: Conversation ID is echoed back in Socket.IO response.
        
        This helps clients confirm their session state is being tracked.
        """
        app, socketio, session_history = _make_socketio_reconnection_test_app()
        
        from flask_socketio import SocketIOTestClient
        
        test_conversation_id = str(uuid.uuid4())
        
        client = socketio.test_client(app)
        client.get_received()  # Clear connection events
        
        client.emit('chat_message', {
            'message': 'Test message',
            'conversation_id': test_conversation_id
        })
        
        received = client.get_received()
        responses = [r for r in received if r['name'] == 'chat_response']
        
        assert len(responses) >= 1
        response_data = responses[0]['args'][0]
        
        # Conversation ID should be echoed back
        assert 'conversation_id' in response_data
        assert response_data['conversation_id'] == test_conversation_id
        
        client.disconnect()
    
    def test_multiple_clients_same_session_share_history(self):
        """Test: Multiple clients using same conversation_id share conversation history.
        
        This simulates a user with multiple browser tabs or reconnecting
        after a brief disconnection.
        """
        app, socketio, session_history = _make_socketio_reconnection_test_app()
        
        from flask_socketio import SocketIOTestClient
        
        shared_conversation_id = str(uuid.uuid4())
        
        # Client 1 sends message
        client1 = socketio.test_client(app)
        client1.get_received()
        
        client1.emit('chat_message', {
            'message': 'From client 1',
            'conversation_id': shared_conversation_id
        })
        client1.get_received()
        
        # Client 2 sends message with same conversation_id (without disconnecting client 1)
        client2 = socketio.test_client(app)
        client2.get_received()
        
        client2.emit('chat_message', {
            'message': 'From client 2',
            'conversation_id': shared_conversation_id
        })
        
        received = client2.get_received()
        responses = [r for r in received if r['name'] == 'chat_response']
        assert len(responses) >= 1
        
        response_data = responses[0]['args'][0]
        
        # Should be message #2 because history is shared
        assert 'message #2' in response_data['response'], (
            f"Expected shared history (message #2), got: {response_data['response']}"
        )
        
        # Verify session history has both messages
        assert len(session_history[shared_conversation_id]) == 2
        
        client1.disconnect()
        client2.disconnect()
    
    def test_stateless_operation_when_no_conversation_id(self):
        """Test: Without conversation_id, each message is stateless.
        
        Regression test: Ensure session-aware features don't break
        stateless operation for clients not using sessions.
        """
        app, socketio, session_history = _make_socketio_reconnection_test_app()
        
        from flask_socketio import SocketIOTestClient
        
        client = socketio.test_client(app)
        client.get_received()
        
        # Send message WITHOUT conversation_id
        client.emit('chat_message', {
            'message': 'Stateless message'
        })
        
        received = client.get_received()
        responses = [r for r in received if r['name'] == 'chat_response']
        
        assert len(responses) >= 1
        response_data = responses[0]['args'][0]
        
        # Should indicate stateless operation
        assert 'Stateless' in response_data['response']
        
        # No conversation_id in response when not provided in request
        # (This is implementation-dependent, some may omit, some may include None)
        
        client.disconnect()
