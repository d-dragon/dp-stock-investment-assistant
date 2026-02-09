"""
End-to-end runtime verification tests for STM wiring.

Reference: specs/spec-driven-development-pilot/tasks.md - T041
Verifies that Phase 9 integration gaps are fixed:
- Gap 0: create_react_agent → create_agent migration
- Gap 1: Checkpointer wired into APIServer and main.py
- Gap 2: MongoDB config keys match actual config.yaml structure

Success Criteria:
- Agent starts with checkpointer when langchain.memory.enabled: true
- /api/chat with session_id persists conversation to MongoDB
- Multi-turn context recall works across messages
- Stateless mode (no session_id) still works
- All existing tests pass with no deprecation warnings
"""

import json
import uuid
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from utils.memory_config import MemoryConfig


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def memory_enabled_config():
    """Configuration with STM enabled and correct MongoDB keys."""
    return {
        'app': {'log_level': 'INFO'},
        'model': {
            'provider': 'openai',
            'name': 'gpt-4',
            'allow_fallback': False,
        },
        'openai': {
            'api_key': 'test-key-fake',
            'model': 'gpt-4',
            'temperature': 0.7,
        },
        'database': {
            'mongodb': {
                'connection_string': 'mongodb://testuser:testpass@localhost:27017/test_db',
                'database_name': 'stock_assistant_test',
            }
        },
        'langchain': {
            'memory': {
                'enabled': True,
                'summarize_threshold': 4000,
                'max_messages': 50,
                'messages_to_keep': 10,
                'max_content_size': 32768,
                'summary_max_length': 500,
                'context_load_timeout_ms': 500,
                'state_save_timeout_ms': 50,
                'checkpoint_collection': 'agent_checkpoints_test',
                'conversations_collection': 'conversations_test',
            },
        },
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 1,
        },
    }


@pytest.fixture
def memory_disabled_config(memory_enabled_config):
    """Configuration with STM disabled."""
    config = memory_enabled_config.copy()
    config['langchain'] = {
        'memory': {
            'enabled': False,
        }
    }
    return config


@pytest.fixture
def generate_session_id():
    """Generate a valid UUID v4 session_id."""
    return str(uuid.uuid4())


# ============================================================================
# TEST: CHECKPOINTER CREATION
# ============================================================================

class TestCheckpointerCreation:
    """Verify create_checkpointer reads correct config keys (T039)."""

    def test_create_checkpointer_uses_database_mongodb_path(self, memory_enabled_config):
        """Verify config path: database.mongodb.connection_string (not mongodb.uri)."""
        from core.langgraph_bootstrap import create_checkpointer

        with patch('langgraph.checkpoint.mongodb.MongoDBSaver') as mock_saver, \
             patch('pymongo.MongoClient') as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value = mock_client
            mock_saver.return_value = MagicMock()
            result = create_checkpointer(memory_enabled_config)

            assert result is not None
            mock_client_cls.assert_called_once_with(
                'mongodb://testuser:testpass@localhost:27017/test_db',
            )
            mock_saver.assert_called_once_with(
                client=mock_client,
                db_name='stock_assistant_test',
                checkpoint_collection_name='agent_checkpoints_test',
            )

    def test_create_checkpointer_returns_none_when_disabled(self, memory_disabled_config):
        """Verify checkpointer is None when memory disabled."""
        from core.langgraph_bootstrap import create_checkpointer

        result = create_checkpointer(memory_disabled_config)
        assert result is None

    def test_create_checkpointer_returns_none_on_empty_connection_string(self, memory_enabled_config):
        """Verify graceful fallback when connection_string is empty."""
        from core.langgraph_bootstrap import create_checkpointer

        memory_enabled_config['database']['mongodb']['connection_string'] = ''
        result = create_checkpointer(memory_enabled_config)
        assert result is None

    def test_create_checkpointer_handles_import_error(self, memory_enabled_config):
        """Verify graceful fallback when MongoDBSaver package not installed."""
        from core.langgraph_bootstrap import create_checkpointer

        with patch.dict('sys.modules', {'langgraph.checkpoint.mongodb': None}):
            result = create_checkpointer(memory_enabled_config)
            assert result is None

    def test_create_checkpointer_handles_connection_error(self, memory_enabled_config):
        """Verify graceful fallback when MongoDB connection fails."""
        from core.langgraph_bootstrap import create_checkpointer

        with patch('langgraph.checkpoint.mongodb.MongoDBSaver', side_effect=Exception("Connection refused")):
            result = create_checkpointer(memory_enabled_config)
            assert result is None


# ============================================================================
# TEST: AGENT IMPORT MIGRATION (T038)
# ============================================================================

class TestAgentImportMigration:
    """Verify create_react_agent → create_agent migration."""

    def test_agent_uses_create_agent_not_create_react_agent(self):
        """Verify stock_assistant_agent imports from langchain.agents."""
        import core.stock_assistant_agent as agent_module
        
        # Check the module uses create_agent (from langchain.agents)
        assert hasattr(agent_module, 'create_agent')
        
        # The old import should NOT be present
        assert not hasattr(agent_module, 'create_react_agent')

    def test_agent_build_uses_system_prompt_param(self, memory_enabled_config):
        """Verify _build_agent_executor uses system_prompt= (not prompt=)."""
        from core.stock_assistant_agent import StockAssistantAgent

        with patch('core.stock_assistant_agent.create_agent') as mock_create:
            mock_create.return_value = MagicMock()
            with patch('core.stock_assistant_agent.ModelClientFactory'):
                with patch('core.stock_assistant_agent.get_tool_registry') as mock_reg:
                    mock_tool = MagicMock()
                    mock_tool.name = 'test_tool'
                    mock_reg.return_value = MagicMock()
                    mock_reg.return_value.get_enabled_tools.return_value = [mock_tool]
                    mock_reg.return_value.__len__ = lambda self: 1

                    with patch.object(StockAssistantAgent, '_initialize_tools'):
                        agent = StockAssistantAgent.__new__(StockAssistantAgent)
                        agent.config = memory_enabled_config
                        agent.logger = MagicMock()
                        agent._checkpointer = None
                        agent._tool_registry = mock_reg.return_value

                        agent._build_agent_executor()

                        # Verify create_agent was called with system_prompt
                        call_kwargs = mock_create.call_args
                        assert 'system_prompt' in call_kwargs.kwargs or \
                               (len(call_kwargs.args) >= 3), \
                               "create_agent should be called with system_prompt parameter"

    def test_no_deprecation_warning_on_import(self):
        """Verify no LangGraphDeprecatedSinceV10 warning on agent import."""
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # Force re-import to check for warnings
            import importlib
            import core.stock_assistant_agent
            importlib.reload(core.stock_assistant_agent)
            
            deprecation_warnings = [
                x for x in w
                if 'create_react_agent' in str(x.message)
                or 'LangGraphDeprecated' in str(x.category.__name__)
            ]
            assert len(deprecation_warnings) == 0, \
                f"Should not have deprecation warnings: {[str(w.message) for w in deprecation_warnings]}"


# ============================================================================
# TEST: API SERVER CHECKPOINTER WIRING (T040)
# ============================================================================

class TestAPIServerCheckpointerWiring:
    """Verify APIServer wires checkpointer into agent."""

    @patch('web.api_server.ServiceFactory')
    @patch('web.api_server.RepositoryFactory')
    @patch('web.api_server.OpenAIModelRegistry')
    @patch('web.api_server.ConfigLoader')
    @patch('web.api_server.DataManager')
    @patch('web.api_server.StockAssistantAgent')
    @patch('web.api_server.create_checkpointer')
    def test_api_server_passes_checkpointer_to_agent(
        self,
        mock_create_cp,
        mock_agent_cls,
        mock_dm,
        mock_config_loader,
        mock_model_registry,
        mock_repo_factory,
        mock_service_factory,
        memory_enabled_config,
    ):
        """APIServer should call create_checkpointer and pass to agent."""
        mock_checkpointer = MagicMock()
        mock_create_cp.return_value = mock_checkpointer
        mock_config_loader.load_config.return_value = memory_enabled_config
        mock_agent_cls.return_value = MagicMock()
        mock_dm.return_value = MagicMock()
        
        # Mock RepositoryFactory methods
        mock_repo_inst = MagicMock()
        mock_repo_factory.return_value = mock_repo_inst
        mock_repo_inst.get_cache_repository.return_value = MagicMock()
        mock_repo_factory.create_cache_repository.return_value = MagicMock()
        
        # Mock ServiceFactory
        mock_svc_inst = MagicMock()
        mock_service_factory.return_value = mock_svc_inst
        mock_svc_inst.get_chat_service.return_value = MagicMock()

        from web.api_server import APIServer
        server = APIServer()

        # Verify create_checkpointer was called with config
        mock_create_cp.assert_called_once_with(memory_enabled_config)

        # Verify agent was constructed with checkpointer
        mock_agent_cls.assert_called_once()
        call_kwargs = mock_agent_cls.call_args
        assert call_kwargs.kwargs.get('checkpointer') is mock_checkpointer, \
            "APIServer must pass checkpointer to StockAssistantAgent"

    @patch('web.api_server.ServiceFactory')
    @patch('web.api_server.RepositoryFactory')
    @patch('web.api_server.OpenAIModelRegistry')
    @patch('web.api_server.ConfigLoader')
    @patch('web.api_server.DataManager')
    @patch('web.api_server.StockAssistantAgent')
    @patch('web.api_server.create_checkpointer')
    def test_api_server_works_when_checkpointer_none(
        self,
        mock_create_cp,
        mock_agent_cls,
        mock_dm,
        mock_config_loader,
        mock_model_registry,
        mock_repo_factory,
        mock_service_factory,
        memory_disabled_config,
    ):
        """APIServer should work when checkpointer is None (disabled)."""
        mock_create_cp.return_value = None
        mock_config_loader.load_config.return_value = memory_disabled_config
        mock_agent_cls.return_value = MagicMock()
        mock_dm.return_value = MagicMock()

        mock_repo_inst = MagicMock()
        mock_repo_factory.return_value = mock_repo_inst
        mock_repo_inst.get_cache_repository.return_value = MagicMock()
        mock_repo_factory.create_cache_repository.return_value = MagicMock()

        mock_svc_inst = MagicMock()
        mock_service_factory.return_value = mock_svc_inst
        mock_svc_inst.get_chat_service.return_value = MagicMock()

        from web.api_server import APIServer
        server = APIServer()

        # Checkpointer should be None
        call_kwargs = mock_agent_cls.call_args
        assert call_kwargs.kwargs.get('checkpointer') is None

    @patch('web.api_server.ServiceFactory')
    @patch('web.api_server.RepositoryFactory')
    @patch('web.api_server.OpenAIModelRegistry')
    @patch('web.api_server.ConfigLoader')
    @patch('web.api_server.DataManager')
    @patch('web.api_server.StockAssistantAgent')
    @patch('web.api_server.create_checkpointer')
    def test_api_server_does_not_override_injected_agent(
        self,
        mock_create_cp,
        mock_agent_cls,
        mock_dm,
        mock_config_loader,
        mock_model_registry,
        mock_repo_factory,
        mock_service_factory,
        memory_enabled_config,
    ):
        """When agent is injected, APIServer should NOT create a new one."""
        mock_checkpointer = MagicMock()
        mock_create_cp.return_value = mock_checkpointer
        mock_config_loader.load_config.return_value = memory_enabled_config
        mock_dm.return_value = MagicMock()

        mock_repo_inst = MagicMock()
        mock_repo_factory.return_value = mock_repo_inst
        mock_repo_inst.get_cache_repository.return_value = MagicMock()
        mock_repo_factory.create_cache_repository.return_value = MagicMock()

        mock_svc_inst = MagicMock()
        mock_service_factory.return_value = mock_svc_inst
        mock_svc_inst.get_chat_service.return_value = MagicMock()

        injected_agent = MagicMock()
        from web.api_server import APIServer
        server = APIServer(agent=injected_agent)

        # Agent class should NOT be called when agent is injected
        mock_agent_cls.assert_not_called()
        assert server.agent is injected_agent


# ============================================================================
# TEST: MAIN.PY CHECKPOINTER WIRING (T040)
# ============================================================================

class TestMainCheckpointerWiring:
    """Verify main.py wires checkpointer in cli/both modes."""

    @patch('main.APIServer')
    @patch('main.create_checkpointer')
    @patch('main.DataManager')
    @patch('main.StockAssistantAgent')
    @patch('main.ConfigLoader')
    def test_cli_mode_passes_checkpointer(
        self,
        mock_config_loader,
        mock_agent_cls,
        mock_dm,
        mock_create_cp,
        mock_api_server,
        memory_enabled_config,
    ):
        """CLI mode should create checkpointer and pass to agent."""
        mock_config_loader.load_config.return_value = memory_enabled_config
        mock_checkpointer = MagicMock()
        mock_create_cp.return_value = mock_checkpointer
        mock_agent_inst = MagicMock()
        mock_agent_cls.return_value = mock_agent_inst

        import sys
        with patch.object(sys, 'argv', ['main.py', '--mode', 'cli']):
            from main import main
            main()

        mock_create_cp.assert_called_once_with(memory_enabled_config)
        call_kwargs = mock_agent_cls.call_args
        assert call_kwargs.kwargs.get('checkpointer') is mock_checkpointer


# ============================================================================
# TEST: FULL FLOW — MULTI-TURN WITH MOCKED CHECKPOINTER
# ============================================================================

class TestMultiTurnSessionFlow:
    """End-to-end flow: session creation → context recall → persistence."""

    def test_multi_turn_with_session_id_uses_thread_id(self, memory_enabled_config, generate_session_id):
        """Full flow: two queries with same session_id share thread_id."""
        from core.stock_assistant_agent import StockAssistantAgent
        from langchain_core.messages import AIMessage

        mock_checkpointer = MagicMock()

        with patch('core.stock_assistant_agent.create_agent') as mock_create:
            mock_executor = MagicMock()
            # Simulate agent responses
            mock_executor.invoke.return_value = {
                "messages": [AIMessage(content="I can help with AAPL.")]
            }
            mock_create.return_value = mock_executor

            with patch('core.stock_assistant_agent.ModelClientFactory'):
                with patch.object(StockAssistantAgent, '_initialize_tools'):
                    agent = StockAssistantAgent.__new__(StockAssistantAgent)
                    agent.config = memory_enabled_config
                    agent.data_manager = MagicMock()
                    agent.logger = MagicMock()
                    agent._checkpointer = mock_checkpointer
                    agent._tool_registry = MagicMock()
                    agent._tool_registry.get_enabled_tools.return_value = []
                    agent._agent_executor = mock_executor

                    session_id = generate_session_id

                    # First message
                    result1 = agent.process_query("Tell me about AAPL", session_id=session_id)
                    assert result1 == "I can help with AAPL."

                    # Verify thread_id was passed
                    call1_config = mock_executor.invoke.call_args_list[0][1].get('config')
                    assert call1_config is not None
                    assert call1_config['configurable']['thread_id'] == session_id

                    # Second message (follow-up)
                    mock_executor.invoke.return_value = {
                        "messages": [AIMessage(content="Based on our discussion about AAPL...")]
                    }
                    result2 = agent.process_query("What's the outlook?", session_id=session_id)
                    assert "AAPL" in result2

                    # Same thread_id
                    call2_config = mock_executor.invoke.call_args_list[1][1].get('config')
                    assert call2_config['configurable']['thread_id'] == session_id

    def test_stateless_mode_no_thread_id(self, memory_enabled_config):
        """Verify no thread_id when session_id is None."""
        from core.stock_assistant_agent import StockAssistantAgent
        from langchain_core.messages import AIMessage

        with patch('core.stock_assistant_agent.create_agent') as mock_create:
            mock_executor = MagicMock()
            mock_executor.invoke.return_value = {
                "messages": [AIMessage(content="Hello!")]
            }
            mock_create.return_value = mock_executor

            with patch('core.stock_assistant_agent.ModelClientFactory'):
                with patch.object(StockAssistantAgent, '_initialize_tools'):
                    agent = StockAssistantAgent.__new__(StockAssistantAgent)
                    agent.config = memory_enabled_config
                    agent.data_manager = MagicMock()
                    agent.logger = MagicMock()
                    agent._checkpointer = None
                    agent._tool_registry = MagicMock()
                    agent._tool_registry.get_enabled_tools.return_value = []
                    agent._agent_executor = mock_executor

                    result = agent.process_query("Hello")
                    assert result == "Hello!"

                    # Verify no thread_id config
                    call_config = mock_executor.invoke.call_args[1].get('config')
                    assert call_config is None


# ============================================================================
# TEST: MASK CONNECTION STRING
# ============================================================================

class TestMaskConnectionString:
    """Verify password masking in connection string logging."""

    def test_masks_password_in_connection_string(self):
        """Password should be replaced with *** in logs."""
        from core.langgraph_bootstrap import _mask_connection_string

        masked = _mask_connection_string("mongodb://admin:s3cret@host:27017/db")
        assert "s3cret" not in masked
        assert "***" in masked
        assert "admin" in masked

    def test_handles_no_auth_connection_string(self):
        """Connection string without auth should pass through unchanged."""
        from core.langgraph_bootstrap import _mask_connection_string

        result = _mask_connection_string("mongodb://localhost:27017/db")
        assert result == "mongodb://localhost:27017/db"

    def test_handles_special_chars_in_password(self):
        """Passwords with special chars should still be masked."""
        from core.langgraph_bootstrap import _mask_connection_string

        masked = _mask_connection_string("mongodb://user:p@ss%23word@host/db")
        assert "p@ss%23word" not in masked
        assert "***" in masked


# ============================================================================
# TEST: CONFIG STRUCTURE ALIGNMENT
# ============================================================================

class TestConfigStructureAlignment:
    """Verify code reads config keys matching actual config.yaml structure."""

    def test_checkpointer_reads_database_mongodb_connection_string(self, memory_enabled_config):
        """create_checkpointer must read database.mongodb.connection_string."""
        from core.langgraph_bootstrap import create_checkpointer

        # Remove old-style keys to ensure code doesn't fall back
        assert 'mongodb' not in memory_enabled_config or \
               'uri' not in memory_enabled_config.get('mongodb', {}), \
               "Test config should NOT have old-style mongodb.uri"

        with patch('langgraph.checkpoint.mongodb.MongoDBSaver') as mock_saver, \
             patch('pymongo.MongoClient') as mock_client_cls:
            mock_client_cls.return_value = MagicMock()
            mock_saver.return_value = MagicMock()
            result = create_checkpointer(memory_enabled_config)
            assert result is not None

    def test_old_config_keys_do_not_work(self):
        """Old-style config (mongodb.uri) should NOT produce a checkpointer."""
        from core.langgraph_bootstrap import create_checkpointer

        old_style_config = {
            'langchain': {'memory': {'enabled': True,
                'summarize_threshold': 4000, 'max_messages': 50,
                'messages_to_keep': 10, 'max_content_size': 32768,
                'summary_max_length': 500, 'context_load_timeout_ms': 500,
                'state_save_timeout_ms': 50,
                'checkpoint_collection': 'agent_checkpoints',
                'conversations_collection': 'conversations'}},
            'mongodb': {
                'uri': 'mongodb://localhost:27017/db',
                'database': 'stock_assistant',
            },
        }
        result = create_checkpointer(old_style_config)
        assert result is None, "Old-style mongodb.uri should not work anymore"
