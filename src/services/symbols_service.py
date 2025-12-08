"""Service helpers focused on symbol discovery and metadata lookups."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Dict, Iterator, List, Optional

from data.repositories.symbol_repository import SymbolRepository
from data.repositories.watchlist_repository import WatchlistRepository
from services.base import BaseService, HealthReport
from utils.cache import CacheBackend
from utils.service_utils import batched, normalize_document


class SymbolsService(BaseService):
    """Read-heavy orchestration layer for symbol metadata and discovery flows."""

    SYMBOL_CACHE_TTL = 300
    SEARCH_CACHE_TTL = 90
    DEFAULT_BATCH_SIZE = 25

    def __init__(
        self,
        *,
        symbol_repository: SymbolRepository,
        watchlist_repository: Optional[WatchlistRepository] = None,
        cache: Optional[CacheBackend] = None,
        time_provider: Optional[Callable[[], str]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        super().__init__(cache=cache, time_provider=time_provider, logger=logger)
        self._symbol_repository = symbol_repository
        self._watchlist_repository = watchlist_repository

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_symbol(self, symbol: str, *, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        cache_key = f"symbol:detail:{symbol.upper()}"
        if use_cache and self.cache:
            cached = self.cache.get_json(cache_key)
            if cached:
                return cached

        try:
            record = self._symbol_repository.get_by_symbol(symbol)
        except Exception:
            self.logger.exception("Failed to load symbol", extra={"symbol": symbol})
            return None

        if not record:
            return None

        payload = normalize_document(record, id_fields=("_id",))
        if use_cache and self.cache:
            self.cache.set_json(cache_key, payload, ttl_seconds=self.SYMBOL_CACHE_TTL)
        return payload

    def search_symbols(
        self,
        query: str,
        *,
        limit: int = 25,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        normalized_query = query.strip()
        if not normalized_query:
            return []

        cache_key = f"symbol:search:{normalized_query.lower()}:{limit}"
        if use_cache and self.cache:
            cached = self.cache.get_json(cache_key)
            if cached:
                return cached.get("items", [])

        try:
            records = self._symbol_repository.search_by_name(normalized_query, limit=limit)
        except Exception:
            self.logger.exception("Symbol search failed", extra={"query": normalized_query})
            records = []

        payload = [normalize_document(doc, id_fields=("_id",)) for doc in records]

        if use_cache and self.cache:
            self.cache.set_json(cache_key, {"items": payload}, ttl_seconds=self.SEARCH_CACHE_TTL)

        return payload

    async def search_symbols_async(
        self,
        query: str,
        *,
        limit: int = 25,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, lambda: self.search_symbols(query, limit=limit, use_cache=use_cache)
        )

    def stream_symbols(
        self,
        *,
        sector: Optional[str] = None,
        asset_type: Optional[str] = None,
        chunk_size: int = DEFAULT_BATCH_SIZE,
    ) -> Iterator[List[Dict[str, Any]]]:
        records: List[Dict[str, Any]]
        try:
            if sector:
                records = self._symbol_repository.get_by_sector(sector, limit=chunk_size * 20)
            elif asset_type:
                records = self._symbol_repository.get_by_asset_type(asset_type, limit=chunk_size * 20)
            else:
                records = self._symbol_repository.get_tracked_symbols(limit=chunk_size * 20)
        except Exception:
            self.logger.exception(
                "Streaming symbol fetch failed", extra={"sector": sector, "asset_type": asset_type}
            )
            records = []

        serialized = [normalize_document(doc, id_fields=("_id",)) for doc in records]
        yield from batched(serialized, chunk_size)

    def related_watchlists(self, symbol: str, *, limit: int = 5) -> List[Dict[str, Any]]:
        if not self._watchlist_repository:
            return []
        try:
            watchlists = self._watchlist_repository.get_watchlists_containing_symbol(symbol, limit=limit)
            return [normalize_document(doc, id_fields=("_id", "workspace_id", "user_id")) for doc in watchlists]
        except Exception:
            self.logger.exception("Failed to load related watchlists", extra={"symbol": symbol})
            return []

    # ------------------------------------------------------------------
    # Health + internals
    # ------------------------------------------------------------------
    def health_check(self) -> HealthReport:
        return self._dependencies_health_report(
            required={"symbol_repository": self._symbol_repository},
            optional={"watchlist_repository": self._watchlist_repository},
        )
