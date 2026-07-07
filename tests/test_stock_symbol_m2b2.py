"""M2B.2 tests for internal StockSymbolTool symbol-store behavior."""

from __future__ import annotations

import pytest

from core.tools.normalization import NormalizedOutputKind
from core.tools.stock_symbol import StockSymbolTool
from tests.fixtures.tool_system_m2b2.symbols import InMemorySymbolRepository
from tests.helpers.tool_system_m2b2_helpers import assert_degraded, assert_normalized_kind


@pytest.fixture
def symbol_tool():
    return StockSymbolTool(symbol_repository=InMemorySymbolRepository(), cache=None, enable_cache=False)


@pytest.mark.parametrize(
    "input_symbol,expected_symbol,expected_exchange,expected_type",
    [
        ("FPT", "FPT", "HOSE", "equity"),
        ("HOSE:FPT", "FPT", "HOSE", "equity"),
        ("HNX:SHS", "SHS", "HNX", "equity"),
        ("UPCOM:BSR", "BSR", "UPCOM", "equity"),
        ("VNINDEX", "VNINDEX", "HOSE", "index"),
        ("VN30", "VN30", "HOSE", "index"),
        ("HNXINDEX", "HNXINDEX", "HNX", "index"),
        ("UPINDEX", "UPINDEX", "UPCOM", "index"),
    ],
)
def test_canonical_symbol_and_index_identity(symbol_tool, input_symbol, expected_symbol, expected_exchange, expected_type):
    result = symbol_tool._run(action="lookup", symbol=input_symbol)
    output = result["normalized_output"]
    identity = output["content"]["identity"]

    assert result["status"] == "ok"
    assert_normalized_kind(output, NormalizedOutputKind.SYSTEM_RECORD)
    assert identity["symbol"] == expected_symbol
    assert identity["exchange"] == expected_exchange
    assert identity["currency"] == "VND"
    assert identity["asset_type"] == expected_type


def test_ticker_only_ambiguity_degrades_with_candidates(symbol_tool):
    result = symbol_tool._run(action="lookup", symbol="ABC")

    assert result["status"] == "degraded"
    assert_degraded(result["normalized_output"], "ambiguous_symbol")
    assert {candidate["exchange"] for candidate in result["candidates"]} == {"HOSE", "HNX"}


def test_duplicate_alias_can_resolve_with_exchange_hint(symbol_tool):
    result = symbol_tool._run(action="lookup", symbol="ABC", exchange="HNX")
    identity = result["normalized_output"]["content"]["identity"]

    assert result["status"] == "ok"
    assert identity["symbol"] == "ABC"
    assert identity["exchange"] == "HNX"


@pytest.mark.parametrize("action", ["quote", "history", "fundamentals"])
def test_live_quote_history_and_fundamental_requests_are_not_symbol_tool_responsibilities(symbol_tool, action):
    result = symbol_tool._run(action=action, symbol="FPT")

    assert result["status"] == "degraded"
    assert_degraded(result["normalized_output"], "live_market_data_not_owned")
    assert result["envelope"]["selected_adapter"] == "internal_symbol_store"


def test_system_record_output_shape_contains_internal_symbol_store_metadata(symbol_tool):
    result = symbol_tool._run(action="lookup", symbol="HOSE:FPT")
    output = result["normalized_output"]

    assert output["kind"] == "SystemRecord"
    assert output["source_metadata"]["provider_id"] == "internal_symbol_store"
    assert output["content"]["coverage"] == ["identity", "aliases", "coverage", "tags"]
    assert "current_price" not in output["content"]
    assert result["envelope"]["normalized_output_ref"] == output["output_id"]


def test_normalized_search_outputs_system_records(symbol_tool):
    result = symbol_tool._run(action="search", query="FPT", normalized=True)

    assert result["count"] == 1
    assert result["output_kinds"] == ["SystemRecord"]
    assert result["normalized_outputs"][0]["content"]["identity"]["symbol"] == "FPT"


def test_symbol_list_and_coverage_outputs_use_internal_store(symbol_tool):
    listed = symbol_tool._run(action="list", exchange="HOSE", limit=3)
    coverage = symbol_tool._run(action="coverage", symbol="FPT")

    assert listed["source"] == "internal_symbol_store"
    assert listed["count"] == 3
    assert "identity" in coverage["coverage"]
    assert "vn30" in coverage["tags"]


def test_stale_symbol_record_returns_degraded_state(symbol_tool):
    result = symbol_tool._run(action="lookup", symbol="STALE")

    assert result["status"] == "degraded"
    assert_degraded(result["normalized_output"], "stale_record")


def test_existing_get_info_path_preserves_legacy_data_manager_behavior():
    class DataManager:
        def get_stock_info(self, symbol):
            return {"name": "FPT", "current_price": 1, "sector": "Technology"}

    tool = StockSymbolTool(data_manager=DataManager(), cache=None, enable_cache=False)
    result = tool._run(action="get_info", symbol="fpt")

    assert result["symbol"] == "FPT"
    assert result["source"] == "yahoo_finance"
    assert result["current_price"] == 1
