"""TradingView visualization provenance tool.

This tool builds chart, widget, deep-link, ticker-tape, heatmap, screener,
and symbol-validation payloads as visualization provenance. It does not
produce canonical market evidence.

Reference: .github/instructions/backend-python.instructions.md § Service Layer
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from .base import AgentTool
from .normalization import NormalizedOutput, make_visualization_provenance_output, normalize_symbol_code
from utils.cache import CacheBackend


class TradingViewTool(AgentTool):
    """Build TradingView visualization payloads as non-evidence provenance."""
    
    name: str = "tradingview"
    description: str = (
        "TradingView visualization provenance for charts, widgets, links, "
        "ticker tape, heatmaps, screeners, and symbol validation. "
        "Outputs are not canonical market evidence."
    )
    
    def __init__(
        self,
        cache: Optional[CacheBackend] = None,
        cache_ttl_seconds: int = 300,
        enable_cache: bool = True,
        logger: Optional[logging.Logger] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize TradingViewTool.
        
        Args:
            cache: CacheBackend for result caching
            cache_ttl_seconds: Cache TTL in seconds (default 300)
            enable_cache: Whether caching is enabled
            logger: Optional logger instance
            **kwargs: Additional BaseTool arguments
        """
        super().__init__(
            cache=cache,
            cache_ttl_seconds=cache_ttl_seconds,
            enable_cache=enable_cache,
            logger=logger,
            **kwargs,
        )
    
    def _execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Build a visualization provenance payload."""

        action = str(kwargs.get("action", "chart")).lower()
        symbol = normalize_symbol_code(str(kwargs.get("symbol") or ""))
        if not symbol:
            return self._provenance_output(
                symbol="",
                action=action,
                payload={"validation_status": "degraded", "reason": "missing_symbol"},
                warning="TradingView symbol is required.",
            ).to_dict()

        payload = self._build_payload(action=action, symbol=symbol, options=kwargs)
        output = self._provenance_output(symbol=symbol, action=action, payload=payload)
        self.logger.info("TradingView visualization provenance built: action=%s symbol=%s", action, symbol)
        return output.to_dict()
    
    def get_chart_url(self, symbol: str, **kwargs: Any) -> Dict[str, Any]:
        """Get TradingView chart URL provenance for a symbol."""

        return self._run(action="get_chart_url", symbol=symbol, **kwargs)
    
    def get_widget(self, symbol: str, widget_type: str = "chart", **kwargs: Any) -> Dict[str, Any]:
        """Get TradingView widget provenance for a symbol."""

        return self._run(
            action="get_widget",
            symbol=symbol,
            widget_type=widget_type,
            **kwargs,
        )
    
    def get_analysis(self, symbol: str, **kwargs: Any) -> Dict[str, Any]:
        """Return visualization-only analysis provenance, not evidence."""

        return self._run(action="get_analysis", symbol=symbol, **kwargs)

    def _build_payload(self, *, action: str, symbol: str, options: Dict[str, Any]) -> Dict[str, Any]:
        interval = str(options.get("interval") or "1D")
        widget_type = str(options.get("widget_type") or "chart")
        base_url = f"https://www.tradingview.com/chart/?symbol={symbol}&interval={interval}"
        supported_intervals = {"1D", "1W", "1M", "4H", "1H"}
        supported_widgets = {"chart", "advanced_chart", "symbol_overview", "ticker_tape", "heatmap", "screener"}
        payload: Dict[str, Any] = {
            "action": action,
            "symbol": symbol,
            "interval": interval,
            "validation_status": "valid",
            "generated_by": "TradingViewTool",
        }
        if interval not in supported_intervals:
            payload["validation_status"] = "degraded"
            payload["reason"] = "invalid_interval"
            return payload
        if action in {"get_chart_url", "chart", "deep_link"}:
            payload["chart_url"] = base_url
            payload["deep_link"] = base_url
        elif action in {"get_widget", "widget"}:
            if widget_type not in supported_widgets:
                payload["validation_status"] = "degraded"
                payload["reason"] = "unsupported_widget"
                return payload
            payload["widget_type"] = widget_type
            payload["widget_payload"] = {
                "symbol": symbol,
                "interval": interval,
                "type": widget_type,
                "canonical_evidence": False,
            }
        elif action in {"ticker_tape", "heatmap", "screener", "get_analysis"}:
            payload["widget_type"] = action
            payload["rows"] = []
            payload["canonical_evidence"] = False
        elif action == "validate_symbol":
            payload["validation_status"] = "valid" if symbol else "degraded"
        else:
            payload["validation_status"] = "degraded"
            payload["reason"] = "unsupported_visualization_action"
        return payload

    @staticmethod
    def _provenance_output(
        *,
        symbol: str,
        action: str,
        payload: Dict[str, Any],
        warning: str = "TradingView output is visualization provenance only.",
    ) -> NormalizedOutput:
        source_reference = payload.get("chart_url") or f"tradingview:{action}:{symbol}"
        return make_visualization_provenance_output(
            provider_id="tradingview",
            symbol=symbol,
            payload=payload,
            source_url_or_reference=str(source_reference),
            warnings=(warning,),
        )
    
    def health_check(self) -> tuple[bool, Dict[str, Any]]:
        """Check tool health.
        
        Returns healthy when provenance builders are available.
        
        Returns:
        Tuple of (True, details_dict) with visualization provenance status
        """
        base_healthy, details = super().health_check()
        
        details["implementation_status"] = "visualization_provenance"
        details["phase"] = "visualization_provenance"
        details["status"] = "ready"
        details["canonical_evidence"] = False
        return True, details
