"""Cross-boundary integration scenario fixtures.

Each scenario defines the expected path through route classification, tool surface
exposure, gateway admission, provider selection, normalization, and response outcome.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class IntegrationScenario:
    """A single cross-boundary integration test case.

    Attributes:
        id: Unique scenario identifier (e.g., "INT-001")
        prompt: The user-facing prompt text
        expected_route: Expected StockQueryRoute category
        expected_tool_family: Expected tool family exposed by ToolSurfaceBuilder
        expected_gateway_decision: Expected admission outcome ("admitted"|"blocked"|"degraded")
        expected_provider_posture: Expected provider class or degraded reason
        expected_output_kind: Expected NormalizedOutputKind
        expected_warnings: Expected warnings or degraded-state reasons
        expected_response_outcome: Expected user-facing response description
        description: Human-readable purpose of this scenario
    """
    id: str
    prompt: str
    expected_route: str
    expected_tool_family: str
    expected_gateway_decision: str
    expected_provider_posture: str
    expected_output_kind: str
    expected_warnings: List[str] = field(default_factory=list)
    expected_response_outcome: str = ""
    description: str = ""


# --- US1: Integrated Readiness Scenarios ---

INTEGRATED_READINESS_SCENARIOS: List[IntegrationScenario] = [
    IntegrationScenario(
        id="INT-001",
        prompt="What is the current price of FPT?",
        expected_route="PRICE_CHECK",
        expected_tool_family="market_data",
        expected_gateway_decision="admitted",
        expected_provider_posture="vietnam_native_public_web",
        expected_output_kind="EVIDENCE_FACT",
        expected_warnings=[],
        expected_response_outcome="Price quote with source attribution",
        description="Basic Vietnam symbol price check through full pipeline",
    ),
    IntegrationScenario(
        id="INT-002",
        prompt="Show me the price history for HOSE:FPT over the last 30 days",
        expected_route="TECHNICAL_ANALYSIS",
        expected_tool_family="market_data",
        expected_gateway_decision="admitted",
        expected_provider_posture="vietnam_native_public_web",
        expected_output_kind="EVIDENCE_FACT",
        expected_warnings=[],
        expected_response_outcome="Price history with source metadata and date range",
        description="Vietnam symbol with exchange prefix history query",
    ),
    IntegrationScenario(
        id="INT-003",
        prompt="What are the fundamentals for VNM?",
        expected_route="FUNDAMENTALS",
        expected_tool_family="market_data",
        expected_gateway_decision="admitted",
        expected_provider_posture="vietnam_native_public_web",
        expected_output_kind="EVIDENCE_FACT",
        expected_warnings=[],
        expected_response_outcome="Fundamental metrics with source attribution",
        description="Vietnam fundamentals query",
    ),
    IntegrationScenario(
        id="INT-004",
        prompt="Show me a chart for AAPL",
        expected_route="TECHNICAL_ANALYSIS",
        expected_tool_family="tradingview",
        expected_gateway_decision="admitted",
        expected_provider_posture="visualization",
        expected_output_kind="VISUALIZATION_PROVENANCE",
        expected_warnings=[],
        expected_response_outcome="Chart visualization with provenance classification",
        description="Visualization request routed to TradingView tool family",
    ),
    IntegrationScenario(
        id="INT-005",
        prompt="Show me a TradingView widget for FPT",
        expected_route="TECHNICAL_ANALYSIS",
        expected_tool_family="tradingview",
        expected_gateway_decision="admitted",
        expected_provider_posture="visualization",
        expected_output_kind="VISUALIZATION_PROVENANCE",
        expected_warnings=[],
        expected_response_outcome="Widget visualization with provenance classification",
        description="TradingView widget request",
    ),
    IntegrationScenario(
        id="INT-006",
        prompt="What is P/E ratio of Apple?",
        expected_route="FUNDAMENTALS",
        expected_tool_family="market_data",
        expected_gateway_decision="admitted",
        expected_provider_posture="international_fallback",
        expected_output_kind="EVIDENCE_FACT",
        expected_warnings=["international_fallback_used"],
        expected_response_outcome="Fundamental metrics with international fallback attribution",
        description="International symbol falls back to non-Vietnam provider",
    ),
    IntegrationScenario(
        id="INT-007",
        prompt="Gia cua co phieu FPT hom nay la bao nhieu?",
        expected_route="PRICE_CHECK",
        expected_tool_family="market_data",
        expected_gateway_decision="admitted",
        expected_provider_posture="vietnam_native_public_web",
        expected_output_kind="EVIDENCE_FACT",
        expected_warnings=[],
        expected_response_outcome="Price quote with Vietnamese language prompt",
        description="Vietnamese language price check through full pipeline",
    ),
    IntegrationScenario(
        id="INT-008",
        prompt="Phan tich co ban cua co phieu VNM",
        expected_route="FUNDAMENTALS",
        expected_tool_family="market_data",
        expected_gateway_decision="admitted",
        expected_provider_posture="vietnam_native_public_web",
        expected_output_kind="EVIDENCE_FACT",
        expected_warnings=[],
        expected_response_outcome="Fundamentals analysis with Vietnamese language prompt",
        description="Vietnamese language fundamentals query",
    ),
    IntegrationScenario(
        id="INT-009",
        prompt="Biểu đồ kỹ thuật của FPT",
        expected_route="TECHNICAL_ANALYSIS",
        expected_tool_family="tradingview",
        expected_gateway_decision="admitted",
        expected_provider_posture="visualization",
        expected_output_kind="VISUALIZATION_PROVENANCE",
        expected_warnings=[],
        expected_response_outcome="Chart with Vietnamese/mixed-language prompt",
        description="Mixed Vietnamese-English technical analysis request",
    ),
    IntegrationScenario(
        id="INT-010",
        prompt="Show me the market breadth today",
        expected_route="MARKET_WATCH",
        expected_tool_family="market_data",
        expected_gateway_decision="admitted",
        expected_provider_posture="vietnam_native_public_web",
        expected_output_kind="EVIDENCE_FACT",
        expected_warnings=[],
        expected_response_outcome="Market breadth data with source attribution",
        description="Market breadth query through full pipeline",
    ),
    IntegrationScenario(
        id="INT-011",
        prompt="Write a comprehensive investment report on FPT",
        expected_route="IDEAS",
        expected_tool_family="deferred_report",
        expected_gateway_decision="degraded",
        expected_provider_posture="not_yet_admitted",
        expected_output_kind="DEGRADED_STATE",
        expected_warnings=["report_persistence_not_yet_admitted"],
        expected_response_outcome="Degraded state: report generation not yet available",
        description="Report-like prompt degraded rather than expanding scope",
    ),
    IntegrationScenario(
        id="INT-012",
        prompt="What's happening in the stock market?",
        expected_route="GENERAL_CHAT",
        expected_tool_family="no_tool_exposed",
        expected_gateway_decision="not_applicable",
        expected_provider_posture="none",
        expected_output_kind="GENERAL_CHAT",
        expected_warnings=[],
        expected_response_outcome="General chat response without tool invocation",
        description="Ambiguous/unsupported prompt degrades appropriately",
    ),
]

# --- Degraded Path Scenarios ---

DEGRADED_PATH_SCENARIOS: List[IntegrationScenario] = [
    IntegrationScenario(
        id="DEG-001",
        prompt="What is the price of UNKNOWN_SYMBOL_XYZ?",
        expected_route="PRICE_CHECK",
        expected_tool_family="market_data",
        expected_gateway_decision="blocked",
        expected_provider_posture="unknown_symbol",
        expected_output_kind="DEGRADED_STATE",
        expected_warnings=["unknown_symbol"],
        expected_response_outcome="Degraded state: unknown symbol",
        description="Unknown symbol produces degraded state",
    ),
    IntegrationScenario(
        id="DEG-002",
        prompt="Get insider trading data for FPT",
        expected_route="FUNDAMENTALS",
        expected_tool_family="market_data",
        expected_gateway_decision="degraded",
        expected_provider_posture="not_yet_admitted",
        expected_output_kind="DEGRADED_STATE",
        expected_warnings=["data_category_not_yet_available"],
        expected_response_outcome="Degraded state: insider trading data not yet available",
        description="Unsupported data category produces degraded state",
    ),
]


def get_all_integrated_scenarios() -> List[IntegrationScenario]:
    """Return all integrated readiness and degraded path scenarios."""
    return INTEGRATED_READINESS_SCENARIOS + DEGRADED_PATH_SCENARIOS
