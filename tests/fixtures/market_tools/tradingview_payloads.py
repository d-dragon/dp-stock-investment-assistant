"""TradingView visualization fixture payloads."""

from __future__ import annotations


TRADINGVIEW_ACTIONS = (
    "get_chart_url",
    "get_widget",
    "get_analysis",
    "validate_symbol",
    "ticker_tape",
    "heatmap",
    "screener",
)

SUPPORTED_INTERVALS = ("1D", "1W", "1M")
SUPPORTED_WIDGETS = ("advanced_chart", "symbol_overview", "ticker_tape", "heatmap", "screener")
