"""Unit tests for SymbolsService."""

from __future__ import annotations

import asyncio
from unittest.mock import ANY, MagicMock

import pytest

from services.symbols_service import SymbolsService
from utils.cache import CacheBackend


@pytest.fixture
def symbol_repo() -> MagicMock:
    repo = MagicMock()
    repo.get_by_symbol.return_value = {"_id": "1", "symbol": "AAPL", "name": "Apple"}
    repo.search_by_name.return_value = [
        {"_id": "1", "symbol": "AAPL", "name": "Apple"},
        {"_id": "2", "symbol": "MSFT", "name": "Microsoft"},
    ]
    repo.get_tracked_symbols.return_value = repo.search_by_name.return_value
    repo.health_check.return_value = (True, {"component": "symbol_repository", "status": "ready"})
    return repo


@pytest.fixture
def cache_backend() -> MagicMock:
    cache = MagicMock(spec=CacheBackend)
    cache.is_available.return_value = True
    cache.ping.return_value = True
    return cache


def test_get_symbol_uses_cache_hit(symbol_repo: MagicMock) -> None:
    cache = MagicMock(spec=CacheBackend)
    cache.get_json.return_value = {"symbol": "AAPL"}

    service = SymbolsService(symbol_repository=symbol_repo, cache=cache)
    result = service.get_symbol("AAPL")

    assert result == {"symbol": "AAPL"}
    symbol_repo.get_by_symbol.assert_not_called()


def test_search_symbols_sets_cache(symbol_repo: MagicMock, cache_backend: MagicMock) -> None:
    cache_backend.get_json.return_value = None

    service = SymbolsService(symbol_repository=symbol_repo, cache=cache_backend)
    result = service.search_symbols("app", limit=2)

    assert len(result) == 2
    cache_backend.set_json.assert_called_once_with(
        "symbol:search:app:2",
        {"items": ANY},
        ttl_seconds=SymbolsService.SEARCH_CACHE_TTL,
    )


def test_stream_symbols_uses_repository(symbol_repo: MagicMock) -> None:
    service = SymbolsService(symbol_repository=symbol_repo)
    batches = list(service.stream_symbols(chunk_size=1))

    assert len(batches) == 2
    assert batches[0][0]["symbol"] == "AAPL"
    symbol_repo.get_tracked_symbols.assert_called_once()


def test_search_symbols_async(symbol_repo: MagicMock) -> None:
    service = SymbolsService(symbol_repository=symbol_repo)
    result = asyncio.run(service.search_symbols_async("apple"))

    assert result
    symbol_repo.search_by_name.assert_called_once()


def test_related_watchlists_without_repository_returns_empty(symbol_repo: MagicMock) -> None:
    service = SymbolsService(symbol_repository=symbol_repo)
    assert service.related_watchlists("AAPL") == []


def test_health_check_collects_dependency_status(symbol_repo: MagicMock, cache_backend: MagicMock) -> None:
    watchlist_repo = MagicMock()
    watchlist_repo.health_check.return_value = (
        True,
        {"component": "watchlist_repository", "status": "ready"},
    )

    service = SymbolsService(
        symbol_repository=symbol_repo,
        watchlist_repository=watchlist_repo,
        cache=cache_backend,
    )

    ok, payload = service.health_check()
    assert ok is True
    assert payload["dependencies"]["symbol_repository"]["status"] == "ready"
