"""Tests for TradingView visualization provenance."""

from __future__ import annotations

import pytest

from core.tools.normalization import NormalizedOutputKind
from core.tools.tradingview import TradingViewTool
from tests.fixtures.market_tools.tradingview_payloads import TRADINGVIEW_ACTIONS


@pytest.mark.parametrize("action", TRADINGVIEW_ACTIONS)
def test_tradingview_actions_return_visualization_provenance(action):
    result = TradingViewTool(cache=None, enable_cache=False)._run(action=action, symbol="HOSE:FPT")

    assert result["kind"] == NormalizedOutputKind.VISUALIZATION_PROVENANCE.value
    assert result["content"]["canonical_evidence"] is False
    assert result["source_metadata"]["provider_id"] == "tradingview"
    assert result["source_metadata"]["provider_class"] == "visualization"


def test_tradingview_numeric_rows_are_not_canonical_evidence():
    result = TradingViewTool(cache=None, enable_cache=False)._run(action="screener", symbol="HOSE:FPT")

    assert result["content"]["canonical_evidence"] is False
    assert result["kind"] == "VisualizationProvenance"


@pytest.mark.parametrize(
    "kwargs,reason",
    [
        ({"action": "get_chart_url", "symbol": ""}, "missing_symbol"),
        ({"action": "get_chart_url", "symbol": "HOSE:FPT", "interval": "2Y"}, "invalid_interval"),
        ({"action": "get_widget", "symbol": "HOSE:FPT", "widget_type": "raw_quote"}, "unsupported_widget"),
        ({"action": "unknown", "symbol": "HOSE:FPT"}, "unsupported_visualization_action"),
    ],
)
def test_tradingview_degraded_visualization_cases(kwargs, reason):
    result = TradingViewTool(cache=None, enable_cache=False)._run(**kwargs)

    assert result["kind"] == "VisualizationProvenance"
    assert result["content"]["canonical_evidence"] is False
    assert result["content"]["validation_status"] == "degraded"
    assert result["content"]["reason"] == reason


def test_tradingview_health_reports_visualization_only_status():
    healthy, details = TradingViewTool(cache=None, enable_cache=False).health_check()

    assert healthy is True
    assert details["implementation_status"] == "visualization_provenance"
    assert details["canonical_evidence"] is False
