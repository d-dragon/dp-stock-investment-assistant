"""M2B.1 tool descriptor inventory and validation helpers."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field, replace
from enum import Enum
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from ..routes import StockQueryRoute


DESCRIPTOR_VERSION = "m2b1.1"


class BaselineInventoryState(str, Enum):
    """Current implementation posture for a baseline tool."""

    ACTIVE = "active"
    SCAFFOLD = "scaffold"
    PLACEHOLDER = "placeholder"


class ExposureStatus(str, Enum):
    """Internal exposure state used by descriptors and policy."""

    MODEL_VISIBLE = "model_visible"
    HIDDEN = "hidden"
    DISABLED = "disabled"
    NON_EXPOSED = "non_exposed"


class LicenseMode(str, Enum):
    """M2B.1 license posture categories."""

    FIRST_PARTY_REVIEWED = "first_party_reviewed"
    NOT_APPLICABLE = "not_applicable"
    UNCLEAR = "unclear"
    PROHIBITED = "prohibited"


class RiskClass(str, Enum):
    """M2B.1 admitted risk classes."""

    READ_ONLY = "read_only"
    BOUNDED_NON_MUTATING = "bounded_non_mutating"
    MUTATING = "mutating"
    HIGH_RISK = "high_risk"


class MutationPolicy(str, Enum):
    """Tool mutation posture."""

    NONE = "none"
    NON_MUTATING = "non_mutating"
    MUTATING = "mutating"


@dataclass(frozen=True)
class BaselineToolInventoryItem:
    """Named M2B.1 baseline inventory entry."""

    tool_name: str
    tool_class: str
    implementation_status: BaselineInventoryState
    registry_status: str
    model_exposure_default: ExposureStatus
    descriptor_status: str = "complete"


@dataclass(frozen=True)
class ToolCapabilityDescriptor:
    """Model-safe capability descriptor for one tool."""

    name: str
    display_name: str
    purpose: str
    input_schema: Mapping[str, Any]
    route_coverage: Sequence[str]
    output_kind: str
    locale_coverage: Sequence[str]
    examples: Sequence[Mapping[str, Any]] = field(default_factory=tuple)
    enabled: bool = True
    model_visible: bool = True
    non_exposed_reason: Optional[str] = None
    descriptor_version: str = DESCRIPTOR_VERSION
    descriptor_hash: str = ""

    def with_hash(self) -> "ToolCapabilityDescriptor":
        """Return a copy with a deterministic descriptor hash."""

        return replace(self, descriptor_hash=canonical_descriptor_hash(self))

    def model_visible_dict(self) -> Dict[str, Any]:
        """Return only the fields permitted for model-visible exposure."""

        return {
            "name": self.name,
            "display_name": self.display_name,
            "purpose": self.purpose,
            "input_schema": dict(self.input_schema),
            "route_coverage": list(self.route_coverage),
            "output_kind": self.output_kind,
            "locale_coverage": list(self.locale_coverage),
            "examples": [dict(example) for example in self.examples],
            "enabled": self.enabled,
            "model_visible": self.model_visible,
            "non_exposed_reason": self.non_exposed_reason,
            "descriptor_version": self.descriptor_version,
            "descriptor_hash": self.descriptor_hash,
        }


@dataclass(frozen=True)
class ToolPolicyDescriptor:
    """Internal policy descriptor for gateway admission."""

    tool_name: str
    risk_class: RiskClass
    license_mode: LicenseMode
    freshness_policy: Mapping[str, Any]
    cache_policy: Mapping[str, Any]
    timeout_budget_ms: int
    credential_owner: str
    mutation_policy: MutationPolicy
    required_metadata: Sequence[str]
    enabled_environments: Sequence[str]
    exposure_status: ExposureStatus
    allowed_routes: Sequence[str]
    descriptor_version: str = DESCRIPTOR_VERSION
    descriptor_hash: str = ""

    def with_hash(self) -> "ToolPolicyDescriptor":
        """Return a copy with a deterministic descriptor hash."""

        return replace(self, descriptor_hash=canonical_descriptor_hash(self))


@dataclass(frozen=True)
class DescriptorValidationIssue:
    """Machine-detectable descriptor validation issue."""

    code: str
    tool_name: str
    message: str


@dataclass(frozen=True)
class DescriptorValidationResult:
    """Aggregate descriptor validation result."""

    valid: bool
    issues: Sequence[DescriptorValidationIssue] = field(default_factory=tuple)

    def has_code(self, code: str) -> bool:
        """Return true when any issue has the supplied code."""

        return any(issue.code == code for issue in self.issues)


FORBIDDEN_MODEL_VISIBLE_FIELDS = {
    "credential",
    "credentials",
    "credential_owner",
    "provider_fallback_rules",
    "parser_limits",
    "internal_license_policy",
    "timeout_budget_ms",
    "provider_details",
    "provider_adapter",
    "raw_gateway_trace",
}


def _normalize(value: Any) -> Any:
    """Normalize descriptor content into deterministic JSON-safe values."""

    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(k): _normalize(v) for k, v in sorted(value.items())}
    if isinstance(value, (list, tuple, set)):
        return [_normalize(item) for item in value]
    return value


def canonical_descriptor_hash(descriptor: Any) -> str:
    """Hash canonical descriptor content while excluding generated hash fields."""

    payload = asdict(descriptor) if hasattr(descriptor, "__dataclass_fields__") else dict(descriptor)
    payload.pop("descriptor_hash", None)
    canonical = json.dumps(_normalize(payload), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def expected_descriptor_hash(descriptor: Any) -> str:
    """Return the expected hash for the supplied descriptor content."""

    return canonical_descriptor_hash(descriptor)


def get_baseline_tool_inventory() -> Sequence[BaselineToolInventoryItem]:
    """Return the named M2B.1 baseline inventory."""

    return (
        BaselineToolInventoryItem(
            tool_name="stock_symbol",
            tool_class="StockSymbolTool",
            implementation_status=BaselineInventoryState.ACTIVE,
            registry_status="registered",
            model_exposure_default=ExposureStatus.MODEL_VISIBLE,
        ),
        BaselineToolInventoryItem(
            tool_name="tradingview",
            tool_class="TradingViewTool",
            implementation_status=BaselineInventoryState.PLACEHOLDER,
            registry_status="unregistered",
            model_exposure_default=ExposureStatus.NON_EXPOSED,
        ),
        BaselineToolInventoryItem(
            tool_name="reporting",
            tool_class="ReportingTool",
            implementation_status=BaselineInventoryState.SCAFFOLD,
            registry_status="registered",
            model_exposure_default=ExposureStatus.NON_EXPOSED,
        ),
    )


def _baseline_capabilities() -> Sequence[ToolCapabilityDescriptor]:
    """Build unhashed baseline capability descriptors."""

    return (
        ToolCapabilityDescriptor(
            name="stock_symbol",
            display_name="Stock symbol lookup",
            purpose="Retrieve stock symbol metadata and current price information for admitted lookup routes.",
            input_schema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["get_info", "search"]},
                    "symbol": {"type": "string"},
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 25},
                },
                "required_any": [["symbol"], ["query"]],
            },
            route_coverage=(StockQueryRoute.PRICE_CHECK.value, StockQueryRoute.FUNDAMENTALS.value),
            output_kind="market_data_lookup",
            locale_coverage=("any",),
            examples=({"action": "get_info", "symbol": "AAPL"},),
        ),
        ToolCapabilityDescriptor(
            name="tradingview",
            display_name="TradingView visualization",
            purpose="Reserved visualization capability for a later phase; not exposed while placeholder code remains.",
            input_schema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["get_chart_url", "get_widget", "get_analysis"]},
                    "symbol": {"type": "string"},
                },
                "required": ["symbol"],
            },
            route_coverage=(StockQueryRoute.TECHNICAL_ANALYSIS.value,),
            output_kind="visualization_provenance",
            locale_coverage=("any",),
            enabled=False,
            model_visible=False,
            non_exposed_reason="placeholder_disabled_m2b1",
        ),
        ToolCapabilityDescriptor(
            name="reporting",
            display_name="Report scaffold",
            purpose="Reserved non-mutating report scaffold; not exposed as a substitute for unsupported routes in M2B.1.",
            input_schema={
                "type": "object",
                "properties": {
                    "report_type": {"type": "string", "enum": ["symbol", "portfolio", "market"]},
                    "symbol": {"type": "string"},
                    "portfolio_id": {"type": "string"},
                },
            },
            route_coverage=(StockQueryRoute.MARKET_WATCH.value, StockQueryRoute.PORTFOLIO.value),
            output_kind="report_scaffold",
            locale_coverage=("any",),
            enabled=True,
            model_visible=False,
            non_exposed_reason="scaffold_not_admitted_m2b1",
        ),
    )


def _baseline_policies() -> Sequence[ToolPolicyDescriptor]:
    """Build unhashed baseline policy descriptors."""

    return (
        ToolPolicyDescriptor(
            tool_name="stock_symbol",
            risk_class=RiskClass.READ_ONLY,
            license_mode=LicenseMode.FIRST_PARTY_REVIEWED,
            freshness_policy={"mode": "provider_or_repository", "stale_after_seconds": 900},
            cache_policy={"enabled": True, "ttl_seconds": 60},
            timeout_budget_ms=2500,
            credential_owner="tool_dependency",
            mutation_policy=MutationPolicy.NONE,
            required_metadata=("route", "descriptor_hash", "admission_outcome"),
            enabled_environments=("development", "test", "production"),
            exposure_status=ExposureStatus.MODEL_VISIBLE,
            allowed_routes=(StockQueryRoute.PRICE_CHECK.value, StockQueryRoute.FUNDAMENTALS.value),
        ),
        ToolPolicyDescriptor(
            tool_name="tradingview",
            risk_class=RiskClass.READ_ONLY,
            license_mode=LicenseMode.UNCLEAR,
            freshness_policy={"mode": "not_applicable"},
            cache_policy={"enabled": False},
            timeout_budget_ms=0,
            credential_owner="none",
            mutation_policy=MutationPolicy.NONE,
            required_metadata=("route", "descriptor_hash", "admission_outcome"),
            enabled_environments=("none",),
            exposure_status=ExposureStatus.NON_EXPOSED,
            allowed_routes=(),
        ),
        ToolPolicyDescriptor(
            tool_name="reporting",
            risk_class=RiskClass.BOUNDED_NON_MUTATING,
            license_mode=LicenseMode.NOT_APPLICABLE,
            freshness_policy={"mode": "not_applicable"},
            cache_policy={"enabled": True, "ttl_seconds": 600},
            timeout_budget_ms=1000,
            credential_owner="none",
            mutation_policy=MutationPolicy.NON_MUTATING,
            required_metadata=("route", "descriptor_hash", "admission_outcome"),
            enabled_environments=("development", "test", "production"),
            exposure_status=ExposureStatus.NON_EXPOSED,
            allowed_routes=(),
        ),
    )


def get_baseline_tool_descriptors() -> Dict[str, Dict[str, Any]]:
    """Return baseline capability and policy descriptors keyed by tool name."""

    capabilities = {descriptor.name: descriptor.with_hash() for descriptor in _baseline_capabilities()}
    policies = {descriptor.tool_name: descriptor.with_hash() for descriptor in _baseline_policies()}
    return {"capabilities": capabilities, "policies": policies}


def get_capability_descriptor(tool_name: str) -> Optional[ToolCapabilityDescriptor]:
    """Look up a baseline capability descriptor by current tool name."""

    return get_baseline_tool_descriptors()["capabilities"].get(tool_name)


def get_policy_descriptor(tool_name: str) -> Optional[ToolPolicyDescriptor]:
    """Look up a baseline policy descriptor by current tool name."""

    return get_baseline_tool_descriptors()["policies"].get(tool_name)


def _append_issue(
    issues: List[DescriptorValidationIssue],
    code: str,
    tool_name: str,
    message: str,
) -> None:
    issues.append(DescriptorValidationIssue(code=code, tool_name=tool_name, message=message))


def _validate_capability(
    capability: ToolCapabilityDescriptor,
    issues: List[DescriptorValidationIssue],
) -> None:
    if not capability.name:
        _append_issue(issues, "malformed_descriptor", "<unknown>", "Capability descriptor name is required")
    if not capability.descriptor_hash:
        _append_issue(issues, "missing_integrity_marker", capability.name, "Capability descriptor hash is required")
    elif capability.descriptor_hash != expected_descriptor_hash(capability):
        _append_issue(issues, "descriptor_drift", capability.name, "Capability descriptor hash does not match content")
    if not capability.route_coverage:
        _append_issue(issues, "malformed_descriptor", capability.name, "Capability route coverage is required")
    for route in capability.route_coverage:
        try:
            StockQueryRoute(route)
        except ValueError:
            _append_issue(issues, "unknown_route", capability.name, f"Unknown route coverage: {route}")
    if not capability.model_visible and not capability.non_exposed_reason:
        _append_issue(issues, "malformed_descriptor", capability.name, "Non-visible capability requires a reason")
    visible_keys = set(capability.model_visible_dict())
    leaked = visible_keys.intersection(FORBIDDEN_MODEL_VISIBLE_FIELDS)
    if leaked:
        _append_issue(issues, "forbidden_model_visible_field", capability.name, f"Forbidden fields: {sorted(leaked)}")


def _validate_policy(
    policy: ToolPolicyDescriptor,
    capability: Optional[ToolCapabilityDescriptor],
    issues: List[DescriptorValidationIssue],
) -> None:
    if not policy.tool_name:
        _append_issue(issues, "malformed_descriptor", "<unknown>", "Policy tool_name is required")
    if not policy.descriptor_hash:
        _append_issue(issues, "missing_integrity_marker", policy.tool_name, "Policy descriptor hash is required")
    elif policy.descriptor_hash != expected_descriptor_hash(policy):
        _append_issue(issues, "descriptor_drift", policy.tool_name, "Policy descriptor hash does not match content")
    if policy.timeout_budget_ms < 0:
        _append_issue(issues, "malformed_descriptor", policy.tool_name, "Timeout budget cannot be negative")
    if policy.mutation_policy == MutationPolicy.MUTATING:
        _append_issue(issues, "unsupported_mutation_policy", policy.tool_name, "M2B.1 does not admit mutating tools")
    for route in policy.allowed_routes:
        try:
            StockQueryRoute(route)
        except ValueError:
            _append_issue(issues, "unknown_route", policy.tool_name, f"Unknown allowed route: {route}")
    if capability is None:
        _append_issue(issues, "missing_capability_descriptor", policy.tool_name, "Policy has no matching capability")
        return
    if policy.descriptor_version != capability.descriptor_version:
        _append_issue(issues, "policy_capability_mismatch", policy.tool_name, "Descriptor versions differ")
    if set(policy.allowed_routes) - set(capability.route_coverage):
        _append_issue(issues, "policy_capability_mismatch", policy.tool_name, "Policy allows routes outside capability coverage")
    if policy.exposure_status == ExposureStatus.MODEL_VISIBLE and not capability.model_visible:
        _append_issue(issues, "policy_capability_mismatch", policy.tool_name, "Policy exposes a non-visible capability")


def validate_descriptor_inventory(
    capability_descriptors: Optional[Mapping[str, ToolCapabilityDescriptor]] = None,
    policy_descriptors: Optional[Mapping[str, ToolPolicyDescriptor]] = None,
    required_tool_names: Optional[Iterable[str]] = None,
) -> DescriptorValidationResult:
    """Validate descriptor completeness, integrity, and capability-policy alignment."""

    baseline = get_baseline_tool_descriptors()
    capabilities = dict(capability_descriptors or baseline["capabilities"])
    policies = dict(policy_descriptors or baseline["policies"])
    required_names = set(required_tool_names or [item.tool_name for item in get_baseline_tool_inventory()])
    issues: List[DescriptorValidationIssue] = []

    duplicate_names = [name for name in capabilities if list(capabilities).count(name) > 1]
    for name in duplicate_names:
        _append_issue(issues, "duplicate_tool_name", name, "Duplicate capability descriptor name")

    for tool_name in sorted(required_names):
        capability = capabilities.get(tool_name)
        policy = policies.get(tool_name)
        if capability is None:
            _append_issue(issues, "missing_capability_descriptor", tool_name, "Missing capability descriptor")
        if policy is None:
            _append_issue(issues, "missing_policy_descriptor", tool_name, "Missing policy descriptor")
        if capability is not None:
            _validate_capability(capability, issues)
        if policy is not None:
            _validate_policy(policy, capability, issues)

    for tool_name, capability in capabilities.items():
        if tool_name not in required_names:
            _validate_capability(capability, issues)
        if capability.name != tool_name:
            _append_issue(issues, "duplicate_tool_name", tool_name, "Capability key does not match descriptor name")

    for tool_name, policy in policies.items():
        if tool_name not in required_names:
            _validate_policy(policy, capabilities.get(tool_name), issues)

    return DescriptorValidationResult(valid=not issues, issues=tuple(issues))
