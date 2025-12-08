"""Unit tests for UserService."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.services.user_service import UserService
from src.services.workspace_service import WorkspaceService
from src.utils.cache import CacheBackend


@pytest.fixture
def user_repo() -> MagicMock:
    repo = MagicMock()
    repo.health_check.return_value = (True, {"component": "user_repository", "status": "ready"})
    return repo


@pytest.fixture
def workspace_service() -> MagicMock:
    svc = MagicMock(spec=WorkspaceService)
    svc.health_check.return_value = (True, {"component": "workspace_service", "status": "ready"})
    svc.list_workspaces.return_value = [{"_id": "w1", "name": "Alpha"}]
    return svc


@pytest.fixture
def symbols_service() -> MagicMock:
    svc = MagicMock()
    svc.health_check.return_value = (True, {"component": "symbols_service", "status": "ready"})
    return svc


@pytest.fixture
def watchlist_repo() -> MagicMock:
    repo = MagicMock()
    repo.health_check.return_value = (True, {"component": "watchlist_repository", "status": "ready"})
    repo.get_by_user_id.return_value = [
        {"_id": "wl1", "user_id": "user-1", "workspace_id": "w1", "symbols": ["AAPL", "MSFT"]}
    ]
    return repo


def build_service(
    user_repo: MagicMock,
    workspace_service: MagicMock,
    symbols_service: MagicMock,
    watchlist_repo: MagicMock | None,
    cache: CacheBackend | MagicMock | None = None,
) -> UserService:
    return UserService(
        user_repository=user_repo,
        workspace_provider=workspace_service,  # Protocol-based parameter
        symbol_provider=symbols_service,       # Protocol-based parameter
        watchlist_repository=watchlist_repo,
        cache=cache,
    )


def test_get_user_profile_uses_cache_hit(user_repo: MagicMock, workspace_service: MagicMock, symbols_service: MagicMock) -> None:
    cache = MagicMock(spec=CacheBackend)
    cache.get_json.return_value = {"_id": "cached"}

    service = build_service(user_repo, workspace_service, symbols_service, watchlist_repo=None, cache=cache)
    result = service.get_user_profile("user-1")

    assert result == {"_id": "cached"}
    user_repo.get_by_id.assert_not_called()


def test_get_user_overview_includes_workspaces_and_symbols(
    user_repo: MagicMock,
    workspace_service: MagicMock,
    symbols_service: MagicMock,
    watchlist_repo: MagicMock,
) -> None:
    user_repo.get_by_id.return_value = {"_id": "user-1", "group_id": "group-1", "name": "Jamie"}
    symbols_service.get_symbol.side_effect = [
        {"symbol": "AAPL"},
        {"symbol": "MSFT"},
    ]

    service = build_service(user_repo, workspace_service, symbols_service, watchlist_repo, cache=None)

    overview = service.get_user_overview("user-1", symbol_limit=5)

    assert overview is not None
    assert overview["name"] == "Jamie"
    assert overview["workspaces"] == workspace_service.list_workspaces.return_value
    assert len(overview["watchlists"]) == 1
    assert [symbol["symbol"] for symbol in overview["symbols"]] == ["AAPL", "MSFT"]
    watchlist_repo.get_by_user_id.assert_called_once_with("user-1", limit=5)


def test_favorite_symbols_deduplicates_and_limits(
    user_repo: MagicMock,
    workspace_service: MagicMock,
    symbols_service: MagicMock,
    watchlist_repo: MagicMock,
) -> None:
    watchlist_repo.get_by_user_id.return_value = [
        {"symbols": ["aapl", "msft", "AAPL"]},
        {"symbols": ["msft", "amzn"]},
    ]
    symbols_service.get_symbol.side_effect = lambda ticker: {"symbol": ticker}

    service = build_service(user_repo, workspace_service, symbols_service, watchlist_repo, cache=None)

    result = service.favorite_symbols("user-1", limit=2)

    assert len(result) == 2
    assert [entry["symbol"] for entry in result] == ["AAPL", "MSFT"]


def test_health_check_reports_dependency_status(
    user_repo: MagicMock,
    workspace_service: MagicMock,
    symbols_service: MagicMock,
    watchlist_repo: MagicMock,
) -> None:
    service = build_service(user_repo, workspace_service, symbols_service, watchlist_repo, cache=None)

    ok, payload = service.health_check()

    assert ok is True
    dependencies = payload["dependencies"]
    assert dependencies["user_repository"]["status"] == "ready"
    assert dependencies["workspace_provider"]["status"] == "ready"  # Updated key name
    assert dependencies["symbol_provider"]["status"] == "ready"     # Updated key name


def test_create_or_update_user_creates_new_record(
    user_repo: MagicMock,
    workspace_service: MagicMock,
    symbols_service: MagicMock,
) -> None:
    cache = MagicMock(spec=CacheBackend)
    new_user_id = "507f1f77bcf86cd799439011"
    user_repo.create.return_value = new_user_id
    user_repo.get_by_id.return_value = {"_id": new_user_id, "name": "Ava"}

    service = build_service(user_repo, workspace_service, symbols_service, watchlist_repo=None, cache=cache)

    payload = {"name": "Ava", "email": "ava@example.com", "_id": "ignored"}
    result = service.create_or_update_user(payload)

    assert result == {"_id": new_user_id, "name": "Ava"}
    user_repo.create.assert_called_once_with({"name": "Ava", "email": "ava@example.com"})
    user_repo.update.assert_not_called()
    cache.delete.assert_called_once_with(f"user:profile:{new_user_id}")


def test_create_or_update_user_updates_existing_record(
    user_repo: MagicMock,
    workspace_service: MagicMock,
    symbols_service: MagicMock,
) -> None:
    cache = MagicMock(spec=CacheBackend)
    user_repo.update.return_value = True
    user_repo.get_by_id.return_value = {"_id": "user-99", "name": "Updated"}

    service = build_service(user_repo, workspace_service, symbols_service, watchlist_repo=None, cache=cache)

    result = service.create_or_update_user({"name": "Updated"}, user_id="user-99")

    assert result == {"_id": "user-99", "name": "Updated"}
    user_repo.update.assert_called_once_with("user-99", {"name": "Updated"})
    user_repo.create.assert_not_called()
    cache.delete.assert_called_once_with("user:profile:user-99")


def test_update_user_profile_filters_reserved_fields(
    user_repo: MagicMock,
    workspace_service: MagicMock,
    symbols_service: MagicMock,
) -> None:
    cache = MagicMock(spec=CacheBackend)
    user_repo.update.return_value = True
    user_repo.get_by_id.return_value = {"_id": "user-1", "name": "Sky"}

    service = build_service(user_repo, workspace_service, symbols_service, watchlist_repo=None, cache=cache)

    result = service.update_user_profile(
        "user-1",
        {"name": "Sky", "role": "admin", "_id": "blocked"},
        allowed_fields=("name", "role"),
    )

    assert result == {"_id": "user-1", "name": "Sky"}
    user_repo.update.assert_called_once_with("user-1", {"name": "Sky", "role": "admin"})
    cache.delete.assert_called_once_with("user:profile:user-1")


def test_update_user_profile_raises_when_no_allowed_fields(
    user_repo: MagicMock,
    workspace_service: MagicMock,
    symbols_service: MagicMock,
) -> None:
    service = build_service(user_repo, workspace_service, symbols_service, watchlist_repo=None, cache=None)

    with pytest.raises(ValueError):
        service.update_user_profile("user-1", {"_id": "only"})


def test_get_user_by_email_returns_full_profile(
    user_repo: MagicMock,
    workspace_service: MagicMock,
    symbols_service: MagicMock,
) -> None:
    """Test get_user_by_email returns full profile for existing user."""
    user_repo.get_by_email.return_value = {"_id": "user-123", "email": "test@example.com"}
    user_repo.get_by_id.return_value = {"_id": "user-123", "email": "test@example.com", "name": "Test User"}

    service = build_service(user_repo, workspace_service, symbols_service, watchlist_repo=None, cache=None)
    result = service.get_user_by_email("test@example.com")

    assert result is not None
    assert result["_id"] == "user-123" or result.get("id") == "user-123"
    assert result["email"] == "test@example.com"
    assert result["name"] == "Test User"
    user_repo.get_by_email.assert_called_once_with("test@example.com")


def test_get_user_by_email_raises_on_empty_email(
    user_repo: MagicMock,
    workspace_service: MagicMock,
    symbols_service: MagicMock,
) -> None:
    """Test get_user_by_email raises ValueError for empty email."""
    service = build_service(user_repo, workspace_service, symbols_service, watchlist_repo=None, cache=None)
    
    with pytest.raises(ValueError, match="email is required"):
        service.get_user_by_email("")
    
    user_repo.get_by_email.assert_not_called()


def test_get_user_by_email_returns_none_when_not_found(
    user_repo: MagicMock,
    workspace_service: MagicMock,
    symbols_service: MagicMock,
) -> None:
    """Test get_user_by_email returns None when user not found."""
    user_repo.get_by_email.return_value = None

    service = build_service(user_repo, workspace_service, symbols_service, watchlist_repo=None, cache=None)
    result = service.get_user_by_email("notfound@example.com")

    assert result is None
    user_repo.get_by_email.assert_called_once_with("notfound@example.com")


def test_get_user_by_email_uses_cache(
    user_repo: MagicMock,
    workspace_service: MagicMock,
    symbols_service: MagicMock,
) -> None:
    """Test get_user_by_email uses email cache on subsequent calls."""
    cache = MagicMock(spec=CacheBackend)
    user_repo.get_by_email.return_value = {"_id": "user-123", "email": "cached@example.com"}
    user_repo.get_by_id.return_value = {"_id": "user-123", "email": "cached@example.com", "name": "Cached User"}
    
    service = build_service(user_repo, workspace_service, symbols_service, watchlist_repo=None, cache=cache)
    
    # First call - cache miss, should fetch from DB and store in cache
    cache.get_json.return_value = None
    result1 = service.get_user_by_email("cached@example.com")
    
    assert result1 is not None
    assert result1["name"] == "Cached User"
    cache.set_json.assert_called()  # Email→user_id mapping stored
    
    # Second call - cache hit, should use cached user_id
    cache.get_json.return_value = "user-123"
    user_repo.reset_mock()
    result2 = service.get_user_by_email("cached@example.com")
    
    assert result2 is not None
    user_repo.get_by_email.assert_not_called()  # DB query avoided
