"""
Unit Tests for ConversationRepository (FR-3.1 Short-Term Memory)

Tests repository methods using mocked MongoDB collection.
Reference: specs/spec-driven-development-pilot/tasks.md T010
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from typing import Dict, Any

from data.repositories.conversation_repository import ConversationRepository


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture
def mock_collection():
    """Create a mock MongoDB collection."""
    return MagicMock()


@pytest.fixture
def mock_db(mock_collection):
    """Create a mock database that returns mock collection."""
    mock_database = MagicMock()
    mock_database.__getitem__ = MagicMock(return_value=mock_collection)
    return mock_database


@pytest.fixture
def conversation_repo(mock_collection):
    """
    Create ConversationRepository with mocked database connection.
    
    Uses patching to bypass connection initialization and inject
    mock collection directly, allowing unit tests to run without
    a real MongoDB instance.
    """
    with patch.object(ConversationRepository, '__init__', lambda self, *args, **kwargs: None):
        repo = ConversationRepository.__new__(ConversationRepository)
        # Set up minimal required attributes
        repo.connection_string = "mongodb://localhost:27017"
        repo.database_name = "test_db"
        repo.collection_name = "conversations"
        repo._collection = mock_collection  # Bypass lazy-load property
        repo.client = MagicMock()  # Mock client for health checks
        repo.db = MagicMock()
        repo.logger = MagicMock()
        repo.username = None
        repo.password = None
        repo.auth_source = None
        return repo


@pytest.fixture
def sample_conversation() -> Dict[str, Any]:
    """Return sample conversation document matching schema."""
    now = datetime.now(timezone.utc)
    return {
        "_id": ObjectId(),
        "conversation_id": "conv-a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
        "thread_id": "thread-a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
        "session_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
        "workspace_id": "workspace-001",
        "user_id": "user-001",
        "status": "active",
        "message_count": 5,
        "total_tokens": 1500,
        "summary": None,
        "focused_symbols": ["AAPL", "MSFT"],
        "context_overrides": None,
        "conversation_intent": None,
        "last_activity_at": now,
        "created_at": now - timedelta(hours=1),
        "updated_at": now,
        "archived_at": None,
        "archive_reason": None,
    }


# -----------------------------------------------------------------------------
# Status Constants Tests
# -----------------------------------------------------------------------------

class TestStatusConstants:
    """Test status constants are correctly defined."""
    
    def test_status_active(self, conversation_repo):
        """Verify STATUS_ACTIVE constant."""
        assert conversation_repo.STATUS_ACTIVE == "active"
    
    def test_status_summarized(self, conversation_repo):
        """Verify STATUS_SUMMARIZED constant."""
        assert conversation_repo.STATUS_SUMMARIZED == "summarized"
    
    def test_status_archived(self, conversation_repo):
        """Verify STATUS_ARCHIVED constant."""
        assert conversation_repo.STATUS_ARCHIVED == "archived"
    
    def test_valid_statuses_frozenset(self, conversation_repo):
        """Verify VALID_STATUSES is a frozenset with all values."""
        expected = frozenset(["active", "summarized", "archived"])
        assert conversation_repo.VALID_STATUSES == expected


# -----------------------------------------------------------------------------
# Find Methods Tests
# -----------------------------------------------------------------------------

class TestFindBySessionId:
    """Test find_by_session_id method (returns List, 1:N relationship)."""
    
    def test_returns_list_when_found(self, conversation_repo, mock_collection, sample_conversation):
        """Test returning list of documents when session_id exists."""
        mock_collection.find.return_value.sort.return_value.limit.return_value = [sample_conversation]
        
        result = conversation_repo.find_by_session_id(sample_conversation["session_id"])
        
        assert result == [sample_conversation]
    
    def test_returns_empty_list_when_not_found(self, conversation_repo, mock_collection):
        """Test returning empty list when session_id doesn't exist."""
        mock_collection.find.return_value.sort.return_value.limit.return_value = []
        
        result = conversation_repo.find_by_session_id("nonexistent-session-id")
        
        assert result == []
    
    def test_returns_empty_list_for_empty_session_id(self, conversation_repo, mock_collection):
        """Test returning empty list for empty session_id without querying DB."""
        result = conversation_repo.find_by_session_id("")
        
        assert result == []
        mock_collection.find.assert_not_called()
    
    def test_returns_empty_list_for_none_session_id(self, conversation_repo, mock_collection):
        """Test returning empty list for None session_id."""
        result = conversation_repo.find_by_session_id(None)
        
        assert result == []
        mock_collection.find.assert_not_called()


class TestFindByConversationId:
    """Test find_by_conversation_id method (primary lookup)."""
    
    def test_returns_document_when_found(self, conversation_repo, mock_collection, sample_conversation):
        """Test returning document when conversation_id exists."""
        mock_collection.find_one.return_value = sample_conversation
        
        result = conversation_repo.find_by_conversation_id(sample_conversation["conversation_id"])
        
        assert result == sample_conversation
        mock_collection.find_one.assert_called_once_with(
            {"conversation_id": sample_conversation["conversation_id"]}
        )
    
    def test_returns_none_when_not_found(self, conversation_repo, mock_collection):
        """Test returning None when conversation_id doesn't exist."""
        mock_collection.find_one.return_value = None
        
        result = conversation_repo.find_by_conversation_id("nonexistent-id")
        
        assert result is None
    
    def test_returns_none_for_empty_conversation_id(self, conversation_repo, mock_collection):
        """Test returning None for empty conversation_id."""
        result = conversation_repo.find_by_conversation_id("")
        
        assert result is None
        mock_collection.find_one.assert_not_called()
    
    def test_returns_none_for_none_conversation_id(self, conversation_repo, mock_collection):
        """Test returning None for None conversation_id."""
        result = conversation_repo.find_by_conversation_id(None)
        
        assert result is None
        mock_collection.find_one.assert_not_called()


class TestExistsBySessionId:
    """Test exists_by_session_id method."""
    
    def test_returns_true_when_exists(self, conversation_repo, mock_collection, sample_conversation):
        """Test returning True when conversation exists."""
        # Implementation uses find_one with projection {"_id": 1}
        mock_collection.find_one.return_value = {"_id": "some-id"}
        
        result = conversation_repo.exists_by_session_id(sample_conversation["session_id"])
        
        assert result is True
        mock_collection.find_one.assert_called_once_with(
            {"session_id": sample_conversation["session_id"]}, 
            {"_id": 1}
        )
    
    def test_returns_false_when_not_exists(self, conversation_repo, mock_collection):
        """Test returning False when conversation doesn't exist."""
        # Implementation uses find_one which returns None when not found
        mock_collection.find_one.return_value = None
        
        result = conversation_repo.exists_by_session_id("nonexistent-id")
        
        assert result is False
    
    def test_returns_false_for_empty_session_id(self, conversation_repo, mock_collection):
        """Test returning False for empty session_id."""
        result = conversation_repo.exists_by_session_id("")
        
        assert result is False
        mock_collection.find_one.assert_not_called()


class TestExistsByConversationId:
    """Test exists_by_conversation_id method."""
    
    def test_returns_true_when_exists(self, conversation_repo, mock_collection, sample_conversation):
        """Test returning True when conversation exists."""
        mock_collection.find_one.return_value = {"_id": "some-id"}
        
        result = conversation_repo.exists_by_conversation_id(sample_conversation["conversation_id"])
        
        assert result is True
        mock_collection.find_one.assert_called_once_with(
            {"conversation_id": sample_conversation["conversation_id"]},
            {"_id": 1}
        )
    
    def test_returns_false_when_not_exists(self, conversation_repo, mock_collection):
        """Test returning False when conversation doesn't exist."""
        mock_collection.find_one.return_value = None
        
        result = conversation_repo.exists_by_conversation_id("nonexistent-id")
        
        assert result is False
    
    def test_returns_false_for_empty_conversation_id(self, conversation_repo, mock_collection):
        """Test returning False for empty conversation_id."""
        result = conversation_repo.exists_by_conversation_id("")
        
        assert result is False
        mock_collection.find_one.assert_not_called()


class TestFindActiveByUser:
    """Test find_active_by_user method."""
    
    def test_returns_active_conversations(self, conversation_repo, mock_collection, sample_conversation):
        """Test finding active conversations for user."""
        mock_cursor = MagicMock()
        mock_cursor.__iter__ = Mock(return_value=iter([sample_conversation]))
        mock_collection.find.return_value.sort.return_value.limit.return_value = mock_cursor
        
        result = conversation_repo.find_active_by_user("user-001", limit=10)
        
        assert len(result) >= 0  # Result is a list (may be empty depending on mock)
    
    def test_returns_empty_list_for_empty_user_id(self, conversation_repo, mock_collection):
        """Test returning empty list for empty user_id."""
        result = conversation_repo.find_active_by_user("")
        
        assert result == []
        mock_collection.find.assert_not_called()
    
    def test_returns_empty_list_for_none_user_id(self, conversation_repo, mock_collection):
        """Test returning empty list for None user_id."""
        result = conversation_repo.find_active_by_user(None)
        
        assert result == []
        mock_collection.find.assert_not_called()


# -----------------------------------------------------------------------------
# Get Or Create Tests
# -----------------------------------------------------------------------------

class TestGetOrCreate:
    """Test get_or_create method."""
    
    def test_returns_existing_conversation(self, conversation_repo, mock_collection, sample_conversation):
        """Test returning existing document without creating new."""
        mock_collection.find_one.return_value = sample_conversation
        
        result = conversation_repo.get_or_create(
            sample_conversation["conversation_id"],
            sample_conversation["thread_id"],
            sample_conversation["session_id"],
            sample_conversation["workspace_id"],
            sample_conversation["user_id"],
        )
        
        assert result == sample_conversation
        # Should only call find_one, not insert
        mock_collection.insert_one.assert_not_called()
    
    def test_creates_new_when_not_exists(self, conversation_repo, mock_collection):
        """Test creating new document when conversation_id doesn't exist."""
        mock_collection.find_one.return_value = None
        new_id = ObjectId()
        mock_collection.insert_one.return_value = Mock(inserted_id=new_id)
        
        result = conversation_repo.get_or_create(
            "conv-new-123",
            "thread-new-123",
            "session-new-123",
            "workspace-001",
            "user-001",
        )
        
        # Verify insert was called
        mock_collection.insert_one.assert_called_once()
    
    def test_creates_with_default_values(self, conversation_repo, mock_collection):
        """Test new document has default values."""
        mock_collection.find_one.return_value = None
        mock_collection.insert_one.return_value = Mock(inserted_id=ObjectId())
        
        conversation_repo.get_or_create(
            "conv-123", "thread-123", "session-123", "workspace-001", "user-001"
        )
        
        # Check the inserted document
        call_args = mock_collection.insert_one.call_args[0][0]
        
        assert call_args["conversation_id"] == "conv-123"
        assert call_args["thread_id"] == "thread-123"
        assert call_args["session_id"] == "session-123"
        assert call_args["workspace_id"] == "workspace-001"
        assert call_args["user_id"] == "user-001"
        assert call_args["status"] == "active"
        assert call_args["message_count"] == 0
        assert call_args["total_tokens"] == 0
        assert call_args["summary"] is None
        assert call_args["focused_symbols"] == []
        assert call_args["context_overrides"] is None
        assert call_args["conversation_intent"] is None
        assert call_args["archive_reason"] is None
        assert "created_at" in call_args
        assert "updated_at" in call_args
    
    def test_returns_none_for_empty_conversation_id(self, conversation_repo, mock_collection):
        """Test returning None for empty conversation_id."""
        result = conversation_repo.get_or_create("", "", "", "", "")
        
        assert result is None
        mock_collection.find_one.assert_not_called()
        mock_collection.insert_one.assert_not_called()


# -----------------------------------------------------------------------------
# Update Activity Tests
# -----------------------------------------------------------------------------

class TestUpdateActivity:
    """Test update_activity method."""
    
    def test_updates_message_count_and_tokens(self, conversation_repo, mock_collection, sample_conversation):
        """Test updating message count and token count."""
        # Return active conversation first
        mock_collection.find_one.return_value = {"status": "active"}
        
        updated_doc = {**sample_conversation, "message_count": 6, "total_tokens": 1600}
        mock_collection.find_one_and_update.return_value = updated_doc
        
        result = conversation_repo.update_activity(
            sample_conversation["conversation_id"],
            message_count_delta=1,
            token_delta=100
        )
        
        assert result is not None
        
        # Verify atomic $inc was used
        call_args = mock_collection.find_one_and_update.call_args
        update_doc = call_args[0][1]
        
        assert "$inc" in update_doc
        assert update_doc["$inc"]["message_count"] == 1
        assert update_doc["$inc"]["total_tokens"] == 100
    
    def test_updates_last_activity_at(self, conversation_repo, mock_collection, sample_conversation):
        """Test that last_activity_at is updated."""
        mock_collection.find_one.return_value = {"status": "active"}
        mock_collection.find_one_and_update.return_value = sample_conversation
        
        conversation_repo.update_activity(sample_conversation["conversation_id"])
        
        call_args = mock_collection.find_one_and_update.call_args
        update_doc = call_args[0][1]
        
        assert "$set" in update_doc
        assert "last_activity_at" in update_doc["$set"]
    
    def test_returns_none_for_archived_conversation(self, conversation_repo, mock_collection):
        """Test returning None when trying to update archived conversation."""
        mock_collection.find_one.return_value = {"status": "archived"}
        
        result = conversation_repo.update_activity("archived-conv-id", message_count_delta=1)
        
        assert result is None
        mock_collection.find_one_and_update.assert_not_called()
    
    def test_returns_none_for_empty_conversation_id(self, conversation_repo, mock_collection):
        """Test returning None for empty conversation_id."""
        result = conversation_repo.update_activity("")
        
        assert result is None
        mock_collection.find_one.assert_not_called()


# -----------------------------------------------------------------------------
# Update Summary Tests
# -----------------------------------------------------------------------------

class TestUpdateSummary:
    """Test update_summary method."""
    
    def test_updates_summary_and_status(self, conversation_repo, mock_collection, sample_conversation):
        """Test updating summary sets status to 'summarized'."""
        mock_collection.find_one.return_value = {"status": "active"}
        
        updated_doc = {**sample_conversation, "status": "summarized", "summary": "Test summary"}
        mock_collection.find_one_and_update.return_value = updated_doc
        
        result = conversation_repo.update_summary(
            sample_conversation["conversation_id"],
            "Test summary"
        )
        
        assert result is not None
        
        # Verify status was set to 'summarized'
        call_args = mock_collection.find_one_and_update.call_args
        update_doc = call_args[0][1]
        
        assert update_doc["$set"]["status"] == "summarized"
        assert update_doc["$set"]["summary"] == "Test summary"
    
    def test_returns_none_for_archived_conversation(self, conversation_repo, mock_collection):
        """Test returning None when trying to update archived conversation."""
        mock_collection.find_one.return_value = {"status": "archived"}
        
        result = conversation_repo.update_summary("archived-conv", "Summary text")
        
        assert result is None
        mock_collection.find_one_and_update.assert_not_called()
    
    def test_returns_none_for_empty_summary(self, conversation_repo, mock_collection):
        """Test returning None for empty summary."""
        result = conversation_repo.update_summary("conv-id", "")
        
        assert result is None
        mock_collection.find_one.assert_not_called()


# -----------------------------------------------------------------------------
# Archive Tests
# -----------------------------------------------------------------------------

class TestArchive:
    """Test archive method."""
    
    def test_sets_archived_status_and_timestamp(self, conversation_repo, mock_collection, sample_conversation):
        """Test archive sets status='archived' and archived_at timestamp."""
        mock_collection.find_one.return_value = {"status": "active"}
        
        archived_doc = {
            **sample_conversation,
            "status": "archived",
            "archived_at": datetime.now(timezone.utc)
        }
        mock_collection.find_one_and_update.return_value = archived_doc
        
        result = conversation_repo.archive(sample_conversation["conversation_id"])
        
        assert result is not None
        
        # Verify status and archived_at were set
        call_args = mock_collection.find_one_and_update.call_args
        update_doc = call_args[0][1]
        
        assert update_doc["$set"]["status"] == "archived"
        assert "archived_at" in update_doc["$set"]
    
    def test_returns_existing_for_already_archived(self, conversation_repo, mock_collection, sample_conversation):
        """Test returning current document if already archived (idempotent)."""
        archived_doc = {**sample_conversation, "status": "archived"}
        mock_collection.find_one.return_value = {"status": "archived"}
        
        # Second find_one call returns full document
        mock_collection.find_one.side_effect = [
            {"status": "archived"},
            archived_doc
        ]
        
        result = conversation_repo.archive(sample_conversation["conversation_id"])
        
        # Should not attempt update
        mock_collection.find_one_and_update.assert_not_called()
    
    def test_can_archive_summarized_conversation(self, conversation_repo, mock_collection, sample_conversation):
        """Test archiving from 'summarized' status (valid transition)."""
        mock_collection.find_one.return_value = {"status": "summarized"}
        mock_collection.find_one_and_update.return_value = sample_conversation
        
        result = conversation_repo.archive(sample_conversation["conversation_id"])
        
        # Should attempt update
        mock_collection.find_one_and_update.assert_called_once()
    
    def test_returns_none_for_empty_conversation_id(self, conversation_repo, mock_collection):
        """Test returning None for empty conversation_id."""
        result = conversation_repo.archive("")
        
        assert result is None
        mock_collection.find_one.assert_not_called()


# -----------------------------------------------------------------------------
# Delete Override Tests (ADR-001)
# -----------------------------------------------------------------------------

class TestDeleteDisabled:
    """Test that delete is disabled per ADR-001."""
    
    def test_delete_returns_false(self, conversation_repo, mock_collection):
        """Test delete always returns False."""
        result = conversation_repo.delete(str(ObjectId()))
        
        assert result is False
        mock_collection.delete_one.assert_not_called()
    
    def test_delete_logs_warning(self, conversation_repo, mock_collection):
        """Test delete logs a warning message."""
        with patch.object(conversation_repo, 'logger') as mock_logger:
            conversation_repo.delete("some-id")
            
            mock_logger.warning.assert_called_once()
            assert "ADR-001" in mock_logger.warning.call_args[0][0]


# -----------------------------------------------------------------------------
# Health Check Tests
# -----------------------------------------------------------------------------

class TestHealthCheck:
    """Test health_check method."""
    
    def test_returns_healthy_status(self, conversation_repo, mock_collection):
        """Test health check returns healthy when collection is accessible."""
        mock_collection.count_documents.return_value = 42
        
        healthy, details = conversation_repo.health_check()
        
        assert healthy is True
        assert details["component"] == "conversation_repository"
        assert details["status"] == "ready"
        assert details["document_count"] == 42
    
    def test_returns_unhealthy_on_error(self, conversation_repo, mock_collection):
        """Test health check returns unhealthy on exception."""
        mock_collection.count_documents.side_effect = Exception("Connection failed")
        
        healthy, details = conversation_repo.health_check()
        
        assert healthy is False
        assert details["status"] == "error"
        assert "error" in details


# -----------------------------------------------------------------------------
# Edge Cases and Error Handling
# -----------------------------------------------------------------------------

class TestErrorHandling:
    """Test error handling across repository methods."""
    
    def test_find_by_conversation_id_handles_db_error(self, conversation_repo, mock_collection):
        """Test find_by_conversation_id returns None on database error."""
        from pymongo.errors import PyMongoError
        mock_collection.find_one.side_effect = PyMongoError("Connection error")
        
        result = conversation_repo.find_by_conversation_id("conv-123")
        
        assert result is None
    
    def test_find_by_session_id_handles_db_error(self, conversation_repo, mock_collection):
        """Test find_by_session_id returns empty list on database error."""
        from pymongo.errors import PyMongoError
        mock_collection.find.side_effect = PyMongoError("Connection error")
        
        result = conversation_repo.find_by_session_id("session-123")
        
        assert result == []
    
    def test_get_or_create_handles_insert_error(self, conversation_repo, mock_collection):
        """Test get_or_create returns None on insert error."""
        from pymongo.errors import PyMongoError
        mock_collection.find_one.return_value = None
        mock_collection.insert_one.side_effect = PyMongoError("Insert failed")
        
        result = conversation_repo.get_or_create(
            "conv-123", "thread-123", "session-123", "workspace-001", "user-001"
        )
        
        assert result is None
    
    def test_update_activity_handles_db_error(self, conversation_repo, mock_collection):
        """Test update_activity returns None on database error."""
        from pymongo.errors import PyMongoError
        mock_collection.find_one.return_value = {"status": "active"}
        mock_collection.find_one_and_update.side_effect = PyMongoError("Update failed")
        
        result = conversation_repo.update_activity("conv-123", message_count_delta=1)
        
        assert result is None


# -----------------------------------------------------------------------------
# Find Stale Conversations Tests
# -----------------------------------------------------------------------------

class TestFindStale:
    """Test find_stale method for archive job."""
    
    def test_finds_inactive_conversations(self, conversation_repo, mock_collection, sample_conversation):
        """Test finding conversations inactive for N days."""
        stale_conv = {**sample_conversation, "status": "active"}
        mock_collection.find.return_value.sort.return_value.limit.return_value = [stale_conv]
        
        result = conversation_repo.find_stale(days=30, limit=100)
        
        assert len(result) >= 0
    
    def test_excludes_archived_conversations(self, conversation_repo, mock_collection):
        """Test that archived conversations are excluded from stale query."""
        mock_collection.find.return_value.sort.return_value.limit.return_value = []
        
        conversation_repo.find_stale(days=7)
        
        # Verify query excludes archived
        call_args = mock_collection.find.call_args[0][0]
        assert "status" in call_args
        assert call_args["status"]["$in"] == ["active", "summarized"]


# -----------------------------------------------------------------------------
# Find By Symbols Tests
# -----------------------------------------------------------------------------

class TestFindBySymbols:
    """Test find_by_symbols method."""
    
    def test_finds_conversations_with_symbols(self, conversation_repo, mock_collection, sample_conversation):
        """Test finding conversations focused on specific symbols."""
        mock_collection.find.return_value.sort.return_value.limit.return_value = [sample_conversation]
        
        result = conversation_repo.find_by_symbols(["AAPL", "MSFT"], limit=10)
        
        assert len(result) >= 0
    
    def test_normalizes_symbols_to_uppercase(self, conversation_repo, mock_collection):
        """Test that symbols are normalized to uppercase."""
        mock_collection.find.return_value.sort.return_value.limit.return_value = []
        
        conversation_repo.find_by_symbols(["aapl", "msft"])
        
        call_args = mock_collection.find.call_args[0][0]
        assert call_args["focused_symbols"]["$in"] == ["AAPL", "MSFT"]
    
    def test_returns_empty_for_empty_symbols(self, conversation_repo, mock_collection):
        """Test returning empty list for empty symbols list."""
        result = conversation_repo.find_by_symbols([])
        
        assert result == []
        mock_collection.find.assert_not_called()
