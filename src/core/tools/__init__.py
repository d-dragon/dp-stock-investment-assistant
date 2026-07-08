"""LangChain Tools Module for Stock Investment Assistant.

This module provides a suite of LangChain-compatible tools for stock data
retrieval, analysis, and reporting. All tools extend CachingTool which
provides Redis/in-memory caching integration.

Tools:
    - StockSymbolTool: Retrieve stock prices and symbol information
    - ReportingTool: Generate investment reports (markdown)
    - TradingViewTool: TradingView integration (placeholder for Phase 2)

Registry:
    - ToolRegistry: Central registry for tool management

Reference: .github/instructions/backend-python.instructions.md § Model Factory
"""

from .base import CachingTool
from .registry import ToolRegistry, get_tool_registry, reset_tool_registry
from .stock_symbol import StockSymbolTool
from .reporting import ReportingTool
from .tradingview import TradingViewTool
from .market_data import (
    MarketDataEvidence,
    MarketDataOutputType,
    MarketDataRequest,
    VietnamMarketDataTool,
    default_vietnam_provider_descriptors,
    market_evidence_output,
    no_market_source_output,
    select_vietnam_provider,
    tradingview_values_are_canonical,
    vietnam_provider_policy,
)
from .descriptors import (
    BaselineInventoryState,
    ExposureStatus,
    LicenseMode,
    MutationPolicy,
    RiskClass,
    ToolCapabilityDescriptor,
    ToolPolicyDescriptor,
    get_baseline_tool_descriptors,
    get_baseline_tool_inventory,
    validate_descriptor_inventory,
)
from .gateway import (
    DegradedToolResult,
    GatewayAdmissionDecision,
    ToolGateway,
    ToolTraceRecord,
)
from .surface import (
    RouteFilteredToolSurface,
    RouteSurfaceRequest,
    ToolSurfaceBuilder,
)
from .normalization import (
    AdmissionOutcome,
    AttributionCoverageCounters,
    CanonicalSymbolIdentity,
    DegradedReason,
    DegradedState,
    FreshnessStatus,
    InternalSymbolRecord,
    NormalizedOutput,
    NormalizedOutputKind,
    SourceMetadata,
    ToolExecutionEnvelope,
    attribution_coverage_counters,
    cache_freshness_metadata,
    has_complete_market_attribution,
    make_degraded_output,
    make_evidence_fact_output,
    make_system_record_output,
    make_visualization_provenance_output,
)
from .provider_policy import (
    CredentialOwner,
    DataCategory,
    LicensePosture,
    ProviderAdapterDescriptor,
    ProviderClass,
    ProviderSelectionDecision,
    ProviderSelectionPolicy,
)
from .context import (
    RetainedDerivative,
    ToolContextPack,
    assemble_tool_context_pack,
    reject_whole_pack_persistence,
    validate_retained_derivative,
)
from .mutation_receipts import (
    MutationReceipt,
    MutationStatus,
    disabled_mutation_receipt,
    guard_symbol_mutation,
)

__all__ = [
    # Base
    "CachingTool",
    # Registry
    "ToolRegistry",
    "get_tool_registry",
    "reset_tool_registry",
    # Tools
    "StockSymbolTool",
    "ReportingTool",
    "TradingViewTool",
    "VietnamMarketDataTool",
    "MarketDataEvidence",
    "MarketDataOutputType",
    "MarketDataRequest",
    "default_vietnam_provider_descriptors",
    "market_evidence_output",
    "no_market_source_output",
    "select_vietnam_provider",
    "tradingview_values_are_canonical",
    "vietnam_provider_policy",
    # M2B.1 descriptors
    "BaselineInventoryState",
    "ExposureStatus",
    "LicenseMode",
    "MutationPolicy",
    "RiskClass",
    "ToolCapabilityDescriptor",
    "ToolPolicyDescriptor",
    "get_baseline_tool_descriptors",
    "get_baseline_tool_inventory",
    "validate_descriptor_inventory",
    # M2B.1 surface and gateway
    "RouteFilteredToolSurface",
    "RouteSurfaceRequest",
    "ToolSurfaceBuilder",
    "DegradedToolResult",
    "GatewayAdmissionDecision",
    "ToolGateway",
    "ToolTraceRecord",
    # M2B.2 normalization/context/provider contracts
    "AdmissionOutcome",
    "AttributionCoverageCounters",
    "CanonicalSymbolIdentity",
    "DegradedReason",
    "DegradedState",
    "FreshnessStatus",
    "InternalSymbolRecord",
    "NormalizedOutput",
    "NormalizedOutputKind",
    "SourceMetadata",
    "ToolExecutionEnvelope",
    "attribution_coverage_counters",
    "cache_freshness_metadata",
    "has_complete_market_attribution",
    "make_degraded_output",
    "make_evidence_fact_output",
    "make_system_record_output",
    "make_visualization_provenance_output",
    "CredentialOwner",
    "DataCategory",
    "LicensePosture",
    "ProviderAdapterDescriptor",
    "ProviderClass",
    "ProviderSelectionDecision",
    "ProviderSelectionPolicy",
    "RetainedDerivative",
    "ToolContextPack",
    "assemble_tool_context_pack",
    "reject_whole_pack_persistence",
    "validate_retained_derivative",
    "MutationReceipt",
    "MutationStatus",
    "disabled_mutation_receipt",
    "guard_symbol_mutation",
]
