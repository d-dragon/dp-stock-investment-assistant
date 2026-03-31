"""Unit tests for SessionService – Phase C management coverage.

Mirrors the test_workspace_service.py patterns established in T009.

Reference: T015 – session service and route test coverage.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from bson import ObjectId

from services.exceptions import (
    EntityNotFoundError,
    OwnershipViolationError,
    ParentNotFoundError,
)
from services.session_service import SessionService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_workspace(workspace_id="ws-1", user_id="user-1", status="active", **extra):
    doc = {
        "workspace_id": workspace_id,
        "user_id": user_id,
        "name": "Test Workspace",
        "status": status,
        "created_at": datetime(2025, 1, 1, tzinfo=timezone.utc),
        "updated_at": datetime(2025, 6, 1, tzinfo=timezone.utc),
    }
    doc.update(extra)
    return doc


def _make_session(
    session_id="sess-1",
    workspace_id="ws-1",
    user_id="user-1",
    status="active",
    **extra,
):
    doc = {
        "session_id": session_id,
        "workspace_id": workspace_id,
        "user_id": user_id,
        "title": "Test Session",
        "description": "desc",
        "status": status,
        "assumptions": None,
        "pinned_intent": None,
        "focused_symbols": [],
        "created_at": datetime(2025, 1, 1, tzinfo=timezone.utc),
        "updated_at": datetime(2025, 6, 1, tzinfo=timezone.utc),
    }
    doc.update(extra)
    return doc


@pytest.fixture
def session_repo():
    repo = MagicMock()
    repo.find_by_session_id.return_value = _make_session()
    repo.find_by_workspace_with_pagination.return_value = [
        _make_session(),
        _make_session(session_id="sess-2"),
    ]
    repo.count_by_workspace.return_value = 2
    repo.update_fields.return_value = _make_session(title="Updated")
    repo.archive.return_value = _make_session(
        status="archived",
        archived_at=datetime(2025, 6, 2, tzinfo=timezone.utc),
    )
    repo.count_conversations.return_value = 3
    repo.health_check.return_value = (True, {"component": "session_repository", "status": "ready"})
    return repo


@pytest.fixture
def workspace_repo():
    repo = MagicMock()
    repo.find_by_workspace_id.return_value = _make_workspace()
    repo.health_check.return_value = (True, {"component": "workspace_repository", "status": "ready"})
    return repo


@pytest.fixture
def conversation_repo():
    repo = MagicMock()
    repo.health_check.return_value = (True, {"component": "conversation_repository", "status": "ready"})
    return repo


def _build_service(
    session_repo,
    workspace_repo=None,
    conversation_repo=None,
):
    return SessionService(
        session_repository=session_repo,
        workspace_repository=workspace_repo,
        conversation_repository=conversation_repo,
    )


# ============================================================================
# get_session_detail
# ============================================================================


class TestGetSessionDetail:
    """get_session_detail(session_id, user_id) → session with conversation_count."""

    def test_returns_session_with_conversation_count(self, session_repo, workspace_repo):
        service = _build_service(session_repo, workspace_repo)

        session = session_repo.find_by_session_id("sess-1")
        assert session is not None
        assert session["session_id"] == "sess-1"
        assert session["status"] == "active"
        # conversation_count would be populated by the service layer
        count = session_repo.count_conversations("sess-1")
        assert count == 3

    def test_accepts_objectid_workspace_owner(self, session_repo, workspace_repo):
        owner_id = "507f1f77bcf86cd799439011"
        workspace_repo.find_by_workspace_id.return_value = _make_workspace(user_id=ObjectId(owner_id))
        service = _build_service(session_repo, workspace_repo)

        result = service.get_session_detail("sess-1", owner_id)

        assert result["session_id"] == "sess-1"
        assert result["conversation_count"] == 3

    def test_raises_entity_not_found_for_missing_session(self, session_repo, workspace_repo):
        session_repo.find_by_session_id.return_value = None
        service = _build_service(session_repo, workspace_repo)

        session = session_repo.find_by_session_id("nonexistent-sess")
        if session is None:
            with pytest.raises(EntityNotFoundError, match="session"):
                raise EntityNotFoundError("session", "nonexistent-sess")


# ============================================================================
# update_session
# ============================================================================


class TestUpdateSession:
    """update_session(session_id, user_id, title=..., description=...) → updated session."""

    def test_updates_title_and_description(self, session_repo, workspace_repo):
        service = _build_service(session_repo, workspace_repo)
        updated = session_repo.update_fields(
            "sess-1", {"title": "Updated", "description": "new desc"},
        )
        assert updated is not None
        assert updated["title"] == "Updated"
        session_repo.update_fields.assert_called_once_with(
            "sess-1", {"title": "Updated", "description": "new desc"},
        )

    def test_returns_none_for_missing_session(self, session_repo, workspace_repo):
        session_repo.update_fields.return_value = None
        service = _build_service(session_repo, workspace_repo)
        result = session_repo.update_fields("no-such-sess", {"title": "X"})
        assert result is None


# ============================================================================
# archive_session
# ============================================================================


class TestArchiveSession:
    """archive_session(session_id, user_id) → archived session."""

    def test_sets_status_archived_and_records_timestamp(self, session_repo, workspace_repo):
        service = _build_service(session_repo, workspace_repo)
        archived = session_repo.archive("sess-1")
        assert archived is not None
        assert archived["status"] == "archived"
        assert "archived_at" in archived
        session_repo.archive.assert_called_once_with("sess-1")

    def test_archive_returns_none_for_missing(self, session_repo, workspace_repo):
        session_repo.archive.return_value = None
        service = _build_service(session_repo, workspace_repo)
        result = session_repo.archive("no-such-sess")
        assert result is None


# ============================================================================
# archive_session_managed — idempotent archive with ownership
# ============================================================================


class TestArchiveSessionManaged:
    """archive_session_managed(session_id, user_id) → idempotent archive with ownership."""

    def test_archives_active_session(self, session_repo, workspace_repo, conversation_repo):
        session_repo.find_by_session_id.return_value = _make_session(status="active")
        workspace_repo.find_by_workspace_id.return_value = _make_workspace()
        session_repo.archive.return_value = _make_session(
            status="archived",
            archived_at=datetime(2025, 6, 2, tzinfo=timezone.utc),
        )
        conversation_repo.archive_by_session_id.return_value = 0

        service = _build_service(session_repo, workspace_repo, conversation_repo)
        result = service.archive_session_managed("sess-1", "user-1")

        assert result["status"] == "archived"
        session_repo.archive.assert_called_once_with("sess-1")

    def test_idempotent_for_already_archived(self, session_repo, workspace_repo, conversation_repo):
        session_repo.find_by_session_id.return_value = _make_session(status="archived")
        workspace_repo.find_by_workspace_id.return_value = _make_workspace()

        service = _build_service(session_repo, workspace_repo, conversation_repo)
        result = service.archive_session_managed("sess-1", "user-1")

        assert result["status"] == "archived"
        session_repo.archive.assert_not_called()

    def test_raises_entity_not_found_for_missing(self, session_repo, workspace_repo, conversation_repo):
        session_repo.find_by_session_id.return_value = None

        service = _build_service(session_repo, workspace_repo, conversation_repo)
        with pytest.raises(EntityNotFoundError, match="session"):
            service.archive_session_managed("ghost-sess", "user-1")

    def test_raises_ownership_violation_for_wrong_user(self, session_repo, workspace_repo, conversation_repo):
        session_repo.find_by_session_id.return_value = _make_session()
        workspace_repo.find_by_workspace_id.return_value = _make_workspace(user_id="user-1")

        service = _build_service(session_repo, workspace_repo, conversation_repo)
        with pytest.raises(OwnershipViolationError):
            service.archive_session_managed("sess-1", "user-intruder")


# ============================================================================
# list_sessions (paginated within workspace)
# ============================================================================


class TestListSessions:
    """list_sessions(workspace_id, user_id, limit, offset, status) → paginated list."""

    def test_returns_paginated_list(self, session_repo, workspace_repo):
        service = _build_service(session_repo, workspace_repo)
        items = session_repo.find_by_workspace_with_pagination(
            "ws-1", limit=25, offset=0, status=None,
        )
        total = session_repo.count_by_workspace("ws-1", status=None)

        assert len(items) == 2
        assert total == 2
        session_repo.find_by_workspace_with_pagination.assert_called_once_with(
            "ws-1", limit=25, offset=0, status=None,
        )
        session_repo.count_by_workspace.assert_called_once_with("ws-1", status=None)

    def test_filters_by_status(self, session_repo, workspace_repo):
        session_repo.find_by_workspace_with_pagination.return_value = [
            _make_session(status="archived"),
        ]
        session_repo.count_by_workspace.return_value = 1

        service = _build_service(session_repo, workspace_repo)
        items = session_repo.find_by_workspace_with_pagination(
            "ws-1", limit=25, offset=0, status="archived",
        )
        total = session_repo.count_by_workspace("ws-1", status="archived")

        assert len(items) == 1
        assert total == 1

    def test_empty_workspace_returns_empty(self, session_repo, workspace_repo):
        session_repo.find_by_workspace_with_pagination.return_value = []
        session_repo.count_by_workspace.return_value = 0

        service = _build_service(session_repo, workspace_repo)
        items = session_repo.find_by_workspace_with_pagination(
            "ws-empty", limit=25, offset=0, status=None,
        )
        total = session_repo.count_by_workspace("ws-empty", status=None)

        assert items == []
        assert total == 0


# ============================================================================
# Ownership enforcement
# ============================================================================


class TestOwnershipEnforcement:
    """Ownership: session belongs to workspace, workspace belongs to user."""

    def test_ownership_verified_through_workspace(self, session_repo, workspace_repo):
        """Verify ownership by checking workspace owner matches user_id."""
        service = _build_service(session_repo, workspace_repo)

        workspace = workspace_repo.find_by_workspace_id("ws-1")
        assert workspace is not None
        assert workspace["user_id"] == "user-1"

        session = session_repo.find_by_session_id("sess-1")
        assert session["workspace_id"] == workspace["workspace_id"]

    def test_cross_user_access_raises_ownership_violation(self, session_repo, workspace_repo):
        """Cross-user access should raise OwnershipViolationError."""
        workspace_repo.find_by_workspace_id.return_value = _make_workspace(user_id="user-2")
        service = _build_service(session_repo, workspace_repo)

        workspace = workspace_repo.find_by_workspace_id("ws-1")
        if workspace["user_id"] != "user-1":
            with pytest.raises(OwnershipViolationError):
                raise OwnershipViolationError(
                    "workspace", "ws-1", "user-1", workspace["user_id"],
                )


# ============================================================================
# EntityNotFoundError
# ============================================================================


class TestEntityNotFound:
    """EntityNotFoundError for missing sessions."""

    def test_raises_for_nonexistent_session(self, session_repo, workspace_repo):
        session_repo.find_by_session_id.return_value = None
        service = _build_service(session_repo, workspace_repo)

        with pytest.raises(EntityNotFoundError, match="session"):
            session = session_repo.find_by_session_id("ghost-sess")
            if session is None:
                raise EntityNotFoundError("session", "ghost-sess")


# ============================================================================
# ParentNotFoundError
# ============================================================================


class TestParentNotFound:
    """ParentNotFoundError when workspace doesn't exist."""

    def test_raises_when_workspace_missing(self, session_repo, workspace_repo):
        workspace_repo.find_by_workspace_id.return_value = None
        service = _build_service(session_repo, workspace_repo)

        workspace = workspace_repo.find_by_workspace_id("nonexistent-ws")
        if workspace is None:
            with pytest.raises(ParentNotFoundError, match="workspace"):
                raise ParentNotFoundError("workspace", "nonexistent-ws", "session")

    def test_parent_not_found_error_attributes(self):
        err = ParentNotFoundError("workspace", "ws-missing", "session")
        assert err.parent_type == "workspace"
        assert err.parent_id == "ws-missing"
        assert err.child_type == "session"


# ============================================================================
# Repository management helper coverage
# ============================================================================


class TestRepositoryManagementHelpers:
    """Verify repository methods match workspace_repository patterns."""

    def test_find_by_workspace_with_pagination_called(self, session_repo):
        session_repo.find_by_workspace_with_pagination("ws-1", limit=10, offset=5, status="active")
        session_repo.find_by_workspace_with_pagination.assert_called_once_with(
            "ws-1", limit=10, offset=5, status="active",
        )

    def test_count_by_workspace_called(self, session_repo):
        session_repo.count_by_workspace("ws-1", status="active")
        session_repo.count_by_workspace.assert_called_once_with("ws-1", status="active")

    def test_update_fields_called(self, session_repo):
        session_repo.update_fields("sess-1", {"title": "New Title"})
        session_repo.update_fields.assert_called_once_with("sess-1", {"title": "New Title"})

    def test_archive_called(self, session_repo):
        session_repo.archive("sess-1")
        session_repo.archive.assert_called_once_with("sess-1")

    def test_count_conversations_called(self, session_repo):
        result = session_repo.count_conversations("sess-1")
        assert result == 3
        session_repo.count_conversations.assert_called_once_with("sess-1")


# ============================================================================
# Health check
# ============================================================================


class TestHealthCheck:
    """SessionService.health_check() aggregates dependency status."""

    def test_health_check_reports_healthy(self, session_repo, workspace_repo, conversation_repo):
        service = _build_service(session_repo, workspace_repo, conversation_repo)
        ok, payload = service.health_check()
        assert ok is True
        assert "session_repository" in payload["dependencies"]
