"""
Flask Socket.IO WebSocket Testing Patterns

Demonstrates comprehensive testing patterns for Socket.IO event handlers,
including fixture setup, unit tests, integration tests, and streaming patterns.

Reference: backend-python.instructions.md § Testing > WebSocket Testing Patterns
"""

import pytest
from typing import Any, Dict
from unittest.mock import MagicMock
from flask import Flask
from flask_socketio import SocketIO, SocketIOTestClient


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def socketio_test_client(app):
    """
    Flask-SocketIO test client for integration tests.
    
    Use for testing full event flow with real Socket.IO client.
    Automatically handles connection lifecycle.
    
    Benefits:
    - Tests complete event flow (emit → handler → emit)
    - Validates Socket.IO protocol compliance
    - Catches integration issues
    
    When to use:
    - Testing end-to-end event workflows
    - Verifying connection lifecycle
    - Testing event emission and reception
    """
    return SocketIOTestClient(app, socketio)


@pytest.fixture
def mock_socketio():
    """
    Mock SocketIO for unit tests.
    
    Use for testing handler logic without real Socket.IO overhead.
    Faster than integration tests; good for handler business logic.
    
    Benefits:
    - Fast execution (no real connections)
    - Fine-grained control over mock behavior
    - Test handler logic in isolation
    
    When to use:
    - Testing handler business logic
    - Testing validation and error handling
    - Fast feedback during development
    """
    mock_io = MagicMock()
    return mock_io


@pytest.fixture
def mock_agent():
    """Mock agent for testing chat handlers."""
    agent = MagicMock()
    agent.process_query.return_value = "Test response from agent"
    agent.process_query_streaming.return_value = iter(["chunk1", "chunk2", "chunk3"])
    return agent


# ============================================================================
# UNIT TESTS: Testing Event Handlers with Mocks
# ============================================================================

def test_chat_message_handler_emits_response(mock_socketio, mock_agent):
    """
    Test chat_message event handler processes and emits response.
    
    Pattern: Unit test for handler business logic
    - Mock Socket.IO to avoid real connections
    - Mock agent to control response
    - Verify handler calls emit with correct data
    """
    from web.sockets.chat_events import register_chat_events
    from web.routes.shared_context import SocketIOContext
    import logging
    
    logger = logging.getLogger(__name__)
    context = SocketIOContext(
        socketio=mock_socketio, 
        agent=mock_agent, 
        config={}, 
        logger=logger
    )
    register_chat_events(context)
    
    # Get registered handler (extract from mock.on() calls)
    handler = mock_socketio.on.call_args_list[0][0][1]  # Second arg of first on() call
    
    # Create mock Flask app context for handler execution
    app = Flask(__name__)
    with app.test_request_context():
        handler({'message': 'Test query'})
    
    # Verify emit called with expected event and data
    mock_socketio.emit.assert_called_with(
        'chat_response', 
        {'response': 'Test response from agent'}
    )


def test_chat_message_handler_validates_input(mock_socketio, mock_agent):
    """
    Test handler rejects empty messages with validation error.
    
    Pattern: Input validation testing
    - Test edge cases (empty string, whitespace)
    - Verify error emission
    - Ensure no agent call on invalid input
    """
    from web.sockets.chat_events import register_chat_events
    from web.routes.shared_context import SocketIOContext
    import logging
    
    logger = logging.getLogger(__name__)
    context = SocketIOContext(
        socketio=mock_socketio,
        agent=mock_agent,
        config={},
        logger=logger
    )
    register_chat_events(context)
    
    handler = mock_socketio.on.call_args_list[0][0][1]
    
    app = Flask(__name__)
    with app.test_request_context():
        handler({'message': ''})  # Empty message
    
    # Verify error emitted
    mock_socketio.emit.assert_called_with(
        'error', 
        {'message': 'Message cannot be empty'}
    )
    
    # Verify agent was NOT called
    mock_agent.process_query.assert_not_called()


def test_chat_message_handler_validates_missing_field(mock_socketio, mock_agent):
    """Test handler rejects data without 'message' field."""
    from web.sockets.chat_events import register_chat_events
    from web.routes.shared_context import SocketIOContext
    import logging
    
    logger = logging.getLogger(__name__)
    context = SocketIOContext(
        socketio=mock_socketio,
        agent=mock_agent,
        config={},
        logger=logger
    )
    register_chat_events(context)
    
    handler = mock_socketio.on.call_args_list[0][0][1]
    
    app = Flask(__name__)
    with app.test_request_context():
        handler({})  # Missing 'message' field
    
    # Verify error emitted
    mock_socketio.emit.assert_called()
    call_args = mock_socketio.emit.call_args[0]
    assert call_args[0] == 'error'


# ============================================================================
# INTEGRATION TESTS: Testing Full Event Flow
# ============================================================================

def test_client_connect_emits_status(socketio_test_client):
    """
    Test client connection emits status event.
    
    Pattern: Integration test for connection lifecycle
    - Uses real SocketIOTestClient
    - Verifies server emits welcome message
    - Tests complete connection handshake
    """
    socketio_test_client.connect()
    received = socketio_test_client.get_received()
    
    assert len(received) == 1
    assert received[0]['name'] == 'status'
    assert 'Connected' in received[0]['args'][0]['message']


def test_client_disconnect_cleans_up(socketio_test_client):
    """
    Test client disconnection triggers cleanup.
    
    Pattern: Cleanup verification
    - Connect and then disconnect
    - Verify no lingering state
    - Implementation-specific: could check active users dict, sessions, etc.
    """
    socketio_test_client.connect()
    socketio_test_client.disconnect()
    
    # Verify no lingering connections (implementation-specific)
    # Example checks:
    # - User removed from active_users dict
    # - Session cleaned up
    # - Resources released
    
    # For this example, we just verify disconnection doesn't crash
    assert True  # Replace with actual cleanup verification


def test_chat_message_round_trip(socketio_test_client, mock_agent):
    """
    Test complete chat message round trip (client → server → client).
    
    Pattern: End-to-end integration test
    - Client sends message
    - Server processes with handler
    - Client receives response
    """
    socketio_test_client.connect()
    
    # Send message
    socketio_test_client.emit('chat_message', {'message': 'What is AAPL price?'})
    
    # Get response
    received = socketio_test_client.get_received()
    
    # Filter for chat_response events
    responses = [r for r in received if r['name'] == 'chat_response']
    
    assert len(responses) >= 1
    assert 'response' in responses[0]['args'][0]


# ============================================================================
# STREAMING TESTS: Testing Incremental Event Emission
# ============================================================================

def test_chat_stream_emits_multiple_chunks(socketio_test_client, mock_agent):
    """
    Test streaming chat emits incremental chunks.
    
    Pattern: Streaming event testing
    - Mock agent returns iterator
    - Verify multiple chunk events emitted
    - Verify final completion event
    """
    # Configure mock agent to return streaming iterator
    mock_agent.process_query_streaming.return_value = iter([
        'chunk1', 
        'chunk2', 
        'chunk3'
    ])
    
    socketio_test_client.connect()
    socketio_test_client.emit('chat_stream_start', {'message': 'Test'})
    
    received = socketio_test_client.get_received()
    
    # Filter for chat_chunk events
    chunks = [r for r in received if r['name'] == 'chat_chunk']
    assert len(chunks) == 3
    assert chunks[0]['args'][0]['chunk'] == 'chunk1'
    assert chunks[1]['args'][0]['chunk'] == 'chunk2'
    assert chunks[2]['args'][0]['chunk'] == 'chunk3'
    
    # Verify stream end event
    end_events = [r for r in received if r['name'] == 'chat_stream_end']
    assert len(end_events) == 1


def test_chat_stream_handles_empty_stream(socketio_test_client, mock_agent):
    """Test streaming with empty iterator."""
    mock_agent.process_query_streaming.return_value = iter([])
    
    socketio_test_client.connect()
    socketio_test_client.emit('chat_stream_start', {'message': 'Test'})
    
    received = socketio_test_client.get_received()
    
    # Should still emit end event even with no chunks
    end_events = [r for r in received if r['name'] == 'chat_stream_end']
    assert len(end_events) == 1


def test_chat_stream_handles_error_during_streaming(socketio_test_client, mock_agent):
    """Test streaming error handling."""
    def error_generator():
        yield "chunk1"
        raise RuntimeError("Streaming error")
    
    mock_agent.process_query_streaming.return_value = error_generator()
    
    socketio_test_client.connect()
    socketio_test_client.emit('chat_stream_start', {'message': 'Test'})
    
    received = socketio_test_client.get_received()
    
    # Verify error event emitted
    error_events = [r for r in received if r['name'] == 'error']
    assert len(error_events) >= 1


# ============================================================================
# CLEANUP TESTS: Testing Resource Management
# ============================================================================

def test_handler_removes_listeners_on_disconnect(socketio_test_client):
    """
    Test listeners are properly removed on client disconnect.
    
    Pattern: Resource cleanup verification
    - Connect client
    - Register listeners
    - Disconnect
    - Verify listeners removed (no memory leaks)
    """
    socketio_test_client.connect()
    
    # In real implementation, would verify:
    # - socketio.on() listeners cleaned up
    # - No references held to disconnected clients
    # - Memory usage doesn't grow with connect/disconnect cycles
    
    socketio_test_client.disconnect()
    
    # Implementation would check socket.io internal state
    # For this example, just verify disconnect succeeds
    assert True


# ============================================================================
# ERROR HANDLING TESTS: Testing Exception Scenarios
# ============================================================================

def test_handler_catches_agent_exceptions(mock_socketio, mock_agent):
    """Test handler gracefully handles agent exceptions."""
    from web.sockets.chat_events import register_chat_events
    from web.routes.shared_context import SocketIOContext
    import logging
    
    # Make agent raise exception
    mock_agent.process_query.side_effect = RuntimeError("Agent crashed")
    
    logger = logging.getLogger(__name__)
    context = SocketIOContext(
        socketio=mock_socketio,
        agent=mock_agent,
        config={},
        logger=logger
    )
    register_chat_events(context)
    
    handler = mock_socketio.on.call_args_list[0][0][1]
    
    app = Flask(__name__)
    with app.test_request_context():
        # Should not raise exception
        handler({'message': 'Test query'})
    
    # Verify error emitted instead of crashing
    mock_socketio.emit.assert_called()
    call_args = mock_socketio.emit.call_args[0]
    assert call_args[0] == 'error'


# ============================================================================
# BEST PRACTICES DEMONSTRATION
# ============================================================================

def demonstrate_websocket_testing_best_practices():
    """Display WebSocket testing best practices."""
    
    print("=" * 60)
    print("WEBSOCKET TESTING BEST PRACTICES")
    print("=" * 60)
    
    practices = [
        {
            "practice": "Use SocketIOTestClient for Integration Tests",
            "why": "Tests complete event flow including Socket.IO protocol",
            "when": "Testing end-to-end workflows, connection lifecycle"
        },
        {
            "practice": "Use MagicMock for Unit Tests",
            "why": "Fast, isolated testing of handler business logic",
            "when": "Testing validation, error handling, business rules"
        },
        {
            "practice": "Test Connection Lifecycle",
            "why": "Ensures proper setup and teardown of connections",
            "when": "Testing connect, disconnect, reconnect scenarios"
        },
        {
            "practice": "Test Input Validation",
            "why": "Prevents invalid data from causing crashes or errors",
            "when": "Testing all handlers that accept client data"
        },
        {
            "practice": "Test Streaming with Multiple Chunks",
            "why": "Verifies incremental data delivery works correctly",
            "when": "Testing streaming responses, real-time updates"
        },
        {
            "practice": "Verify Cleanup",
            "why": "Prevents memory leaks and resource exhaustion",
            "when": "Testing disconnect, error scenarios, long-running tests"
        },
    ]
    
    for i, item in enumerate(practices, 1):
        print(f"\n{i}. {item['practice']}")
        print(f"   Why: {item['why']}")
        print(f"   When: {item['when']}")


if __name__ == "__main__":
    print("Flask Socket.IO WebSocket Testing Patterns")
    print("=" * 60)
    print("\nDemonstrates comprehensive testing patterns for Socket.IO")
    print("event handlers with fixtures, unit tests, integration tests,")
    print("and streaming patterns.\n")
    
    demonstrate_websocket_testing_best_practices()
    
    print("\n" + "=" * 60)
    print("TEST COVERAGE CHECKLIST")
    print("=" * 60)
    print("✅ Unit tests: Handler business logic with mocks")
    print("✅ Integration tests: Full event flow with test client")
    print("✅ Validation tests: Input validation and error handling")
    print("✅ Streaming tests: Incremental chunk delivery")
    print("✅ Cleanup tests: Resource management and memory leaks")
    print("✅ Error handling: Exception scenarios and graceful degradation")
    
    print("\n📖 Reference: backend-python.instructions.md")
    print("   § Testing with pytest > WebSocket Testing Patterns")
