"""Tests for ChatService."""

import pytest
from unittest.mock import MagicMock
from services.chat_service import ChatService
from services.protocols import AgentProvider


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def mock_config():
    """Minimal configuration for testing."""
    return {
        'model': {
            'provider': 'openai',
            'name': 'gpt-4',
        },
        'openai': {
            'api_key': 'test-key-fake-openai',  # Required for ModelClientFactory
            'model': 'gpt-3.5-turbo',  # Fallback
        },
        'grok': {
            'api_key': 'test-key-fake-grok',  # Required for fallback tests
            'model': 'grok-beta',
        },
    }


@pytest.fixture
def mock_agent():
    """Mock agent implementing AgentProvider protocol."""
    agent = MagicMock(spec=AgentProvider)
    agent.process_query.return_value = "Test response"
    agent.process_query_streaming.return_value = iter(["chunk1", "chunk2", "chunk3"])
    return agent


@pytest.fixture
def mock_agent_with_fallback():
    """Mock agent that returns fallback-prefixed response."""
    agent = MagicMock(spec=AgentProvider)
    agent.process_query.return_value = "[fallback:grok] Fallback response"
    agent.process_query_streaming.return_value = iter([
        "[fallback:grok] Fallback ",
        "response"
    ])
    return agent


@pytest.fixture
def mock_cache():
    """Mock cache backend."""
    cache = MagicMock()
    cache.is_healthy.return_value = True
    return cache


def build_chat_service(
    agent,
    config,
    cache=None,
    time_provider=None,
    logger=None
):
    """Build ChatService with dependencies."""
    return ChatService(
        agent_provider=agent,
        config=config,
        cache=cache,
        time_provider=time_provider,
        logger=logger,
    )


# ============================================================================
# TESTS: SERVICE INITIALIZATION
# ============================================================================

def test_chat_service_initialization(mock_agent, mock_config):
    """Test ChatService initializes with required dependencies."""
    service = build_chat_service(mock_agent, mock_config)
    
    assert service._agent == mock_agent
    assert service._config == mock_config


def test_chat_service_uses_custom_logger(mock_agent, mock_config):
    """Test ChatService accepts custom logger."""
    import logging
    custom_logger = logging.getLogger("test_chat")
    
    service = build_chat_service(mock_agent, mock_config, logger=custom_logger)
    
    assert service.logger == custom_logger


# ============================================================================
# TESTS: HEALTH CHECK
# ============================================================================

def test_health_check_reports_healthy_when_agent_available(mock_agent, mock_config):
    """Test health check reports healthy when agent is available."""
    service = build_chat_service(mock_agent, mock_config)
    
    healthy, details = service.health_check()
    
    assert healthy is True
    assert "checked_at" in details
    assert "agent" in details["dependencies"]


def test_health_check_reports_unhealthy_when_agent_unavailable(mock_config):
    """Test health check reports unhealthy when agent is None."""
    service = build_chat_service(None, mock_config)
    
    healthy, details = service.health_check()
    
    assert healthy is False
    assert "checked_at" in details
    assert "agent" in details["dependencies"]
    assert details["dependencies"]["agent"]["status"] == "missing"


# ============================================================================
# TESTS: EXTRACT_META
# ============================================================================

def test_extract_meta_without_fallback_prefix(mock_agent, mock_config):
    """Test extract_meta returns config defaults for normal response."""
    service = build_chat_service(mock_agent, mock_config)
    
    provider, model, fallback = service.extract_meta("Normal response text")
    
    assert provider == "openai"
    assert model == "gpt-4"
    assert fallback is False


def test_extract_meta_with_fallback_prefix(mock_agent, mock_config):
    """Test extract_meta detects [fallback:provider] prefix."""
    service = build_chat_service(mock_agent, mock_config)
    
    provider, model, fallback = service.extract_meta("[fallback:grok] Response text")
    
    assert provider == "grok"
    assert model == "gpt-4"  # Model unchanged
    assert fallback is True


def test_extract_meta_handles_malformed_fallback_prefix(mock_agent, mock_config):
    """Test extract_meta handles malformed fallback prefix gracefully."""
    service = build_chat_service(mock_agent, mock_config)
    
    # Missing closing bracket
    provider, model, fallback = service.extract_meta("[fallback:grok Response")
    
    assert fallback is True  # Flag set even if parsing fails
    assert provider == "openai"  # Falls back to config default


def test_extract_meta_uses_openai_model_fallback(mock_agent):
    """Test extract_meta falls back to openai.model when model.name missing."""
    config = {
        'model': {
            'provider': 'openai',
            # No 'name' key
        },
        'openai': {
            'model': 'gpt-3.5-turbo',
        },
    }
    service = build_chat_service(mock_agent, config)
    
    provider, model, fallback = service.extract_meta("Test")
    
    assert model == "gpt-3.5-turbo"


# ============================================================================
# TESTS: STRIP_FALLBACK_PREFIX
# ============================================================================

def test_strip_fallback_prefix_removes_prefix(mock_agent, mock_config):
    """Test strip_fallback_prefix removes [fallback:provider] prefix."""
    service = build_chat_service(mock_agent, mock_config)
    
    cleaned = service.strip_fallback_prefix("[fallback:grok] Response text")
    
    assert cleaned == "Response text"


def test_strip_fallback_prefix_strips_leading_whitespace(mock_agent, mock_config):
    """Test strip_fallback_prefix removes leading whitespace after prefix."""
    service = build_chat_service(mock_agent, mock_config)
    
    cleaned = service.strip_fallback_prefix("[fallback:grok]   Response text")
    
    assert cleaned == "Response text"


def test_strip_fallback_prefix_leaves_normal_text_unchanged(mock_agent, mock_config):
    """Test strip_fallback_prefix doesn't modify text without prefix."""
    service = build_chat_service(mock_agent, mock_config)
    
    cleaned = service.strip_fallback_prefix("Normal response text")
    
    assert cleaned == "Normal response text"


def test_strip_fallback_prefix_handles_missing_closing_bracket(mock_agent, mock_config):
    """Test strip_fallback_prefix leaves text unchanged if no closing bracket."""
    service = build_chat_service(mock_agent, mock_config)
    
    cleaned = service.strip_fallback_prefix("[fallback:grok Response")
    
    assert cleaned == "[fallback:grok Response"


# ============================================================================
# TESTS: GET_TIMESTAMP
# ============================================================================

def test_get_timestamp_returns_iso_format(mock_agent, mock_config):
    """Test get_timestamp returns ISO 8601 formatted timestamp."""
    service = build_chat_service(mock_agent, mock_config)
    
    timestamp = service.get_timestamp()
    
    # Check format: YYYY-MM-DDTHH:MM:SSZ
    assert len(timestamp) == 20
    assert timestamp[-1] == "Z"
    assert "T" in timestamp


def test_get_timestamp_uses_injectable_time_provider(mock_agent, mock_config):
    """Test get_timestamp uses injectable time provider for testability."""
    fixed_time = "2024-01-01T12:00:00Z"
    time_provider = MagicMock(return_value=fixed_time)
    
    service = build_chat_service(mock_agent, mock_config, time_provider=time_provider)
    
    timestamp = service.get_timestamp()
    
    assert timestamp == fixed_time
    time_provider.assert_called_once()


# ============================================================================
# TESTS: STREAM_CHAT_RESPONSE
# ============================================================================

def test_stream_chat_response_emits_meta_event(mock_agent, mock_config):
    """Test stream_chat_response emits meta event with provider/model info."""
    service = build_chat_service(mock_agent, mock_config)
    
    stream = service.stream_chat_response("Test query")
    events = list(stream)
    
    # First event should be meta
    assert "data: " in events[0]
    assert "meta" in events[0]
    assert "openai" in events[0] or "gpt" in events[0]


def test_stream_chat_response_emits_content_chunks(mock_agent, mock_config):
    """Test stream_chat_response emits content chunks from agent."""
    service = build_chat_service(mock_agent, mock_config)
    
    stream = service.stream_chat_response("Test query")
    events = list(stream)
    
    # Should have meta + 3 chunks + done + [DONE]
    assert len(events) >= 5
    
    # Check for chunk events
    chunk_events = [e for e in events if '"chunk"' in e]
    assert len(chunk_events) == 3


def test_stream_chat_response_emits_done_event(mock_agent, mock_config):
    """Test stream_chat_response emits done event with completion metadata."""
    service = build_chat_service(mock_agent, mock_config)
    
    stream = service.stream_chat_response("Test query")
    events = list(stream)
    
    # Find done event
    done_events = [e for e in events if '"event": "done"' in e or '"done"' in e]
    assert len(done_events) >= 1


def test_stream_chat_response_emits_terminator(mock_agent, mock_config):
    """Test stream_chat_response emits [DONE] terminator."""
    service = build_chat_service(mock_agent, mock_config)
    
    stream = service.stream_chat_response("Test query")
    events = list(stream)
    
    # Last event should be [DONE]
    assert "[DONE]" in events[-1]


def test_stream_chat_response_calls_agent_with_query(mock_agent, mock_config):
    """Test stream_chat_response calls agent.process_query_streaming."""
    service = build_chat_service(mock_agent, mock_config)
    
    list(service.stream_chat_response("Test query"))
    
    mock_agent.process_query_streaming.assert_called_once_with(
        "Test query", provider=None
    )


def test_stream_chat_response_passes_provider_override(mock_agent, mock_config):
    """Test stream_chat_response passes provider override to agent."""
    service = build_chat_service(mock_agent, mock_config)
    
    list(service.stream_chat_response("Test query", provider_override="grok"))
    
    mock_agent.process_query_streaming.assert_called_once_with(
        "Test query", provider="grok"
    )


def test_stream_chat_response_handles_agent_exception(mock_agent, mock_config):
    """Test stream_chat_response emits error event when agent raises exception."""
    mock_agent.process_query_streaming.side_effect = RuntimeError("Agent error")
    service = build_chat_service(mock_agent, mock_config)
    
    stream = service.stream_chat_response("Test query")
    events = list(stream)
    
    # Should emit error event
    error_events = [e for e in events if '"error"' in e]
    assert len(error_events) >= 1


def test_stream_chat_response_detects_fallback_in_completion(
    mock_agent_with_fallback, mock_config
):
    """Test stream_chat_response detects fallback prefix in completion metadata."""
    service = build_chat_service(mock_agent_with_fallback, mock_config)
    
    stream = service.stream_chat_response("Test query")
    events = list(stream)
    
    # Find done event and check fallback flag
    done_events = [e for e in events if '"event": "done"' in e or '"done"' in e]
    assert len(done_events) >= 1
    
    # Should contain fallback: true
    assert '"fallback": true' in done_events[0]


# ============================================================================
# TESTS: INTEGRATION WITH MODEL CLIENT FACTORY
# ============================================================================

def test_stream_chat_response_uses_model_client_factory(mock_agent, mock_config, monkeypatch):
    """Test stream_chat_response calls ModelClientFactory.get_client."""
    # CRITICAL: Must patch at services.chat_service level because ChatService
    # imports ModelClientFactory at module level (line 10 of chat_service.py)
    from services import chat_service
    
    # Create a simple object with string attributes (not MagicMock)
    # This ensures provider and model_name are JSON-serializable
    class MockClient:
        def __init__(self):
            self.provider = "grok"
            self.model_name = "grok-beta"
    
    mock_client = MockClient()
    
    # Create a proper mock factory class
    mock_get_client = MagicMock(return_value=mock_client)
    
    # Mock the class method properly
    mock_factory_class = MagicMock()
    mock_factory_class.get_client = mock_get_client
    
    # Patch at chat_service module level, NOT core.model_factory!
    monkeypatch.setattr(chat_service, "ModelClientFactory", mock_factory_class)
    
    service = build_chat_service(mock_agent, mock_config)
    
    # Consume the stream
    events = list(service.stream_chat_response("Test query", provider_override="grok"))
    
    # Should call factory with provider override
    mock_get_client.assert_called_once()
    call_kwargs = mock_get_client.call_args[1]
    assert call_kwargs.get("provider") == "grok"
    
    # Verify meta event was emitted with correct provider
    meta_events = [e for e in events if '"event": "meta"' in e]
    assert len(meta_events) == 1
    assert '"provider": "grok"' in meta_events[0]


# ============================================================================
# TESTS: EDGE CASES
# ============================================================================

def test_stream_chat_response_handles_empty_chunks(mock_agent, mock_config):
    """Test stream_chat_response skips empty chunks from agent."""
    mock_agent.process_query_streaming.return_value = iter(["", "chunk1", None, "chunk2", ""])
    service = build_chat_service(mock_agent, mock_config)
    
    stream = service.stream_chat_response("Test query")
    events = list(stream)
    
    # Should only emit non-empty chunks
    chunk_events = [e for e in events if '"chunk"' in e]
    assert len(chunk_events) == 2  # Only chunk1 and chunk2


def test_extract_meta_with_empty_config(mock_agent):
    """Test extract_meta handles minimal/empty config gracefully."""
    config = {}
    service = build_chat_service(mock_agent, config)
    
    provider, model, fallback = service.extract_meta("Test")
    
    assert provider == "openai"  # Default fallback
    assert model == "gpt-4"  # Default fallback
    assert fallback is False


def test_strip_fallback_prefix_with_empty_string(mock_agent, mock_config):
    """Test strip_fallback_prefix handles empty string."""
    service = build_chat_service(mock_agent, mock_config)
    
    cleaned = service.strip_fallback_prefix("")
    
    assert cleaned == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
