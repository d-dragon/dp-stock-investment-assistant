"""Architecture boundary verification test cases.

Covers risk class enforcement, prompt boundary safety, symbol-tool separation,
gateway purity, registry integrity, and STM evidence freedom.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class RiskClassScenario:
    """A single risk class verification case.

    Attributes:
        id: Unique scenario identifier
        tool_name: Name of the tool being verified
        declared_risk_class: Expected risk class in ToolRegistry
        admitted_by_gateway: Whether the gateway admits calls at this risk level
        prompt_policy_can_downgrade: Whether prompt-facing policy can reclassify
        expected_behavior: Expected outcome
        description: Purpose of this scenario
    """
    id: str
    tool_name: str
    declared_risk_class: str
    admitted_by_gateway: bool
    prompt_policy_can_downgrade: bool
    expected_behavior: str
    description: str = ""


RISK_CLASS_SCENARIOS: List[RiskClassScenario] = [
    RiskClassScenario(
        id="RC-001",
        tool_name="StockSymbolTool",
        declared_risk_class="read_only_evidence",
        admitted_by_gateway=True,
        prompt_policy_can_downgrade=False,
        expected_behavior="admitted",
        description="StockSymbolTool is read_only_evidence, admitted by gateway, and prompt policy cannot reclassify",
    ),
    RiskClassScenario(
        id="RC-002",
        tool_name="TradingViewTool",
        declared_risk_class="read_only_evidence",
        admitted_by_gateway=True,
        prompt_policy_can_downgrade=False,
        expected_behavior="admitted",
        description="TradingViewTool is read_only_evidence, admitted by gateway",
    ),
    RiskClassScenario(
        id="RC-003",
        tool_name="market_data",
        declared_risk_class="read_only_evidence",
        admitted_by_gateway=True,
        prompt_policy_can_downgrade=False,
        expected_behavior="admitted",
        description="Market data tools are read_only_evidence, admitted by gateway",
    ),
]


@dataclass(frozen=True)
class PromptSafetyScenario:
    """Verifies that raw payloads are excluded from prompt assembly."""
    id: str
    payload_type: str
    expected_in_prompt: bool
    description: str = ""


PROMPT_SAFETY_SCENARIOS: List[PromptSafetyScenario] = [
    PromptSafetyScenario(
        id="PS-001",
        payload_type="raw_provider_payload",
        expected_in_prompt=False,
        description="Raw provider payloads must not reach prompt assembly",
    ),
    PromptSafetyScenario(
        id="PS-002",
        payload_type="chart_widget_content",
        expected_in_prompt=False,
        description="Chart widget content must not reach prompt assembly as instructions",
    ),
    PromptSafetyScenario(
        id="PS-003",
        payload_type="tool_descriptor_text",
        expected_in_prompt=False,
        description="Tool descriptor text must not reach prompt assembly as authority",
    ),
]


@dataclass(frozen=True)
class SymbolMarketDataSeparationScenario:
    """Verifies StockSymbolTool handles identity only, market-data tools handle quotes."""
    id: str
    request_type: str
    expected_routing_tool: str
    description: str = ""


SYMBOL_SEPARATION_SCENARIOS: List[SymbolMarketDataSeparationScenario] = [
    SymbolMarketDataSeparationScenario(
        id="SS-001",
        request_type="symbol_lookup",
        expected_routing_tool="StockSymbolTool",
        description="Symbol identity lookup routes to StockSymbolTool",
    ),
    SymbolMarketDataSeparationScenario(
        id="SS-002",
        request_type="price_quote",
        expected_routing_tool="market_data",
        description="Price quote routes to market_data tool family, not StockSymbolTool",
    ),
    SymbolMarketDataSeparationScenario(
        id="SS-003",
        request_type="price_history",
        expected_routing_tool="market_data",
        description="Price history routes to market_data tool family, not StockSymbolTool",
    ),
    SymbolMarketDataSeparationScenario(
        id="SS-004",
        request_type="fundamentals",
        expected_routing_tool="market_data",
        description="Fundamentals routes to market_data tool family, not StockSymbolTool",
    ),
    SymbolMarketDataSeparationScenario(
        id="SS-005",
        request_type="market_breadth",
        expected_routing_tool="market_data",
        description="Market breadth routes to market_data tool family",
    ),
]
