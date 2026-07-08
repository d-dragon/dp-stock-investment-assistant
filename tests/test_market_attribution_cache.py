"""Tests for market attribution, freshness, cache, and trace safety."""

from __future__ import annotations

from core.routes import StockQueryRoute
from core.tools.gateway import ToolGateway, sanitize_trace_payload
from core.tools.market_data import MarketDataOutputType, VietnamMarketDataTool, market_evidence_output
from core.tools.normalization import (
    DegradedReason,
    FreshnessStatus,
    attribution_coverage_counters,
    cache_freshness_metadata,
    make_degraded_output,
)
from core.tools.registry import ToolRegistry
from core.tools.surface import ToolSurfaceBuilder
from tests.fixtures.market_tools.market_payloads import QUOTE_PAYLOAD
from tests.fixtures.market_tools.symbols import FPT
from tests.helpers.market_tool_helpers import assert_all_outputs_safe, assert_market_attribution


def test_market_fact_attribution_and_cache_freshness_metadata_are_complete():
    output = market_evidence_output(
        output_type=MarketDataOutputType.MARKET_FACT,
        identity=FPT,
        content=QUOTE_PAYLOAD,
    )
    freshness = cache_freshness_metadata(
        provider_id="hose_official",
        retrieved_at="2026-07-07T00:01:00Z",
        source_timestamp="2026-07-07T00:00:00Z",
        freshness_status=FreshnessStatus.CURRENT,
        ttl_seconds=60,
    )

    assert_market_attribution(output)
    assert freshness["freshness_status"] == "current"
    assert freshness["ttl_seconds"] == 60


def test_gateway_trace_metadata_is_sanitized_for_provider_backed_calls():
    registry = ToolRegistry()
    registry.register(VietnamMarketDataTool(cache=None, enable_cache=False), enabled=True)
    surface = ToolSurfaceBuilder(registry=registry).build_for_route(StockQueryRoute.PRICE_CHECK)
    gateway = ToolGateway(registry)

    result = gateway.execute_tool(
        route=StockQueryRoute.PRICE_CHECK,
        tool_name="market_data",
        args={"action": "quote", "symbol": "FPT"},
        surface=surface,
        provider_state={"cache_status": "miss", "freshness": "current"},
    )

    assert result["normalized_output"]["kind"] == "EvidenceFact"
    trace = gateway.trace_records[-1].sanitized_dict()
    assert trace["selected_tool"] == "market_data"
    assert trace["cache_status"] == "miss"
    assert "credential" not in repr(trace).lower()


def test_sanitize_trace_payload_removes_unsafe_public_metadata():
    payload = {
        "selected_adapter": "hose_official",
        "raw_payload": {"secret": "value"},
        "credential_token": "secret",
        "safe": "kept",
    }

    sanitized = sanitize_trace_payload(payload)
    assert sanitized == {"selected_adapter": "hose_official", "safe": "kept"}


def test_attribution_coverage_counters_track_complete_and_degraded_outputs():
    complete = market_evidence_output(
        output_type=MarketDataOutputType.MARKET_FACT,
        identity=FPT,
        content=QUOTE_PAYLOAD,
    )
    degraded = make_degraded_output(
        code=DegradedReason.NO_SOURCE_AVAILABLE.value,
        safe_message="No source.",
        reason=DegradedReason.NO_SOURCE_AVAILABLE,
        tool_name="market_data",
    )
    stale = market_evidence_output(
        output_type=MarketDataOutputType.MARKET_FACT,
        identity=FPT,
        content=QUOTE_PAYLOAD,
        freshness_status=FreshnessStatus.STALE,
    )

    counters = attribution_coverage_counters((complete, degraded, stale)).to_dict()

    assert counters["complete_attribution"] == 2
    assert counters["degraded_no_source"] == 1
    assert counters["stale_cache"] == 1
    assert_all_outputs_safe((complete, degraded, stale))
