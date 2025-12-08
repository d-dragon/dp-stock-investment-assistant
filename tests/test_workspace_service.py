"""Unit tests for WorkspaceService."""

from __future__ import annotations

import asyncio
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
    workspace_id = "64b7a0f71a2b3c4d5e6f7a8b"
    workspace_repo.create.return_value = workspace_id
    workspace_repo.get_by_id.return_value = {
        "_id": ObjectId(workspace_id),
        "user_id": ObjectId(user_id),
        "name": "New Workspace",
    }

    service = WorkspaceService(workspace_repository=workspace_repo, cache=cache_backend)

    result = service.create_workspace(user_id, name=" New Workspace ", description="notes")

    assert result["name"] == "New Workspace"
    assert result["_id"] == workspace_id
    workspace_repo.create.assert_called_once()
    created_payload = workspace_repo.create.call_args[0][0]
    assert created_payload["user_id"] == ObjectId(user_id)
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
