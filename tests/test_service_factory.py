"""Unit tests for ServiceFactory."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from services.factory import ServiceFactory
from utils.cache import CacheBackend


@pytest.fixture
def config() -> dict:
    return {
        "database": {
            "mongodb": {
                "connection_string": "mongodb://localhost:27017",
                "database_name": "test_db",
            }
        }
    }


@pytest.fixture
def repository_factory() -> MagicMock:
    factory = MagicMock()
    factory.get_workspace_repository.return_value = MagicMock(name="WorkspaceRepository")
    factory.get_session_repository.return_value = MagicMock(name="SessionRepository")
    factory.get_watchlist_repository.return_value = MagicMock(name="WatchlistRepository")
    factory.get_symbol_repository.return_value = MagicMock(name="SymbolRepository")
    return factory


@pytest.fixture
def cache_backend() -> MagicMock:
    return MagicMock(spec=CacheBackend)


def test_workspace_service_is_singleton(config: dict, repository_factory: MagicMock, cache_backend: MagicMock) -> None:
    factory = ServiceFactory(
        config,
        repository_factory=repository_factory,
        cache_backend=cache_backend,
    )

    service_a = factory.get_workspace_service()
    service_b = factory.get_workspace_service()

    assert service_a is service_b
    repository_factory.get_workspace_repository.assert_called_once()


def test_symbols_service_is_singleton(config: dict, repository_factory: MagicMock, cache_backend: MagicMock) -> None:
    factory = ServiceFactory(
        config,
        repository_factory=repository_factory,
        cache_backend=cache_backend,
    )

    service_a = factory.get_symbols_service()
    service_b = factory.get_symbols_service()

    assert service_a is service_b
    repository_factory.get_symbol_repository.assert_called_once()


def test_symbols_service_requires_repository(config: dict, repository_factory: MagicMock, cache_backend: MagicMock) -> None:
    repository_factory.get_symbol_repository.return_value = None

    factory = ServiceFactory(
        config,
        repository_factory=repository_factory,
        cache_backend=cache_backend,
    )

    with pytest.raises(RuntimeError):
        factory.get_symbols_service()
