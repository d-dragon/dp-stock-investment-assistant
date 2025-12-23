"""
Core package for DP Stock-Investment Assistant.
"""

# package marker for `core`
# (can be empty)

from .agent import StockAgent
from .ai_client import AIClient
from .data_manager import DataManager
from .routes import RouteResult, StockQueryRoute
from .stock_query_router import StockQueryRouter, get_stock_query_router

__all__ = [
    'StockAgent',
    'AIClient',
    'DataManager',
    'StockQueryRoute',
    'RouteResult',
    'StockQueryRouter',
    'get_stock_query_router',
]


