"""
End-to-end runtime verification tests for STM wiring.

Reference: specs/spec-driven-development-pilot/tasks.md - T041
Verifies that Phase 9 integration gaps are fixed:
- Gap 0: create_react_agent → create_agent migration
- Gap 1: Checkpointer wired into APIServer and main.py
- Gap 2: MongoDB config keys match actual config.yaml structure

Success Criteria:
- Agent starts with checkpointer when langchain.memory.enabled: true
- /api/chat with conversation_id persists conversation to MongoDB
- Multi-turn context recall works across messages
- Stateless mode (no conversation_id) still works
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
def generate_conversation_id():
    """Generate a valid UUID v4 conversation_id."""
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

    def test_multi_turn_with_conversation_id_uses_thread_id(self, memory_enabled_config, generate_conversation_id):
        """Full flow: two queries with same conversation_id share thread_id."""
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

                    conversation_id = generate_conversation_id

                    # First message
                    result1 = agent.process_query("Tell me about AAPL", conversation_id=conversation_id)
                    assert result1 == "I can help with AAPL."

                    # Verify thread_id was passed
                    call1_config = mock_executor.invoke.call_args_list[0][1].get('config')
                    assert call1_config is not None
                    assert call1_config['configurable']['thread_id'] == conversation_id

                    # Second message (follow-up)
                    mock_executor.invoke.return_value = {
                        "messages": [AIMessage(content="Based on our discussion about AAPL...")]
                    }
                    result2 = agent.process_query("What's the outlook?", conversation_id=conversation_id)
                    assert "AAPL" in result2

                    # Same thread_id
                    call2_config = mock_executor.invoke.call_args_list[1][1].get('config')
                    assert call2_config['configurable']['thread_id'] == conversation_id

    def test_stateless_mode_no_thread_id(self, memory_enabled_config):
        """Verify no thread_id when conversation_id is None."""
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


# ============================================================================
# TEST: RUNTIME METADATA CONSISTENCY (T032 / US5)
# ============================================================================

class TestRuntimeMetadataConsistency:
    """Verify conversation metadata stays consistent with management API view.

    After processing a query through the agent:
    - message_count should increment
    - last_activity_at should update
    - total_tokens should accumulate
    """

    @pytest.fixture
    def mock_conversation_repo(self):
        """Mock ConversationRepository with in-memory state."""
        repo = MagicMock()
        # Mutable state simulating a live conversation document
        state = {
            "conversation_id": "conv-123",
            "session_id": "sess-abc",
            "workspace_id": "ws-xyz",
            "user_id": "user-1",
            "status": "active",
            "message_count": 0,
            "total_tokens": 0,
            "last_activity_at": None,
        }

        def update_metadata_side_effect(conversation_id, **kwargs):
            delta_msg = kwargs.get("message_count_delta", 0)
            delta_tok = kwargs.get("token_delta", 0)
            ts = kwargs.get("last_activity_at")
            state["message_count"] += delta_msg
            state["total_tokens"] += delta_tok
            if ts:
                state["last_activity_at"] = ts
            return dict(state)

        repo.update_metadata.side_effect = update_metadata_side_effect
        repo.find_by_conversation_id.side_effect = lambda cid: dict(state) if cid == "conv-123" else None
        repo.health_check.return_value = (True, {"component": "conversation_repository"})
        repo._state = state  # expose for assertions
        return repo

    def test_message_count_increments_after_record(self, mock_conversation_repo):
        """After recording metadata, message_count should be incremented."""
        from services.conversation_service import ConversationService

        svc = ConversationService(conversation_repository=mock_conversation_repo)
        svc.record_message_metadata("conv-123", tokens_used=50)

        assert mock_conversation_repo._state["message_count"] == 1

    def test_total_tokens_accumulate_after_record(self, mock_conversation_repo):
        """Tokens should accumulate across multiple record calls."""
        from services.conversation_service import ConversationService

        svc = ConversationService(conversation_repository=mock_conversation_repo)
        svc.record_message_metadata("conv-123", tokens_used=50)
        svc.record_message_metadata("conv-123", tokens_used=30)

        assert mock_conversation_repo._state["total_tokens"] == 80

    def test_last_activity_at_updates_after_record(self, mock_conversation_repo):
        """last_activity_at should be set after recording metadata."""
        from services.conversation_service import ConversationService

        svc = ConversationService(conversation_repository=mock_conversation_repo)
        svc.record_message_metadata("conv-123", tokens_used=10)

        assert mock_conversation_repo._state["last_activity_at"] is not None

    def test_management_api_view_matches_after_record(self, mock_conversation_repo):
        """get_conversation should reflect the updated metadata."""
        from services.conversation_service import ConversationService

        svc = ConversationService(conversation_repository=mock_conversation_repo)
        svc.record_message_metadata("conv-123", tokens_used=100)
        svc.record_message_metadata("conv-123", tokens_used=200)

        doc = svc.get_conversation("conv-123")
        assert doc["message_count"] == 2
        assert doc["total_tokens"] == 300


# ============================================================================
# TEST: RECONCILIATION ANOMALY DETECTION (T036)
# ============================================================================

class TestReconciliationAnomalyDetection:
    """Verify reconciliation scan detects drift between checkpoint and management state."""

    @pytest.fixture
    def mock_conversation_repo(self):
        """Conversation repository mock with configurable behaviour."""
        repo = MagicMock()
        repo.health_check.return_value = (True, {"component": "conversation_repo"})
        # Defaults: nothing found
        repo.find_by_thread_id.return_value = None
        repo.get_all.return_value = []
        repo.find_stale.return_value = []
        return repo

    @pytest.fixture
    def mock_checkpointer(self):
        """Checkpointer mock that supports list/get."""
        cp = MagicMock()
        cp.list.return_value = []
        cp.get.return_value = None
        return cp

    @pytest.fixture
    def reconciliation_service(self, mock_conversation_repo, mock_checkpointer):
        from services.runtime_reconciliation_service import RuntimeReconciliationService

        return RuntimeReconciliationService(
            conversation_repo=mock_conversation_repo,
            checkpointer=mock_checkpointer,
        )

    # ---- Orphaned threads ----

    def test_detects_orphaned_thread(
        self, reconciliation_service, mock_checkpointer, mock_conversation_repo
    ):
        """Thread in checkpointer with no matching conversation is flagged."""
        mock_checkpointer.list.return_value = [{"thread_id": "orphan-123"}]
        mock_conversation_repo.find_by_thread_id.return_value = None

        report = reconciliation_service.scan()

        assert report["anomaly_count"] >= 1
        orphans = [a for a in report["anomalies"] if a["type"] == "orphaned_thread"]
        assert len(orphans) == 1
        assert orphans[0]["thread_id"] == "orphan-123"
        assert orphans[0]["severity"] == "warning"

    def test_no_orphan_when_conversation_exists(
        self, reconciliation_service, mock_checkpointer, mock_conversation_repo
    ):
        """Thread with a matching conversation is NOT flagged as orphaned."""
        mock_checkpointer.list.return_value = [{"thread_id": "known-456"}]
        mock_conversation_repo.find_by_thread_id.return_value = {
            "conversation_id": "conv-456",
            "thread_id": "known-456",
            "status": "active",
        }

        report = reconciliation_service.scan()

        orphans = [a for a in report["anomalies"] if a["type"] == "orphaned_thread"]
        assert len(orphans) == 0

    # ---- Metadata drift ----

    def test_detects_metadata_drift(
        self, reconciliation_service, mock_checkpointer, mock_conversation_repo
    ):
        """Management message_count != checkpoint message count is flagged."""
        mock_conversation_repo.get_all.return_value = [
            {
                "conversation_id": "conv-drift",
                "thread_id": "thread-drift",
                "status": "active",
                "message_count": 5,
            }
        ]
        # Checkpoint has 7 messages
        mock_checkpointer.get.return_value = {
            "channel_values": {
                "messages": [f"msg-{i}" for i in range(7)]
            }
        }

        report = reconciliation_service.scan()

        drift = [a for a in report["anomalies"] if a["type"] == "metadata_drift"]
        assert len(drift) == 1
        assert drift[0]["expected"] == 5
        assert drift[0]["actual"] == 7
        assert drift[0]["field"] == "message_count"

    def test_no_drift_when_counts_match(
        self, reconciliation_service, mock_checkpointer, mock_conversation_repo
    ):
        """Matching message counts produce no drift anomaly."""
        mock_conversation_repo.get_all.return_value = [
            {
                "conversation_id": "conv-ok",
                "thread_id": "thread-ok",
                "status": "active",
                "message_count": 3,
            }
        ]
        mock_checkpointer.get.return_value = {
            "channel_values": {"messages": ["a", "b", "c"]}
        }

        report = reconciliation_service.scan()

        drift = [a for a in report["anomalies"] if a["type"] == "metadata_drift"]
        assert len(drift) == 0

    # ---- Stale conversations ----

    def test_detects_stale_conversation(
        self, reconciliation_service, mock_conversation_repo
    ):
        """Active conversation with old last_activity_at is flagged."""
        from datetime import datetime, timedelta, timezone

        old_ts = datetime.now(timezone.utc) - timedelta(days=60)
        mock_conversation_repo.find_stale.return_value = [
            {
                "conversation_id": "conv-stale",
                "status": "active",
                "last_activity_at": old_ts,
            }
        ]

        report = reconciliation_service.scan()

        stale = [a for a in report["anomalies"] if a["type"] == "stale_conversation"]
        assert len(stale) == 1
        assert stale[0]["conversation_id"] == "conv-stale"
        assert stale[0]["severity"] == "info"

    def test_no_stale_when_none_found(
        self, reconciliation_service, mock_conversation_repo
    ):
        """No stale-conversation anomaly when repository returns empty."""
        mock_conversation_repo.find_stale.return_value = []

        report = reconciliation_service.scan()

        stale = [a for a in report["anomalies"] if a["type"] == "stale_conversation"]
        assert len(stale) == 0

    # ---- Missing threads ----

    def test_detects_missing_thread(
        self, reconciliation_service, mock_checkpointer, mock_conversation_repo
    ):
        """Conversation with thread_id absent from checkpointer is flagged."""
        mock_conversation_repo.get_all.return_value = [
            {
                "conversation_id": "conv-missing",
                "thread_id": "thread-gone",
                "status": "active",
                "message_count": 2,
            }
        ]
        mock_checkpointer.get.return_value = None  # thread doesn't exist

        report = reconciliation_service.scan()

        missing = [a for a in report["anomalies"] if a["type"] == "missing_thread"]
        assert len(missing) == 1
        assert missing[0]["thread_id"] == "thread-gone"
        assert missing[0]["severity"] == "error"

    def test_no_missing_thread_when_checkpoint_exists(
        self, reconciliation_service, mock_checkpointer, mock_conversation_repo
    ):
        """Conversation whose thread exists in checkpointer is NOT flagged."""
        mock_conversation_repo.get_all.return_value = [
            {
                "conversation_id": "conv-ok",
                "thread_id": "thread-ok",
                "status": "active",
                "message_count": 3,
            }
        ]
        mock_checkpointer.get.return_value = {
            "channel_values": {"messages": ["a", "b", "c"]}
        }

        report = reconciliation_service.scan()

        missing = [a for a in report["anomalies"] if a["type"] == "missing_thread"]
        assert len(missing) == 0

    # ---- Report structure ----

    def test_scan_report_contains_required_fields(self, reconciliation_service):
        """Report must contain correlation_id, timestamps, anomaly_count, anomalies."""
        report = reconciliation_service.scan()

        assert "correlation_id" in report
        assert "started_at" in report
        assert "completed_at" in report
        assert "duration_ms" in report
        assert "scope" in report
        assert "anomaly_count" in report
        assert "anomalies" in report
        assert isinstance(report["anomalies"], list)

    def test_scan_without_checkpointer_skips_checkpoint_checks(
        self, mock_conversation_repo
    ):
        """When checkpointer is None, orphaned/drift/missing checks are skipped."""
        from services.runtime_reconciliation_service import RuntimeReconciliationService

        svc = RuntimeReconciliationService(
            conversation_repo=mock_conversation_repo,
            checkpointer=None,
        )

        report = svc.scan()

        # Only stale-conversation detection should run (no checkpointer needed)
        checkpoint_types = {"orphaned_thread", "metadata_drift", "missing_thread"}
        for anomaly in report["anomalies"]:
            assert anomaly["type"] not in checkpoint_types

    # ---- Error resilience ----

    def test_scan_continues_on_orphan_detection_error(
        self, reconciliation_service, mock_checkpointer, mock_conversation_repo
    ):
        """If orphan detection raises, scan still returns a valid report."""
        mock_checkpointer.list.side_effect = RuntimeError("connection lost")
        mock_conversation_repo.find_stale.return_value = [
            {"conversation_id": "conv-stale", "status": "active", "last_activity_at": "old"}
        ]

        report = reconciliation_service.scan()

        # Stale detection should still produce results
        assert report["anomaly_count"] >= 1
        assert any(a["type"] == "stale_conversation" for a in report["anomalies"])


# ============================================================================
# TEST: RECONCILIATION STRUCTURED LOGGING (T037)
# ============================================================================

class TestReconciliationStructuredLogging:
    """Verify scan emits structured log events: scan_started, anomaly_detected, scan_completed."""

    @pytest.fixture
    def mock_conversation_repo(self):
        repo = MagicMock()
        repo.health_check.return_value = (True, {})
        repo.find_by_thread_id.return_value = None
        repo.get_all.return_value = []
        repo.find_stale.return_value = []
        return repo

    @pytest.fixture
    def mock_checkpointer(self):
        cp = MagicMock()
        cp.list.return_value = []
        cp.get.return_value = None
        return cp

    @pytest.fixture
    def reconciliation_service(self, mock_conversation_repo, mock_checkpointer):
        from services.runtime_reconciliation_service import RuntimeReconciliationService

        return RuntimeReconciliationService(
            conversation_repo=mock_conversation_repo,
            checkpointer=mock_checkpointer,
        )

    def test_scan_started_log_with_correlation_id(self, reconciliation_service):
        """scan() must emit a scan_started log with correlation_id."""
        mock_logger = MagicMock()
        reconciliation_service._logger = mock_logger
        reconciliation_service.scan()

        info_calls = mock_logger.info.call_args_list
        started_calls = [
            c for c in info_calls
            if c.kwargs.get("extra", {}).get("action") == "scan_started"
        ]
        assert len(started_calls) == 1, "Expected exactly one scan_started log"
        extra = started_calls[0].kwargs["extra"]
        assert "correlation_id" in extra
        assert len(extra["correlation_id"]) == 36  # UUID format

    def test_scan_completed_log_with_duration(self, reconciliation_service):
        """scan() must emit a scan_completed log with anomaly_count and duration_ms."""
        mock_logger = MagicMock()
        reconciliation_service._logger = mock_logger
        reconciliation_service.scan()

        info_calls = mock_logger.info.call_args_list
        completed_calls = [
            c for c in info_calls
            if c.kwargs.get("extra", {}).get("action") == "scan_completed"
        ]
        assert len(completed_calls) == 1, "Expected exactly one scan_completed log"
        extra = completed_calls[0].kwargs["extra"]
        assert "anomaly_count" in extra
        assert "duration_ms" in extra
        assert isinstance(extra["duration_ms"], (int, float))

    def test_anomaly_detected_log_with_type_and_severity(
        self, reconciliation_service, mock_checkpointer, mock_conversation_repo
    ):
        """Each anomaly must emit an anomaly_detected warning with type and severity."""
        # Inject an orphaned thread
        mock_checkpointer.list.return_value = [{"thread_id": "orphan-log-test"}]
        mock_conversation_repo.find_by_thread_id.return_value = None

        mock_logger = MagicMock()
        reconciliation_service._logger = mock_logger
        reconciliation_service.scan()

        warning_calls = mock_logger.warning.call_args_list
        anomaly_calls = [
            c for c in warning_calls
            if c.kwargs.get("extra", {}).get("action") == "anomaly_detected"
        ]
        assert len(anomaly_calls) >= 1, "Expected at least one anomaly_detected log"
        extra = anomaly_calls[0].kwargs["extra"]
        assert "type" in extra
        assert "severity" in extra
        assert "correlation_id" in extra

    def test_correlation_id_consistent_across_scan(
        self, reconciliation_service, mock_checkpointer, mock_conversation_repo
    ):
        """All log events in a single scan share the same correlation_id."""
        mock_checkpointer.list.return_value = [{"thread_id": "cid-check"}]
        mock_conversation_repo.find_by_thread_id.return_value = None

        mock_logger = MagicMock()
        reconciliation_service._logger = mock_logger
        reconciliation_service.scan()

        all_extras = []
        for call in mock_logger.info.call_args_list + mock_logger.warning.call_args_list:
            extra = call.kwargs.get("extra", {})
            if "correlation_id" in extra:
                all_extras.append(extra["correlation_id"])

        assert len(set(all_extras)) == 1, (
            f"All logs must share one correlation_id, got: {set(all_extras)}"
        )


# ============================================================================
# TEST: STM CONVERSATION ISOLATION (T046 / US8)
# ============================================================================

class TestSTMConversationIsolation:
    """Verify conversation_id == thread_id STM isolation model.

    Replaces legacy session_id == thread_id assumptions with explicit
    coverage for the canonical conversation-scoped STM mapping.
    """

    def test_conversation_id_maps_to_thread_id(self, memory_enabled_config, generate_conversation_id):
        """Canonical mapping: conversation_id passed to agent becomes thread_id."""
        from core.stock_assistant_agent import StockAssistantAgent
        from langchain_core.messages import AIMessage

        with patch('core.stock_assistant_agent.StockAssistantAgent._build_agent_executor'):
            agent = StockAssistantAgent.__new__(StockAssistantAgent)
            agent._config = memory_enabled_config
            agent._checkpointer = MagicMock()
            agent._agent_executor = MagicMock()
            agent._agent_executor.invoke.return_value = {
                "messages": [AIMessage(content="Response")]
            }
            agent._use_react = True
            agent._use_streaming = False
            agent.logger = MagicMock()

            cid = generate_conversation_id
            agent.process_query("Test", conversation_id=cid)

            config = agent._agent_executor.invoke.call_args[1].get('config', {})
            assert config['configurable']['thread_id'] == cid

    def test_same_conversation_restore_yields_same_checkpoint(
        self, memory_enabled_config, generate_conversation_id
    ):
        """Same conversation_id across turns yields same thread_id → same checkpoint."""
        from core.stock_assistant_agent import StockAssistantAgent
        from langchain_core.messages import AIMessage

        with patch('core.stock_assistant_agent.StockAssistantAgent._build_agent_executor'):
            agent = StockAssistantAgent.__new__(StockAssistantAgent)
            agent._config = memory_enabled_config
            agent._checkpointer = MagicMock()
            agent._agent_executor = MagicMock()
            agent._agent_executor.invoke.return_value = {
                "messages": [AIMessage(content="Answer")]
            }
            agent._use_react = True
            agent._use_streaming = False
            agent.logger = MagicMock()

            cid = generate_conversation_id

            # Turn 1
            agent.process_query("First question", conversation_id=cid)
            tid_1 = agent._agent_executor.invoke.call_args_list[0][1]['config']['configurable']['thread_id']

            # Turn 2 (resumed conversation)
            agent.process_query("Follow-up", conversation_id=cid)
            tid_2 = agent._agent_executor.invoke.call_args_list[1][1]['config']['configurable']['thread_id']

            assert tid_1 == tid_2 == cid

    def test_cross_conversation_isolation(self, memory_enabled_config):
        """Different conversation_ids yield different thread_ids → independent checkpoints."""
        from core.stock_assistant_agent import StockAssistantAgent
        from langchain_core.messages import AIMessage

        with patch('core.stock_assistant_agent.StockAssistantAgent._build_agent_executor'):
            agent = StockAssistantAgent.__new__(StockAssistantAgent)
            agent._config = memory_enabled_config
            agent._checkpointer = MagicMock()
            agent._agent_executor = MagicMock()
            agent._agent_executor.invoke.return_value = {
                "messages": [AIMessage(content="Response")]
            }
            agent._use_react = True
            agent._use_streaming = False
            agent.logger = MagicMock()

            cid_a = str(uuid.uuid4())
            cid_b = str(uuid.uuid4())

            agent.process_query("Question A", conversation_id=cid_a)
            tid_a = agent._agent_executor.invoke.call_args_list[0][1]['config']['configurable']['thread_id']

            agent.process_query("Question B", conversation_id=cid_b)
            tid_b = agent._agent_executor.invoke.call_args_list[1][1]['config']['configurable']['thread_id']

            assert tid_a == cid_a
            assert tid_b == cid_b
            assert tid_a != tid_b

    def test_stateless_mode_no_checkpoint_binding(self, memory_enabled_config):
        """No conversation_id means no checkpoint binding (stateless mode)."""
        from core.stock_assistant_agent import StockAssistantAgent
        from langchain_core.messages import AIMessage

        with patch('core.stock_assistant_agent.StockAssistantAgent._build_agent_executor'):
            agent = StockAssistantAgent.__new__(StockAssistantAgent)
            agent._config = memory_enabled_config
            agent._checkpointer = MagicMock()
            agent._agent_executor = MagicMock()
            agent._agent_executor.invoke.return_value = {
                "messages": [AIMessage(content="Stateless response")]
            }
            agent._use_react = True
            agent._use_streaming = False
            agent.logger = MagicMock()

            # No conversation_id → stateless
            agent.process_query("Hello")

            config = agent._agent_executor.invoke.call_args[1].get('config')
            if config and 'configurable' in config:
                assert config['configurable'].get('thread_id') is None

    def test_resumed_checkpoint_retrieval_preserves_thread_id(
        self, memory_enabled_config
    ):
        """Starting a new message in an existing conversation retrieves prior checkpoint thread_id."""
        from core.stock_assistant_agent import StockAssistantAgent
        from langchain_core.messages import AIMessage

        cid = str(uuid.uuid4())

        with patch('core.stock_assistant_agent.StockAssistantAgent._build_agent_executor'):
            agent = StockAssistantAgent.__new__(StockAssistantAgent)
            agent._config = memory_enabled_config
            agent._checkpointer = MagicMock()
            agent._agent_executor = MagicMock()
            agent._agent_executor.invoke.return_value = {
                "messages": [AIMessage(content="Resumed")]
            }
            agent._use_react = True
            agent._use_streaming = False
            agent.logger = MagicMock()

            # Simulate resuming: first query in a "previously-active" conversation
            agent.process_query("Continue from where we left off", conversation_id=cid)

            config = agent._agent_executor.invoke.call_args[1].get('config', {})
            # The thread_id MUST equal the conversation_id so the checkpointer
            # retrieves the correct prior checkpoint
            assert config['configurable']['thread_id'] == cid
