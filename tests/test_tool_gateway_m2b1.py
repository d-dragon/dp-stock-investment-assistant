"""Focused M2B.1 tests for descriptors, route surfaces, gateway admission, and traces."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock

import pytest

from src.core.routes import StockQueryRoute
from src.core.tools.base import AgentTool, CachingTool
from src.core.tools.descriptors import (
    ExposureStatus,
    LicenseMode,
    RiskClass,
    ToolCapabilityDescriptor,
    ToolPolicyDescriptor,
    get_baseline_tool_descriptors,
    validate_descriptor_inventory,
)
from src.core.tools.gateway import (
    DegradedToolResult,
    ToolGateway,
    sanitize_trace_payload,
    safe_public_metadata,
)
from src.core.tools.registry import ToolRegistry
from src.core.tools.stock_symbol import StockSymbolTool
from src.core.tools.surface import RouteSurfaceRequest, ToolSurfaceBuilder


class CountingTool(AgentTool):
    """Small registry-backed tool fixture."""

    name: str = "stock_symbol"
    description: str = "Counting stock lookup"

    def __init__(self) -> None:
        super().__init__(cache=None, enable_cache=False)
        object.__setattr__(self, "calls", 0)

    def _execute(self, **kwargs: Any) -> Dict[str, Any]:
        object.__setattr__(self, "calls", self.calls + 1)
        return {"symbol": kwargs.get("symbol"), "source": "fixture"}


@pytest.fixture
def baseline_descriptors():
    return get_baseline_tool_descriptors()


@pytest.fixture
def registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(CountingTool(), enabled=True)
    return registry


@pytest.fixture
def surface_builder(registry: ToolRegistry) -> ToolSurfaceBuilder:
    return ToolSurfaceBuilder(registry=registry, environment="production")


@pytest.fixture
def price_surface(surface_builder: ToolSurfaceBuilder):
    return surface_builder.build_for_route(StockQueryRoute.PRICE_CHECK)


@pytest.fixture
def gateway(registry: ToolRegistry) -> ToolGateway:
    return ToolGateway(registry)


def test_descriptor_inventory_has_all_m2b1_baseline_descriptors(baseline_descriptors):
    capabilities = baseline_descriptors["capabilities"]
    policies = baseline_descriptors["policies"]

    assert set(capabilities) == {"stock_symbol", "market_data", "tradingview", "reporting"}
    assert set(policies) == {"stock_symbol", "market_data", "tradingview", "reporting"}
    for tool_name in capabilities:
        assert capabilities[tool_name].descriptor_version
        assert capabilities[tool_name].descriptor_hash
        assert policies[tool_name].descriptor_version
        assert policies[tool_name].descriptor_hash


def test_descriptor_model_visible_fields_are_safe(baseline_descriptors):
    forbidden = {
        "credentials",
        "credential_owner",
        "provider_fallback_rules",
        "parser_limits",
        "internal_license_policy",
        "timeout_budget_ms",
        "provider_details",
        "raw_gateway_trace",
    }

    for descriptor in baseline_descriptors["capabilities"].values():
        visible = descriptor.model_visible_dict()
        assert not forbidden.intersection(visible)


def test_descriptor_active_visualization_and_scaffold_status_is_explicit(baseline_descriptors):
    market_data = baseline_descriptors["capabilities"]["market_data"]
    tradingview = baseline_descriptors["capabilities"]["tradingview"]
    reporting = baseline_descriptors["capabilities"]["reporting"]
    market_data_policy = baseline_descriptors["policies"]["market_data"]
    tradingview_policy = baseline_descriptors["policies"]["tradingview"]
    reporting_policy = baseline_descriptors["policies"]["reporting"]

    assert market_data.enabled is True
    assert market_data.model_visible is True
    assert market_data_policy.exposure_status == ExposureStatus.MODEL_VISIBLE
    assert tradingview.enabled is True
    assert tradingview.model_visible is True
    assert tradingview.output_kind == "visualization_provenance"
    assert tradingview_policy.exposure_status == ExposureStatus.MODEL_VISIBLE
    assert reporting.model_visible is False
    assert reporting.non_exposed_reason
    assert reporting_policy.exposure_status == ExposureStatus.NON_EXPOSED


def test_descriptor_integrity_failures_are_machine_detectable(baseline_descriptors):
    capabilities = dict(baseline_descriptors["capabilities"])
    policies = dict(baseline_descriptors["policies"])
    capabilities["stock_symbol"] = replace(capabilities["stock_symbol"], purpose="tampered")

    result = validate_descriptor_inventory(capabilities, policies)

    assert result.valid is False
    assert result.has_code("descriptor_drift")


def test_descriptor_missing_and_policy_capability_mismatch_fail_closed(baseline_descriptors):
    capabilities = dict(baseline_descriptors["capabilities"])
    policies = dict(baseline_descriptors["policies"])
    capabilities.pop("tradingview")
    policies["stock_symbol"] = replace(
        policies["stock_symbol"],
        allowed_routes=(StockQueryRoute.PRICE_CHECK.value, StockQueryRoute.NEWS_ANALYSIS.value),
    ).with_hash()

    result = validate_descriptor_inventory(capabilities, policies)

    assert result.valid is False
    assert result.has_code("missing_capability_descriptor")
    assert result.has_code("policy_capability_mismatch")


@pytest.mark.parametrize(
    "route,expected",
    [
        (StockQueryRoute.PRICE_CHECK, ["stock_symbol"]),
        (StockQueryRoute.FUNDAMENTALS, ["stock_symbol"]),
        (StockQueryRoute.TECHNICAL_ANALYSIS, []),
        (StockQueryRoute.MARKET_WATCH, []),
        (StockQueryRoute.PORTFOLIO, []),
        (StockQueryRoute.NEWS_ANALYSIS, []),
        (StockQueryRoute.IDEAS, []),
        (StockQueryRoute.GENERAL_CHAT, []),
    ],
)
def test_route_surface_expected_tools(route, expected, surface_builder):
    surface = surface_builder.build_for_route(route)

    assert surface.exposed_tool_names == expected


def test_route_surface_filters_disabled_context_risk_license_and_feature_flags(surface_builder):
    surface = surface_builder.build(
        RouteSurfaceRequest(
            route=StockQueryRoute.PRICE_CHECK,
            feature_flags={"tool:stock_symbol": False},
            available_context={"blocked_tools": ["reporting"]},
            allowed_risk_classes=(RiskClass.BOUNDED_NON_MUTATING,),
            registry_enabled_tools=("stock_symbol",),
            capability_descriptors=surface_builder.capability_descriptors,
            policy_descriptors=surface_builder.policy_descriptors,
        )
    )

    assert surface.exposed_tool_names == []
    assert "feature_flag_blocked" in surface.filter_reasons["stock_symbol"]
    assert "risk_blocked" in surface.filter_reasons["stock_symbol"]
    assert "registry_disabled" in surface.filter_reasons["tradingview"]
    assert "registry_disabled" in surface.filter_reasons["market_data"]
    assert "context_blocked" in surface.filter_reasons["reporting"]


def test_route_surface_exposes_empty_list_for_unsupported_route(surface_builder):
    surface = surface_builder.build_for_route(StockQueryRoute.NEWS_ANALYSIS)

    assert surface.exposed_tools == ()
    assert "stock_symbol" in surface.hidden_tools
    assert surface.surface_hash


def test_provider_adapter_names_and_filter_reasons_are_not_model_visible(price_surface):
    visible = price_surface.model_visible_descriptors()

    assert visible
    rendered = repr(visible).lower()
    assert "yahoo" not in rendered
    assert "provider_adapter" not in rendered
    assert "filter_reasons" not in rendered


def test_agent_source_builds_filtered_surface_before_react_invocation():
    source = Path("src/core/stock_assistant_agent.py").read_text(encoding="utf-8")

    assert "_build_tool_surface_for_query" in source
    assert "_build_executor_for_query" in source
    assert "create_wrapped_tools" in source
    assert "turn_executor = self._build_executor_for_query(query)" in source


def test_gateway_admission_allows_registry_backed_call_once(gateway, registry, price_surface):
    result = gateway.execute_tool(
        route=StockQueryRoute.PRICE_CHECK,
        tool_name="stock_symbol",
        args={"action": "get_info", "symbol": "AAPL"},
        surface=price_surface,
    )

    tool = registry.get("stock_symbol")
    assert result == {"symbol": "AAPL", "source": "fixture"}
    assert tool.calls == 1


@pytest.mark.parametrize(
    "tool_name,args,route,expected_code",
    [
        ("missing", {"symbol": "AAPL"}, StockQueryRoute.PRICE_CHECK, "missing_descriptor"),
        ("stock_symbol", {"symbol": "AAPL"}, StockQueryRoute.NEWS_ANALYSIS, "tool_not_exposed_for_route"),
        ("stock_symbol", {"action": "invalid", "symbol": "AAPL"}, StockQueryRoute.PRICE_CHECK, "invalid_arguments"),
    ],
)
def test_gateway_admission_denials_do_not_execute_underlying_tool(
    gateway, registry, price_surface, tool_name, args, route, expected_code
):
    surface = price_surface if route == StockQueryRoute.PRICE_CHECK else None
    result = gateway.execute_tool(route=route, tool_name=tool_name, args=args, surface=surface)

    assert isinstance(result, DegradedToolResult)
    assert result.machine_code == expected_code
    assert result.execute_underlying_tool is False
    assert registry.get("stock_symbol").calls == 0


def test_gateway_blocks_descriptor_drift_before_execution(registry, price_surface, baseline_descriptors):
    capabilities = dict(baseline_descriptors["capabilities"])
    capabilities["stock_symbol"] = replace(capabilities["stock_symbol"], display_name="Tampered")
    gateway = ToolGateway(registry, capability_descriptors=capabilities)

    result = gateway.execute_tool(
        route=StockQueryRoute.PRICE_CHECK,
        tool_name="stock_symbol",
        args={"action": "get_info", "symbol": "AAPL"},
        surface=price_surface,
    )

    assert isinstance(result, DegradedToolResult)
    assert result.machine_code == "descriptor_drift"
    assert registry.get("stock_symbol").calls == 0


def test_gateway_blocks_provider_cache_and_freshness_failures(gateway, registry, price_surface):
    result = gateway.execute_tool(
        route=StockQueryRoute.PRICE_CHECK,
        tool_name="stock_symbol",
        args={"action": "get_info", "symbol": "AAPL"},
        surface=price_surface,
        provider_state={"status": "unavailable", "cache_status": "unknown", "freshness": "stale"},
    )

    assert isinstance(result, DegradedToolResult)
    assert result.machine_code == "provider_or_cache_unavailable"
    assert registry.get("stock_symbol").calls == 0


def test_gateway_denied_result_contract_is_stable(gateway, price_surface):
    decision = gateway.evaluate_admission(
        route=StockQueryRoute.PRICE_CHECK,
        tool_name="stock_symbol",
        args={"action": "get_info"},
        surface=price_surface,
    )

    assert decision.outcome in {"blocked", "degraded"}
    assert decision.machine_code == "invalid_arguments"
    assert decision.execute_underlying_tool is False
    assert decision.safe_message
    assert decision.trace_record.degraded_state_reason == "invalid_arguments"


def test_runtime_compatibility_uses_tool_registry_and_caching_tool(registry, gateway, price_surface):
    wrapped = gateway.create_wrapped_tools(route=StockQueryRoute.PRICE_CHECK, surface=price_surface)

    assert len(wrapped) == 1
    assert isinstance(wrapped[0], AgentTool)
    assert isinstance(registry.get("stock_symbol"), AgentTool)
    assert wrapped[0]._run(action="get_info", symbol="AAPL") == {"symbol": "AAPL", "source": "fixture"}
    assert registry.get("stock_symbol").calls == 1


def test_trace_completeness_ratio_meets_m2b1_threshold(gateway, price_surface):
    for symbol in ("AAPL", "MSFT", "NVDA", "VCB"):
        gateway.execute_tool(
            route=StockQueryRoute.PRICE_CHECK,
            tool_name="stock_symbol",
            args={"action": "get_info", "symbol": symbol},
            surface=price_surface,
        )

    assert gateway.trace_completeness_ratio() >= 0.95


def test_trace_sanitization_removes_sensitive_fields():
    payload = {
        "route": "price_check",
        "api_key": "secret",
        "credential_owner": "provider",
        "raw_provider_payload": "<html>",
        "safe": {"token": "hidden", "value": "kept"},
    }

    sanitized = sanitize_trace_payload(payload)

    assert "api_key" not in sanitized
    assert "credential_owner" not in sanitized
    assert "raw_provider_payload" not in sanitized
    assert sanitized["safe"] == {"value": "kept"}


def test_public_metadata_excludes_internal_gateway_trace(gateway, price_surface):
    decision = gateway.evaluate_admission(
        route=StockQueryRoute.PRICE_CHECK,
        tool_name="stock_symbol",
        args={"action": "get_info"},
        surface=price_surface,
    )

    metadata = safe_public_metadata(decision)

    assert "trace_record" not in metadata
    assert "descriptor_hash" not in metadata
    assert metadata["tool_gateway_status"] == decision.outcome
    assert metadata["tool_gateway_reason"] == "invalid_arguments"


@pytest.mark.performance
def test_performance_and_route_reduction(surface_builder, gateway, price_surface):
    start = __import__("time").perf_counter()
    surface = surface_builder.build_for_route(StockQueryRoute.PRICE_CHECK)
    gateway.evaluate_admission(
        route=StockQueryRoute.PRICE_CHECK,
        tool_name="stock_symbol",
        args={"action": "get_info", "symbol": "AAPL"},
        surface=surface,
    )
    elapsed_ms = (__import__("time").perf_counter() - start) * 1000

    assert elapsed_ms < 50
    assert surface_builder.baseline_candidate_count() > 1
    assert surface_builder.reduction_ratio(price_surface) >= 0.20


def test_existing_stock_symbol_tool_behavior_is_unchanged():
    data_manager = MagicMock()
    data_manager.get_stock_info.return_value = {
        "name": "Apple Inc.",
        "current_price": 175.5,
        "previous_close": 174.0,
        "market_cap": 1,
        "pe_ratio": 28.0,
        "dividend_yield": 0.01,
        "sector": "Technology",
        "industry": "Consumer Electronics",
    }
    tool = StockSymbolTool(data_manager=data_manager, cache=None, enable_cache=False)

    result = tool._run(action="get_info", symbol="aapl")

    assert result["symbol"] == "AAPL"
    assert result["source"] == "yahoo_finance"
