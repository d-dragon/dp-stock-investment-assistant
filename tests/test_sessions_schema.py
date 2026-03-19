"""
Tests for Sessions Schema (FR-004, FR-009, FR-009a)

Validates sessions schema structure, indexes, and helper functions
per specs/agent-session-with-stm-wiring/spec.md.
"""

import pytest

from data.schema.sessions_schema import (
    SESSIONS_SCHEMA,
    SESSIONS_INDEXES,
    get_sessions_validation,
    get_sessions_indexes,
)


# -----------------------------------------------------------------------------
# Schema Structure Tests
# -----------------------------------------------------------------------------

class TestSessionsSchema:
    """Test SESSIONS_SCHEMA structure per spec FR-004."""

    def test_schema_is_object_type(self):
        """Verify schema defines an object type."""
        assert SESSIONS_SCHEMA["bsonType"] == "object"

    def test_schema_required_fields(self):
        """Verify required fields match spec."""
        required = SESSIONS_SCHEMA["required"]

        assert "session_id" in required
        assert "workspace_id" in required
        assert "title" in required
        assert len(required) == 3

    def test_session_id_is_uuid_string_pattern(self):
        """Verify session_id uses UUID v4 pattern."""
        props = SESSIONS_SCHEMA["properties"]["session_id"]

        assert props["bsonType"] == "string"
        assert "pattern" in props
        assert "4[0-9a-f]{3}" in props["pattern"]

    def test_workspace_id_is_string(self):
        """Verify workspace_id is string (not objectId) per FR-003."""
        props = SESSIONS_SCHEMA["properties"]["workspace_id"]

        assert props["bsonType"] == "string"

    def test_user_id_is_string(self):
        """Verify user_id field exists and is string."""
        props = SESSIONS_SCHEMA["properties"]["user_id"]

        assert props["bsonType"] == "string"

    def test_title_is_string(self):
        """Verify title field is string."""
        props = SESSIONS_SCHEMA["properties"]["title"]

        assert props["bsonType"] == "string"

    def test_status_enum_values(self):
        """Verify status enum includes active, closed, archived (no 'open')."""
        status_prop = SESSIONS_SCHEMA["properties"]["status"]

        assert "enum" in status_prop
        assert set(status_prop["enum"]) == {"active", "closed", "archived"}
        assert "open" not in status_prop["enum"]

    def test_assumptions_nullable(self):
        """Verify assumptions allows null."""
        prop = SESSIONS_SCHEMA["properties"]["assumptions"]

        assert prop["bsonType"] == ["string", "null"]

    def test_pinned_intent_nullable(self):
        """Verify pinned_intent allows null."""
        prop = SESSIONS_SCHEMA["properties"]["pinned_intent"]

        assert prop["bsonType"] == ["string", "null"]

    def test_focused_symbols_array_type(self):
        """Verify focused_symbols is array of strings."""
        prop = SESSIONS_SCHEMA["properties"]["focused_symbols"]

        assert prop["bsonType"] == "array"
        assert "items" in prop
        assert prop["items"]["bsonType"] == "string"

    def test_linked_symbol_ids_array_type(self):
        """Verify linked_symbol_ids is array of strings."""
        prop = SESSIONS_SCHEMA["properties"]["linked_symbol_ids"]

        assert prop["bsonType"] == "array"
        assert "items" in prop
        assert prop["items"]["bsonType"] == "string"

    def test_created_at_is_date(self):
        """Verify created_at is date type."""
        prop = SESSIONS_SCHEMA["properties"]["created_at"]

        assert prop["bsonType"] == "date"

    def test_updated_at_is_date(self):
        """Verify updated_at is date type."""
        prop = SESSIONS_SCHEMA["properties"]["updated_at"]

        assert prop["bsonType"] == "date"

    def test_schema_has_all_expected_properties(self):
        """Verify schema has all expected property fields."""
        properties = SESSIONS_SCHEMA["properties"]
        expected_fields = [
            "session_id",
            "workspace_id",
            "user_id",
            "title",
            "status",
            "assumptions",
            "pinned_intent",
            "focused_symbols",
            "linked_symbol_ids",
            "created_at",
            "updated_at",
        ]

        for field in expected_fields:
            assert field in properties, f"Missing field: {field}"

        assert len(properties) == 11


# -----------------------------------------------------------------------------
# Index Tests
# -----------------------------------------------------------------------------

class TestSessionsIndexes:
    """Test SESSIONS_INDEXES structure per spec."""

    def test_has_3_indexes(self):
        """Verify there are exactly 3 indexes."""
        assert len(SESSIONS_INDEXES) == 3

    def test_session_id_unique_index(self):
        """Verify session_id has unique index (idx_sessions_session_id)."""
        idx = next(
            (i for i in SESSIONS_INDEXES
             if i["options"]["name"] == "idx_sessions_session_id"),
            None
        )

        assert idx is not None
        assert idx["keys"] == [("session_id", 1)]
        assert idx["options"]["unique"] is True

    def test_workspace_id_index(self):
        """Verify workspace_id has non-unique index."""
        idx = next(
            (i for i in SESSIONS_INDEXES
             if i["options"]["name"] == "idx_sessions_workspace"),
            None
        )

        assert idx is not None
        assert idx["keys"] == [("workspace_id", 1)]

    def test_workspace_status_compound_index(self):
        """Verify compound index on workspace_id + status."""
        idx = next(
            (i for i in SESSIONS_INDEXES
             if i["options"]["name"] == "idx_sessions_workspace_status"),
            None
        )

        assert idx is not None
        assert idx["keys"] == [("workspace_id", 1), ("status", 1)]

    def test_session_id_index_has_background(self):
        """Verify session_id unique index uses background: true."""
        idx = next(
            (i for i in SESSIONS_INDEXES
             if i["options"]["name"] == "idx_sessions_session_id"),
            None
        )

        assert idx["options"].get("background") is True


# -----------------------------------------------------------------------------
# Helper Function Tests
# -----------------------------------------------------------------------------

class TestGetSessionsValidation:
    """Test get_sessions_validation() helper."""

    def test_returns_dict(self):
        """Verify returns dict with validator key."""
        result = get_sessions_validation()

        assert isinstance(result, dict)
        assert "validator" in result
        assert "$jsonSchema" in result["validator"]

    def test_schema_is_sessions_schema(self):
        """Verify embedded schema matches SESSIONS_SCHEMA."""
        result = get_sessions_validation()

        assert result["validator"]["$jsonSchema"] is SESSIONS_SCHEMA

    def test_validation_level_moderate(self):
        """Verify validation level is moderate."""
        result = get_sessions_validation()

        assert result["validationLevel"] == "moderate"

    def test_validation_action_warn(self):
        """Verify validation action is warn."""
        result = get_sessions_validation()

        assert result["validationAction"] == "warn"


class TestGetSessionsIndexes:
    """Test get_sessions_indexes() helper."""

    def test_returns_indexes_list(self):
        """Verify returns same as SESSIONS_INDEXES."""
        result = get_sessions_indexes()

        assert result is SESSIONS_INDEXES

    def test_returns_list_of_dicts(self):
        """Verify each index entry has keys and options."""
        result = get_sessions_indexes()

        assert isinstance(result, list)
        for idx in result:
            assert "keys" in idx
            assert "options" in idx
            assert "name" in idx["options"]
