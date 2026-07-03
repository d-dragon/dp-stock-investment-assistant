"""Route-filtered tool surface construction for M2B.1."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from ..routes import StockQueryRoute
from .descriptors import (
    ExposureStatus,
    LicenseMode,
    RiskClass,
    ToolCapabilityDescriptor,
    ToolPolicyDescriptor,
    canonical_descriptor_hash,
    get_baseline_tool_descriptors,
    validate_descriptor_inventory,
)
from .registry import ToolRegistry


@dataclass(frozen=True)
class RouteSurfaceRequest:
    """Inputs used to construct a one-turn model-visible tool surface."""

    route: StockQueryRoute
    locale: Optional[str] = None
    feature_flags: Mapping[str, bool] = field(default_factory=dict)
    available_context: Mapping[str, Any] = field(default_factory=dict)
    allowed_risk_classes: Sequence[RiskClass] = (RiskClass.READ_ONLY, RiskClass.BOUNDED_NON_MUTATING)
    registry_enabled_tools: Sequence[str] = field(default_factory=tuple)
    capability_descriptors: Mapping[str, ToolCapabilityDescriptor] = field(default_factory=dict)
    policy_descriptors: Mapping[str, ToolPolicyDescriptor] = field(default_factory=dict)


@dataclass(frozen=True)
class RouteFilteredToolSurface:
    """Model-visible tool surface plus internal filter evidence."""

    route: StockQueryRoute
    exposed_tools: Sequence[ToolCapabilityDescriptor]
    hidden_tools: Sequence[str]
    filter_reasons: Mapping[str, Sequence[str]]
    descriptor_versions: Mapping[str, Mapping[str, str]]
    surface_hash: str
    latency_ms: float = 0.0

    @property
    def exposed_tool_names(self) -> List[str]:
        """Return exposed tool names."""

        return [tool.name for tool in self.exposed_tools]

    def model_visible_descriptors(self) -> List[Dict[str, Any]]:
        """Return safe model-visible descriptors for exposed tools."""

        return [tool.model_visible_dict() for tool in self.exposed_tools]


class ToolSurfaceBuilder:
    """Build route-filtered tool surfaces from descriptors and registry state."""

    def __init__(
        self,
        *,
        capability_descriptors: Optional[Mapping[str, ToolCapabilityDescriptor]] = None,
        policy_descriptors: Optional[Mapping[str, ToolPolicyDescriptor]] = None,
        registry: Optional[ToolRegistry] = None,
        environment: str = "production",
    ) -> None:
        descriptors = get_baseline_tool_descriptors()
        self.capability_descriptors = dict(capability_descriptors or descriptors["capabilities"])
        self.policy_descriptors = dict(policy_descriptors or descriptors["policies"])
        self.registry = registry
        self.environment = environment

    def build(self, request: RouteSurfaceRequest) -> RouteFilteredToolSurface:
        """Build a filtered surface for one classified route."""

        start = time.perf_counter()
        capabilities = dict(request.capability_descriptors or self.capability_descriptors)
        policies = dict(request.policy_descriptors or self.policy_descriptors)
        validation = validate_descriptor_inventory(capabilities, policies)
        registry_enabled = set(request.registry_enabled_tools or self._registry_enabled_names())
        allowed_risk_classes = {risk.value if isinstance(risk, RiskClass) else str(risk) for risk in request.allowed_risk_classes}
        exposed: List[ToolCapabilityDescriptor] = []
        hidden: List[str] = []
        reasons: Dict[str, List[str]] = {}
        descriptor_versions: Dict[str, Dict[str, str]] = {}

        for tool_name, capability in sorted(capabilities.items()):
            policy = policies.get(tool_name)
            tool_reasons: List[str] = []

            if validation.has_code("descriptor_drift"):
                drifted = [issue.tool_name for issue in validation.issues if issue.code == "descriptor_drift"]
                if tool_name in drifted:
                    tool_reasons.append("descriptor_drift")
            if not validation.valid:
                tool_issue_codes = [
                    issue.code
                    for issue in validation.issues
                    if issue.tool_name in {tool_name, "<unknown>"}
                ]
                if tool_issue_codes:
                    tool_reasons.extend(sorted(set(tool_issue_codes)))
            if policy is None:
                tool_reasons.append("missing_policy_descriptor")
            else:
                if policy.exposure_status != ExposureStatus.MODEL_VISIBLE:
                    tool_reasons.append(f"exposure_status:{policy.exposure_status.value}")
                if policy.risk_class.value not in allowed_risk_classes:
                    tool_reasons.append("risk_blocked")
                if policy.license_mode in {LicenseMode.UNCLEAR, LicenseMode.PROHIBITED}:
                    tool_reasons.append("license_blocked")
                if self.environment not in policy.enabled_environments:
                    tool_reasons.append("environment_blocked")
                if request.route.value not in policy.allowed_routes:
                    tool_reasons.append("route_blocked")

            if not capability.enabled:
                tool_reasons.append("disabled")
            if not capability.model_visible:
                tool_reasons.append(capability.non_exposed_reason or "non_exposed")
            if request.route.value not in capability.route_coverage:
                tool_reasons.append("route_not_covered")
            if tool_name not in registry_enabled:
                tool_reasons.append("registry_disabled")
            if request.feature_flags.get(tool_name) is False or request.feature_flags.get(f"tool:{tool_name}") is False:
                tool_reasons.append("feature_flag_blocked")
            if tool_name in request.available_context.get("blocked_tools", ()):
                tool_reasons.append("context_blocked")

            if tool_reasons:
                hidden.append(tool_name)
                reasons[tool_name] = tuple(sorted(set(tool_reasons)))
                continue

            exposed.append(capability)
            descriptor_versions[tool_name] = {
                "capability_version": capability.descriptor_version,
                "capability_hash": capability.descriptor_hash,
                "policy_version": policy.descriptor_version if policy else "",
                "policy_hash": policy.descriptor_hash if policy else "",
            }

        surface_hash = self._surface_hash(request.route, exposed, descriptor_versions)
        latency_ms = (time.perf_counter() - start) * 1000
        return RouteFilteredToolSurface(
            route=request.route,
            exposed_tools=tuple(exposed),
            hidden_tools=tuple(hidden),
            filter_reasons={name: tuple(values) for name, values in reasons.items()},
            descriptor_versions=descriptor_versions,
            surface_hash=surface_hash,
            latency_ms=latency_ms,
        )

    def build_for_route(
        self,
        route: StockQueryRoute,
        *,
        locale: Optional[str] = None,
        feature_flags: Optional[Mapping[str, bool]] = None,
        available_context: Optional[Mapping[str, Any]] = None,
        allowed_risk_classes: Optional[Iterable[RiskClass]] = None,
    ) -> RouteFilteredToolSurface:
        """Convenience helper using the configured registry and descriptors."""

        return self.build(
            RouteSurfaceRequest(
                route=route,
                locale=locale,
                feature_flags=feature_flags or {},
                available_context=available_context or {},
                allowed_risk_classes=tuple(allowed_risk_classes or (RiskClass.READ_ONLY, RiskClass.BOUNDED_NON_MUTATING)),
                registry_enabled_tools=tuple(self._registry_enabled_names()),
                capability_descriptors=self.capability_descriptors,
                policy_descriptors=self.policy_descriptors,
            )
        )

    def _registry_enabled_names(self) -> Sequence[str]:
        if self.registry is None:
            return tuple(self.capability_descriptors)
        return tuple(tool.name for tool in self.registry.get_enabled_tools())

    @staticmethod
    def _surface_hash(
        route: StockQueryRoute,
        exposed: Sequence[ToolCapabilityDescriptor],
        descriptor_versions: Mapping[str, Mapping[str, str]],
    ) -> str:
        return canonical_descriptor_hash(
            {
                "route": route.value,
                "exposed_tools": [tool.name for tool in exposed],
                "descriptor_versions": {name: dict(values) for name, values in descriptor_versions.items()},
            }
        )

    def baseline_candidate_count(self) -> int:
        """Return unfiltered baseline descriptor count for comparison."""

        return len(self.capability_descriptors)

    def reduction_ratio(self, surface: RouteFilteredToolSurface) -> float:
        """Return model-visible candidate reduction ratio versus baseline inventory."""

        baseline = self.baseline_candidate_count()
        if baseline <= 0:
            return 0.0
        return (baseline - len(surface.exposed_tools)) / baseline
