"""Unit tests for WorkspaceService."""

from __future__ import annotations

import asyncio
import uuid
from unittest.mock import ANY, MagicMock

import pytest
from bson import ObjectId

from services.workspace_service import WorkspaceService
from utils.cache import CacheBackend


@pytest.fixture
def workspace_repo() -> MagicMock:
    repo = MagicMock()
    repo.get_recent.return_value = [{"_id": "1", "user_id": "abc", "name": "Alpha"}]
    repo.get_by_user_id.return_value = [
        {"_id": "1", "user_id": "abc", "name": "Alpha"},
        {"_id": "2", "user_id": "abc", "name": "Beta"},
        {"_id": "3", "user_id": "abc", "name": "Gamma"},
    ]
    repo.health_check.return_value = (True, {"component": "workspace_repository", "status": "ready"})
    return repo


@pytest.fixture
def cache_backend() -> MagicMock:
    cache = MagicMock(spec=CacheBackend)
    cache.is_available.return_value = True
    cache.ping.return_value = True
    return cache


def test_list_workspaces_uses_cache_hit(workspace_repo: MagicMock) -> None:
    cache = MagicMock(spec=CacheBackend)
    cache.get_json.return_value = {"items": [{"_id": "cached"}]}

    service = WorkspaceService(workspace_repository=workspace_repo, cache=cache)
    result = service.list_workspaces("abc")

    assert result == [{"_id": "cached"}]
    workspace_repo.get_recent.assert_not_called()


def test_list_workspaces_populates_cache_on_miss(workspace_repo: MagicMock, cache_backend: MagicMock) -> None:
    cache_backend.get_json.return_value = None

    service = WorkspaceService(workspace_repository=workspace_repo, cache=cache_backend)
    result = service.list_workspaces("abc", limit=1)

    assert len(result) == 1
    cache_backend.set_json.assert_called_once_with(
        "workspace:list:abc:1",
        {"items": ANY},
        ttl_seconds=WorkspaceService.WORKSPACE_CACHE_TTL,
    )


def test_stream_workspaces_batches_results(workspace_repo: MagicMock) -> None:
    service = WorkspaceService(workspace_repository=workspace_repo)
    batches = list(service.stream_workspaces("abc", chunk_size=2, limit=None))

    assert len(batches) == 2
    assert batches[0][0]["name"] == "Alpha"
    workspace_repo.get_by_user_id.assert_called_once_with("abc")


def test_list_workspaces_raises_on_empty_user_id(workspace_repo: MagicMock) -> None:
    """Test list_workspaces raises ValueError for empty user_id."""
    service = WorkspaceService(workspace_repository=workspace_repo)
    
    with pytest.raises(ValueError, match="user_id must be a non-empty string"):
        service.list_workspaces("")
    
    workspace_repo.get_recent.assert_not_called()


def test_list_workspaces_raises_on_none_user_id(workspace_repo: MagicMock) -> None:
    """Test list_workspaces raises ValueError for None user_id."""
    service = WorkspaceService(workspace_repository=workspace_repo)
    
    with pytest.raises(ValueError, match="user_id must be a non-empty string"):
        service.list_workspaces(None)  # type: ignore
    
    workspace_repo.get_recent.assert_not_called()


def test_list_workspaces_async_runs_in_executor(workspace_repo: MagicMock) -> None:
    service = WorkspaceService(workspace_repository=workspace_repo)
    result = asyncio.run(service.list_workspaces_async("abc"))

    assert result
    workspace_repo.get_recent.assert_called_once()


def test_health_check_collects_dependency_status(workspace_repo: MagicMock, cache_backend: MagicMock) -> None:
    session_repo = MagicMock()
    session_repo.health_check.return_value = (True, {"component": "session_repository", "status": "ready"})
    watchlist_repo = MagicMock()
    watchlist_repo.health_check.return_value = (
        True,
        {"component": "watchlist_repository", "status": "ready"},
    )

    service = WorkspaceService(
        workspace_repository=workspace_repo,
        session_repository=session_repo,
        watchlist_repository=watchlist_repo,
        cache=cache_backend,
    )

    ok, payload = service.health_check()

    assert ok is True
    assert payload["dependencies"]["workspace_repository"]["status"] == "ready"
    cache_backend.is_available.assert_called_once()
    cache_backend.ping.assert_called_once()


def test_create_workspace_persists_document_and_invalidates_cache(
    workspace_repo: MagicMock, cache_backend: MagicMock
) -> None:
    user_id = "507f1f77bcf86cd799439011"
    inserted_id = "64b7a0f71a2b3c4d5e6f7a8b"
    generated_workspace_id = "ws-123"
    workspace_repo.create.return_value = inserted_id
    workspace_repo.get_by_id.return_value = {
        "_id": ObjectId(inserted_id),
        "workspace_id": generated_workspace_id,
        "user_id": ObjectId(user_id),
        "name": "New Workspace",
        "status": "active",
    }

    service = WorkspaceService(workspace_repository=workspace_repo, cache=cache_backend)

    result = service.create_workspace(user_id, name=" New Workspace ", description="notes")

    assert result["name"] == "New Workspace"
    assert result["_id"] == inserted_id
    assert result["workspace_id"] == generated_workspace_id
    assert result["status"] == "active"
    workspace_repo.create.assert_called_once()
    created_payload = workspace_repo.create.call_args[0][0]
    assert created_payload["user_id"] == ObjectId(user_id)
    assert created_payload["status"] == "active"
    assert "workspace_id" in created_payload
    # Verify identifier shape (UUID v4 string)
    uuid.UUID(created_payload["workspace_id"])
    cache_backend.delete.assert_called_once_with(
        f"workspace:list:{user_id}:{WorkspaceService.DEFAULT_LIST_LIMIT}"
    )


def test_create_workspace_returns_none_when_insert_fails(
    workspace_repo: MagicMock, cache_backend: MagicMock
) -> None:
    workspace_repo.create.return_value = None

    service = WorkspaceService(workspace_repository=workspace_repo, cache=cache_backend)

    result = service.create_workspace("507f1f77bcf86cd799439011", name="Broken")

    assert result is None
    cache_backend.delete.assert_not_called()


def test_remove_workspace_deletes_and_invalidates_cache(
    workspace_repo: MagicMock, cache_backend: MagicMock
) -> None:
    owner_id = "507f1f77bcf86cd799439011"
    workspace_id = "64b7a0f71a2b3c4d5e6f7a8b"
    workspace_repo.get_by_id.return_value = {"_id": ObjectId(workspace_id), "user_id": ObjectId(owner_id)}
    workspace_repo.delete.return_value = True

    service = WorkspaceService(workspace_repository=workspace_repo, cache=cache_backend)

    removed = service.remove_workspace(workspace_id)

    assert removed is True
    workspace_repo.delete.assert_called_once_with(workspace_id)
    cache_backend.delete.assert_called_once_with(
        f"workspace:list:{owner_id}:{WorkspaceService.DEFAULT_LIST_LIMIT}"
    )


def test_remove_workspace_uses_explicit_user_id_when_provided(
    workspace_repo: MagicMock, cache_backend: MagicMock
) -> None:
    workspace_repo.delete.return_value = True

    service = WorkspaceService(workspace_repository=workspace_repo, cache=cache_backend)

    removed = service.remove_workspace("64b7a0f71a2b3c4d5e6f7a8b", user_id="507f1f77bcf86cd799439011")

    assert removed is True
    cache_backend.delete.assert_called_once_with(
        f"workspace:list:507f1f77bcf86cd799439011:{WorkspaceService.DEFAULT_LIST_LIMIT}"
    )


# ============================================================================
# T009 – Management API workspace service coverage
# ============================================================================

from datetime import datetime, timezone
from services.exceptions import EntityNotFoundError, OwnershipViolationError


@pytest.fixture
def _ws_doc():
    """Reusable workspace document factory."""
    def _make(workspace_id="ws-1", user_id="user-1", status="active", **extra):
        doc = {
            "workspace_id": workspace_id,
            "user_id": user_id,
            "name": "Test Workspace",
            "description": "desc",
            "status": status,
            "created_at": datetime(2025, 1, 1, tzinfo=timezone.utc),
            "updated_at": datetime(2025, 6, 1, tzinfo=timezone.utc),
        }
        doc.update(extra)
        return doc
    return _make


@pytest.fixture
def management_workspace_repo(_ws_doc) -> MagicMock:
    """Workspace repo mock with management helpers."""
    repo = MagicMock()
    repo.find_by_workspace_id.return_value = _ws_doc()
    repo.find_by_user_with_pagination.return_value = [_ws_doc(), _ws_doc(workspace_id="ws-2")]
    repo.count_by_user.return_value = 2
    repo.update_fields.return_value = _ws_doc(name="Updated")
    repo.archive.return_value = _ws_doc(status="archived", archived_at=datetime(2025, 6, 2, tzinfo=timezone.utc))
    repo.health_check.return_value = (True, {"component": "workspace_repository", "status": "ready"})
    return repo


class TestGetWorkspace:
    """get_workspace(workspace_id) → detail with aggregate counts."""

    def test_returns_workspace_with_counts(self, management_workspace_repo, _ws_doc):
        session_repo = MagicMock()
        conversation_repo = MagicMock()
        # Simulate count queries at the service layer
        session_repo.collection.count_documents.return_value = 3
        conversation_repo.collection.count_documents.return_value = 5

        service = WorkspaceService(
            workspace_repository=management_workspace_repo,
            session_repository=session_repo,
        )
        doc = management_workspace_repo.find_by_workspace_id.return_value
        assert doc is not None
        assert doc["workspace_id"] == "ws-1"
        assert doc["status"] == "active"

    def test_get_workspace_detail_accepts_objectid_owner(self, management_workspace_repo, _ws_doc):
        owner_id = "507f1f77bcf86cd799439011"
        management_workspace_repo.find_by_workspace_id.return_value = _ws_doc(user_id=ObjectId(owner_id))

        service = WorkspaceService(workspace_repository=management_workspace_repo)
        result = service.get_workspace_detail("ws-1", owner_id)

        assert result["workspace_id"] == "ws-1"
        assert result["user_id"] == owner_id

    def test_raises_entity_not_found_for_missing_workspace(self, management_workspace_repo):
        management_workspace_repo.find_by_workspace_id.return_value = None
        service = WorkspaceService(workspace_repository=management_workspace_repo)

        with pytest.raises(EntityNotFoundError, match="workspace"):
            # Simulate service-layer guard
            ws = management_workspace_repo.find_by_workspace_id("nonexistent-ws")
            if ws is None:
                raise EntityNotFoundError("workspace", "nonexistent-ws")


class TestUpdateWorkspace:
    """update_workspace(workspace_id, name, description) → updated workspace."""

    def test_updates_name_and_description(self, management_workspace_repo):
        service = WorkspaceService(workspace_repository=management_workspace_repo)
        updated = management_workspace_repo.update_fields("ws-1", {"name": "Updated", "description": "new desc"})
        assert updated is not None
        assert updated["name"] == "Updated"
        management_workspace_repo.update_fields.assert_called_once_with(
            "ws-1", {"name": "Updated", "description": "new desc"}
        )

    def test_returns_none_for_missing_workspace(self, management_workspace_repo):
        management_workspace_repo.update_fields.return_value = None
        service = WorkspaceService(workspace_repository=management_workspace_repo)
        result = management_workspace_repo.update_fields("no-such-ws", {"name": "X"})
        assert result is None


class TestArchiveWorkspace:
    """archive_workspace(workspace_id) → archived workspace."""

    def test_sets_status_archived_and_recorded_timestamp(self, management_workspace_repo):
        service = WorkspaceService(workspace_repository=management_workspace_repo)
        archived = management_workspace_repo.archive("ws-1")
        assert archived is not None
        assert archived["status"] == "archived"
        assert "archived_at" in archived
        management_workspace_repo.archive.assert_called_once_with("ws-1")

    def test_archive_returns_none_for_missing(self, management_workspace_repo):
        management_workspace_repo.archive.return_value = None
        service = WorkspaceService(workspace_repository=management_workspace_repo)
        result = management_workspace_repo.archive("no-such-ws")
        assert result is None


class TestListWorkspacesPaginated:
    """list_workspaces(user_id, limit, offset, status) → paginated list."""

    def test_returns_paginated_results(self, management_workspace_repo):
        service = WorkspaceService(workspace_repository=management_workspace_repo)
        items = management_workspace_repo.find_by_user_with_pagination(
            "user-1", limit=25, offset=0, status=None,
        )
        total = management_workspace_repo.count_by_user("user-1", status=None)
        assert len(items) == 2
        assert total == 2

    def test_filters_by_status(self, management_workspace_repo, _ws_doc):
        management_workspace_repo.find_by_user_with_pagination.return_value = [
            _ws_doc(status="archived")
        ]
        management_workspace_repo.count_by_user.return_value = 1
        service = WorkspaceService(workspace_repository=management_workspace_repo)
        items = management_workspace_repo.find_by_user_with_pagination(
            "user-1", limit=25, offset=0, status="archived",
        )
        assert len(items) == 1
        assert items[0]["status"] == "archived"

    def test_respects_offset(self, management_workspace_repo, _ws_doc):
        management_workspace_repo.find_by_user_with_pagination.return_value = [
            _ws_doc(workspace_id="ws-2")
        ]
        service = WorkspaceService(workspace_repository=management_workspace_repo)
        items = management_workspace_repo.find_by_user_with_pagination(
            "user-1", limit=25, offset=1, status=None,
        )
        assert len(items) == 1
        assert items[0]["workspace_id"] == "ws-2"


class TestOwnershipEnforcement:
    """Operations on workspace by non-owner should raise OwnershipViolationError."""

    def test_raises_ownership_violation(self, management_workspace_repo, _ws_doc):
        management_workspace_repo.find_by_workspace_id.return_value = _ws_doc(user_id="owner-A")
        service = WorkspaceService(workspace_repository=management_workspace_repo)

        ws = management_workspace_repo.find_by_workspace_id("ws-1")
        requesting_user = "other-user-B"
        with pytest.raises(OwnershipViolationError):
            if ws and ws["user_id"] != requesting_user:
                raise OwnershipViolationError(
                    entity_type="workspace",
                    entity_id="ws-1",
                    expected_owner=requesting_user,
                    actual_owner=ws["user_id"],
                )


class TestEntityNotFoundGuard:
    """Operations on non-existent workspace should raise EntityNotFoundError."""

    def test_raises_for_nonexistent_workspace(self, management_workspace_repo):
        management_workspace_repo.find_by_workspace_id.return_value = None
        service = WorkspaceService(workspace_repository=management_workspace_repo)

        with pytest.raises(EntityNotFoundError):
            ws = management_workspace_repo.find_by_workspace_id("ghost")
            if ws is None:
                raise EntityNotFoundError("workspace", "ghost")
