"""Deterministic market route-evaluation tests."""

from __future__ import annotations

from core.routes import StockQueryRoute
from core.stock_query_router import (
    MARKET_TOOL_FAMILY_BY_ROUTE,
    classify_market_tool_family,
    evaluate_market_route_cases,
)
from core.tools.registry import ToolRegistry
from core.tools.surface import ToolSurfaceBuilder
from core.tools.market_data import VietnamMarketDataTool
from core.tools.tradingview import TradingViewTool
from tests.fixtures.market_tools.route_cases import ROUTE_CASES
from tests.helpers.market_tool_helpers import assert_route_metrics


def test_route_accuracy_precision_and_recall_meet_threshold():
    metrics = evaluate_market_route_cases(ROUTE_CASES)

    assert_route_metrics(metrics, minimum=0.85)


def test_route_tool_family_mapping_is_bounded_to_admitted_families():
    assert MARKET_TOOL_FAMILY_BY_ROUTE[StockQueryRoute.PRICE_CHECK] == ("market_data", "stock_symbol")
    assert MARKET_TOOL_FAMILY_BY_ROUTE[StockQueryRoute.TECHNICAL_ANALYSIS] == ("market_data", "tradingview")
    assert MARKET_TOOL_FAMILY_BY_ROUTE[StockQueryRoute.PORTFOLIO] == ()


def test_ambiguous_and_report_like_queries_are_not_executed_as_reports():
    ambiguous = classify_market_tool_family("ABC")
    report = classify_market_tool_family("Generate an investment report for FPT")

    assert ambiguous["route"] == StockQueryRoute.GENERAL_CHAT
    assert ambiguous["degraded"] is True
    assert report["tool_family"] == "report_fixture"
    assert report["deferred_scope"] is True
    assert report["degraded_reason"] == "report_generation_deferred"


def test_route_surface_exposes_market_tools_without_generic_web_or_report_generation():
    registry = ToolRegistry()
    registry.register(VietnamMarketDataTool(cache=None, enable_cache=False), enabled=True)
    registry.register(TradingViewTool(cache=None, enable_cache=False), enabled=True)
    surface_builder = ToolSurfaceBuilder(registry=registry)

    price_surface = surface_builder.build_for_route(StockQueryRoute.PRICE_CHECK)
    chart_surface = surface_builder.build_for_route(StockQueryRoute.TECHNICAL_ANALYSIS)

    assert "market_data" in price_surface.exposed_tool_names
    assert "tradingview" in chart_surface.exposed_tool_names
    assert "reporting" not in chart_surface.exposed_tool_names
    assert "generic_web_fetch" not in chart_surface.exposed_tool_names
