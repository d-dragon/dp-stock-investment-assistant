"""Stock Symbol Tool for retrieving stock price and symbol information.

Provides stock data lookup using DataManager (Yahoo Finance) and 
SymbolRepository (MongoDB) with caching support.

Reference: .github/instructions/backend-python.instructions.md § Data Manager
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Union

from pydantic import Field

from src.core.tools.base import CachingTool
from src.core.data_manager import DataManager
from src.data.repositories.symbol_repository import SymbolRepository
from src.utils.cache import CacheBackend


class StockSymbolTool(CachingTool):
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
        elif action == "search":
            return self._search_symbols(kwargs)
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
