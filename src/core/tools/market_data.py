"""Vietnam market-data tool family.

The module provides deterministic, provider-policy-aware builders for Vietnam
market evidence. It does not perform live provider fetches or production
provider enablement; callers may supply reviewed fixture/provider payloads or
receive explicit degraded states.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Mapping, Optional, Sequence

from .base import AgentTool
from .normalization import (
    CanonicalSymbolIdentity,
    DegradedReason,
    FreshnessStatus,
    NormalizedOutput,
    NormalizedOutputKind,
    SourceMetadata,
    attribution_coverage_counters,
    cache_freshness_metadata,
    make_degraded_output,
    make_evidence_fact_output,
    normalize_symbol_code,
    utc_now_iso,
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
from utils.cache import CacheBackend


class MarketDataOutputType(str, Enum):
    MARKET_FACT = "MarketFact"
    PRICE_HISTORY_SERIES = "PriceHistorySeries"
    FUNDAMENTAL_EVIDENCE = "FundamentalEvidence"
    BREADTH_AND_FLOW_EVIDENCE = "BreadthAndFlowEvidence"
    DISCLOSURE_CORPORATE_ACTION_EVIDENCE = "DisclosureCorporateActionEvidence"
    INDICATOR_EVIDENCE = "IndicatorEvidence"


@dataclass(frozen=True)
class MarketDataRequest:
    """Provider-neutral request for one Vietnam market-data category."""

    action: str
    symbol: Optional[str] = None
    exchange: Optional[str] = None
    currency: str = "VND"
    category: DataCategory = DataCategory.QUOTE
    indicator: Optional[str] = None

    @property
    def identity(self) -> Optional[CanonicalSymbolIdentity]:
        if not self.symbol:
            return None
        return CanonicalSymbolIdentity(
            symbol=self.symbol,
            exchange=self.exchange,
            currency=self.currency,
        )


@dataclass(frozen=True)
class MarketDataEvidence:
    """Small wrapper around a normalized output and provider decision."""

    output: NormalizedOutput
    provider_decision: ProviderSelectionDecision
    tool_family: str = "market_data"
    warnings: Sequence[str] = field(default_factory=tuple)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_family": self.tool_family,
            "provider_decision": self.provider_decision.to_metadata(),
            "normalized_output": self.output.to_dict(),
            "warnings": list(self.warnings),
        }


def default_vietnam_provider_descriptors() -> Dict[str, ProviderAdapterDescriptor]:
    """Return reviewed and gated provider descriptors for policy tests."""

    required = ("provider_id", "source_url_or_reference", "retrieved_at", "freshness_status")
    return {
        "hose_official": ProviderAdapterDescriptor(
            provider_id="hose_official",
            provider_class=ProviderClass.OFFICIAL,
            supported_markets=("VN",),
            supported_data_categories=(
                DataCategory.QUOTE,
                DataCategory.HISTORY,
                DataCategory.INDICATOR,
                DataCategory.BREADTH,
                DataCategory.FLOW,
                DataCategory.DISCLOSURE,
                DataCategory.CORPORATE_ACTION,
            ),
            license_posture=LicensePosture.REVIEWED,
            credential_owner=CredentialOwner.APPLICATION,
            freshness_policy={"mode": "market_session"},
            parser_limits={"fixture_only": True},
            source_attribution_requirements=required,
            production_eligible=True,
            integrity_marker="hose:vietnam-market",
        ),
        "hnx_official": ProviderAdapterDescriptor(
            provider_id="hnx_official",
            provider_class=ProviderClass.OFFICIAL,
            supported_markets=("VN",),
            supported_data_categories=(DataCategory.QUOTE, DataCategory.HISTORY, DataCategory.BREADTH),
            license_posture=LicensePosture.REVIEWED,
            credential_owner=CredentialOwner.APPLICATION,
            freshness_policy={"mode": "market_session"},
            parser_limits={"fixture_only": True},
            source_attribution_requirements=required,
            production_eligible=True,
            integrity_marker="hnx:vietnam-market",
        ),
        "vsdc": ProviderAdapterDescriptor(
            provider_id="vsdc",
            provider_class=ProviderClass.OFFICIAL,
            supported_markets=("VN",),
            supported_data_categories=(DataCategory.DISCLOSURE, DataCategory.CORPORATE_ACTION),
            license_posture=LicensePosture.REVIEWED,
            credential_owner=CredentialOwner.NONE,
            freshness_policy={"mode": "published_event"},
            parser_limits={"fixture_only": True},
            source_attribution_requirements=required,
            production_eligible=True,
            integrity_marker="vsdc:vietnam-market",
        ),
        "fiingroup": ProviderAdapterDescriptor(
            provider_id="fiingroup",
            provider_class=ProviderClass.LICENSED,
            supported_markets=("VN",),
            supported_data_categories=(DataCategory.FUNDAMENTAL, DataCategory.STATEMENT, DataCategory.FLOW),
            license_posture=LicensePosture.REVIEWED,
            credential_owner=CredentialOwner.APPLICATION,
            freshness_policy={"mode": "licensed_feed"},
            parser_limits={"fixture_only": True},
            source_attribution_requirements=required,
            production_eligible=True,
            integrity_marker="fiingroup:vietnam-market",
        ),
        "vietstock": ProviderAdapterDescriptor(
            provider_id="vietstock",
            provider_class=ProviderClass.PUBLIC_WEB,
            supported_markets=("VN",),
            supported_data_categories=(DataCategory.FUNDAMENTAL, DataCategory.DISCLOSURE),
            license_posture=LicensePosture.UNCLEAR,
            credential_owner=CredentialOwner.NONE,
            freshness_policy={"mode": "public_web_review_required"},
            parser_limits={"fixture_only": True},
            source_attribution_requirements=required,
            production_eligible=False,
            integrity_marker="vietstock:vietnam-market",
            redistribution_posture="unclear",
        ),
        "cafef": ProviderAdapterDescriptor(
            provider_id="cafef",
            provider_class=ProviderClass.PUBLIC_WEB,
            supported_markets=("VN",),
            supported_data_categories=(DataCategory.FUNDAMENTAL, DataCategory.NEWS),
            license_posture=LicensePosture.UNCLEAR,
            credential_owner=CredentialOwner.NONE,
            freshness_policy={"mode": "public_web_review_required"},
            parser_limits={"fixture_only": True},
            source_attribution_requirements=required,
            production_eligible=False,
            integrity_marker="cafef:vietnam-market",
            redistribution_posture="unclear",
        ),
        "vnstock": ProviderAdapterDescriptor(
            provider_id="vnstock",
            provider_class=ProviderClass.WRAPPER,
            supported_markets=("VN",),
            supported_data_categories=(DataCategory.QUOTE, DataCategory.HISTORY, DataCategory.FUNDAMENTAL),
            license_posture=LicensePosture.UNCLEAR,
            credential_owner=CredentialOwner.NONE,
            freshness_policy={"mode": "wrapper_review_required"},
            parser_limits={"fixture_only": True},
            source_attribution_requirements=required,
            production_eligible=False,
            integrity_marker="vnstock:vietnam-market",
            redistribution_posture="unclear",
        ),
        "yahoo_fallback": ProviderAdapterDescriptor(
            provider_id="yahoo_fallback",
            provider_class=ProviderClass.INTERNATIONAL_FALLBACK,
            supported_markets=("US", "VN"),
            supported_data_categories=(DataCategory.QUOTE, DataCategory.HISTORY),
            license_posture=LicensePosture.REVIEWED,
            credential_owner=CredentialOwner.NONE,
            freshness_policy={"mode": "best_effort_fallback"},
            parser_limits={"fixture_only": True},
            source_attribution_requirements=required,
            production_eligible=True,
            integrity_marker="yahoo:vietnam-market",
        ),
        "tradingview": ProviderAdapterDescriptor(
            provider_id="tradingview",
            provider_class=ProviderClass.VISUALIZATION,
            supported_markets=("VN", "US", "GLOBAL"),
            supported_data_categories=(DataCategory.VISUALIZATION,),
            license_posture=LicensePosture.NOT_APPLICABLE,
            credential_owner=CredentialOwner.NONE,
            freshness_policy={"mode": "visualization_only"},
            parser_limits={"no_canonical_evidence": True},
            source_attribution_requirements=("provider_id", "source_url_or_reference"),
            production_eligible=True,
            integrity_marker="tradingview:visualization",
            redistribution_posture="not_applicable",
        ),
    }


def vietnam_provider_policy(category: DataCategory, *, route: str = "price_check") -> ProviderSelectionPolicy:
    """Build a Vietnam-first provider policy for one market-data category."""

    if category in {DataCategory.FUNDAMENTAL, DataCategory.STATEMENT}:
        order = ("fiingroup", "vietstock", "cafef", "vnstock", "yahoo_fallback")
    elif category in {DataCategory.DISCLOSURE, DataCategory.CORPORATE_ACTION}:
        order = ("vsdc", "hose_official", "hnx_official", "vietstock")
    elif category in {DataCategory.BREADTH, DataCategory.FLOW}:
        order = ("hose_official", "hnx_official", "fiingroup", "yahoo_fallback")
    else:
        order = ("hose_official", "hnx_official", "vnstock", "yahoo_fallback")
    return ProviderSelectionPolicy(
        tool_name="market_data",
        route=route,
        provider_order=order,
        fallback_eligibility={provider_id: True for provider_id in order[:-1]} | {order[-1]: False},
        market_session_rules={"VN": "weekday_market_session"},
        freshness_expectations={category.value: "source_timestamp_required"},
        timeout_budget=2.5,
        fail_closed_conditions=("blocked_license", "missing_credential_scope", "missing_source"),
        degraded_state_mapping={
            "provider_down": DegradedReason.PROVIDER_DOWN.value,
            "blocked_license": DegradedReason.BLOCKED_LICENSE.value,
            "stale": DegradedReason.STALE_RECORD.value,
            "unsupported_data_category": DegradedReason.UNSUPPORTED_PROVIDER.value,
        },
    )


def select_vietnam_provider(
    *,
    category: DataCategory,
    market: str = "VN",
    provider_health: Optional[Mapping[str, str]] = None,
    freshness_status: FreshnessStatus = FreshnessStatus.CURRENT,
) -> ProviderSelectionDecision:
    """Select an admitted provider using Vietnam-first ordering."""

    return vietnam_provider_policy(category).select_provider(
        default_vietnam_provider_descriptors(),
        market=market,
        data_category=category,
        provider_health=provider_health,
        freshness_status=freshness_status,
    )


def market_source_metadata(
    *,
    provider_id: str,
    provider_class: str,
    source_reference: str,
    identity: Optional[CanonicalSymbolIdentity],
    source_timestamp: Optional[str] = None,
    published_at: Optional[str] = None,
    effective_at: Optional[str] = None,
    freshness_status: FreshnessStatus = FreshnessStatus.CURRENT,
    license_posture: str = "reviewed",
    warnings: Sequence[str] = (),
) -> SourceMetadata:
    """Build source metadata with exchange/currency copied from canonical identity."""

    return SourceMetadata(
        provider_id=provider_id,
        provider_class=provider_class,
        source_url_or_reference=source_reference,
        retrieved_at=utc_now_iso(),
        source_timestamp=source_timestamp,
        published_at=published_at,
        effective_at=effective_at,
        symbol_identity=identity,
        exchange=identity.exchange if identity else None,
        currency=identity.currency if identity else None,
        license_posture=license_posture,
        freshness_status=freshness_status,
        warnings=tuple(warnings),
    )


def market_evidence_output(
    *,
    output_type: MarketDataOutputType,
    identity: Optional[CanonicalSymbolIdentity],
    content: Mapping[str, Any],
    provider_id: str = "hose_official",
    provider_class: str = "official",
    source_reference: str = "fixture:source",
    source_timestamp: Optional[str] = "2026-07-07T00:00:00Z",
    freshness_status: FreshnessStatus = FreshnessStatus.CURRENT,
    warnings: Sequence[str] = (),
) -> NormalizedOutput:
    """Build a normalized market evidence output or fail closed when attribution is missing."""

    if identity is None:
        return make_degraded_output(
            code=DegradedReason.AMBIGUOUS_SYMBOL.value,
            safe_message="A canonical symbol identity is required before market data can be used.",
            reason=DegradedReason.AMBIGUOUS_SYMBOL,
            tool_name="market_data",
            provider_id=provider_id,
        )
    source = market_source_metadata(
        provider_id=provider_id,
        provider_class=provider_class,
        source_reference=source_reference,
        identity=identity,
        source_timestamp=source_timestamp,
        freshness_status=freshness_status,
        warnings=warnings,
    )
    freshness = cache_freshness_metadata(
        provider_id=provider_id,
        retrieved_at=source.retrieved_at or utc_now_iso(),
        source_timestamp=source_timestamp,
        freshness_status=freshness_status,
        ttl_seconds=60,
        warnings=warnings,
    )
    return make_evidence_fact_output(
        output_type=output_type.value,
        content=content,
        source_metadata=source,
        freshness_metadata=freshness,
        warnings=warnings,
    )


def no_market_source_output(*, category: DataCategory, reason: DegradedReason | str) -> NormalizedOutput:
    """Return a machine-detectable no-source degraded state."""

    code = reason.value if isinstance(reason, DegradedReason) else str(reason)
    return make_degraded_output(
        code=code,
        safe_message=f"No admitted source is available for {category.value}.",
        reason=reason,
        route="market_data",
        tool_name="market_data",
    )


def tradingview_values_are_canonical(output: NormalizedOutput) -> bool:
    """Return true only if a non-visualization output claims TradingView evidence."""

    provider_id = output.source_metadata.provider_id if output.source_metadata else ""
    return provider_id == "tradingview" and output.kind != NormalizedOutputKind.VISUALIZATION_PROVENANCE


class VietnamMarketDataTool(AgentTool):
    """Deterministic market-data tool family for Vietnam-market evidence."""

    name: str = "market_data"
    description: str = (
        "Vietnam market-data evidence for quotes, history, fundamentals, breadth, "
        "flow, disclosures, corporate actions, and indicators with source attribution."
    )

    def __init__(
        self,
        cache: Optional[CacheBackend] = None,
        cache_ttl_seconds: int = 60,
        enable_cache: bool = True,
        logger: Optional[logging.Logger] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            cache=cache,
            cache_ttl_seconds=cache_ttl_seconds,
            enable_cache=enable_cache,
            logger=logger,
            **kwargs,
        )

    def _execute(self, **kwargs: Any) -> Dict[str, Any]:
        action = str(kwargs.get("action") or "quote").lower()
        category = _category_for_action(action)
        symbol = kwargs.get("symbol")
        exchange = kwargs.get("exchange") or _exchange_from_symbol(symbol)
        identity = CanonicalSymbolIdentity(symbol=symbol, exchange=exchange, currency="VND") if symbol else None
        provider_health = kwargs.get("provider_health") if isinstance(kwargs.get("provider_health"), Mapping) else None
        freshness_value = kwargs.get("freshness_status", FreshnessStatus.CURRENT.value)
        if isinstance(freshness_value, FreshnessStatus):
            freshness = freshness_value
        else:
            freshness = FreshnessStatus(str(freshness_value))
        decision = select_vietnam_provider(
            category=category,
            provider_health=provider_health,
            freshness_status=freshness,
        )
        if not decision.allowed:
            output = no_market_source_output(
                category=category,
                reason=decision.degraded_reason or DegradedReason.NO_SOURCE_AVAILABLE.value,
            )
            return MarketDataEvidence(output=output, provider_decision=decision, warnings=decision.warnings).to_dict()
        payload = _payload_for_action(action, symbol=symbol, indicator=kwargs.get("indicator"))
        output = market_evidence_output(
            output_type=_output_type_for_action(action),
            identity=identity,
            content=payload,
            provider_id=decision.selected_adapter or "unknown",
            provider_class=default_vietnam_provider_descriptors()[decision.selected_adapter].provider_class.value
            if decision.selected_adapter
            else "unknown",
            source_reference=f"fixture:{decision.selected_adapter}:{normalize_symbol_code(symbol or '')}",
            freshness_status=decision.freshness_status,
            warnings=decision.warnings,
        )
        return MarketDataEvidence(output=output, provider_decision=decision, warnings=decision.warnings).to_dict()

    def attribution_counters(self, outputs: Sequence[NormalizedOutput]) -> Dict[str, int]:
        """Expose attribution counter calculation for tests and review evidence."""

        return attribution_coverage_counters(outputs).to_dict()


def _category_for_action(action: str) -> DataCategory:
    if action in {"quote", "price"}:
        return DataCategory.QUOTE
    if action in {"history", "ohlcv"}:
        return DataCategory.HISTORY
    if action == "indicator":
        return DataCategory.INDICATOR
    if action in {"fundamental", "fundamentals"}:
        return DataCategory.FUNDAMENTAL
    if action == "statement":
        return DataCategory.STATEMENT
    if action == "breadth":
        return DataCategory.BREADTH
    if action == "flow":
        return DataCategory.FLOW
    if action == "disclosure":
        return DataCategory.DISCLOSURE
    if action in {"corporate_action", "corporate-action"}:
        return DataCategory.CORPORATE_ACTION
    return DataCategory.QUOTE


def _output_type_for_action(action: str) -> MarketDataOutputType:
    if action in {"history", "ohlcv"}:
        return MarketDataOutputType.PRICE_HISTORY_SERIES
    if action == "indicator":
        return MarketDataOutputType.INDICATOR_EVIDENCE
    if action in {"fundamental", "fundamentals", "statement"}:
        return MarketDataOutputType.FUNDAMENTAL_EVIDENCE
    if action in {"breadth", "flow"}:
        return MarketDataOutputType.BREADTH_AND_FLOW_EVIDENCE
    if action in {"disclosure", "corporate_action", "corporate-action"}:
        return MarketDataOutputType.DISCLOSURE_CORPORATE_ACTION_EVIDENCE
    return MarketDataOutputType.MARKET_FACT


def _payload_for_action(action: str, *, symbol: Optional[str], indicator: Optional[str]) -> Dict[str, Any]:
    normalized_symbol = normalize_symbol_code(symbol or "")
    if action in {"history", "ohlcv"}:
        return {"symbol": normalized_symbol, "rows": [{"close": 100000, "volume": 1000}], "unit": "VND"}
    if action == "indicator":
        return {"symbol": normalized_symbol, "indicator": indicator or "sma_20", "value": 100000, "lineage": "price_history"}
    if action in {"fundamental", "fundamentals"}:
        return {"symbol": normalized_symbol, "period": "2026Q1", "metric": "roe", "value": 0.18}
    if action == "statement":
        return {"symbol": normalized_symbol, "period": "2026Q1", "statement": "income", "fields": {"revenue": 1}}
    if action == "breadth":
        return {"market": "VN", "time_window": "session", "advancers": 100, "decliners": 80}
    if action == "flow":
        return {"market": "VN", "time_window": "session", "foreign_net_buy": 1000000}
    if action == "disclosure":
        return {"symbol": normalized_symbol, "event_type": "disclosure", "published_at": "2026-07-07T00:00:00Z"}
    if action in {"corporate_action", "corporate-action"}:
        return {"symbol": normalized_symbol, "event_type": "dividend", "effective_at": "2026-07-31T00:00:00Z"}
    return {"symbol": normalized_symbol, "price": 100000, "unit": "VND"}


def _exchange_from_symbol(symbol: Optional[str]) -> Optional[str]:
    if not symbol:
        return None
    if ":" in symbol:
        return symbol.split(":", 1)[0].upper()
    if normalize_symbol_code(symbol) in {"SHS"}:
        return "HNX"
    if normalize_symbol_code(symbol) in {"BSR"}:
        return "UPCOM"
    return "HOSE"
