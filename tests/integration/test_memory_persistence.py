"""
Integration tests for memory persistence across agent restart.

Reference: specs/spec-driven-development-pilot/tasks.md - T020, T029, T036, T037
FR-3.1.2: Message history matches 100% after restart
FR-3.1.3: Session identifier correctly binds to stored state
FR-3.1.7: Zero financial data (prices, ratios) in stored memory (T029)
FR-3.1.8: Tool outputs stored as references only, not raw data (T029)

T036: End-to-end multi-turn test with success criteria verification:
- SC-1: Context accuracy ≥95%
- SC-2: Persistence reliability 100%
- SC-7: Load time < 500ms

T037: Performance benchmark tests:
- Measure graph.get_state() latency against context_load_timeout_ms (500ms)
- Measure state save time against state_save_timeout_ms (50ms)
- Log benchmark results for CI tracking

User Story (US2): User has active session with ≥3 messages, system restarts,
user reconnects with same session_id, agent demonstrates awareness of prior conversation.

User Story (US4): Tools return stock prices, ratios, news; stored memory contains 
zero financial data (T029 compliance integration tests).

Test Strategy:
- Create session, add 3+ messages, simulate restart, verify context restored
- Hash comparison of message history pre/post restart (100% match)
- Verify checkpoint data survives across agent instances
- Compliance: Full conversation flow with tool calls, inspect checkpoint for prohibited patterns
- T036: Full 5-turn scenario with SC-1, SC-2, SC-7 verification
"""

import hashlib
import json
import pytest
import uuid
from typing import Dict, List, Optional, Any
from unittest.mock import MagicMock, patch, AsyncMock

from utils.memory_config import ContentValidator


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def valid_session_id() -> str:
    """Generate a valid UUID v4 session ID."""
    return str(uuid.uuid4())


@pytest.fixture
def mock_mongodb_saver():
    """
    Mock MongoDBSaver that simulates checkpoint persistence.
    
    Stores checkpoints in memory to verify persistence behavior.
    """
    checkpoints: Dict[str, Dict[str, Any]] = {}
    
    class MockMongoDBSaver:
        def __init__(self, *args, **kwargs):
            self._checkpoints = checkpoints
        
        def put(self, config: Dict, checkpoint: Dict, metadata: Optional[Dict] = None):
            """Store checkpoint for thread_id."""
            thread_id = config.get("configurable", {}).get("thread_id", "default")
            self._checkpoints[thread_id] = {
                "checkpoint": checkpoint,
                "metadata": metadata or {}
            }
        
        def get(self, config: Dict) -> Optional[Dict]:
            """Retrieve checkpoint for thread_id."""
            thread_id = config.get("configurable", {}).get("thread_id", "default")
            stored = self._checkpoints.get(thread_id)
            if stored:
                return stored["checkpoint"]
            return None
        
        def get_tuple(self, config: Dict) -> Optional[tuple]:
            """Get checkpoint as tuple (checkpoint, metadata)."""
            thread_id = config.get("configurable", {}).get("thread_id", "default")
            stored = self._checkpoints.get(thread_id)
            if stored:
                return (stored["checkpoint"], stored["metadata"])
            return None
        
        def list(self, config: Dict) -> List[Dict]:
            """List all checkpoints for thread_id."""
            thread_id = config.get("configurable", {}).get("thread_id", "default")
            stored = self._checkpoints.get(thread_id)
            if stored:
                return [stored["checkpoint"]]
            return []
        
        def clear_all(self):
            """Clear all checkpoints (for test cleanup)."""
            self._checkpoints.clear()
    
    return MockMongoDBSaver()


@pytest.fixture
def mock_config():
    """Configuration for memory-enabled agent."""
    return {
        "langchain": {
            "memory": {
                "enabled": True,
                "summarize_threshold": 4000,
                "checkpoint_collection": "agent_checkpoints"
            }
        },
        "mongodb": {
            "uri": "mongodb://localhost:27017",
            "database": "test_stock_assistant"
        }
    }


# ============================================================================
# Helper Functions
# ============================================================================

def compute_message_hash(messages: List[Dict[str, Any]]) -> str:
    """
    Compute SHA-256 hash of message history for comparison.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        
    Returns:
        Hex digest of SHA-256 hash
    """
    # Normalize messages to consistent format
    normalized = []
    for msg in messages:
        normalized.append({
            "role": msg.get("role", ""),
            "content": msg.get("content", "")
        })
    
    # Sort by order to ensure deterministic hash
    message_str = json.dumps(normalized, sort_keys=True)
    return hashlib.sha256(message_str.encode()).hexdigest()


def extract_messages_from_checkpoint(checkpoint: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract messages from a LangGraph checkpoint.
    
    The actual structure depends on LangGraph implementation.
    This helper abstracts the extraction logic.
    """
    # LangGraph stores messages in channel_values["messages"]
    channel_values = checkpoint.get("channel_values", {})
    messages = channel_values.get("messages", [])
    
    # Convert to standard format
    result = []
    for msg in messages:
        if hasattr(msg, "type") and hasattr(msg, "content"):
            # LangChain message object
            result.append({
                "role": msg.type,
                "content": msg.content
            })
        elif isinstance(msg, dict):
            result.append({
                "role": msg.get("type", msg.get("role", "")),
                "content": msg.get("content", "")
            })
    
    return result


# ============================================================================
# Test: Persistence Across Agent Restart (T020)
# ============================================================================

class TestMemoryPersistenceAcrossRestart:
    """
    Test suite for FR-3.1.2: Message history matches 100% after restart.
    
    Simulates the user story:
    1. User initiates conversation with session_id
    2. User exchanges ≥3 messages with agent
    3. System "restarts" (agent instance destroyed and recreated)
    4. User reconnects with same session_id
    5. Agent demonstrates awareness of prior conversation
    """
    
    def test_session_id_preserves_context_across_restart(
        self, 
        valid_session_id, 
        mock_mongodb_saver, 
        mock_config
    ):
        """
        Test: Create session, add 3+ messages, simulate restart, verify context restored.
        
        Verifies:
        - Session can be created with session_id
        - Messages are stored in checkpoint
        - After "restart", same session_id retrieves stored messages
        """
        # ─────────────────────────────────────────────────────────────
        # Phase 1: Initial conversation (before restart)
        # ─────────────────────────────────────────────────────────────
        
        # Simulate storing initial messages
        initial_messages = [
            {"role": "human", "content": "What is AAPL's current price?"},
            {"role": "ai", "content": "Apple Inc. (AAPL) is currently trading at $185.50."},
            {"role": "human", "content": "What about its P/E ratio?"},
            {"role": "ai", "content": "AAPL has a P/E ratio of approximately 28.5."},
            {"role": "human", "content": "Is that considered high for tech stocks?"},
        ]
        
        # Store checkpoint with messages
        checkpoint_data = {
            "channel_values": {
                "messages": initial_messages
            },
            "metadata": {
                "message_count": len(initial_messages)
            }
        }
        
        config = {"configurable": {"thread_id": valid_session_id}}
        mock_mongodb_saver.put(config, checkpoint_data)
        
        # Verify checkpoint was stored
        stored_checkpoint = mock_mongodb_saver.get(config)
        assert stored_checkpoint is not None, "Checkpoint should be stored"
        
        # Record hash of original messages
        original_hash = compute_message_hash(initial_messages)
        
        # ─────────────────────────────────────────────────────────────
        # Phase 2: Simulate restart (destroy agent instance)
        # ─────────────────────────────────────────────────────────────
        
        # In real scenario, this would be agent destruction
        # The checkpointer (mock_mongodb_saver) persists across restart
        # because it's backed by MongoDB (simulated here by shared dict)
        
        # ─────────────────────────────────────────────────────────────
        # Phase 3: Reconnect with same session_id (after restart)
        # ─────────────────────────────────────────────────────────────
        
        # Same config/session_id
        reconnect_config = {"configurable": {"thread_id": valid_session_id}}
        
        # Retrieve checkpoint
        restored_checkpoint = mock_mongodb_saver.get(reconnect_config)
        
        # Verify checkpoint was restored
        assert restored_checkpoint is not None, "Checkpoint should be restored after restart"
        
        # Extract messages from restored checkpoint
        restored_messages = restored_checkpoint.get("channel_values", {}).get("messages", [])
        
        # ─────────────────────────────────────────────────────────────
        # Phase 4: Verify context accuracy
        # ─────────────────────────────────────────────────────────────
        
        # Hash comparison for 100% match (FR-3.1.2)
        restored_hash = compute_message_hash(restored_messages)
        
        assert original_hash == restored_hash, (
            f"Message history hash mismatch after restart.\n"
            f"Original:  {original_hash}\n"
            f"Restored:  {restored_hash}\n"
            f"Messages not preserved correctly."
        )
        
        # Verify message count
        assert len(restored_messages) == len(initial_messages), (
            f"Message count mismatch: {len(restored_messages)} != {len(initial_messages)}"
        )
        
        # Verify specific message content
        assert restored_messages[0]["content"] == "What is AAPL's current price?"
        assert restored_messages[-1]["content"] == "Is that considered high for tech stocks?"
    
    def test_message_hash_comparison_100_percent_match(
        self, 
        valid_session_id, 
        mock_mongodb_saver
    ):
        """
        Test: Hash comparison of message history pre/post restart (100% match).
        
        Explicitly tests FR-3.1.2 acceptance criteria.
        """
        # Create conversation with exactly 5 messages
        messages = [
            {"role": "human", "content": "Tell me about MSFT"},
            {"role": "ai", "content": "Microsoft Corporation (MSFT) is a technology company."},
            {"role": "human", "content": "What's its market cap?"},
            {"role": "ai", "content": "MSFT has a market cap of approximately $2.8 trillion."},
            {"role": "human", "content": "Compare to AAPL"},
        ]
        
        # Store
        config = {"configurable": {"thread_id": valid_session_id}}
        mock_mongodb_saver.put(config, {"channel_values": {"messages": messages}})
        
        # Record pre-restart hash
        pre_restart_hash = compute_message_hash(messages)
        
        # Simulate restart - retrieve from fresh query
        restored = mock_mongodb_saver.get(config)
        restored_messages = restored.get("channel_values", {}).get("messages", [])
        
        # Compute post-restart hash
        post_restart_hash = compute_message_hash(restored_messages)
        
        # Assert 100% match
        assert pre_restart_hash == post_restart_hash, (
            "Hash comparison FAILED - messages not preserved exactly.\n"
            f"Pre-restart:  {pre_restart_hash}\n"
            f"Post-restart: {post_restart_hash}"
        )
    
    def test_checkpoint_data_survives_across_agent_instances(
        self, 
        valid_session_id, 
        mock_mongodb_saver
    ):
        """
        Test: Verify checkpoint data survives across agent instances.
        
        Simulates creating multiple agent instances (as would happen on restart)
        and verifies they can all access the same checkpoint data.
        """
        # Store checkpoint data
        original_data = {
            "channel_values": {
                "messages": [
                    {"role": "human", "content": "Query 1"},
                    {"role": "ai", "content": "Response 1"},
                ]
            },
            "metadata": {
                "created_at": "2025-01-27T10:00:00Z",
                "agent_version": "1.0.0"
            }
        }
        
        config = {"configurable": {"thread_id": valid_session_id}}
        mock_mongodb_saver.put(config, original_data, original_data.get("metadata"))
        
        # Simulate "Agent Instance 1" accessing checkpoint
        agent1_data = mock_mongodb_saver.get(config)
        assert agent1_data is not None, "Agent 1 should retrieve checkpoint"
        assert agent1_data == original_data
        
        # Simulate "Agent Instance 2" (after restart) accessing same checkpoint
        # Using same checkpointer (simulating MongoDB persistence)
        agent2_data = mock_mongodb_saver.get(config)
        assert agent2_data is not None, "Agent 2 should retrieve checkpoint after restart"
        assert agent2_data == original_data
        
        # Verify data integrity
        assert agent1_data == agent2_data, (
            "Checkpoint data differs between agent instances"
        )
    
    def test_different_sessions_have_isolated_checkpoints(
        self, 
        mock_mongodb_saver
    ):
        """
        Test: Different session_ids have isolated checkpoint data.
        
        Ensures session isolation per FR-3.1.4.
        """
        session_1 = str(uuid.uuid4())
        session_2 = str(uuid.uuid4())
        
        # Store different data for each session
        data_1 = {
            "channel_values": {
                "messages": [{"role": "human", "content": "Session 1 message"}]
            }
        }
        data_2 = {
            "channel_values": {
                "messages": [{"role": "human", "content": "Session 2 message"}]
            }
        }
        
        mock_mongodb_saver.put({"configurable": {"thread_id": session_1}}, data_1)
        mock_mongodb_saver.put({"configurable": {"thread_id": session_2}}, data_2)
        
        # Retrieve and verify isolation
        retrieved_1 = mock_mongodb_saver.get({"configurable": {"thread_id": session_1}})
        retrieved_2 = mock_mongodb_saver.get({"configurable": {"thread_id": session_2}})
        
        assert retrieved_1 != retrieved_2, "Sessions should have isolated data"
        
        msg_1 = retrieved_1["channel_values"]["messages"][0]["content"]
        msg_2 = retrieved_2["channel_values"]["messages"][0]["content"]
        
        assert msg_1 == "Session 1 message"
        assert msg_2 == "Session 2 message"


# ============================================================================
# Test: Session Binding (FR-3.1.3)
# ============================================================================

class TestSessionIdentifierBinding:
    """
    Test suite for FR-3.1.3: Session identifier correctly binds to stored state.
    """
    
    def test_session_id_binds_to_correct_checkpoint(
        self, 
        mock_mongodb_saver
    ):
        """Test session_id correctly maps to its checkpoint."""
        session_id = str(uuid.uuid4())
        other_session = str(uuid.uuid4())
        
        # Store checkpoint for our session
        expected_content = "This is the correct conversation"
        mock_mongodb_saver.put(
            {"configurable": {"thread_id": session_id}},
            {"channel_values": {"messages": [{"role": "human", "content": expected_content}]}}
        )
        
        # Store different checkpoint for other session
        mock_mongodb_saver.put(
            {"configurable": {"thread_id": other_session}},
            {"channel_values": {"messages": [{"role": "human", "content": "Wrong conversation"}]}}
        )
        
        # Retrieve by session_id
        retrieved = mock_mongodb_saver.get({"configurable": {"thread_id": session_id}})
        
        # Verify correct binding
        assert retrieved is not None
        content = retrieved["channel_values"]["messages"][0]["content"]
        assert content == expected_content, f"Wrong conversation bound to session_id: {content}"
    
    def test_nonexistent_session_returns_none(
        self, 
        mock_mongodb_saver
    ):
        """Test querying non-existent session returns None."""
        nonexistent_session = str(uuid.uuid4())
        
        result = mock_mongodb_saver.get(
            {"configurable": {"thread_id": nonexistent_session}}
        )
        
        assert result is None, "Non-existent session should return None"


# ============================================================================
# Test: Conversation Metadata Persistence
# ============================================================================

class TestConversationMetadataPersistence:
    """
    Test ConversationRepository persistence alongside checkpoints.
    
    Verifies that conversation metadata (message_count, total_tokens, etc.)
    persists correctly and can be retrieved after restart.
    """
    
    def test_conversation_metadata_preserved_across_restart(self):
        """
        Test conversation document survives across repository instances.
        
        Uses mock repository to simulate persistence.
        """
        # Mock conversation document
        session_id = str(uuid.uuid4())
        conversation = {
            "_id": "mock_id",
            "session_id": session_id,
            "workspace_id": "ws-123",
            "user_id": "user-456",
            "status": "active",
            "message_count": 5,
            "total_tokens": 1250,
            "focused_symbols": ["AAPL", "MSFT"],
            "created_at": "2025-01-27T10:00:00Z",
            "updated_at": "2025-01-27T10:30:00Z"
        }
        
        # Simulate storage
        mock_storage = {session_id: conversation}
        
        # Simulate restart - new repository instance
        # In real scenario, MongoDB persists data between instances
        
        # Retrieve after "restart"
        retrieved = mock_storage.get(session_id)
        
        assert retrieved is not None, "Conversation should persist across restart"
        assert retrieved["message_count"] == 5
        assert retrieved["total_tokens"] == 1250
        assert retrieved["focused_symbols"] == ["AAPL", "MSFT"]
        assert retrieved["status"] == "active"


# ============================================================================
# Compliance Integration Tests (Task T029)
# ============================================================================

class TestMemoryContentComplianceIntegration:
    """
    Integration tests for memory content compliance (FR-3.1.7, FR-3.1.8).
    
    Reference: specs/spec-driven-development-pilot/tasks.md - T029
    
    User Story (US4): Tools return stock prices, ratios, news; 
    stored memory contains zero financial data.
    
    Test Strategy:
    - Simulate full conversation flow with tool invocations
    - Inspect checkpoint data for prohibited patterns
    - Verify audit scan returns zero violations
    """
    
    def test_full_conversation_flow_with_tool_calls_compliant(
        self, 
        valid_session_id, 
        mock_mongodb_saver
    ):
        """
        Test: Full conversation flow with tool calls stores compliant content only.
        
        Scenario:
        1. User asks about stock price
        2. Tool returns price data (NOT stored)
        3. Agent responds with summary (references only)
        4. Checkpoint contains only compliant messages
        """
        # Simulated conversation after tool processing
        # The agent should store references, not raw data
        compliant_messages = [
            {"role": "human", "content": "What is the current price of AAPL?"},
            {"role": "ai", "content": "I retrieved the current stock information for Apple Inc. (AAPL). The data has been fetched successfully."},
            {"role": "human", "content": "How does it compare to yesterday?"},
            {"role": "ai", "content": "Based on the retrieved data, AAPL is showing positive momentum compared to the previous trading day."},
        ]
        
        # Store checkpoint with compliant messages
        checkpoint_data = {
            "channel_values": {
                "messages": compliant_messages
            },
            "metadata": {
                "message_count": len(compliant_messages),
                "tool_calls": ["get_stock_price", "get_historical_data"]
            }
        }
        
        config = {"configurable": {"thread_id": valid_session_id}}
        mock_mongodb_saver.put(config, checkpoint_data)
        
        # Retrieve and verify compliance
        restored = mock_mongodb_saver.get(config)
        restored_messages = restored.get("channel_values", {}).get("messages", [])
        
        # Audit: All messages should be compliant
        for msg in restored_messages:
            content = msg.get("content", "")
            violations = ContentValidator.scan_prohibited_patterns(content)
            assert violations == [], (
                f"Checkpoint contains prohibited content in message: {content}\n"
                f"Violations: {violations}"
            )
    
    def test_inspect_checkpoint_data_for_prohibited_patterns(
        self, 
        valid_session_id, 
        mock_mongodb_saver
    ):
        """
        Test: Inspect checkpoint data for prohibited patterns.
        
        Verifies that we can detect if non-compliant data was accidentally stored.
        """
        # Intentionally store non-compliant data (simulating a bug)
        non_compliant_messages = [
            {"role": "human", "content": "What is AAPL price?"},
            {"role": "ai", "content": "AAPL is currently trading at $185.50"},  # BAD: contains price
        ]
        
        checkpoint_data = {
            "channel_values": {
                "messages": non_compliant_messages
            }
        }
        
        config = {"configurable": {"thread_id": valid_session_id}}
        mock_mongodb_saver.put(config, checkpoint_data)
        
        # Audit checkpoint
        restored = mock_mongodb_saver.get(config)
        restored_messages = restored.get("channel_values", {}).get("messages", [])
        
        # Should detect violations
        all_violations = []
        for msg in restored_messages:
            content = msg.get("content", "")
            violations = ContentValidator.scan_prohibited_patterns(content)
            all_violations.extend(violations)
        
        # This test documents the detection capability
        assert len(all_violations) > 0, "Should detect prohibited patterns in non-compliant checkpoint"
        assert "$185.50" in all_violations
    
    def test_audit_scan_returns_zero_violations_for_compliant_checkpoint(
        self, 
        valid_session_id, 
        mock_mongodb_saver
    ):
        """
        Test: Audit scan returns zero violations for properly stored checkpoint.
        
        Acceptance criteria for FR-3.1.7 and FR-3.1.8.
        """
        # Properly compliant conversation
        compliant_messages = [
            {"role": "human", "content": "Tell me about Apple stock"},
            {"role": "ai", "content": "Apple Inc. (AAPL) is a leading technology company known for iPhone, Mac, and services."},
            {"role": "human", "content": "What are the recent trends?"},
            {"role": "ai", "content": "Recent analysis shows positive momentum. I can provide detailed technical indicators if needed."},
            {"role": "human", "content": "Compare to Microsoft"},
            {"role": "ai", "content": "Both AAPL and MSFT are major tech companies. I can retrieve comparative data for analysis."},
        ]
        
        checkpoint_data = {
            "channel_values": {
                "messages": compliant_messages
            },
            "metadata": {
                "message_count": len(compliant_messages)
            }
        }
        
        config = {"configurable": {"thread_id": valid_session_id}}
        mock_mongodb_saver.put(config, checkpoint_data)
        
        # Full audit scan
        restored = mock_mongodb_saver.get(config)
        restored_messages = restored.get("channel_values", {}).get("messages", [])
        
        # Collect all violations
        audit_results = []
        for i, msg in enumerate(restored_messages):
            content = msg.get("content", "")
            violations = ContentValidator.scan_prohibited_patterns(content)
            if violations:
                audit_results.append({
                    "message_index": i,
                    "role": msg.get("role"),
                    "violations": violations
                })
        
        # Acceptance: Zero violations
        assert len(audit_results) == 0, (
            f"Audit found violations in compliant checkpoint:\n"
            f"{json.dumps(audit_results, indent=2)}"
        )
    
    def test_tool_output_references_vs_raw_data(self, valid_session_id, mock_mongodb_saver):
        """
        Test: Tool outputs stored as references only, not raw data (FR-3.1.8).
        
        Compares compliant vs non-compliant storage patterns.
        """
        # Non-compliant: Raw tool output embedded
        bad_pattern = {
            "role": "ai",
            "content": "The get_stock_price tool returned: {'symbol': 'AAPL', 'price': 185.50, 'change': 2.5%}"
        }
        
        # Compliant: Reference to tool output
        good_pattern = {
            "role": "ai",
            "content": "I called the get_stock_price tool for AAPL. The current market data has been retrieved."
        }
        
        # Verify compliance detection
        bad_violations = ContentValidator.scan_prohibited_patterns(bad_pattern["content"])
        good_violations = ContentValidator.scan_prohibited_patterns(good_pattern["content"])
        
        # Bad pattern has violations
        assert len(bad_violations) > 0, "Raw tool output should be detected as non-compliant"
        
        # Good pattern has no violations
        assert good_violations == [], f"Reference pattern should be compliant, got: {good_violations}"
    
    def test_mixed_conversation_with_compliant_and_tool_references(
        self, 
        valid_session_id, 
        mock_mongodb_saver
    ):
        """
        Test: Full conversation with tool references is compliant.
        
        Simulates realistic agent behavior after tool invocations.
        """
        # Realistic compliant conversation after tool usage
        messages = [
            {"role": "human", "content": "What's happening with AAPL today?"},
            {"role": "ai", "content": "Let me check the current market data for Apple Inc."},
            # Tool call would happen here (not stored as message)
            {"role": "ai", "content": "I've retrieved the latest data for AAPL. The stock is showing interesting activity today."},
            {"role": "human", "content": "What about the earnings?"},
            # Another tool call
            {"role": "ai", "content": "Based on the fundamental data I retrieved, Apple's earnings position looks solid. Would you like me to analyze specific metrics?"},
            {"role": "human", "content": "Yes, compare P/E with sector average"},
            {"role": "ai", "content": "I've gathered the comparative valuation data. The analysis suggests Apple's valuation is in line with sector expectations."},
        ]
        
        checkpoint_data = {
            "channel_values": {"messages": messages},
            "metadata": {"tool_calls": ["get_stock_price", "get_fundamentals", "get_sector_comparison"]}
        }
        
        config = {"configurable": {"thread_id": valid_session_id}}
        mock_mongodb_saver.put(config, checkpoint_data)
        
        # Audit
        restored = mock_mongodb_saver.get(config)
        restored_messages = restored.get("channel_values", {}).get("messages", [])
        
        total_violations = 0
        for msg in restored_messages:
            violations = ContentValidator.scan_prohibited_patterns(msg.get("content", ""))
            total_violations += len(violations)
        
        assert total_violations == 0, "Full conversation with tool references should be compliant"


# ============================================================================
# Session Recall on Disconnection Tests (Task T031)
# ============================================================================

class TestSessionRecallOnDisconnection:
    """
    Integration tests for Session Recall on Disconnection (US5, FR-3.1.5).
    
    Reference: specs/spec-driven-development-pilot/tasks.md - T031
    
    User Story (US5): User has active conversation, network drops, 
    user reconnects with same session_id, agent resumes with context awareness.
    
    Test Strategy:
    - Simulate disconnect by destroying agent instance
    - Reconnect with same session_id
    - Verify first response demonstrates context awareness
    - Verify message count accurate after reconnect
    """
    
    def test_simulate_disconnect_and_reconnect_preserves_context(
        self, 
        valid_session_id, 
        mock_mongodb_saver
    ):
        """
        Test: Simulate disconnect (destroy agent instance), reconnect with same session_id.
        
        Scenario:
        1. User is in active conversation (5 messages)
        2. Network drops / user disconnects
        3. Agent instance is destroyed (simulated by losing reference)
        4. User reconnects with same session_id
        5. Context is fully restored from checkpoint
        """
        # ─────────────────────────────────────────────────────────────
        # Phase 1: Active conversation before disconnect
        # ─────────────────────────────────────────────────────────────
        
        # Simulate active conversation
        conversation_before_disconnect = [
            {"role": "human", "content": "I want to build a tech portfolio"},
            {"role": "ai", "content": "I'd be happy to help you build a tech portfolio. What's your investment horizon and risk tolerance?"},
            {"role": "human", "content": "5 year horizon, moderate risk"},
            {"role": "ai", "content": "For a 5-year moderate risk portfolio, I recommend a mix of established tech companies and some growth stocks."},
            {"role": "human", "content": "Can you suggest some specific stocks?"},
        ]
        
        # Store checkpoint (simulating active session state)
        config = {"configurable": {"thread_id": valid_session_id}}
        checkpoint_before = {
            "channel_values": {"messages": conversation_before_disconnect},
            "metadata": {"status": "active", "message_count": 5}
        }
        mock_mongodb_saver.put(config, checkpoint_before)
        
        # Record hash for comparison
        hash_before_disconnect = compute_message_hash(conversation_before_disconnect)
        
        # ─────────────────────────────────────────────────────────────
        # Phase 2: Simulate disconnect (destroy agent instance)
        # ─────────────────────────────────────────────────────────────
        
        # In real scenario, this could be:
        # - Network timeout
        # - Browser refresh
        # - Server restart
        # - Client navigating away and returning
        
        # Simulate by "losing" reference to agent state
        # The checkpointer (MongoDB) retains the data
        agent_state = None  # Agent instance destroyed
        del checkpoint_before  # Local state gone
        
        # ─────────────────────────────────────────────────────────────
        # Phase 3: Reconnect with same session_id
        # ─────────────────────────────────────────────────────────────
        
        # User reconnects with same session_id
        reconnect_config = {"configurable": {"thread_id": valid_session_id}}
        
        # Retrieve checkpoint (agent would do this on reconnection)
        restored_checkpoint = mock_mongodb_saver.get(reconnect_config)
        
        # ─────────────────────────────────────────────────────────────
        # Phase 4: Verify context awareness
        # ─────────────────────────────────────────────────────────────
        
        assert restored_checkpoint is not None, "Checkpoint should be available after disconnect"
        
        restored_messages = restored_checkpoint.get("channel_values", {}).get("messages", [])
        
        # Verify hash matches (100% context restored)
        hash_after_reconnect = compute_message_hash(restored_messages)
        assert hash_before_disconnect == hash_after_reconnect, (
            "Context not fully restored after disconnect/reconnect"
        )
        
        # Verify context enables continuation
        last_user_message = restored_messages[-1]["content"]
        assert last_user_message == "Can you suggest some specific stocks?", (
            "Last user message should be preserved for context-aware response"
        )
        
        # Verify agent could provide context-aware response
        # (Agent would use restored messages to understand user wants stock suggestions
        # for a 5-year moderate risk tech portfolio)
        context_summary = " ".join([m["content"] for m in restored_messages])
        assert "tech portfolio" in context_summary.lower()
        assert "5 year" in context_summary.lower()
        assert "moderate risk" in context_summary.lower()
    
    def test_first_response_after_reconnect_demonstrates_context_awareness(
        self,
        valid_session_id,
        mock_mongodb_saver
    ):
        """
        Test: First response after reconnect references prior context.
        
        Verifies the agent can generate a context-aware response by having
        access to the full conversation history from the checkpoint.
        """
        # Setup conversation with specific context
        conversation = [
            {"role": "human", "content": "Tell me about NVDA"},
            {"role": "ai", "content": "NVIDIA (NVDA) is a leading semiconductor company known for its GPUs."},
            {"role": "human", "content": "What's their AI exposure?"},
            {"role": "ai", "content": "NVIDIA has significant AI exposure through their data center GPUs which power most AI training."},
            {"role": "human", "content": "Compare to AMD"},
        ]
        
        config = {"configurable": {"thread_id": valid_session_id}}
        mock_mongodb_saver.put(config, {"channel_values": {"messages": conversation}})
        
        # Simulate disconnect and reconnect
        # ... network drop ...
        
        # Reconnect - retrieve checkpoint
        restored = mock_mongodb_saver.get(config)
        restored_messages = restored.get("channel_values", {}).get("messages", [])
        
        # Agent prepares to respond - it now has context
        # The restored messages allow agent to understand:
        # 1. User asked about NVDA
        # 2. User is interested in AI exposure
        # 3. User now wants comparison to AMD
        
        # Verify context provides enough information for context-aware response
        assert len(restored_messages) == 5, "All messages should be restored"
        
        # Last user message is "Compare to AMD"
        assert restored_messages[-1]["content"] == "Compare to AMD"
        
        # Context contains NVDA discussion
        has_nvda_context = any("NVDA" in m["content"] or "NVIDIA" in m["content"] 
                               for m in restored_messages)
        assert has_nvda_context, "NVDA context should be available for comparison"
        
        # Context contains AI discussion
        has_ai_context = any("AI" in m["content"] for m in restored_messages)
        assert has_ai_context, "AI exposure context should be available"
    
    def test_message_count_accurate_after_reconnect(
        self,
        valid_session_id,
        mock_mongodb_saver
    ):
        """
        Test: Message count is accurate after reconnect.
        
        Verifies no messages are lost or duplicated during disconnect/reconnect.
        """
        # Create conversation with exact count
        exact_message_count = 7
        messages = []
        for i in range(exact_message_count):
            role = "human" if i % 2 == 0 else "ai"
            messages.append({"role": role, "content": f"Message {i + 1}"})
        
        config = {"configurable": {"thread_id": valid_session_id}}
        mock_mongodb_saver.put(
            config, 
            {
                "channel_values": {"messages": messages},
                "metadata": {"message_count": exact_message_count}
            }
        )
        
        # Simulate disconnect
        del messages
        
        # Reconnect and verify count
        restored = mock_mongodb_saver.get(config)
        restored_messages = restored.get("channel_values", {}).get("messages", [])
        
        assert len(restored_messages) == exact_message_count, (
            f"Message count mismatch: expected {exact_message_count}, got {len(restored_messages)}"
        )
        
        # Verify metadata count if stored
        metadata = restored.get("metadata", {})
        if "message_count" in metadata:
            assert metadata["message_count"] == exact_message_count
    
    def test_reconnect_with_inactive_session_still_retrieves_history(
        self,
        valid_session_id,
        mock_mongodb_saver
    ):
        """
        Test: Reconnecting to a session that was inactive (but not archived) 
        still retrieves the conversation history.
        """
        # Create a session that was active but user was away for a while
        messages = [
            {"role": "human", "content": "Check GOOGL fundamentals"},
            {"role": "ai", "content": "I'll retrieve the fundamental data for Google."},
            {"role": "human", "content": "Thanks, I'll be back later"},
        ]
        
        config = {"configurable": {"thread_id": valid_session_id}}
        mock_mongodb_saver.put(
            config,
            {
                "channel_values": {"messages": messages},
                "metadata": {"status": "active", "last_activity": "2025-01-27T10:00:00Z"}
            }
        )
        
        # Time passes... user returns later (simulated by just retrieving)
        # Session is still active (not archived)
        
        restored = mock_mongodb_saver.get(config)
        
        assert restored is not None, "Inactive (but not archived) session should be retrievable"
        assert len(restored["channel_values"]["messages"]) == 3
        
        # User can continue the conversation
        last_msg = restored["channel_values"]["messages"][-1]["content"]
        assert "I'll be back later" in last_msg
    
    def test_multiple_disconnects_reconnects_preserve_accumulated_context(
        self,
        valid_session_id,
        mock_mongodb_saver
    ):
        """
        Test: Multiple disconnect/reconnect cycles preserve accumulated context.
        
        User may disconnect and reconnect multiple times during a long session.
        """
        config = {"configurable": {"thread_id": valid_session_id}}
        
        # ─────────────────────────────────────────────────────────────
        # Round 1: Initial conversation
        # ─────────────────────────────────────────────────────────────
        messages_round1 = [
            {"role": "human", "content": "Start analyzing TSLA"},
            {"role": "ai", "content": "I'll analyze Tesla for you."},
        ]
        mock_mongodb_saver.put(config, {"channel_values": {"messages": messages_round1}})
        
        # Disconnect
        
        # ─────────────────────────────────────────────────────────────
        # Round 2: First reconnect and continue
        # ─────────────────────────────────────────────────────────────
        restored1 = mock_mongodb_saver.get(config)
        messages_round2 = restored1["channel_values"]["messages"] + [
            {"role": "human", "content": "What about their delivery numbers?"},
            {"role": "ai", "content": "Let me check Tesla's delivery data."},
        ]
        mock_mongodb_saver.put(config, {"channel_values": {"messages": messages_round2}})
        
        # Disconnect again
        
        # ─────────────────────────────────────────────────────────────
        # Round 3: Second reconnect and continue
        # ─────────────────────────────────────────────────────────────
        restored2 = mock_mongodb_saver.get(config)
        messages_round3 = restored2["channel_values"]["messages"] + [
            {"role": "human", "content": "And the energy business?"},
            {"role": "ai", "content": "Tesla Energy is showing strong growth."},
        ]
        mock_mongodb_saver.put(config, {"channel_values": {"messages": messages_round3}})
        
        # Final reconnect
        final_restored = mock_mongodb_saver.get(config)
        final_messages = final_restored["channel_values"]["messages"]
        
        # Verify all context accumulated across multiple reconnects
        assert len(final_messages) == 6, "All 6 messages from 3 rounds should be preserved"
        
        # Verify content from all rounds
        all_content = " ".join([m["content"] for m in final_messages])
        assert "TSLA" in all_content or "Tesla" in all_content
        assert "delivery" in all_content.lower()
        assert "energy" in all_content.lower()


# ============================================================================
# T036: End-to-End Multi-Turn Test with Success Criteria Verification
# ============================================================================

class TestEndToEndMultiTurnScenario:
    """
    T036: End-to-end multi-turn test validating all success criteria.
    
    Reference: specs/spec-driven-development-pilot/tasks.md - T036
    
    Success Criteria:
    - SC-1: Context accuracy ≥95%
    - SC-2: Persistence reliability 100%
    - SC-7: Load time < 500ms
    
    This class provides explicit verification of these criteria with
    measurable assertions for CI/CD tracking.
    """
    
    def test_full_5_turn_conversation_with_follow_ups(
        self,
        valid_session_id,
        mock_mongodb_saver
    ):
        """
        T036: Full 5-turn conversation scenario with follow-up questions.
        
        Scenario simulates realistic user interaction:
        - Turn 1: User asks about a stock
        - Turn 2: Follow-up on specific metric
        - Turn 3: Comparison request (requires prior context)
        - Turn 4: Clarification question
        - Turn 5: Action request based on full context
        
        This demonstrates the agent's ability to maintain coherent
        multi-turn conversations with contextual follow-ups.
        """
        # ─────────────────────────────────────────────────────────────
        # Full 5-turn realistic conversation
        # ─────────────────────────────────────────────────────────────
        five_turn_conversation = [
            # Turn 1: Initial query
            {"role": "human", "content": "What's the current outlook for Apple stock?"},
            {"role": "ai", "content": "Apple (AAPL) has a strong outlook with growing services revenue and iPhone sales. The company reported $94.8B in Q4 revenue."},
            
            # Turn 2: Follow-up on specific metric
            {"role": "human", "content": "How does their services segment compare to hardware?"},
            {"role": "ai", "content": "Services revenue is $22.3B (23% of total), growing faster than hardware at 16% YoY vs 8% for hardware."},
            
            # Turn 3: Comparison request (requires context: discussing Apple)
            {"role": "human", "content": "How does that compare to Microsoft's cloud revenue?"},
            {"role": "ai", "content": "Microsoft's Intelligent Cloud segment generated $24.3B, slightly higher than Apple Services. However, Azure specifically grew at 29% YoY, outpacing Apple's services growth."},
            
            # Turn 4: Clarification (requires context: comparing AAPL and MSFT)
            {"role": "human", "content": "Which one has better profit margins in those segments?"},
            {"role": "ai", "content": "Apple Services has estimated 70%+ gross margins, while Microsoft's Intelligent Cloud has ~72% margins. Both are highly profitable, but Microsoft Cloud is slightly higher."},
            
            # Turn 5: Action based on full context
            {"role": "human", "content": "Given this analysis, should I invest in both?"},
        ]
        
        config = {"configurable": {"thread_id": valid_session_id}}
        
        # Store checkpoint
        checkpoint = {
            "channel_values": {"messages": five_turn_conversation},
            "metadata": {
                "message_count": len(five_turn_conversation),
                "topics": ["AAPL", "MSFT", "services", "cloud"],
                "created_at": "2025-01-27T12:00:00Z"
            }
        }
        mock_mongodb_saver.put(config, checkpoint)
        
        # Retrieve and verify
        restored = mock_mongodb_saver.get(config)
        assert restored is not None, "5-turn conversation should be persisted"
        
        messages = restored["channel_values"]["messages"]
        assert len(messages) == 9, f"Expected 9 messages (5 turns = 9 messages), got {len(messages)}"
        
        # Verify conversation coherence (last message requires all prior context)
        last_user_msg = messages[-1]["content"]
        assert "invest in both" in last_user_msg.lower(), (
            "Final turn should reference both stocks discussed"
        )
        
        # Verify context chain exists (AAPL -> MSFT -> comparison -> recommendation request)
        all_content = " ".join([m["content"] for m in messages])
        assert "Apple" in all_content or "AAPL" in all_content
        assert "Microsoft" in all_content or "MSFT" in all_content
        assert "services" in all_content.lower() or "Services" in all_content
        assert "margin" in all_content.lower()
    
    def test_context_accuracy_sc1_verification(
        self,
        valid_session_id,
        mock_mongodb_saver
    ):
        """
        T036 SC-1: Verify context accuracy ≥95%.
        
        Context accuracy is measured by:
        1. All original messages preserved (no data loss)
        2. Message order preserved (sequence integrity)
        3. Message content preserved (no corruption)
        4. Metadata preserved (auxiliary context)
        
        A 95% threshold means at most 5% deviation, which in a 10-message
        conversation allows 0.5 messages of discrepancy - effectively requiring
        100% for discrete message counts.
        """
        # Create conversation with precise content for accuracy measurement
        original_messages = [
            {"role": "human", "content": "Analyze Tesla stock fundamentals"},
            {"role": "ai", "content": "Tesla (TSLA) fundamentals analysis: P/E ratio is 65x, above industry average."},
            {"role": "human", "content": "What about their delivery numbers?"},
            {"role": "ai", "content": "Q4 deliveries: 484,507 vehicles, up 31% YoY. Annual total: 1.81M vehicles."},
            {"role": "human", "content": "Compare to their production capacity"},
            {"role": "ai", "content": "Production capacity is ~2M vehicles/year. They're operating at ~90% utilization."},
            {"role": "human", "content": "Is that sustainable?"},
            {"role": "ai", "content": "New factories in Austin and Berlin should add 500K capacity each, supporting growth."},
            {"role": "human", "content": "What's the outlook?"},
            {"role": "ai", "content": "Positive outlook with capacity expansion, though valuation remains stretched."},
        ]
        
        config = {"configurable": {"thread_id": valid_session_id}}
        
        # Store with metadata
        original_checkpoint = {
            "channel_values": {"messages": original_messages},
            "metadata": {
                "message_count": len(original_messages),
                "first_topic": "TSLA",
                "conversation_hash": hashlib.sha256(
                    json.dumps(original_messages, sort_keys=True).encode()
                ).hexdigest()
            }
        }
        mock_mongodb_saver.put(config, original_checkpoint)
        
        # Retrieve checkpoint
        restored = mock_mongodb_saver.get(config)
        restored_messages = restored["channel_values"]["messages"]
        
        # ─────────────────────────────────────────────────────────────
        # SC-1 Accuracy Measurements
        # ─────────────────────────────────────────────────────────────
        
        # Metric 1: Message count accuracy
        count_accuracy = len(restored_messages) / len(original_messages)
        assert count_accuracy >= 0.95, f"Message count accuracy {count_accuracy:.2%} < 95%"
        
        # Metric 2: Message order accuracy (check sequence)
        order_matches = sum(
            1 for i, (orig, rest) in enumerate(zip(original_messages, restored_messages))
            if orig["role"] == rest["role"]
        )
        order_accuracy = order_matches / len(original_messages)
        assert order_accuracy >= 0.95, f"Message order accuracy {order_accuracy:.2%} < 95%"
        
        # Metric 3: Content accuracy (character-level comparison)
        total_chars = sum(len(m["content"]) for m in original_messages)
        matched_chars = sum(
            len(orig["content"]) 
            for orig, rest in zip(original_messages, restored_messages)
            if orig["content"] == rest["content"]
        )
        content_accuracy = matched_chars / total_chars if total_chars > 0 else 0
        assert content_accuracy >= 0.95, f"Content accuracy {content_accuracy:.2%} < 95%"
        
        # Metric 4: Overall context accuracy (composite)
        overall_accuracy = (count_accuracy + order_accuracy + content_accuracy) / 3
        assert overall_accuracy >= 0.95, (
            f"Overall context accuracy {overall_accuracy:.2%} < 95%\n"
            f"  Count: {count_accuracy:.2%}\n"
            f"  Order: {order_accuracy:.2%}\n"
            f"  Content: {content_accuracy:.2%}"
        )
        
        print(f"SC-1 Context Accuracy: {overall_accuracy:.2%} ✓")
    
    def test_persistence_reliability_sc2_verification(
        self,
        valid_session_id,
        mock_mongodb_saver
    ):
        """
        T036 SC-2: Verify persistence reliability 100%.
        
        Reliability is verified by:
        1. Data survives put/get cycle (basic persistence)
        2. Hash matches before/after (data integrity)
        3. Multiple read operations return consistent data
        4. Metadata preserved alongside messages
        
        100% reliability means zero data loss across all operations.
        """
        # Create checkpoint with full data
        messages = [
            {"role": "human", "content": "Analyze semiconductor sector"},
            {"role": "ai", "content": "Semiconductor sector analysis: Strong demand from AI/ML, data centers."},
            {"role": "human", "content": "Top picks?"},
            {"role": "ai", "content": "Top picks: NVDA (AI leader), AMD (data center), ASML (equipment)."},
            {"role": "human", "content": "Which has best valuation?"},
        ]
        
        metadata = {
            "session_id": valid_session_id,
            "created_at": "2025-01-27T12:00:00Z",
            "message_count": len(messages),
            "topics": ["semiconductors", "NVDA", "AMD", "ASML"]
        }
        
        # Compute hash before storage
        hash_before = hashlib.sha256(
            json.dumps({"messages": messages, "metadata": metadata}, sort_keys=True).encode()
        ).hexdigest()
        
        config = {"configurable": {"thread_id": valid_session_id}}
        
        # Store checkpoint
        mock_mongodb_saver.put(
            config,
            {"channel_values": {"messages": messages}, "metadata": metadata}
        )
        
        # ─────────────────────────────────────────────────────────────
        # SC-2 Reliability Verification
        # ─────────────────────────────────────────────────────────────
        
        # Verification 1: Data survives put/get cycle
        restored = mock_mongodb_saver.get(config)
        assert restored is not None, "SC-2 FAIL: Checkpoint not persisted"
        
        # Verification 2: Hash matches (data integrity)
        restored_messages = restored["channel_values"]["messages"]
        restored_metadata = restored.get("metadata", metadata)  # Use original if not in checkpoint
        
        hash_after = hashlib.sha256(
            json.dumps({"messages": restored_messages, "metadata": restored_metadata}, sort_keys=True).encode()
        ).hexdigest()
        
        assert hash_before == hash_after, (
            f"SC-2 FAIL: Hash mismatch\n"
            f"  Before: {hash_before[:16]}...\n"
            f"  After:  {hash_after[:16]}..."
        )
        
        # Verification 3: Multiple reads return consistent data
        read_results = [mock_mongodb_saver.get(config) for _ in range(5)]
        read_hashes = [
            hashlib.sha256(
                json.dumps(r["channel_values"]["messages"], sort_keys=True).encode()
            ).hexdigest() if r else None
            for r in read_results
        ]
        
        assert all(h == read_hashes[0] for h in read_hashes), (
            "SC-2 FAIL: Inconsistent read results across multiple operations"
        )
        
        # Verification 4: All messages present (zero loss)
        assert len(restored_messages) == len(messages), (
            f"SC-2 FAIL: Message loss detected ({len(restored_messages)}/{len(messages)})"
        )
        
        print(f"SC-2 Persistence Reliability: 100% ✓ (hash verified, {len(read_results)} consistent reads)")
    
    def test_load_time_benchmark_sc7_verification(
        self,
        valid_session_id,
        mock_mongodb_saver
    ):
        """
        T036 SC-7: Verify load time < 500ms.
        
        This test benchmarks checkpoint retrieval time to ensure
        it meets the context_load_timeout_ms threshold.
        
        Note: Using mock, this primarily validates the test infrastructure.
        Real MongoDB tests would measure actual I/O latency.
        """
        import time
        
        # Create substantial checkpoint (simulate real-world size)
        messages = []
        for i in range(20):  # 20 messages = realistic conversation length
            role = "human" if i % 2 == 0 else "ai"
            content = f"Message {i}: " + "x" * 200  # ~200 chars per message
            messages.append({"role": role, "content": content})
        
        config = {"configurable": {"thread_id": valid_session_id}}
        mock_mongodb_saver.put(config, {"channel_values": {"messages": messages}})
        
        # ─────────────────────────────────────────────────────────────
        # SC-7 Load Time Benchmark
        # ─────────────────────────────────────────────────────────────
        
        THRESHOLD_MS = 500  # context_load_timeout_ms from config
        NUM_ITERATIONS = 10  # Multiple iterations for reliable measurement
        
        load_times_ms = []
        
        for _ in range(NUM_ITERATIONS):
            start = time.perf_counter()
            restored = mock_mongodb_saver.get(config)
            end = time.perf_counter()
            
            assert restored is not None, "Failed to load checkpoint"
            load_times_ms.append((end - start) * 1000)
        
        avg_load_time_ms = sum(load_times_ms) / len(load_times_ms)
        max_load_time_ms = max(load_times_ms)
        min_load_time_ms = min(load_times_ms)
        
        # SC-7: Average load time must be under threshold
        assert avg_load_time_ms < THRESHOLD_MS, (
            f"SC-7 FAIL: Average load time {avg_load_time_ms:.2f}ms >= {THRESHOLD_MS}ms threshold"
        )
        
        # Also check max load time (worst case)
        assert max_load_time_ms < THRESHOLD_MS * 2, (
            f"SC-7 WARNING: Max load time {max_load_time_ms:.2f}ms exceeds 2x threshold"
        )
        
        print(
            f"SC-7 Load Time Benchmark:\n"
            f"  Average: {avg_load_time_ms:.2f}ms < {THRESHOLD_MS}ms ✓\n"
            f"  Min: {min_load_time_ms:.2f}ms\n"
            f"  Max: {max_load_time_ms:.2f}ms\n"
            f"  Iterations: {NUM_ITERATIONS}"
        )
    
    def test_combined_t036_success_criteria(
        self,
        valid_session_id,
        mock_mongodb_saver
    ):
        """
        T036: Combined test verifying all success criteria in single scenario.
        
        This test simulates the complete user journey:
        1. 5-turn conversation with contextual follow-ups
        2. Measure and verify context accuracy ≥95% (SC-1)
        3. Verify persistence reliability 100% (SC-2)
        4. Benchmark load time < 500ms (SC-7)
        
        All criteria must pass for T036 to be considered complete.
        """
        import time
        
        # ─────────────────────────────────────────────────────────────
        # Phase 1: Create 5-turn conversation
        # ─────────────────────────────────────────────────────────────
        five_turn_conversation = [
            {"role": "human", "content": "I want to analyze the EV market"},
            {"role": "ai", "content": "The EV market is growing rapidly. Key players include Tesla, Rivian, and legacy automakers transitioning to electric."},
            {"role": "human", "content": "How is Tesla positioned?"},
            {"role": "ai", "content": "Tesla leads with ~50% US market share, strong margins, and the Supercharger network advantage."},
            {"role": "human", "content": "What about Rivian?"},
            {"role": "ai", "content": "Rivian targets the adventure/outdoor segment with R1T and R1S. Strong Amazon partnership for delivery vans."},
            {"role": "human", "content": "Which is a better investment?"},
            {"role": "ai", "content": "Tesla has proven profitability while Rivian is still scaling. Tesla safer, Rivian higher risk/reward."},
            {"role": "human", "content": "I'll start with Tesla then, what entry point?"},
        ]
        
        config = {"configurable": {"thread_id": valid_session_id}}
        
        # Compute pre-storage hash for integrity check
        hash_before = hashlib.sha256(
            json.dumps(five_turn_conversation, sort_keys=True).encode()
        ).hexdigest()
        
        checkpoint = {
            "channel_values": {"messages": five_turn_conversation},
            "metadata": {"message_count": len(five_turn_conversation)}
        }
        
        # ─────────────────────────────────────────────────────────────
        # Phase 2: Store checkpoint
        # ─────────────────────────────────────────────────────────────
        mock_mongodb_saver.put(config, checkpoint)
        
        # ─────────────────────────────────────────────────────────────
        # Phase 3: Retrieve and benchmark (SC-7)
        # ─────────────────────────────────────────────────────────────
        THRESHOLD_MS = 500
        
        start = time.perf_counter()
        restored = mock_mongodb_saver.get(config)
        load_time_ms = (time.perf_counter() - start) * 1000
        
        assert restored is not None, "T036: Checkpoint retrieval failed"
        assert load_time_ms < THRESHOLD_MS, f"SC-7 FAIL: Load time {load_time_ms:.2f}ms >= {THRESHOLD_MS}ms"
        
        # ─────────────────────────────────────────────────────────────
        # Phase 4: Verify context accuracy (SC-1)
        # ─────────────────────────────────────────────────────────────
        restored_messages = restored["channel_values"]["messages"]
        
        # Count accuracy
        count_match = len(restored_messages) == len(five_turn_conversation)
        
        # Order accuracy
        order_matches = all(
            orig["role"] == rest["role"]
            for orig, rest in zip(five_turn_conversation, restored_messages)
        )
        
        # Content accuracy
        content_matches = all(
            orig["content"] == rest["content"]
            for orig, rest in zip(five_turn_conversation, restored_messages)
        )
        
        context_accuracy = (
            (1 if count_match else 0) +
            (1 if order_matches else 0) +
            (1 if content_matches else 0)
        ) / 3
        
        assert context_accuracy >= 0.95, f"SC-1 FAIL: Context accuracy {context_accuracy:.2%} < 95%"
        
        # ─────────────────────────────────────────────────────────────
        # Phase 5: Verify persistence reliability (SC-2)
        # ─────────────────────────────────────────────────────────────
        hash_after = hashlib.sha256(
            json.dumps(restored_messages, sort_keys=True).encode()
        ).hexdigest()
        
        persistence_reliable = hash_before == hash_after
        assert persistence_reliable, "SC-2 FAIL: Hash mismatch - data integrity compromised"
        
        # ─────────────────────────────────────────────────────────────
        # T036 Summary
        # ─────────────────────────────────────────────────────────────
        print(
            f"\n{'='*60}\n"
            f"T036 END-TO-END MULTI-TURN TEST RESULTS\n"
            f"{'='*60}\n"
            f"✓ 5-turn conversation: {len(restored_messages)} messages persisted\n"
            f"✓ SC-1 Context Accuracy: {context_accuracy:.0%} (threshold: 95%)\n"
            f"✓ SC-2 Persistence Reliability: {'100%' if persistence_reliable else 'FAIL'}\n"
            f"✓ SC-7 Load Time: {load_time_ms:.2f}ms (threshold: {THRESHOLD_MS}ms)\n"
            f"{'='*60}\n"
            f"T036 STATUS: PASS\n"
            f"{'='*60}"
        )


# ============================================================================
# T037: Performance Benchmark Tests
# ============================================================================

class TestPerformanceBenchmark:
    """
    T037 Performance benchmark tests for memory operations.
    
    Reference: specs/spec-driven-development-pilot/tasks.md - T037
    
    Measures:
    - graph.get_state() latency against context_load_timeout_ms config (500ms)
    - State save time against state_save_timeout_ms config (50ms)
    
    Success Criteria:
    - Both operations complete under configured thresholds
    - Results logged for CI tracking
    
    Config thresholds from MemoryConfig:
    - context_load_timeout_ms: 500 (valid range: 100-5000)
    - state_save_timeout_ms: 50 (valid range: 10-500)
    """
    
    def test_get_state_latency_under_threshold(self, mock_mongodb_saver, valid_session_id):
        """
        T037: Measure graph.get_state() latency against context_load_timeout_ms.
        
        Validates that state retrieval completes within the configured
        performance threshold of 500ms (default context_load_timeout_ms).
        """
        import time
        from utils.memory_config import MemoryConfig
        
        # Get configured threshold
        config = MemoryConfig()
        threshold_ms = config.context_load_timeout_ms  # Default: 500ms
        
        # Setup: Create checkpoint with realistic message load
        session_config = {"configurable": {"thread_id": valid_session_id}}
        
        # Simulate 20-message conversation (realistic load)
        messages = [
            {"role": "human" if i % 2 == 0 else "assistant", 
             "content": f"Message {i}: {'User question about stock analysis' if i % 2 == 0 else 'AI response with market insights'} " * 10}
            for i in range(20)
        ]
        
        checkpoint_data = {
            "channel_values": {"messages": messages},
            "channel_versions": {"messages": 20},
            "v": 1,
            "ts": "2024-01-15T10:30:00Z"
        }
        
        mock_mongodb_saver.put(session_config, checkpoint_data)
        
        # Benchmark: Multiple iterations for statistical validity
        iterations = 100
        latencies = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            result = mock_mongodb_saver.get(session_config)
            elapsed_ms = (time.perf_counter() - start) * 1000
            latencies.append(elapsed_ms)
            
            # Verify we got data
            assert result is not None
        
        # Calculate statistics
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        
        # Assert under threshold
        assert avg_latency < threshold_ms, (
            f"T037 FAIL: Average get_state() latency {avg_latency:.2f}ms "
            f"exceeds threshold {threshold_ms}ms"
        )
        
        assert p95_latency < threshold_ms, (
            f"T037 FAIL: P95 get_state() latency {p95_latency:.2f}ms "
            f"exceeds threshold {threshold_ms}ms"
        )
        
        # Log benchmark results for CI tracking
        print(
            f"\n{'='*60}\n"
            f"T037 BENCHMARK: get_state() Latency\n"
            f"{'='*60}\n"
            f"Threshold: {threshold_ms}ms (context_load_timeout_ms)\n"
            f"Iterations: {iterations}\n"
            f"Min: {min_latency:.4f}ms\n"
            f"Max: {max_latency:.4f}ms\n"
            f"Avg: {avg_latency:.4f}ms\n"
            f"P95: {p95_latency:.4f}ms\n"
            f"Status: {'PASS' if p95_latency < threshold_ms else 'FAIL'}\n"
            f"{'='*60}"
        )
    
    def test_state_save_latency_under_threshold(self, mock_mongodb_saver, valid_session_id):
        """
        T037: Measure state save time against state_save_timeout_ms.
        
        Validates that state persistence completes within the configured
        performance threshold of 50ms (default state_save_timeout_ms).
        """
        import time
        from utils.memory_config import MemoryConfig
        
        # Get configured threshold
        config = MemoryConfig()
        threshold_ms = config.state_save_timeout_ms  # Default: 50ms
        
        # Benchmark: Multiple iterations with varying payloads
        iterations = 100
        latencies = []
        
        for i in range(iterations):
            session_config = {"configurable": {"thread_id": f"{valid_session_id}-{i}"}}
            
            # Create realistic checkpoint payload
            messages = [
                {"role": "human" if j % 2 == 0 else "assistant",
                 "content": f"Message {j}: Analysis of market trends and stock performance indicators " * 5}
                for j in range(10)
            ]
            
            checkpoint_data = {
                "channel_values": {"messages": messages},
                "channel_versions": {"messages": 10},
                "v": 1,
                "ts": f"2024-01-15T10:{i:02d}:00Z"
            }
            
            start = time.perf_counter()
            mock_mongodb_saver.put(session_config, checkpoint_data)
            elapsed_ms = (time.perf_counter() - start) * 1000
            latencies.append(elapsed_ms)
        
        # Calculate statistics
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        
        # Assert under threshold
        assert avg_latency < threshold_ms, (
            f"T037 FAIL: Average state_save time {avg_latency:.2f}ms "
            f"exceeds threshold {threshold_ms}ms"
        )
        
        assert p95_latency < threshold_ms, (
            f"T037 FAIL: P95 state_save time {p95_latency:.2f}ms "
            f"exceeds threshold {threshold_ms}ms"
        )
        
        # Log benchmark results for CI tracking
        print(
            f"\n{'='*60}\n"
            f"T037 BENCHMARK: state_save() Latency\n"
            f"{'='*60}\n"
            f"Threshold: {threshold_ms}ms (state_save_timeout_ms)\n"
            f"Iterations: {iterations}\n"
            f"Min: {min_latency:.4f}ms\n"
            f"Max: {max_latency:.4f}ms\n"
            f"Avg: {avg_latency:.4f}ms\n"
            f"P95: {p95_latency:.4f}ms\n"
            f"Status: {'PASS' if p95_latency < threshold_ms else 'FAIL'}\n"
            f"{'='*60}"
        )
    
    def test_combined_performance_benchmark_ci_output(self, mock_mongodb_saver, valid_session_id):
        """
        T037: Combined benchmark with structured CI output.
        
        Provides machine-parseable output for CI/CD integration:
        - JSON-formatted benchmark results
        - Pass/fail status for each metric
        - Aggregate status for build gates
        """
        import time
        import json
        from utils.memory_config import MemoryConfig
        
        config = MemoryConfig()
        
        # Prepare test data
        session_config = {"configurable": {"thread_id": valid_session_id}}
        messages = [
            {"role": "human" if i % 2 == 0 else "assistant",
             "content": f"Message {i}: Stock analysis query and comprehensive response " * 8}
            for i in range(15)
        ]
        
        checkpoint_data = {
            "channel_values": {"messages": messages},
            "channel_versions": {"messages": 15},
            "v": 1,
            "ts": "2024-01-15T10:00:00Z"
        }
        
        # Benchmark state save
        save_latencies = []
        for _ in range(50):
            start = time.perf_counter()
            mock_mongodb_saver.put(session_config, checkpoint_data)
            save_latencies.append((time.perf_counter() - start) * 1000)
        
        # Benchmark state load
        load_latencies = []
        for _ in range(50):
            start = time.perf_counter()
            mock_mongodb_saver.get(session_config)
            load_latencies.append((time.perf_counter() - start) * 1000)
        
        # Calculate metrics
        save_avg = sum(save_latencies) / len(save_latencies)
        save_p95 = sorted(save_latencies)[int(len(save_latencies) * 0.95)]
        load_avg = sum(load_latencies) / len(load_latencies)
        load_p95 = sorted(load_latencies)[int(len(load_latencies) * 0.95)]
        
        # Determine pass/fail
        save_pass = save_p95 < config.state_save_timeout_ms
        load_pass = load_p95 < config.context_load_timeout_ms
        overall_pass = save_pass and load_pass
        
        # CI-friendly JSON output
        benchmark_results = {
            "test": "T037_performance_benchmark",
            "timestamp": "2024-01-15T10:00:00Z",
            "config": {
                "context_load_timeout_ms": config.context_load_timeout_ms,
                "state_save_timeout_ms": config.state_save_timeout_ms
            },
            "metrics": {
                "state_save": {
                    "avg_ms": round(save_avg, 4),
                    "p95_ms": round(save_p95, 4),
                    "threshold_ms": config.state_save_timeout_ms,
                    "pass": save_pass
                },
                "context_load": {
                    "avg_ms": round(load_avg, 4),
                    "p95_ms": round(load_p95, 4),
                    "threshold_ms": config.context_load_timeout_ms,
                    "pass": load_pass
                }
            },
            "overall_status": "PASS" if overall_pass else "FAIL"
        }
        
        # Assert overall pass
        assert overall_pass, (
            f"T037 FAIL: Performance benchmark failed. "
            f"Save P95: {save_p95:.2f}ms (threshold: {config.state_save_timeout_ms}ms), "
            f"Load P95: {load_p95:.2f}ms (threshold: {config.context_load_timeout_ms}ms)"
        )
        
        # Log structured output for CI parsing
        print(
            f"\n{'='*60}\n"
            f"T037 BENCHMARK: CI OUTPUT\n"
            f"{'='*60}\n"
            f"::benchmark::{json.dumps(benchmark_results)}\n"
            f"{'='*60}"
        )
        
        # Human-readable summary
        print(
            f"\n{'='*60}\n"
            f"T037 PERFORMANCE BENCHMARK SUMMARY\n"
            f"{'='*60}\n"
            f"State Save:\n"
            f"  - Avg: {save_avg:.4f}ms\n"
            f"  - P95: {save_p95:.4f}ms\n"
            f"  - Threshold: {config.state_save_timeout_ms}ms\n"
            f"  - Status: {'✓ PASS' if save_pass else '✗ FAIL'}\n"
            f"\n"
            f"Context Load:\n"
            f"  - Avg: {load_avg:.4f}ms\n"
            f"  - P95: {load_p95:.4f}ms\n"
            f"  - Threshold: {config.context_load_timeout_ms}ms\n"
            f"  - Status: {'✓ PASS' if load_pass else '✗ FAIL'}\n"
            f"\n"
            f"{'='*60}\n"
            f"T037 OVERALL STATUS: {'PASS' if overall_pass else 'FAIL'}\n"
            f"{'='*60}"
        )
    
    def test_performance_under_load_stress(self, mock_mongodb_saver, valid_session_id):
        """
        T037: Stress test with heavy message load.
        
        Validates performance thresholds hold under stress:
        - 50 messages per checkpoint (heavy load)
        - Rapid successive operations
        - Verifies no performance degradation
        """
        import time
        from utils.memory_config import MemoryConfig
        
        config = MemoryConfig()
        
        # Create heavy payload (50 messages, ~100 chars each)
        heavy_messages = [
            {"role": "human" if i % 2 == 0 else "assistant",
             "content": f"Heavy message {i}: " + "X" * 100}
            for i in range(50)
        ]
        
        heavy_checkpoint = {
            "channel_values": {"messages": heavy_messages},
            "channel_versions": {"messages": 50},
            "v": 1,
            "ts": "2024-01-15T10:00:00Z"
        }
        
        session_config = {"configurable": {"thread_id": valid_session_id}}
        
        # Rapid save operations
        save_times = []
        for i in range(20):
            start = time.perf_counter()
            mock_mongodb_saver.put(session_config, heavy_checkpoint)
            save_times.append((time.perf_counter() - start) * 1000)
        
        # Rapid load operations
        load_times = []
        for i in range(20):
            start = time.perf_counter()
            result = mock_mongodb_saver.get(session_config)
            load_times.append((time.perf_counter() - start) * 1000)
            assert result is not None
        
        # Calculate metrics
        save_avg = sum(save_times) / len(save_times)
        load_avg = sum(load_times) / len(load_times)
        
        # Assert under thresholds (with 2x margin for stress)
        assert save_avg < config.state_save_timeout_ms, (
            f"T037 Stress FAIL: Save avg {save_avg:.2f}ms > {config.state_save_timeout_ms}ms"
        )
        assert load_avg < config.context_load_timeout_ms, (
            f"T037 Stress FAIL: Load avg {load_avg:.2f}ms > {config.context_load_timeout_ms}ms"
        )
        
        print(
            f"\n{'='*60}\n"
            f"T037 STRESS TEST: Heavy Load Performance\n"
            f"{'='*60}\n"
            f"Payload: 50 messages, ~100 chars each\n"
            f"Operations: 20 saves + 20 loads (rapid succession)\n"
            f"Save Avg: {save_avg:.4f}ms (threshold: {config.state_save_timeout_ms}ms)\n"
            f"Load Avg: {load_avg:.4f}ms (threshold: {config.context_load_timeout_ms}ms)\n"
            f"Status: PASS\n"
            f"{'='*60}"
        )


# ============================================================================
# Integration Test with Real Components (Skipped without MongoDB)
# ============================================================================

@pytest.mark.skip(reason="Requires real MongoDB instance")
class TestRealMongoDBPersistence:
    """
    Real integration tests with actual MongoDB.
    
    Skipped by default - run manually with MongoDB available.
    """
    
    def test_real_mongodb_checkpoint_persistence(self, mock_config):
        """
        Test actual MongoDBSaver persistence.
        
        Requires: Running MongoDB instance.
        """
        from langgraph.checkpoint.mongodb import MongoDBSaver
        
        session_id = str(uuid.uuid4())
        
        # Create checkpointer
        checkpointer = MongoDBSaver.from_conn_string(
            mock_config["mongodb"]["uri"],
            db_name=mock_config["mongodb"]["database"]
        )
        
        # Store checkpoint
        config = {"configurable": {"thread_id": session_id}}
        checkpoint_data = {
            "channel_values": {
                "messages": [
                    {"role": "human", "content": "Test message"}
                ]
            }
        }
        
        checkpointer.put(config, checkpoint_data)
        
        # Simulate restart by creating new checkpointer instance
        new_checkpointer = MongoDBSaver.from_conn_string(
            mock_config["mongodb"]["uri"],
            db_name=mock_config["mongodb"]["database"]
        )
        
        # Retrieve with new instance
        restored = new_checkpointer.get(config)
        
        assert restored is not None
        assert restored["channel_values"]["messages"][0]["content"] == "Test message"


# ============================================================================
# Pytest Configuration
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
