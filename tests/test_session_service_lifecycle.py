"""
Tests for SessionService lifecycle, workspace validation, and cascade behavior.

Covers verification findings E1-E5:
- E1: close_session does NOT cascade archive to children
- E2: active→archived transition is blocked (must go through closed)
- E3: archive cascade uses archive_reason="session_archived"
- E5: create_session validates workspace existence
"""

import pytest
from unittest.mock import MagicMock, patch

from services.session_service import SessionService, _VALID_TRANSITIONS
from services.exceptions import InvalidLifecycleTransitionError, OwnershipViolationError, ParentNotFoundError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def session_repo():
    repo = MagicMock()
    repo.health_check.return_value = (True, {"status": "ready"})
    return repo


@pytest.fixture
def conversation_repo():
    repo = MagicMock()
    repo.archive_by_session_id.return_value = 3
    repo.health_check.return_value = (True, {"status": "ready"})
    return repo


@pytest.fixture
def workspace_repo():
    repo = MagicMock()
    repo.get_by_id.return_value = {"_id": "ws-001", "name": "Test Workspace", "user_id": "user-001"}
    repo.find_by_workspace_id = MagicMock(return_value={"_id": "ws-001", "name": "Test Workspace", "user_id": "user-001"})
    repo.health_check.return_value = (True, {"status": "ready"})
    return repo


@pytest.fixture
def service(session_repo, conversation_repo, workspace_repo):
    return SessionService(
        session_repository=session_repo,
        conversation_repository=conversation_repo,
        workspace_repository=workspace_repo,
    )


@pytest.fixture
def service_no_workspace(session_repo, conversation_repo):
    """Service without workspace_repository (backward compat)."""
    return SessionService(
        session_repository=session_repo,
        conversation_repository=conversation_repo,
    )


# ---------------------------------------------------------------------------
# E2: Valid Transitions (active→closed→archived only)
# ---------------------------------------------------------------------------

class TestValidTransitions:
    """E2: Verify active→archived skip is forbidden."""

    def test_active_can_transition_to_closed(self):
        assert "closed" in _VALID_TRANSITIONS["active"]

    def test_active_cannot_transition_to_archived(self):
        assert "archived" not in _VALID_TRANSITIONS["active"]

    def test_closed_can_transition_to_archived(self):
        assert "archived" in _VALID_TRANSITIONS["closed"]

    def test_archived_has_no_transitions(self):
        assert _VALID_TRANSITIONS.get("archived", set()) == set()

    def test_active_to_archived_raises(self, service, session_repo):
        """E2: active→archived must raise InvalidLifecycleTransitionError."""
        session_repo.find_by_session_id.return_value = {
            "session_id": "s1", "status": "active"
        }

        with pytest.raises(InvalidLifecycleTransitionError):
            service.archive_session("s1")

    def test_closed_to_active_raises(self, service, session_repo):
        session_repo.find_by_session_id.return_value = {
            "session_id": "s1", "status": "closed"
        }

        with pytest.raises(InvalidLifecycleTransitionError):
            service._transition("s1", "active")

    def test_archived_to_active_raises(self, service, session_repo):
        session_repo.find_by_session_id.return_value = {
            "session_id": "s1", "status": "archived"
        }

        with pytest.raises(InvalidLifecycleTransitionError):
            service._transition("s1", "active")


# ---------------------------------------------------------------------------
# E1: close_session does NOT cascade
# ---------------------------------------------------------------------------

class TestCloseSessionNoCascade:
    """E1: Closing a session must not archive child conversations."""

    def test_close_session_transitions_to_closed(self, service, session_repo):
        session_repo.find_by_session_id.return_value = {
            "session_id": "s1", "status": "active"
        }
        session_repo.update_status.return_value = {"session_id": "s1", "status": "closed"}

        result = service.close_session("s1")

        assert result is not None
        session_repo.update_status.assert_called_once_with("s1", "closed")

    def test_close_session_does_not_archive_conversations(
        self, service, session_repo, conversation_repo
    ):
        """E1: archive_by_session_id must NOT be called on close."""
        session_repo.find_by_session_id.return_value = {
            "session_id": "s1", "status": "active"
        }
        session_repo.update_status.return_value = {"session_id": "s1", "status": "closed"}

        service.close_session("s1")

        conversation_repo.archive_by_session_id.assert_not_called()


# ---------------------------------------------------------------------------
# E1+E3: archive_session DOES cascade with correct reason
# ---------------------------------------------------------------------------

class TestArchiveSessionCascade:
    """E1+E3: Only archive_session cascades, using 'session_archived' reason."""

    def test_archive_session_cascades_to_conversations(
        self, service, session_repo, conversation_repo
    ):
        session_repo.find_by_session_id.return_value = {
            "session_id": "s1", "status": "closed"
        }
        session_repo.update_status.return_value = {"session_id": "s1", "status": "archived"}

        service.archive_session("s1")

        conversation_repo.archive_by_session_id.assert_called_once_with(
            "s1", archive_reason="session_archived"
        )

    def test_archive_reason_is_session_archived(
        self, service, session_repo, conversation_repo
    ):
        """E3: Reason must be 'session_archived', not 'session_closed'."""
        session_repo.find_by_session_id.return_value = {
            "session_id": "s1", "status": "closed"
        }
        session_repo.update_status.return_value = {"session_id": "s1", "status": "archived"}

        service.archive_session("s1")

        call_args = conversation_repo.archive_by_session_id.call_args
        assert call_args[1]["archive_reason"] == "session_archived"

    def test_archive_returns_updated_session(self, service, session_repo):
        session_repo.find_by_session_id.return_value = {
            "session_id": "s1", "status": "closed"
        }
        expected = {"session_id": "s1", "status": "archived"}
        session_repo.update_status.return_value = expected

        result = service.archive_session("s1")

        assert result == expected


# ---------------------------------------------------------------------------
# E5: Workspace ownership validation in create_session
# ---------------------------------------------------------------------------

class TestWorkspaceValidation:
    """E5: create_session must validate workspace exists."""

    def test_create_session_validates_workspace(self, service, workspace_repo, session_repo):
        session_repo.create.return_value = "new-id"

        result = service.create_session("s1", "ws-001", "user-001", title="Test")

        workspace_repo.find_by_workspace_id.assert_called_once_with("ws-001")
        assert result is not None

    def test_create_session_rejects_unknown_workspace(self, service, workspace_repo, session_repo):
        """E5: Raises ParentNotFoundError when workspace does not exist."""
        workspace_repo.find_by_workspace_id.return_value = None

        with pytest.raises(ParentNotFoundError):
            service.create_session("s1", "ws-bad", "user-001", title="Test")

        workspace_repo.find_by_workspace_id.assert_called_once_with("ws-bad")
        session_repo.create.assert_not_called()

    def test_create_session_works_without_workspace_repo(
        self, service_no_workspace, session_repo
    ):
        """E5: When workspace_repository is absent, skip validation (backward compat)."""
        session_repo.create.return_value = "new-id"

        result = service_no_workspace.create_session("s1", "ws-001", "user-001", title="Test")

        assert result is not None
        session_repo.create.assert_called_once()


# ---------------------------------------------------------------------------
# Health check includes workspace_repository
# ---------------------------------------------------------------------------

class TestHealthCheckWithWorkspace:

    def test_health_check_includes_workspace_repo(self, service):
        healthy, details = service.health_check()
        assert healthy is True

    def test_health_check_without_workspace_repo(self, service_no_workspace):
        healthy, details = service_no_workspace.health_check()
        assert healthy is True
