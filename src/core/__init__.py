"""
Core package for DP Stock-Investment Assistant.
"""

# package marker for `core`; heavyweight exports are lazy-loaded below.
from .routes import RouteResult, StockQueryRoute

__all__ = [
    'StockAgent',
    'AIClient',
    'DataManager',
    'StockQueryRoute',
    'RouteResult',
    'StockQueryRouter',
    'get_stock_query_router',
]


def __getattr__(name: str):
    """Lazy-load heavyweight agent exports on demand."""

    if name == "StockAgent":
        from .agent import StockAgent

        return StockAgent
    if name == "AIClient":
        from .ai_client import AIClient

        return AIClient
    if name == "DataManager":
        from .data_manager import DataManager

        return DataManager
    if name == "StockQueryRouter":
        from .stock_query_router import StockQueryRouter

        return StockQueryRouter
    if name == "get_stock_query_router":
        from .stock_query_router import get_stock_query_router

        return get_stock_query_router
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


