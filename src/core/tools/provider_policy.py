"""Internal provider descriptor and selection policy contracts for M2B.2."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Mapping, Optional, Sequence

from .normalization import DegradedReason, FreshnessStatus, SourceMetadata


class ProviderClass(str, Enum):
    OFFICIAL = "official"
    LICENSED = "licensed"
    PUBLIC_WEB = "public_web"
    WRAPPER = "wrapper"
    INTERNATIONAL_FALLBACK = "international_fallback"
    INTERNAL_SYSTEM = "internal_system"
    VISUALIZATION = "visualization"


class DataCategory(str, Enum):
    SYMBOL_REFERENCE = "symbol_reference"
    QUOTE = "quote"
    HISTORY = "history"
    INDICATOR = "indicator"
    FUNDAMENTAL = "fundamental"
    STATEMENT = "statement"
    BREADTH = "breadth"
    FLOW = "flow"
    DISCLOSURE = "disclosure"
    CORPORATE_ACTION = "corporate_action"
    NEWS = "news"
    VISUALIZATION = "visualization"


class LicensePosture(str, Enum):
    REVIEWED = "reviewed"
    UNREVIEWED = "unreviewed"
    UNCLEAR = "unclear"
    PROHIBITED = "prohibited"
    NOT_APPLICABLE = "not_applicable"


class CredentialOwner(str, Enum):
    NONE = "none"
    APPLICATION = "application"
    USER = "user"
    MISSING = "missing"


class ProviderAdmissionOutcome(str, Enum):
    ALLOWED = "allowed"
    DEGRADED = "degraded"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ProviderAdapterDescriptor:
    """Internal source connector posture below model-visible tools."""

    provider_id: str
    provider_class: ProviderClass
    supported_markets: Sequence[str]
    supported_data_categories: Sequence[DataCategory]
    license_posture: LicensePosture
    credential_owner: CredentialOwner
    freshness_policy: Mapping[str, Any]
    parser_limits: Mapping[str, Any]
    source_attribution_requirements: Sequence[str]
    production_eligible: bool
    integrity_marker: str
    redistribution_posture: str = "reviewed"

    def validation_issues(self) -> Sequence[str]:
        issues = []
        if not self.provider_id:
            issues.append("missing_provider_id")
        if not self.supported_markets:
            issues.append("missing_supported_markets")
        if not self.supported_data_categories:
            issues.append("missing_supported_data_categories")
        if not self.integrity_marker:
            issues.append("missing_integrity_marker")
        if self.license_posture in {LicensePosture.UNREVIEWED, LicensePosture.UNCLEAR, LicensePosture.PROHIBITED}:
            issues.append("license_not_production_ready")
        if self.credential_owner == CredentialOwner.MISSING:
            issues.append("missing_credential_scope")
        if self.redistribution_posture not in {"reviewed", "not_applicable"}:
            issues.append("unclear_redistribution_posture")
        if not self.production_eligible:
            issues.append("not_production_eligible")
        return tuple(issues)

    @property
    def production_admissible(self) -> bool:
        return not self.validation_issues()

    def to_source_metadata(self, *, freshness_status: FreshnessStatus = FreshnessStatus.UNKNOWN) -> SourceMetadata:
        return SourceMetadata(
            provider_id=self.provider_id,
            provider_class=self.provider_class.value,
            license_posture=self.license_posture.value,
            freshness_status=freshness_status,
        )


@dataclass(frozen=True)
class ProviderSelectionDecision:
    """Deterministic provider-selection outcome."""

    selected_adapter: Optional[str]
    admission_outcome: ProviderAdmissionOutcome
    fallback_used: bool = False
    freshness_status: FreshnessStatus = FreshnessStatus.UNKNOWN
    license_status: str = "unknown"
    cache_status: str = "not_applicable"
    degraded_reason: Optional[str] = None
    warnings: Sequence[str] = field(default_factory=tuple)

    @property
    def allowed(self) -> bool:
        return self.admission_outcome == ProviderAdmissionOutcome.ALLOWED

    def to_metadata(self) -> Dict[str, Any]:
        return {
            "selected_adapter": self.selected_adapter,
            "admission_outcome": self.admission_outcome.value,
            "fallback_used": self.fallback_used,
            "freshness_status": self.freshness_status.value,
            "license_status": self.license_status,
            "cache_status": self.cache_status,
            "degraded_reason": self.degraded_reason,
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class ProviderSelectionPolicy:
    """Provider ordering and fail-closed selection rules."""

    tool_name: str
    route: str
    provider_order: Sequence[str]
    fallback_eligibility: Mapping[str, bool]
    market_session_rules: Mapping[str, Any]
    freshness_expectations: Mapping[str, Any]
    timeout_budget: float
    fail_closed_conditions: Sequence[str]
    degraded_state_mapping: Mapping[str, str]

    def select_provider(
        self,
        providers: Mapping[str, ProviderAdapterDescriptor],
        *,
        market: Optional[str] = None,
        data_category: Optional[DataCategory] = None,
        provider_health: Optional[Mapping[str, str]] = None,
        market_session_open: bool = True,
        freshness_status: FreshnessStatus = FreshnessStatus.CURRENT,
    ) -> ProviderSelectionDecision:
        """Select the first policy-admitted provider or return a degraded outcome."""

        provider_health = provider_health or {}
        warnings = []
        if not market_session_open:
            return self._blocked("market_closed", FreshnessStatus.NOT_APPLICABLE)
        for index, provider_id in enumerate(self.provider_order):
            descriptor = providers.get(provider_id)
            if descriptor is None:
                warnings.append(f"missing_provider:{provider_id}")
                continue
            issue = self._first_blocking_issue(descriptor, market=market, data_category=data_category)
            health = provider_health.get(provider_id, "healthy")
            if health in {"down", "unavailable", "failed"}:
                issue = "provider_down"
            if freshness_status == FreshnessStatus.STALE:
                issue = "stale"
            if issue is None:
                return ProviderSelectionDecision(
                    selected_adapter=provider_id,
                    admission_outcome=ProviderAdmissionOutcome.ALLOWED,
                    fallback_used=index > 0,
                    freshness_status=freshness_status,
                    license_status=descriptor.license_posture.value,
                    warnings=tuple(warnings),
                )
            warnings.append(f"{provider_id}:{issue}")
            if index == 0 and not self.fallback_eligibility.get(provider_id, False):
                return self._blocked(issue, freshness_status, warnings=warnings)
        reason = warnings[-1].split(":", 1)[-1] if warnings else "unsupported_provider"
        return self._blocked(reason, freshness_status, warnings=warnings)

    def _first_blocking_issue(
        self,
        descriptor: ProviderAdapterDescriptor,
        *,
        market: Optional[str],
        data_category: Optional[DataCategory],
    ) -> Optional[str]:
        if not descriptor.production_admissible:
            issues = descriptor.validation_issues()
            if "license_not_production_ready" in issues:
                return DegradedReason.BLOCKED_LICENSE.value
            if "missing_credential_scope" in issues:
                return "missing_credential_scope"
            if "unclear_redistribution_posture" in issues:
                return "unclear_redistribution_posture"
            return "not_production_eligible"
        if market and market not in descriptor.supported_markets:
            return "unsupported_market"
        if data_category and data_category not in descriptor.supported_data_categories:
            return "unsupported_data_category"
        return None

    def _blocked(
        self,
        reason: str,
        freshness_status: FreshnessStatus,
        *,
        warnings: Sequence[str] = (),
    ) -> ProviderSelectionDecision:
        mapped = self.degraded_state_mapping.get(reason, reason)
        return ProviderSelectionDecision(
            selected_adapter=None,
            admission_outcome=ProviderAdmissionOutcome.BLOCKED,
            freshness_status=freshness_status,
            license_status="blocked" if "license" in reason else "unknown",
            degraded_reason=mapped,
            warnings=tuple(warnings),
        )


def provider_metadata_for_envelope(decision: ProviderSelectionDecision) -> Dict[str, Any]:
    """Return envelope-ready provider decision metadata."""

    return decision.to_metadata()


def assert_provider_hidden_from_model_visible_surface(surface_payload: Any) -> bool:
    """Return true when provider adapter concepts are absent from model-visible payloads."""

    rendered = repr(surface_payload).lower()
    forbidden = ("provider_adapter", "credential_owner", "parser_limits", "license_posture")
    return not any(term in rendered for term in forbidden)
