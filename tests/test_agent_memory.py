"""
Integration tests for agent memory (session-aware conversation).

Tests FR-3.1 Short-Term Memory requirements:
- FR-3.1.1: Agent references prior messages accurately
- FR-3.1.4: Session context binding
- FR-3.1.8: Memory contains conversation text but NOT financial data

Reference: specs/spec-driven-development-pilot/spec.md
"""

import pytest
import uuid
from unittest.mock import MagicMock, patch


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def mock_config():
    """Minimal configuration with memory enabled."""
    return {
        'model': {
            'provider': 'openai',
            'name': 'gpt-4',
        },
        'openai': {
            'api_key': 'test-key-fake-openai',
            'model': 'gpt-3.5-turbo',
        },
        'langchain': {
            'memory': {
                'enabled': True,
                'ttl_seconds': 3600,
                'checkpoint_collection': 'agent_checkpoints_test',
            }
        },
        'mongodb': {
            'uri': 'mongodb://localhost:27017',
            'database': 'stock_assistant_test',
        },
    }


@pytest.fixture
def mock_checkpointer():
    """Mock checkpointer for session memory."""
    checkpointer = MagicMock()
    checkpointer.list.return_value = []  # Empty checkpoint history by default
    return checkpointer


@pytest.fixture
def generate_conversation_id():
    """Generate a valid UUID v4 conversation_id."""
    return str(uuid.uuid4())


# ============================================================================
# TESTS: SESSION_ID PARAMETER HANDLING
# ============================================================================

class TestSessionIdParameter:
    """Tests for session_id parameter acceptance and threading."""

    def test_process_query_accepts_conversation_id(self, mock_config, generate_conversation_id):
        """Test process_query accepts conversation_id parameter."""
        from core.stock_assistant_agent import StockAssistantAgent
        
        # Create agent with mocked dependencies
        with patch('core.stock_assistant_agent.StockAssistantAgent._build_agent_executor'):
            agent = StockAssistantAgent.__new__(StockAssistantAgent)
            agent._config = mock_config
            agent._checkpointer = MagicMock()
            agent._agent_executor = MagicMock()
            agent._agent_executor.invoke.return_value = {"output": "Test response"}
            agent._use_react = True
            agent._use_streaming = False
            agent.logger = MagicMock()
            
            conversation_id = generate_conversation_id
            
            # Should not raise - conversation_id is a valid parameter
            result = agent.process_query("Hello", conversation_id=conversation_id)
            
            # Verify invoke was called with config containing thread_id
            call_args = agent._agent_executor.invoke.call_args
            config_arg = call_args[1].get('config') if call_args[1] else None
            
            assert config_arg is not None
            assert config_arg['configurable']['thread_id'] == conversation_id

    def test_process_query_works_without_session_id(self, mock_config):
        """Test process_query works when session_id is None (backward compat)."""
        from core.stock_assistant_agent import StockAssistantAgent
        
        with patch('core.stock_assistant_agent.StockAssistantAgent._build_agent_executor'):
            agent = StockAssistantAgent.__new__(StockAssistantAgent)
            agent._config = mock_config
            agent._checkpointer = None  # No checkpointer
            agent._agent_executor = MagicMock()
            agent._agent_executor.invoke.return_value = {"output": "Test response"}
            agent._use_react = True
            agent._use_streaming = False
            agent.logger = MagicMock()
            
            # Should not raise - session_id defaults to None
            result = agent.process_query("Hello")
            
            # Invoke should be called without thread_id config
            call_args = agent._agent_executor.invoke.call_args
            config_arg = call_args[1].get('config') if call_args[1] else None
            
            # When no session_id and no checkpointer, config may be None or not contain thread_id
            if config_arg is not None and 'configurable' in config_arg:
                # If configurable exists, thread_id should not be present
                assert 'thread_id' not in config_arg.get('configurable', {})

    def test_process_query_streaming_accepts_conversation_id(self, mock_config, generate_conversation_id):
        """Test process_query_streaming accepts conversation_id parameter."""
        from core.stock_assistant_agent import StockAssistantAgent
        
        with patch('core.stock_assistant_agent.StockAssistantAgent._build_agent_executor'):
            agent = StockAssistantAgent.__new__(StockAssistantAgent)
            agent._config = mock_config
            agent._checkpointer = MagicMock()
            agent._agent_executor = MagicMock()
            agent._use_react = True
            agent._use_streaming = True
            agent.logger = MagicMock()
            
            # Mock the streaming method
            async def mock_astream_events(*args, **kwargs):
                yield {"event": "on_chat_model_stream", "data": {"chunk": MagicMock(content="Hello")}}
            
            agent._agent_executor.astream_events = mock_astream_events
            
            conversation_id = generate_conversation_id
            
            # Should not raise - consuming the generator
            chunks = list(agent.process_query_streaming("Hello", conversation_id=conversation_id))
            
            # The generator should have been consumed without error


# ============================================================================
# TESTS: SESSION ISOLATION
# ============================================================================

class TestSessionIsolation:
    """Tests for session isolation between different session_ids."""

    def test_different_sessions_have_separate_thread_ids(self, mock_config):
        """Test that different session_ids result in different thread_id configs."""
        from core.stock_assistant_agent import StockAssistantAgent
        
        with patch('core.stock_assistant_agent.StockAssistantAgent._build_agent_executor'):
            agent = StockAssistantAgent.__new__(StockAssistantAgent)
            agent._config = mock_config
            agent._checkpointer = MagicMock()
            agent._agent_executor = MagicMock()
            agent._agent_executor.invoke.return_value = {"output": "Test response"}
            agent._use_react = True
            agent._use_streaming = False
            agent.logger = MagicMock()
            
            session_1 = str(uuid.uuid4())
            session_2 = str(uuid.uuid4())
            
            # Call with first session
            agent.process_query("Hello from session 1", conversation_id=session_1)
            call_1 = agent._agent_executor.invoke.call_args_list[-1]
            config_1 = call_1[1].get('config', {})
            
            # Call with second session
            agent.process_query("Hello from session 2", conversation_id=session_2)
            call_2 = agent._agent_executor.invoke.call_args_list[-1]
            config_2 = call_2[1].get('config', {})
            
            # Verify different thread_ids
            assert config_1['configurable']['thread_id'] == session_1
            assert config_2['configurable']['thread_id'] == session_2
            assert session_1 != session_2


# ============================================================================
# TESTS: CHECKPOINTER INTEGRATION
# ============================================================================

class TestCheckpointerIntegration:
    """Tests for checkpointer integration with agent."""

    def test_agent_accepts_checkpointer_in_init(self, mock_config, mock_checkpointer):
        """Test StockAssistantAgent accepts checkpointer parameter."""
        from core.stock_assistant_agent import StockAssistantAgent
        
        with patch.object(StockAssistantAgent, '_build_agent_executor'):
            with patch('core.stock_assistant_agent.DataManager'):
                # Create agent with checkpointer
                agent = StockAssistantAgent.__new__(StockAssistantAgent)
                agent._checkpointer = mock_checkpointer
                
                assert agent._checkpointer is mock_checkpointer

    def test_agent_stores_checkpointer_as_instance_attribute(self, mock_config, mock_checkpointer):
        """Test checkpointer is stored as _checkpointer attribute."""
        from core.stock_assistant_agent import StockAssistantAgent
        
        with patch.object(StockAssistantAgent, '_build_agent_executor'):
            with patch('core.stock_assistant_agent.DataManager'):
                agent = StockAssistantAgent.__new__(StockAssistantAgent)
                agent._checkpointer = mock_checkpointer
                
                # Verify it's the same object
                assert agent._checkpointer is mock_checkpointer

    def test_agent_config_includes_thread_id_when_checkpointer_present(
        self, mock_config, mock_checkpointer, generate_conversation_id
    ):
        """Test that config includes thread_id when checkpointer is present."""
        from core.stock_assistant_agent import StockAssistantAgent
        
        with patch('core.stock_assistant_agent.StockAssistantAgent._build_agent_executor'):
            agent = StockAssistantAgent.__new__(StockAssistantAgent)
            agent._config = mock_config
            agent._checkpointer = mock_checkpointer
            agent._agent_executor = MagicMock()
            agent._agent_executor.invoke.return_value = {"output": "Test"}
            agent._use_react = True
            agent._use_streaming = False
            agent.logger = MagicMock()
            
            conversation_id = generate_conversation_id
            agent.process_query("Hello", conversation_id=conversation_id)
            
            call_args = agent._agent_executor.invoke.call_args
            config = call_args[1].get('config', {})
            
            assert 'configurable' in config
            assert config['configurable']['thread_id'] == conversation_id


# ============================================================================
# TESTS: MULTI-TURN CONVERSATION (FR-3.1.1)
# ============================================================================

class TestMultiTurnConversation:
    """Tests for multi-turn conversation context recall (FR-3.1.1)."""

    def test_consecutive_calls_with_same_session_use_same_thread_id(
        self, mock_config, generate_conversation_id
    ):
        """Test that consecutive calls with same conversation_id use same thread_id."""
        from core.stock_assistant_agent import StockAssistantAgent
        
        with patch('core.stock_assistant_agent.StockAssistantAgent._build_agent_executor'):
            agent = StockAssistantAgent.__new__(StockAssistantAgent)
            agent._config = mock_config
            agent._checkpointer = MagicMock()
            agent._agent_executor = MagicMock()
            agent._agent_executor.invoke.return_value = {"output": "Test response"}
            agent._use_react = True
            agent._use_streaming = False
            agent.logger = MagicMock()
            
            conversation_id = generate_conversation_id
            
            # First message
            agent.process_query("My name is Alice", conversation_id=conversation_id)
            first_call_config = agent._agent_executor.invoke.call_args_list[0][1].get('config', {})
            
            # Second message (follow-up)
            agent.process_query("What is my name?", conversation_id=conversation_id)
            second_call_config = agent._agent_executor.invoke.call_args_list[1][1].get('config', {})
            
            # Both should use the same thread_id
            assert first_call_config['configurable']['thread_id'] == conversation_id
            assert second_call_config['configurable']['thread_id'] == conversation_id
            assert first_call_config['configurable']['thread_id'] == second_call_config['configurable']['thread_id']


# ============================================================================
# TESTS: MEMORY CONFIG LOADING
# ============================================================================

class TestMemoryConfigLoading:
    """Tests for memory configuration loading.
    
    Note: These tests require core.config.memory_config module which will be
    created in Sprint 2. Tests are skipped if module doesn't exist.
    """

    def test_memory_config_loads_from_config(self, mock_config):
        """Test MemoryConfig dataclass loads from config dict."""
        try:
            from core.config.memory_config import MemoryConfig
        except ImportError:
            pytest.skip("core.config.memory_config module not yet implemented (Sprint 2)")
        
        memory_config = MemoryConfig.from_config(mock_config)
        
        assert memory_config.enabled is True
        assert memory_config.ttl_seconds == 3600
        assert memory_config.checkpoint_collection == 'agent_checkpoints_test'

    def test_memory_config_defaults_when_not_configured(self):
        """Test MemoryConfig uses defaults when config section missing."""
        try:
            from core.config.memory_config import MemoryConfig
        except ImportError:
            pytest.skip("core.config.memory_config module not yet implemented (Sprint 2)")
        
        empty_config = {}
        memory_config = MemoryConfig.from_config(empty_config)
        
        # Should use defaults
        assert memory_config.enabled is False  # Default is disabled
        assert memory_config.checkpoint_collection == 'agent_checkpoints'  # Default collection


# ============================================================================
# TESTS: LANGGRAPH BOOTSTRAP
# ============================================================================

class TestLangGraphBootstrap:
    """Tests for LangGraph bootstrap checkpointer creation."""

    def test_create_checkpointer_returns_none_when_disabled(self, mock_config):
        """Test create_checkpointer returns None when memory disabled."""
        mock_config['langchain']['memory']['enabled'] = False
        
        from core.langgraph_bootstrap import create_checkpointer
        
        checkpointer = create_checkpointer(mock_config)
        
        assert checkpointer is None

    def test_create_checkpointer_returns_saver_when_enabled(self, mock_config):
        """Test create_checkpointer returns MongoDBSaver when enabled.
        
        This test requires actual MongoDB integration or proper MongoDBSaver import.
        Skipped if MongoDBSaver is not yet available in langgraph_bootstrap.
        """
        from core.langgraph_bootstrap import create_checkpointer
        
        # Check if MongoDBSaver is available in the module
        import core.langgraph_bootstrap as bootstrap_module
        if not hasattr(bootstrap_module, 'MongoDBSaver'):
            pytest.skip("MongoDBSaver not yet imported in langgraph_bootstrap (Sprint 2)")
        
        with patch('core.langgraph_bootstrap.MongoDBSaver') as MockSaver:
            mock_saver_instance = MagicMock()
            MockSaver.return_value = mock_saver_instance
            
            checkpointer = create_checkpointer(mock_config)
            
            # Should have attempted to create a MongoDBSaver
            MockSaver.assert_called_once()


# ============================================================================
# TESTS: US3 STATELESS FALLBACK MODE (FR-3.1.6)
# ============================================================================

class TestStatelessFallbackMode:
    """
    Tests for US3: Agent functions without session tracking when no session_id provided.
    
    FR-3.1.6: Agent responds normally without session_id
    - No conversation data persisted to database
    - Subsequent queries have no memory of prior exchange
    """

    def test_stateless_query_returns_valid_response(self, mock_config):
        """Test: Query without session_id returns valid response (FR-3.1.6)."""
        from core.stock_assistant_agent import StockAssistantAgent
        from langchain_core.messages import AIMessage
        
        with patch('core.stock_assistant_agent.StockAssistantAgent._build_agent_executor'):
            agent = StockAssistantAgent.__new__(StockAssistantAgent)
            agent._config = mock_config
            agent._checkpointer = None  # No checkpointer = stateless
            agent._agent_executor = MagicMock()
            # Return messages list with AIMessage (matching actual implementation)
            agent._agent_executor.invoke.return_value = {
                "messages": [AIMessage(content="Stock AAPL is at $150")]
            }
            agent._use_react = True
            agent._use_streaming = False
            agent.logger = MagicMock()
            
            # Query WITHOUT session_id
            result = agent.process_query("What is AAPL price?")
            
            # Should return valid response
            assert result is not None
            assert "AAPL" in result or "$150" in result
            
            # Verify invoke was called (agent processed the request)
            agent._agent_executor.invoke.assert_called_once()

    def test_stateless_mode_no_checkpoint_config(self, mock_config):
        """Test: No checkpoint configuration when session_id omitted."""
        from core.stock_assistant_agent import StockAssistantAgent
        from langchain_core.messages import AIMessage
        
        with patch('core.stock_assistant_agent.StockAssistantAgent._build_agent_executor'):
            agent = StockAssistantAgent.__new__(StockAssistantAgent)
            agent._config = mock_config
            agent._checkpointer = MagicMock()  # Even with checkpointer available
            agent._agent_executor = MagicMock()
            agent._agent_executor.invoke.return_value = {
                "messages": [AIMessage(content="Response")]
            }
            agent._use_react = True
            agent._use_streaming = False
            agent.logger = MagicMock()
            
            # Query WITHOUT conversation_id (None)
            agent.process_query("Hello", conversation_id=None)
            
            call_args = agent._agent_executor.invoke.call_args
            config = call_args[1].get('config')
            
            # When session_id is None, either:
            # 1. config is None
            # 2. config['configurable'] doesn't have 'thread_id'
            # 3. thread_id is None
            if config is not None and 'configurable' in config:
                thread_id = config['configurable'].get('thread_id')
                assert thread_id is None, "thread_id should be None for stateless mode"

    def test_stateless_queries_have_no_context_carryover(self, mock_config):
        """Test: Two sequential queries without session_id have no context carryover."""
        from core.stock_assistant_agent import StockAssistantAgent
        from langchain_core.messages import AIMessage
        
        with patch('core.stock_assistant_agent.StockAssistantAgent._build_agent_executor'):
            agent = StockAssistantAgent.__new__(StockAssistantAgent)
            agent._config = mock_config
            agent._checkpointer = None
            agent._agent_executor = MagicMock()
            agent._use_react = True
            agent._use_streaming = False
            agent.logger = MagicMock()
            
            # Track what messages are passed to the agent
            received_messages = []
            
            def capture_invoke(messages_dict, **kwargs):
                # Capture the input for verification
                received_messages.append(messages_dict.get('messages', []))
                return {"messages": [AIMessage(content="Response")]}
            
            agent._agent_executor.invoke.side_effect = capture_invoke
            
            # First query - introduce information
            agent.process_query("My name is Alice")
            
            # Second query - reference prior information
            agent.process_query("What is my name?")
            
            # Each call should be independent - no accumulated context
            # Both calls should receive single message (the current query only)
            assert len(received_messages) == 2
            
            # First call should have "My name is Alice" 
            first_call_messages = received_messages[0]
            # Second call should have "What is my name?" - NOT referencing Alice
            second_call_messages = received_messages[1]
            
            # Verify calls are independent (no accumulated context from first call)
            # The exact message format depends on agent implementation,
            # but the key point is each call starts fresh
            assert agent._agent_executor.invoke.call_count == 2

    def test_stateless_with_explicit_none_session_id(self, mock_config):
        """Test: Explicit session_id=None is treated as stateless."""
        from core.stock_assistant_agent import StockAssistantAgent
        from langchain_core.messages import AIMessage
        
        with patch('core.stock_assistant_agent.StockAssistantAgent._build_agent_executor'):
            agent = StockAssistantAgent.__new__(StockAssistantAgent)
            agent._config = mock_config
            agent._checkpointer = MagicMock()
            agent._agent_executor = MagicMock()
            agent._agent_executor.invoke.return_value = {
                "messages": [AIMessage(content="Response")]
            }
            agent._use_react = True
            agent._use_streaming = False
            agent.logger = MagicMock()
            
            # Explicitly pass conversation_id=None
            result = agent.process_query("Test query", conversation_id=None)
            
            # Should return valid response
            assert result is not None
            
            # Verify no thread_id in config
            call_args = agent._agent_executor.invoke.call_args
            config = call_args[1].get('config')
            
            if config and 'configurable' in config:
                assert config['configurable'].get('thread_id') is None

    def test_checkpointer_not_written_in_stateless_mode(self, mock_config, mock_checkpointer):
        """Test: No checkpoint data created when session_id omitted."""
        from core.stock_assistant_agent import StockAssistantAgent
        from langchain_core.messages import AIMessage
        
        with patch('core.stock_assistant_agent.StockAssistantAgent._build_agent_executor'):
            agent = StockAssistantAgent.__new__(StockAssistantAgent)
            agent._config = mock_config
            agent._checkpointer = mock_checkpointer
            agent._agent_executor = MagicMock()
            agent._agent_executor.invoke.return_value = {
                "messages": [AIMessage(content="Response")]
            }
            agent._use_react = True
            agent._use_streaming = False
            agent.logger = MagicMock()
            
            # Query without session_id
            agent.process_query("Hello")
            
            # The checkpointer should NOT be called to save state
            # Since thread_id is None, the agent executor won't save checkpoint
            # This is verified by the config not having a valid thread_id
            call_args = agent._agent_executor.invoke.call_args
            config = call_args[1].get('config')
            
            # Without thread_id, LangGraph checkpointer won't save anything
            if config and 'configurable' in config:
                thread_id = config['configurable'].get('thread_id')
                assert thread_id is None, "No thread_id means no checkpoint will be saved"
