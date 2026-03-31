"""Tests for src/services/exceptions.py — service layer exceptions."""

import pytest

from services.exceptions import (
    ArchivedConversationError,
    ConversationNotFoundError,
    EntityNotFoundError,
    InvalidLifecycleTransitionError,
    OwnershipViolationError,
    ParentNotFoundError,
    ServiceError,
    StaleEntityError,
    ValidationError,
)


class TestServiceErrorHierarchy:
    """All custom exceptions must inherit from ServiceError."""

    @pytest.mark.parametrize(
        "exc_class",
        [
            ArchivedConversationError,
            ConversationNotFoundError,
            InvalidLifecycleTransitionError,
            EntityNotFoundError,
            ParentNotFoundError,
            OwnershipViolationError,
            StaleEntityError,
            ValidationError,
        ],
    )
    def test_inherits_from_service_error(self, exc_class):
        assert issubclass(exc_class, ServiceError)


# ---------------------------------------------------------------------------
# EntityNotFoundError
# ---------------------------------------------------------------------------

class TestEntityNotFoundError:

    def test_default_message(self):
        err = EntityNotFoundError("workspace", "ws-123")
        assert err.entity_type == "workspace"
        assert err.entity_id == "ws-123"
        assert "workspace" in str(err)
        assert "ws-123" in str(err)

    def test_custom_message(self):
        err = EntityNotFoundError("session", "s-1", message="Gone")
        assert str(err) == "Gone"
        assert err.message == "Gone"


# ---------------------------------------------------------------------------
# ParentNotFoundError
# ---------------------------------------------------------------------------

class TestParentNotFoundError:

    def test_default_message(self):
        err = ParentNotFoundError("workspace", "ws-1", "session")
        assert err.parent_type == "workspace"
        assert err.parent_id == "ws-1"
        assert err.child_type == "session"
        assert "workspace" in str(err)
        assert "session" in str(err)

    def test_custom_message(self):
        err = ParentNotFoundError("session", "s-1", "conversation", message="Missing parent")
        assert str(err) == "Missing parent"


# ---------------------------------------------------------------------------
# OwnershipViolationError
# ---------------------------------------------------------------------------

class TestOwnershipViolationError:

    def test_default_message(self):
        err = OwnershipViolationError("workspace", "ws-1", "user-a", "user-b")
        assert err.entity_type == "workspace"
        assert err.entity_id == "ws-1"
        assert err.expected_owner == "user-a"
        assert err.actual_owner == "user-b"
        assert "Access denied" in str(err)

    def test_does_not_leak_owner_in_default_message(self):
        err = OwnershipViolationError("workspace", "ws-1", "user-a", "user-b")
        # Default message should NOT expose owner details
        assert "user-a" not in str(err)
        assert "user-b" not in str(err)

    def test_custom_message(self):
        err = OwnershipViolationError("session", "s-1", "u1", "u2", message="Nope")
        assert str(err) == "Nope"


# ---------------------------------------------------------------------------
# StaleEntityError
# ---------------------------------------------------------------------------

class TestStaleEntityError:

    def test_default_message(self):
        err = StaleEntityError("conversation", "c-1")
        assert err.entity_type == "conversation"
        assert err.entity_id == "c-1"
        assert "modified concurrently" in str(err)

    def test_custom_message(self):
        err = StaleEntityError("session", "s-1", message="Stale")
        assert str(err) == "Stale"


# ---------------------------------------------------------------------------
# ValidationError
# ---------------------------------------------------------------------------

class TestValidationError:

    def test_attributes(self):
        err = ValidationError("name", "must not be empty")
        assert err.field == "name"
        assert err.message == "must not be empty"
        assert "name" in str(err)
        assert "must not be empty" in str(err)

    def test_str_format(self):
        err = ValidationError("limit", "must be positive")
        assert str(err) == "Validation error on 'limit': must be positive"
