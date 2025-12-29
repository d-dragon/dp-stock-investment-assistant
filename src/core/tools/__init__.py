"""LangChain Tools Module for Stock Investment Assistant.

This module provides a suite of LangChain-compatible tools for stock data
retrieval, analysis, and reporting. All tools extend CachingTool which
provides Redis/in-memory caching integration.

Tools:
    - StockSymbolTool: Retrieve stock prices and symbol information
    - ReportingTool: Generate investment reports (markdown)
    - TradingViewTool: TradingView integration (placeholder for Phase 2)

Registry:
    - ToolRegistry: Central registry for tool management

Reference: .github/instructions/backend-python.instructions.md § Model Factory
"""

from .base import CachingTool
from .registry import ToolRegistry, get_tool_registry, reset_tool_registry
from .stock_symbol import StockSymbolTool
from .reporting import ReportingTool
from .tradingview import TradingViewTool

__all__ = [
    # Base
    "CachingTool",
    # Registry
    "ToolRegistry",
    "get_tool_registry",
    "reset_tool_registry",
    # Tools
    "StockSymbolTool",
    "ReportingTool",
    "TradingViewTool",
]
