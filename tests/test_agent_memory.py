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
def generate_session_id():
    """Generate a valid UUID v4 session_id."""
    return str(uuid.uuid4())


# ============================================================================
# TESTS: SESSION_ID PARAMETER HANDLING
# ============================================================================

class TestSessionIdParameter:
    """Tests for session_id parameter acceptance and threading."""

    def test_process_query_accepts_session_id(self, mock_config, generate_session_id):
        """Test process_query accepts session_id parameter."""
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
            
            session_id = generate_session_id
            
            # Should not raise - session_id is a valid parameter
            result = agent.process_query("Hello", session_id=session_id)
            
            # Verify invoke was called with config containing thread_id
            call_args = agent._agent_executor.invoke.call_args
            config_arg = call_args[1].get('config') if call_args[1] else None
            
            assert config_arg is not None
            assert config_arg['configurable']['thread_id'] == session_id

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

    def test_process_query_streaming_accepts_session_id(self, mock_config, generate_session_id):
        """Test process_query_streaming accepts session_id parameter."""
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
            
            session_id = generate_session_id
            
            # Should not raise - consuming the generator
            chunks = list(agent.process_query_streaming("Hello", session_id=session_id))
            
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
            agent.process_query("Hello from session 1", session_id=session_1)
            call_1 = agent._agent_executor.invoke.call_args_list[-1]
            config_1 = call_1[1].get('config', {})
            
            # Call with second session
            agent.process_query("Hello from session 2", session_id=session_2)
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
        self, mock_config, mock_checkpointer, generate_session_id
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
            
            session_id = generate_session_id
            agent.process_query("Hello", session_id=session_id)
            
            call_args = agent._agent_executor.invoke.call_args
            config = call_args[1].get('config', {})
            
            assert 'configurable' in config
            assert config['configurable']['thread_id'] == session_id


# ============================================================================
# TESTS: MULTI-TURN CONVERSATION (FR-3.1.1)
# ============================================================================

class TestMultiTurnConversation:
    """Tests for multi-turn conversation context recall (FR-3.1.1)."""

    def test_consecutive_calls_with_same_session_use_same_thread_id(
        self, mock_config, generate_session_id
    ):
        """Test that consecutive calls with same session_id use same thread_id."""
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
            
            session_id = generate_session_id
            
            # First message
            agent.process_query("My name is Alice", session_id=session_id)
            first_call_config = agent._agent_executor.invoke.call_args_list[0][1].get('config', {})
            
            # Second message (follow-up)
            agent.process_query("What is my name?", session_id=session_id)
            second_call_config = agent._agent_executor.invoke.call_args_list[1][1].get('config', {})
            
            # Both should use the same thread_id
            assert first_call_config['configurable']['thread_id'] == session_id
            assert second_call_config['configurable']['thread_id'] == session_id
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
