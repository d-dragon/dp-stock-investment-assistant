"""Tests for Vietnam market-data evidence."""

from __future__ import annotations

import pytest

from core.tools.market_data import (
    MarketDataOutputType,
    VietnamMarketDataTool,
    market_evidence_output,
    no_market_source_output,
    select_vietnam_provider,
    tradingview_values_are_canonical,
)
from core.tools.normalization import DegradedReason, FreshnessStatus, NormalizedOutputKind
from core.tools.provider_policy import DataCategory
from core.tools.stock_symbol import StockSymbolTool
from tests.fixtures.market_tools.market_payloads import (
    BREADTH_PAYLOAD,
    CORPORATE_ACTION_PAYLOAD,
    DISCLOSURE_PAYLOAD,
    FLOW_PAYLOAD,
    FUNDAMENTAL_PAYLOAD,
    HISTORY_PAYLOAD,
    INDICATOR_PAYLOAD,
    QUOTE_PAYLOAD,
)
from tests.fixtures.market_tools.symbols import BSR, FPT, SHS
from tests.helpers.market_tool_helpers import assert_market_attribution, assert_no_raw_payload


@pytest.mark.parametrize(
    "identity,action,expected_type",
    [
        (FPT, "quote", MarketDataOutputType.MARKET_FACT),
        (SHS, "history", MarketDataOutputType.PRICE_HISTORY_SERIES),
        (BSR, "ohlcv", MarketDataOutputType.PRICE_HISTORY_SERIES),
        (FPT, "indicator", MarketDataOutputType.INDICATOR_EVIDENCE),
    ],
)
def test_quote_history_and_indicator_outputs_have_attribution(identity, action, expected_type):
    output = market_evidence_output(
        output_type=expected_type,
        identity=identity,
        content=INDICATOR_PAYLOAD if action == "indicator" else HISTORY_PAYLOAD if action in {"history", "ohlcv"} else QUOTE_PAYLOAD,
    )

    assert output.kind == NormalizedOutputKind.EVIDENCE_FACT
    assert output.content["output_type"] == expected_type.value
    assert_market_attribution(output)


def test_ambiguous_symbol_degrades_before_market_evidence():
    output = market_evidence_output(
        output_type=MarketDataOutputType.MARKET_FACT,
        identity=None,
        content=QUOTE_PAYLOAD,
    )

    assert output.kind == NormalizedOutputKind.DEGRADED_STATE
    assert output.degraded_state.code == DegradedReason.AMBIGUOUS_SYMBOL.value


def test_vietnam_first_provider_selection_and_fallback_metadata():
    decision = select_vietnam_provider(category=DataCategory.QUOTE, provider_health={"hose_official": "down"})

    assert decision.allowed is True
    assert decision.selected_adapter == "hnx_official"
    assert decision.fallback_used is True
    assert "hose_official:provider_down" in decision.warnings


def test_no_source_and_blocked_license_degraded_states_are_machine_detectable():
    output = no_market_source_output(category=DataCategory.FUNDAMENTAL, reason=DegradedReason.BLOCKED_LICENSE)

    assert output.kind == NormalizedOutputKind.DEGRADED_STATE
    assert output.degraded_state.code == DegradedReason.BLOCKED_LICENSE.value
    assert output.degraded_state.tool_name == "market_data"


@pytest.mark.parametrize(
    "action,expected_type,payload",
    [
        ("fundamentals", MarketDataOutputType.FUNDAMENTAL_EVIDENCE, FUNDAMENTAL_PAYLOAD),
        ("statement", MarketDataOutputType.FUNDAMENTAL_EVIDENCE, FUNDAMENTAL_PAYLOAD),
        ("breadth", MarketDataOutputType.BREADTH_AND_FLOW_EVIDENCE, BREADTH_PAYLOAD),
        ("flow", MarketDataOutputType.BREADTH_AND_FLOW_EVIDENCE, FLOW_PAYLOAD),
        ("disclosure", MarketDataOutputType.DISCLOSURE_CORPORATE_ACTION_EVIDENCE, DISCLOSURE_PAYLOAD),
        ("corporate_action", MarketDataOutputType.DISCLOSURE_CORPORATE_ACTION_EVIDENCE, CORPORATE_ACTION_PAYLOAD),
    ],
)
def test_market_categories_are_normalized(action, expected_type, payload):
    output = market_evidence_output(output_type=expected_type, identity=FPT, content=payload)

    assert output.content["output_type"] == expected_type.value
    assert_market_attribution(output)


def test_vietnam_market_data_tool_executes_fixture_only_evidence():
    result = VietnamMarketDataTool(cache=None, enable_cache=False)._run(action="quote", symbol="HOSE:FPT")

    normalized = result["normalized_output"]
    assert result["tool_family"] == "market_data"
    assert normalized["kind"] == "EvidenceFact"
    assert normalized["content"]["symbol"] == "HOSE:FPT"
    assert result["provider_decision"]["selected_adapter"] == "hose_official"
    assert_no_raw_payload(result)


def test_stock_symbol_tool_does_not_own_market_data_evidence():
    stock_symbol = StockSymbolTool(cache=None, enable_cache=False)
    market_data = VietnamMarketDataTool(cache=None, enable_cache=False)

    assert stock_symbol.name == "stock_symbol"
    assert market_data.name == "market_data"
    assert stock_symbol.name != market_data.name


def test_tradingview_values_are_rejected_as_canonical_market_evidence():
    output = market_evidence_output(
        output_type=MarketDataOutputType.MARKET_FACT,
        identity=FPT,
        content=QUOTE_PAYLOAD,
        provider_id="tradingview",
        provider_class="visualization",
        freshness_status=FreshnessStatus.NOT_APPLICABLE,
    )

    assert tradingview_values_are_canonical(output) is True
