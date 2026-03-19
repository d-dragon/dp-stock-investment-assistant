"""
Tests for Conversations Schema (FR-3.1 Short-Term Memory)

Reference: specs/spec-driven-development-pilot/data-model.md
"""

import pytest
from datetime import datetime, timezone
from typing import Dict, Any

from data.schema.conversations_schema import (
    CONVERSATIONS_SCHEMA,
    CONVERSATIONS_INDEXES,
    get_conversations_validation,
    get_conversations_indexes,
    get_default_conversation_document,
)


# -----------------------------------------------------------------------------
# Schema Structure Tests
# -----------------------------------------------------------------------------

class TestConversationsSchema:
    """Test CONVERSATIONS_SCHEMA structure per FR-3.1 spec."""
    
    def test_schema_required_fields(self):
        """Verify required fields match spec."""
        required = CONVERSATIONS_SCHEMA["required"]
        
        assert "conversation_id" in required
        assert "thread_id" in required
        assert "session_id" in required
        assert "workspace_id" in required
        assert "user_id" in required
        assert "status" in required
        assert "created_at" in required
        assert "updated_at" in required
        assert len(required) == 8
    
    def test_schema_has_17_properties(self):
        """Verify schema has all 17 properties per updated data-model."""
        properties = CONVERSATIONS_SCHEMA["properties"]
        expected_fields = [
            "_id",
            "conversation_id",
            "thread_id",
            "session_id",
            "workspace_id",
            "user_id",
            "status",
            "message_count",
            "total_tokens",
            "summary",
            "focused_symbols",
            "context_overrides",
            "conversation_intent",
            "last_activity_at",
            "created_at",
            "updated_at",
            "archived_at",
            "archive_reason",
        ]
        
        for field in expected_fields:
            assert field in properties, f"Missing field: {field}"
        
        assert len(properties) == 18  # 17 + _id
    
    def test_conversation_id_is_uuid_string_pattern(self):
        """Verify conversation_id uses UUID v4 pattern."""
        props = CONVERSATIONS_SCHEMA["properties"]["conversation_id"]
        
        assert props["bsonType"] == "string"
        assert "pattern" in props
        assert "4[0-9a-f]{3}" in props["pattern"]
    
    def test_session_id_is_uuid_string_pattern(self):
        """Verify session_id uses UUID v4 pattern (non-unique FK)."""
        props = CONVERSATIONS_SCHEMA["properties"]["session_id"]
        
        assert props["bsonType"] == "string"
        assert "pattern" in props
        assert "4[0-9a-f]{3}" in props["pattern"]
    
    def test_status_enum_values(self):
        """Verify status has exactly 3 enum values."""
        status_prop = CONVERSATIONS_SCHEMA["properties"]["status"]
        
        assert "enum" in status_prop
        assert set(status_prop["enum"]) == {"active", "summarized", "archived"}
    
    def test_focused_symbols_array_type(self):
        """Verify focused_symbols is array."""
        prop = CONVERSATIONS_SCHEMA["properties"]["focused_symbols"]
        
        assert prop["bsonType"] == "array"
        assert "items" in prop
        assert prop["items"]["bsonType"] == "string"
    
    def test_summary_nullable(self):
        """Verify summary allows null."""
        prop = CONVERSATIONS_SCHEMA["properties"]["summary"]
        
        assert prop["bsonType"] == ["string", "null"]
    
    def test_archived_at_nullable(self):
        """Verify archived_at allows null."""
        prop = CONVERSATIONS_SCHEMA["properties"]["archived_at"]
        
        assert prop["bsonType"] == ["date", "null"]
    
    def test_no_additional_properties(self):
        """Verify additionalProperties is False for strict validation."""
        assert CONVERSATIONS_SCHEMA.get("additionalProperties") is False


# -----------------------------------------------------------------------------
# Index Tests
# -----------------------------------------------------------------------------

class TestConversationsIndexes:
    """Test CONVERSATIONS_INDEXES structure per FR-3.1 spec."""
    
    def test_has_8_indexes(self):
        """Verify there are exactly 8 indexes."""
        assert len(CONVERSATIONS_INDEXES) == 8
    
    def test_conversation_id_unique_index(self):
        """Verify conversation_id has unique index."""
        idx = next(
            (i for i in CONVERSATIONS_INDEXES 
             if i["options"]["name"] == "idx_conversations_conversation_id"),
            None
        )
        
        assert idx is not None
        assert idx["keys"] == [("conversation_id", 1)]
        assert idx["options"]["unique"] is True
    
    def test_thread_id_unique_index(self):
        """Verify thread_id has unique index."""
        idx = next(
            (i for i in CONVERSATIONS_INDEXES 
             if i["options"]["name"] == "idx_conversations_thread_id"),
            None
        )
        
        assert idx is not None
        assert idx["keys"] == [("thread_id", 1)]
        assert idx["options"]["unique"] is True
    
    def test_session_id_non_unique_index(self):
        """Verify session_id has non-unique index (FK, 1:N)."""
        idx = next(
            (i for i in CONVERSATIONS_INDEXES 
             if i["options"]["name"] == "idx_conversations_session_id"),
            None
        )
        
        assert idx is not None
        assert idx["keys"] == [("session_id", 1)]
        assert idx["options"].get("unique") is not True
    
    def test_user_status_index(self):
        """Verify compound index on user_id + status."""
        idx = next(
            (i for i in CONVERSATIONS_INDEXES 
             if i["options"]["name"] == "idx_conversations_user_status"),
            None
        )
        
        assert idx is not None
        assert idx["keys"] == [("user_id", 1), ("status", 1)]
    
    def test_workspace_status_index(self):
        """Verify compound index on workspace_id + status."""
        idx = next(
            (i for i in CONVERSATIONS_INDEXES 
             if i["options"]["name"] == "idx_conversations_workspace_status"),
            None
        )
        
        assert idx is not None
        assert idx["keys"] == [("workspace_id", 1), ("status", 1)]
    
    def test_status_activity_index(self):
        """Verify compound index on status + last_activity_at."""
        idx = next(
            (i for i in CONVERSATIONS_INDEXES 
             if i["options"]["name"] == "idx_conversations_status_activity"),
            None
        )
        
        assert idx is not None
        assert idx["keys"] == [("status", 1), ("last_activity_at", 1)]
    
    def test_symbols_index(self):
        """Verify focused_symbols index exists."""
        idx = next(
            (i for i in CONVERSATIONS_INDEXES 
             if i["options"]["name"] == "idx_conversations_symbols"),
            None
        )
        
        assert idx is not None
        assert idx["keys"] == [("focused_symbols", 1)]
    
    def test_all_indexes_have_background_true(self):
        """Verify all indexes use background: true."""
        for idx in CONVERSATIONS_INDEXES:
            assert idx["options"].get("background") is True


# -----------------------------------------------------------------------------
# Helper Function Tests
# -----------------------------------------------------------------------------

class TestGetConversationsValidation:
    """Test get_conversations_validation() helper."""
    
    def test_returns_dict(self):
        """Verify returns dict with validator key."""
        result = get_conversations_validation()
        
        assert isinstance(result, dict)
        assert "validator" in result
        assert "$jsonSchema" in result["validator"]
    
    def test_validation_level_moderate(self):
        """Verify validation level is moderate."""
        result = get_conversations_validation()
        
        assert result["validationLevel"] == "moderate"
    
    def test_validation_action_warn(self):
        """Verify validation action is warn."""
        result = get_conversations_validation()
        
        assert result["validationAction"] == "warn"


class TestGetConversationsIndexes:
    """Test get_conversations_indexes() helper."""
    
    def test_returns_indexes_list(self):
        """Verify returns same as CONVERSATIONS_INDEXES."""
        result = get_conversations_indexes()
        
        assert result is CONVERSATIONS_INDEXES


# -----------------------------------------------------------------------------
# Default Document Tests
# -----------------------------------------------------------------------------

class TestGetDefaultConversationDocument:
    """Test get_default_conversation_document() helper."""
    
    def test_minimal_args(self):
        """Verify document created with required args."""
        conv_id = "a1b2c3d4-e5f6-4789-a0b1-c2d3e4f56789"
        thread_id = conv_id
        session_id = "b2c3d4e5-f6a7-4890-b1c2-d3e4f5a67890"
        
        doc = get_default_conversation_document(
            conv_id, thread_id, session_id,
            workspace_id="ws-001", user_id="user-001"
        )
        
        assert doc["conversation_id"] == conv_id
        assert doc["thread_id"] == thread_id
        assert doc["session_id"] == session_id
        assert doc["workspace_id"] == "ws-001"
        assert doc["user_id"] == "user-001"
    
    def test_includes_all_required_fields(self):
        """Verify document has all required fields set."""
        conv_id = "a1b2c3d4-e5f6-4789-a0b1-c2d3e4f56789"
        
        doc = get_default_conversation_document(
            conv_id, conv_id, "b2c3d4e5-f6a7-4890-b1c2-d3e4f5a67890",
            workspace_id="ws-001", user_id="user-001"
        )
        
        assert doc["status"] == "active"
        assert "created_at" in doc
        assert "updated_at" in doc
    
    def test_workspace_and_user_are_required(self):
        """Verify workspace_id and user_id are required keyword-only args."""
        conv_id = "a1b2c3d4-e5f6-4789-a0b1-c2d3e4f56789"
        workspace_id = "ws-123"
        user_id = "user-456"
        
        doc = get_default_conversation_document(
            conv_id, conv_id, "b2c3d4e5-f6a7-4890-b1c2-d3e4f5a67890",
            workspace_id=workspace_id,
            user_id=user_id
        )
        
        assert doc["workspace_id"] == workspace_id
        assert doc["user_id"] == user_id
    
    def test_default_numeric_values(self):
        """Verify message_count and total_tokens default to 0."""
        conv_id = "a1b2c3d4-e5f6-4789-a0b1-c2d3e4f56789"
        
        doc = get_default_conversation_document(
            conv_id, conv_id, "b2c3d4e5-f6a7-4890-b1c2-d3e4f5a67890",
            workspace_id="ws-001", user_id="user-001"
        )
        
        assert doc["message_count"] == 0
        assert doc["total_tokens"] == 0
    
    def test_default_null_values(self):
        """Verify summary, context_overrides, conversation_intent, archived_at, archive_reason are None."""
        conv_id = "a1b2c3d4-e5f6-4789-a0b1-c2d3e4f56789"
        
        doc = get_default_conversation_document(
            conv_id, conv_id, "b2c3d4e5-f6a7-4890-b1c2-d3e4f5a67890",
            workspace_id="ws-001", user_id="user-001"
        )
        
        assert doc["summary"] is None
        assert doc["context_overrides"] is None
        assert doc["conversation_intent"] is None
        assert doc["archived_at"] is None
        assert doc["archive_reason"] is None
    
    def test_focused_symbols_empty_array(self):
        """Verify focused_symbols defaults to empty array."""
        conv_id = "a1b2c3d4-e5f6-4789-a0b1-c2d3e4f56789"
        
        doc = get_default_conversation_document(
            conv_id, conv_id, "b2c3d4e5-f6a7-4890-b1c2-d3e4f5a67890",
            workspace_id="ws-001", user_id="user-001"
        )
        
        assert doc["focused_symbols"] == []
    
    def test_timestamps_are_datetime(self):
        """Verify timestamp fields are datetime objects."""
        conv_id = "a1b2c3d4-e5f6-4789-a0b1-c2d3e4f56789"
        
        doc = get_default_conversation_document(
            conv_id, conv_id, "b2c3d4e5-f6a7-4890-b1c2-d3e4f5a67890",
            workspace_id="ws-001", user_id="user-001"
        )
        
        assert isinstance(doc["created_at"], datetime)
        assert isinstance(doc["updated_at"], datetime)
        assert isinstance(doc["last_activity_at"], datetime)
    
    def test_timestamps_are_utc(self):
        """Verify timestamps use UTC timezone."""
        conv_id = "a1b2c3d4-e5f6-4789-a0b1-c2d3e4f56789"
        
        doc = get_default_conversation_document(
            conv_id, conv_id, "b2c3d4e5-f6a7-4890-b1c2-d3e4f5a67890",
            workspace_id="ws-001", user_id="user-001"
        )
        
        assert doc["created_at"].tzinfo == timezone.utc
        assert doc["updated_at"].tzinfo == timezone.utc
    
    def test_has_thread_id_field(self):
        """Verify thread_id is now a separate field."""
        conv_id = "a1b2c3d4-e5f6-4789-a0b1-c2d3e4f56789"
        
        doc = get_default_conversation_document(
            conv_id, conv_id, "b2c3d4e5-f6a7-4890-b1c2-d3e4f5a67890",
            workspace_id="ws-001", user_id="user-001"
        )
        
        assert "thread_id" in doc
        assert doc["thread_id"] == conv_id
    
    def test_no_metadata_object(self):
        """Verify metadata is flattened into direct fields."""
        conv_id = "a1b2c3d4-e5f6-4789-a0b1-c2d3e4f56789"
        
        doc = get_default_conversation_document(
            conv_id, conv_id, "b2c3d4e5-f6a7-4890-b1c2-d3e4f5a67890",
            workspace_id="ws-001", user_id="user-001"
        )
        
        assert "metadata" not in doc
