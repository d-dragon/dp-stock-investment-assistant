"""Stock Symbol Tool for retrieving stock price and symbol information.

Provides stock data lookup using DataManager (Yahoo Finance) and 
SymbolRepository (MongoDB) with caching support.

Reference: .github/instructions/backend-python.instructions.md § Data Manager
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, Union

from pydantic import Field

from .base import AgentTool
from .mutation_receipts import SYMBOL_MUTATION_ACTIONS, guard_symbol_mutation
from .normalization import (
    AdmissionOutcome,
    DegradedReason,
    FreshnessStatus,
    NormalizedOutput,
    ToolExecutionEnvelope,
    internal_symbol_record_from_document,
    make_degraded_output,
    make_system_record_output,
    normalize_symbol_code,
)
from ..data_manager import DataManager
from data.repositories.symbol_repository import SymbolRepository
from utils.cache import CacheBackend


class StockSymbolTool(AgentTool):
    """Tool for retrieving stock symbol information and prices.
    
    Provides two main functionalities:
    1. get_info: Get detailed stock information (price, PE ratio, sector, etc.)
    2. search: Search for symbols by name pattern
    
    Uses DataManager for live price data from Yahoo Finance,
    and SymbolRepository for symbol metadata from MongoDB.
    
    Example:
        >>> tool = StockSymbolTool(
        ...     data_manager=data_manager,
        ...     symbol_repository=symbol_repo,
        ...     cache=cache,
        ... )
        >>> result = tool._run(action="get_info", symbol="AAPL")
        >>> print(result["current_price"])
    """
    
    name: str = "stock_symbol"
    description: str = (
        "Retrieve stock symbol information and prices. "
        "Actions: 'get_info' for stock details, 'search' for symbol lookup. "
        "Input: {action: 'get_info'|'search', symbol: 'AAPL'} or {action: 'search', query: 'Apple'}"
    )
    
    # Tool-specific fields
    default_search_limit: int = Field(default=10, description="Default limit for search results")
    
    # Non-serializable dependencies (stored as class attributes)
    _data_manager: Optional[DataManager] = None
    _symbol_repository: Optional[SymbolRepository] = None
    
    def __init__(
        self,
        data_manager: Optional[DataManager] = None,
        symbol_repository: Optional[SymbolRepository] = None,
        cache: Optional[CacheBackend] = None,
        cache_ttl_seconds: int = 60,
        enable_cache: bool = True,
        default_search_limit: int = 10,
        logger: Optional[logging.Logger] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize StockSymbolTool.
        
        Args:
            data_manager: DataManager for fetching live stock data
            symbol_repository: SymbolRepository for symbol metadata
            cache: CacheBackend for result caching
            cache_ttl_seconds: Cache TTL in seconds (default 60)
            enable_cache: Whether caching is enabled
            default_search_limit: Default limit for search results
            logger: Optional logger instance
            **kwargs: Additional BaseTool arguments
        """
        super().__init__(
            cache=cache,
            cache_ttl_seconds=cache_ttl_seconds,
            enable_cache=enable_cache,
            logger=logger,
            default_search_limit=default_search_limit,
            **kwargs,
        )
        object.__setattr__(self, '_data_manager', data_manager)
        object.__setattr__(self, '_symbol_repository', symbol_repository)
    
    @property
    def data_manager(self) -> Optional[DataManager]:
        """Get the data manager."""
        return self._data_manager
    
    @property
    def symbol_repository(self) -> Optional[SymbolRepository]:
        """Get the symbol repository."""
        return self._symbol_repository
    
    def _execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute stock symbol lookup.
        
        Args:
            action: One of 'get_info' or 'search'
            symbol: Stock symbol for 'get_info' action
            query: Search query for 'search' action
            limit: Maximum results for 'search' (optional)
            
        Returns:
            Dict with stock information or search results
            
        Raises:
            ValueError: If required parameters are missing
        """
        action = kwargs.get("action", "get_info")
        
        if action == "get_info":
            return self._get_stock_info(kwargs)
        elif action == "search" and kwargs.get("normalized") is True:
            return self._search_symbols_normalized(kwargs)
        elif action == "search":
            return self._search_symbols(kwargs)
        elif action == "lookup":
            return self._lookup_symbol_record(kwargs)
        elif action == "list":
            return self._list_symbol_records(kwargs)
        elif action == "coverage":
            return self._symbol_coverage(kwargs)
        elif action in {"quote", "history", "fundamentals"}:
            return self._degrade_live_market_data_request(action)
        elif action in SYMBOL_MUTATION_ACTIONS:
            return self._disabled_symbol_mutation(action, kwargs)
        else:
            raise ValueError(f"Unknown action: {action}. Supported: 'get_info', 'search'")
    
    def _get_stock_info(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed stock information.
        
        Args:
            kwargs: Must contain 'symbol' key
            
        Returns:
            Dict with stock information
        """
        symbol = kwargs.get("symbol")
        if not symbol:
            raise ValueError("'symbol' is required for get_info action")
        
        symbol = symbol.upper().strip()
        result: Dict[str, Any] = {"symbol": symbol, "source": None}
        
        # Try DataManager first (live Yahoo Finance data)
        if self._data_manager:
            try:
                info = self._data_manager.get_stock_info(symbol)
                if info:
                    result.update({
                        "name": info.get("name", "N/A"),
                        "current_price": info.get("current_price", "N/A"),
                        "previous_close": info.get("previous_close", "N/A"),
                        "market_cap": info.get("market_cap", "N/A"),
                        "pe_ratio": info.get("pe_ratio", "N/A"),
                        "dividend_yield": info.get("dividend_yield", "N/A"),
                        "sector": info.get("sector", "N/A"),
                        "industry": info.get("industry", "N/A"),
                        "source": "yahoo_finance",
                    })
                    return result
            except Exception as e:
                self.logger.warning(f"DataManager failed for {symbol}: {e}")
        
        # Fallback to SymbolRepository (MongoDB metadata)
        if self._symbol_repository:
            try:
                symbol_data = self._symbol_repository.get_by_symbol(symbol)
                if symbol_data:
                    result.update({
                        "name": symbol_data.get("name", "N/A"),
                        "asset_type": symbol_data.get("asset_type", "N/A"),
                        "sector": symbol_data.get("classification", {}).get("sector", "N/A"),
                        "industry": symbol_data.get("classification", {}).get("industry", "N/A"),
                        "exchange": symbol_data.get("listing", {}).get("exchange", "N/A"),
                        "source": "mongodb",
                    })
                    return result
            except Exception as e:
                self.logger.warning(f"SymbolRepository failed for {symbol}: {e}")
        
        # No data found
        result["error"] = f"No data found for symbol: {symbol}"
        result["source"] = "none"
        return result
    
    def _search_symbols(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Search for symbols by name pattern.
        
        Args:
            kwargs: Must contain 'query' key, optional 'limit'
            
        Returns:
            Dict with search results
        """
        query = kwargs.get("query")
        if not query:
            raise ValueError("'query' is required for search action")
        
        limit = kwargs.get("limit", self.default_search_limit)
        result: Dict[str, Any] = {
            "query": query,
            "limit": limit,
            "results": [],
            "source": None,
        }
        
        # Use SymbolRepository for search
        if self._symbol_repository:
            try:
                symbols = self._symbol_repository.search_by_name(query, limit=limit)
                result["results"] = [
                    {
                        "symbol": s.get("symbol"),
                        "name": s.get("name"),
                        "asset_type": s.get("asset_type"),
                        "exchange": s.get("listing", {}).get("exchange"),
                    }
                    for s in symbols
                ]
                result["source"] = "mongodb"
                result["count"] = len(result["results"])
                return result
            except Exception as e:
                self.logger.warning(f"SymbolRepository search failed: {e}")
        
        # No repository available
        result["error"] = "Symbol search not available (no repository configured)"
        result["source"] = "none"
        return result
    
    def get_info(self, symbol: str) -> Dict[str, Any]:
        """Convenience method to get stock info.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Dict with stock information
        """
        return self._run(action="get_info", symbol=symbol)
    
    def search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Convenience method to search symbols.
        
        Args:
            query: Search query (e.g., 'Apple')
            limit: Maximum results
            
        Returns:
            Dict with search results
        """
        return self._run(action="search", query=query, limit=limit)

    # ------------------------------------------------------------------
    # M2B.2 internal symbol-store normalization helpers
    # ------------------------------------------------------------------

    def _lookup_symbol_record(self, kwargs: Mapping[str, Any]) -> Dict[str, Any]:
        symbol = kwargs.get("symbol") or kwargs.get("query")
        if not symbol:
            raise ValueError("'symbol' is required for lookup action")
        exchange_hint, symbol_code = self._split_exchange_hint(str(symbol), kwargs.get("exchange"))
        records = self._find_symbol_candidates(symbol_code, exchange=exchange_hint, currency=kwargs.get("currency"))
        if not records:
            return self._normalized_result(
                make_degraded_output(
                    code=DegradedReason.MISSING_SYMBOL.value,
                    safe_message=f"No internal symbol-store record found for {symbol_code}.",
                    reason=DegradedReason.MISSING_SYMBOL,
                    tool_name=self.name,
                )
            )
        if len(records) > 1:
            return self._normalized_result(
                make_degraded_output(
                    code=DegradedReason.AMBIGUOUS_SYMBOL.value,
                    safe_message=f"Symbol {symbol_code} is ambiguous; provide exchange or currency.",
                    reason=DegradedReason.AMBIGUOUS_SYMBOL,
                    tool_name=self.name,
                ),
                candidates=[self._safe_symbol_summary(record) for record in records],
            )
        record = records[0]
        degraded = self._record_degraded_output(record)
        if degraded is not None:
            return self._normalized_result(degraded)
        return self._normalized_result(make_system_record_output(record))

    def _search_symbols_normalized(self, kwargs: Mapping[str, Any]) -> Dict[str, Any]:
        query = kwargs.get("query")
        if not query:
            raise ValueError("'query' is required for search action")
        limit = int(kwargs.get("limit", self.default_search_limit))
        records = self._search_repository(str(query), limit=limit)
        outputs = []
        for record in records[:limit]:
            degraded = self._record_degraded_output(record)
            outputs.append(degraded or make_system_record_output(record))
        return {
            "query": query,
            "count": len(outputs),
            "normalized_outputs": [output.to_dict() for output in outputs],
            "output_kinds": [output.kind.value for output in outputs],
            "source": "internal_symbol_store" if outputs else "none",
        }

    def _list_symbol_records(self, kwargs: Mapping[str, Any]) -> Dict[str, Any]:
        limit = int(kwargs.get("limit", self.default_search_limit))
        exchange = kwargs.get("exchange")
        if self._symbol_repository is None:
            return self._normalized_result(
                make_degraded_output(
                    code=DegradedReason.MISSING_SYMBOL.value,
                    safe_message="Internal symbol-store repository is not configured.",
                    reason=DegradedReason.MISSING_SYMBOL,
                    tool_name=self.name,
                )
            )
        if exchange and hasattr(self._symbol_repository, "get_by_exchange"):
            records = self._symbol_repository.get_by_exchange(str(exchange).upper(), limit=limit)
        elif hasattr(self._symbol_repository, "get_tracked_symbols"):
            records = self._symbol_repository.get_tracked_symbols(limit=limit)
        else:
            records = self._all_fixture_records()[:limit]
        outputs = [make_system_record_output(record) for record in records[:limit]]
        return {
            "count": len(outputs),
            "normalized_outputs": [output.to_dict() for output in outputs],
            "source": "internal_symbol_store" if outputs else "none",
        }

    def _symbol_coverage(self, kwargs: Mapping[str, Any]) -> Dict[str, Any]:
        lookup = self._lookup_symbol_record(kwargs)
        output = lookup.get("normalized_output", {})
        content = output.get("content", {})
        return {
            **lookup,
            "coverage": content.get("coverage", []),
            "tags": content.get("tags", []),
        }

    def _degrade_live_market_data_request(self, action: str) -> Dict[str, Any]:
        return self._normalized_result(
            make_degraded_output(
                code=DegradedReason.LIVE_MARKET_DATA_NOT_OWNED.value,
                safe_message=(
                    f"'{action}' is not owned by the evolved StockSymbolTool boundary; "
                    "use a downstream market-data capability when it is admitted."
                ),
                reason=DegradedReason.LIVE_MARKET_DATA_NOT_OWNED,
                tool_name=self.name,
            )
        )

    def _disabled_symbol_mutation(self, action: str, kwargs: Mapping[str, Any]) -> Dict[str, Any]:
        target = normalize_symbol_code(str(kwargs.get("symbol") or kwargs.get("target_record") or "unknown"))
        return self._normalized_result(
            guard_symbol_mutation(
                action=action,
                target_record=target,
                actor_or_route="stock_symbol",
                allow_test_only=bool(kwargs.get("allow_test_only")),
            )
        )

    def _normalized_result(self, output: NormalizedOutput, **extra: Any) -> Dict[str, Any]:
        envelope = ToolExecutionEnvelope(
            route="stock_symbol_internal",
            selected_tool=self.name,
            descriptor_identity="stock_symbol:m2b2",
            admission_outcome=AdmissionOutcome.DEGRADED if output.degraded_state else AdmissionOutcome.ALLOWED,
            normalized_output=output,
            selected_adapter="internal_symbol_store",
            freshness_status=(
                output.source_metadata.freshness_status
                if output.source_metadata
                else FreshnessStatus.NOT_APPLICABLE
            ),
            warnings=output.warnings,
            degraded_state_reason=output.degraded_state.code if output.degraded_state else None,
            trace_metadata={"public_contract_change": False},
        )
        result = {
            "status": "degraded" if output.degraded_state else "ok",
            "normalized_output": output.to_dict(),
            "envelope": envelope.to_dict(),
            "output_kind": output.kind.value,
            "source": "internal_symbol_store" if not output.degraded_state else "degraded_state",
        }
        result.update(extra)
        return result

    def _find_symbol_candidates(
        self,
        symbol: str,
        *,
        exchange: Any = None,
        currency: Any = None,
    ) -> List[Mapping[str, Any]]:
        symbol_code = normalize_symbol_code(symbol)
        exchange_hint = normalize_symbol_code(str(exchange)) if exchange else None
        currency_hint = normalize_symbol_code(str(currency)) if currency else None
        candidates: List[Mapping[str, Any]] = []
        if self._symbol_repository and hasattr(self._symbol_repository, "get_by_symbol"):
            record = self._symbol_repository.get_by_symbol(symbol_code)
            if record:
                candidates.append(record)
        candidates.extend(self._fixture_records_matching(symbol_code))
        if not candidates:
            candidates.extend(self._search_repository(symbol_code, limit=self.default_search_limit))
        unique = self._dedupe_records(candidates)
        if exchange_hint:
            unique = [record for record in unique if normalize_symbol_code(str(self._listing(record).get("exchange", ""))) == exchange_hint]
        if currency_hint:
            unique = [record for record in unique if normalize_symbol_code(str(self._listing(record).get("currency", ""))) == currency_hint]
        return unique

    def _search_repository(self, query: str, *, limit: int) -> List[Mapping[str, Any]]:
        if self._symbol_repository and hasattr(self._symbol_repository, "search_by_name"):
            try:
                return list(self._symbol_repository.search_by_name(query, limit=limit))
            except Exception as e:
                self.logger.warning(f"SymbolRepository normalized search failed: {e}")
        return self._fixture_records_matching(query)[:limit]

    def _fixture_records_matching(self, query: str) -> List[Mapping[str, Any]]:
        normalized = normalize_symbol_code(query)
        records = []
        for record in self._all_fixture_records():
            aliases = [normalize_symbol_code(str(alias)) for alias in record.get("aliases", ())]
            values = {
                normalize_symbol_code(str(record.get("symbol", ""))),
                normalize_symbol_code(str(record.get("name", ""))),
                *aliases,
            }
            if normalized in values or any(normalized in value for value in values):
                records.append(record)
        return records

    def _all_fixture_records(self) -> List[Mapping[str, Any]]:
        if self._symbol_repository is None:
            return []
        for attr in ("records", "_records", "fixture_records"):
            value = getattr(self._symbol_repository, attr, None)
            if isinstance(value, Mapping):
                return list(value.values())
            if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
                return list(value)
        return []

    def _record_degraded_output(self, record: Mapping[str, Any]) -> Optional[NormalizedOutput]:
        if record.get("stale") or record.get("freshness_status") == "stale":
            return make_degraded_output(
                code=DegradedReason.STALE_RECORD.value,
                safe_message=f"Internal symbol record {record.get('symbol')} is stale.",
                reason=DegradedReason.STALE_RECORD,
                tool_name=self.name,
            )
        if record.get("conflicting") or record.get("conflict"):
            return make_degraded_output(
                code=DegradedReason.CONFLICTING_RECORD.value,
                safe_message=f"Internal symbol record {record.get('symbol')} has conflicting identity data.",
                reason=DegradedReason.CONFLICTING_RECORD,
                tool_name=self.name,
            )
        return None

    @staticmethod
    def _split_exchange_hint(symbol: str, exchange: Any = None) -> Tuple[Optional[str], str]:
        if ":" in symbol:
            left, right = symbol.split(":", 1)
            return normalize_symbol_code(left), normalize_symbol_code(right)
        return (normalize_symbol_code(str(exchange)) if exchange else None), normalize_symbol_code(symbol)

    @staticmethod
    def _listing(record: Mapping[str, Any]) -> Mapping[str, Any]:
        listing = record.get("listing")
        return listing if isinstance(listing, Mapping) else {}

    @staticmethod
    def _dedupe_records(records: Iterable[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
        seen = set()
        unique = []
        for record in records:
            listing = StockSymbolTool._listing(record)
            key = (record.get("symbol"), listing.get("exchange"), listing.get("currency"))
            if key in seen:
                continue
            seen.add(key)
            unique.append(record)
        return unique

    @staticmethod
    def _safe_symbol_summary(record: Mapping[str, Any]) -> Dict[str, Any]:
        listing = StockSymbolTool._listing(record)
        return {
            "symbol": record.get("symbol"),
            "name": record.get("name"),
            "exchange": listing.get("exchange"),
            "currency": listing.get("currency"),
            "asset_type": record.get("asset_type"),
        }
    
    def health_check(self) -> tuple[bool, Dict[str, Any]]:
        """Check tool health including dependencies.
        
        Returns:
            Tuple of (healthy, details_dict)
        """
        base_healthy, details = super().health_check()
        
        # Check DataManager
        details["data_manager_available"] = self._data_manager is not None
        
        # Check SymbolRepository
        details["symbol_repository_available"] = self._symbol_repository is not None
        
        # Tool needs at least one data source
        has_data_source = (
            self._data_manager is not None or
            self._symbol_repository is not None
        )
        details["has_data_source"] = has_data_source
        
        healthy = base_healthy and has_data_source
        details["status"] = "ready" if healthy else "no_data_source"
        
        return healthy, details
