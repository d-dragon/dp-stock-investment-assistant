"""Thin in-process tool gateway for M2B.1 admission and tracing."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping, Optional, Sequence

from ..routes import StockQueryRoute
from .base import AgentTool
from .descriptors import (
    ExposureStatus,
    LicenseMode,
    RiskClass,
    ToolCapabilityDescriptor,
    ToolPolicyDescriptor,
    expected_descriptor_hash,
    get_baseline_tool_descriptors,
)
from .registry import ToolRegistry
from .normalization import (
    AdmissionOutcome,
    NormalizedOutput,
    NormalizedOutputKind,
    ToolExecutionEnvelope,
    classify_normalized_output,
    make_degraded_output,
)
from .surface import RouteFilteredToolSurface


NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True)
class ToolTraceRecord:
    """Internal audit trace for one tool exposure or admission event."""

    route: str
    exposed_tools: Sequence[str]
    selected_tool: str
    selected_adapter: str
    descriptor_version: str
    descriptor_hash: str
    admission_outcome: str
    cache_status: str
    freshness: str
    latency_ms: float
    warning: Optional[str] = None
    degraded_state_reason: Optional[str] = None

    def sanitized_dict(self) -> Dict[str, Any]:
        """Return a secret-free trace dictionary."""

        return sanitize_trace_payload(asdict(self))


@dataclass(frozen=True)
class GatewayAdmissionDecision:
    """Execution-time admission decision for a selected tool."""

    route: str
    tool_name: str
    arguments_status: str
    route_match: bool
    risk_status: str
    license_status: str
    freshness_status: str
    provider_state: str
    descriptor_integrity: str
    timeout_budget_ms: Optional[int]
    outcome: str
    degraded_reason: Optional[str]
    machine_code: str
    safe_message: str
    execute_underlying_tool: bool
    trace_record: ToolTraceRecord


@dataclass(frozen=True)
class DegradedToolResult:
    """Stable non-success result for blocked or degraded tool calls."""

    status: str
    machine_code: str
    safe_message: str
    execute_underlying_tool: bool = False
    trace_record: ToolTraceRecord = field(default=None)  # type: ignore[assignment]

    def to_dict(self) -> Dict[str, Any]:
        """Return a safe public-friendly degraded result."""

        return {
            "status": self.status,
            "machine_code": self.machine_code,
            "message": self.safe_message,
            "execute_underlying_tool": self.execute_underlying_tool,
        }


SENSITIVE_KEY_FRAGMENTS = (
    "secret",
    "credential",
    "password",
    "token",
    "api_key",
    "raw_provider",
    "raw_payload",
    "raw_html",
    "raw_pdf",
    "parser_limit",
)


def sanitize_trace_payload(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Remove sensitive keys from internal trace payloads."""

    sanitized: Dict[str, Any] = {}
    for key, value in payload.items():
        lowered = key.lower()
        if any(fragment in lowered for fragment in SENSITIVE_KEY_FRAGMENTS):
            continue
        if isinstance(value, Mapping):
            sanitized[key] = sanitize_trace_payload(value)
        elif isinstance(value, (list, tuple)):
            sanitized[key] = [
                sanitize_trace_payload(item) if isinstance(item, Mapping) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    return sanitized


def safe_public_metadata(decision: GatewayAdmissionDecision) -> Dict[str, Any]:
    """Summarize only safe warning or degraded-state metadata."""

    metadata: Dict[str, Any] = {"tool_gateway_status": decision.outcome}
    if decision.degraded_reason:
        metadata["tool_gateway_reason"] = decision.machine_code
    if decision.trace_record.warning:
        metadata["tool_gateway_warning"] = decision.trace_record.warning
    return metadata


class ToolGateway:
    """Thin admission facade around the existing ToolRegistry."""

    def __init__(
        self,
        registry: ToolRegistry,
        *,
        capability_descriptors: Optional[Mapping[str, ToolCapabilityDescriptor]] = None,
        policy_descriptors: Optional[Mapping[str, ToolPolicyDescriptor]] = None,
        allowed_risk_classes: Sequence[RiskClass] = (RiskClass.READ_ONLY, RiskClass.BOUNDED_NON_MUTATING),
    ) -> None:
        descriptors = get_baseline_tool_descriptors()
        self.registry = registry
        self.capability_descriptors = dict(capability_descriptors or descriptors["capabilities"])
        self.policy_descriptors = dict(policy_descriptors or descriptors["policies"])
        self.allowed_risk_classes = tuple(allowed_risk_classes)
        self.trace_records: list[ToolTraceRecord] = []

    def evaluate_admission(
        self,
        *,
        route: StockQueryRoute,
        tool_name: str,
        args: Mapping[str, Any],
        surface: Optional[RouteFilteredToolSurface] = None,
        provider_state: Optional[Mapping[str, Any]] = None,
        timeout_budget_ms: Optional[int] = None,
    ) -> GatewayAdmissionDecision:
        """Evaluate admission before any underlying tool execution."""

        start = time.perf_counter()
        capability = self.capability_descriptors.get(tool_name)
        policy = self.policy_descriptors.get(tool_name)
        exposed_tools = list(surface.exposed_tool_names if surface else [])
        if not exposed_tools and capability and route.value in capability.route_coverage:
            exposed_tools = [tool_name] if capability.model_visible else []

        machine_code = "allowed"
        safe_message = "Tool call admitted."
        outcome = "allowed"
        degraded_reason: Optional[str] = None
        execute = True
        arguments_status = "valid"
        route_match = True
        risk_status = "allowed"
        license_status = "allowed"
        freshness_status = NOT_APPLICABLE
        provider_status = NOT_APPLICABLE
        descriptor_integrity = "valid"
        descriptor_version = capability.descriptor_version if capability else ""
        descriptor_hash = capability.descriptor_hash if capability else ""

        def deny(code: str, message: str, *, degraded: bool = True) -> None:
            nonlocal machine_code, safe_message, outcome, degraded_reason, execute
            machine_code = code
            safe_message = message
            outcome = "degraded" if degraded else "blocked"
            degraded_reason = code
            execute = False

        if capability is None or policy is None:
            descriptor_integrity = "missing"
            deny("missing_descriptor", "The requested tool is not available for this request.", degraded=False)
        elif self.registry.get(tool_name) is None:
            deny("unknown_tool", "The requested tool is not registered.", degraded=False)
        elif not self.registry.is_enabled(tool_name):
            deny("registry_disabled", "The requested tool is disabled.", degraded=False)
        elif capability.descriptor_hash != expected_descriptor_hash(capability) or policy.descriptor_hash != expected_descriptor_hash(policy):
            descriptor_integrity = "drifted"
            deny("descriptor_drift", "The requested tool descriptor failed integrity checks.", degraded=False)
        elif tool_name not in exposed_tools:
            route_match = False
            deny("tool_not_exposed_for_route", "The requested tool is not available for this route.", degraded=False)
        elif route.value not in capability.route_coverage or route.value not in policy.allowed_routes:
            route_match = False
            deny("route_tool_mismatch", "The requested tool is not admitted for this route.", degraded=False)
        elif not capability.enabled or not capability.model_visible or policy.exposure_status != ExposureStatus.MODEL_VISIBLE:
            deny("tool_non_exposed", "The requested tool is not exposed for model use.", degraded=False)
        elif policy.risk_class not in self.allowed_risk_classes:
            risk_status = "blocked"
            deny("risk_blocked", "The requested tool risk class is not admitted.", degraded=False)
        elif policy.license_mode in {LicenseMode.UNCLEAR, LicenseMode.PROHIBITED}:
            license_status = "blocked"
            deny("license_blocked", "The requested tool license posture is not admitted.", degraded=False)
        elif not self._arguments_valid(capability, args):
            arguments_status = "invalid"
            deny("invalid_arguments", "The tool arguments are invalid.", degraded=False)
        elif timeout_budget_ms is None and policy.timeout_budget_ms <= 0:
            deny("missing_timeout_budget", "The requested tool has no admitted timeout budget.", degraded=True)
        elif timeout_budget_ms is not None and timeout_budget_ms > policy.timeout_budget_ms:
            deny("timeout_budget_exceeded", "The requested tool exceeds the timeout budget.", degraded=True)
        elif provider_state and provider_state.get("status") in {"failed", "unavailable", "stale"}:
            provider_status = str(provider_state.get("status"))
            freshness_status = str(provider_state.get("freshness", provider_status))
            deny("provider_or_cache_unavailable", "Required tool data is temporarily unavailable.", degraded=True)

        latency_ms = (time.perf_counter() - start) * 1000
        trace = ToolTraceRecord(
            route=route.value,
            exposed_tools=tuple(exposed_tools),
            selected_tool=tool_name,
            selected_adapter=NOT_APPLICABLE,
            descriptor_version=descriptor_version,
            descriptor_hash=descriptor_hash,
            admission_outcome=outcome,
            cache_status=str(provider_state.get("cache_status", NOT_APPLICABLE)) if provider_state else NOT_APPLICABLE,
            freshness=freshness_status,
            latency_ms=latency_ms,
            warning=None if execute else machine_code,
            degraded_state_reason=degraded_reason,
        )
        self.trace_records.append(trace)
        return GatewayAdmissionDecision(
            route=route.value,
            tool_name=tool_name,
            arguments_status=arguments_status,
            route_match=route_match,
            risk_status=risk_status,
            license_status=license_status,
            freshness_status=freshness_status,
            provider_state=provider_status,
            descriptor_integrity=descriptor_integrity,
            timeout_budget_ms=timeout_budget_ms if timeout_budget_ms is not None else (policy.timeout_budget_ms if policy else None),
            outcome=outcome,
            degraded_reason=degraded_reason,
            machine_code=machine_code,
            safe_message=safe_message,
            execute_underlying_tool=execute,
            trace_record=trace,
        )

    def execute_tool(
        self,
        *,
        route: StockQueryRoute,
        tool_name: str,
        args: Mapping[str, Any],
        surface: Optional[RouteFilteredToolSurface] = None,
        provider_state: Optional[Mapping[str, Any]] = None,
        timeout_budget_ms: Optional[int] = None,
    ) -> Any:
        """Evaluate admission and execute the registry-backed tool only when allowed."""

        start = time.perf_counter()
        decision = self.evaluate_admission(
            route=route,
            tool_name=tool_name,
            args=args,
            surface=surface,
            provider_state=provider_state,
            timeout_budget_ms=timeout_budget_ms,
        )
        if not decision.execute_underlying_tool:
            return DegradedToolResult(
                status=decision.outcome,
                machine_code=decision.machine_code,
                safe_message=decision.safe_message,
                trace_record=decision.trace_record,
            )

        tool = self.registry.get(tool_name)
        result = tool._run(**dict(args)) if tool is not None else None
        latency_ms = (time.perf_counter() - start) * 1000
        trace = ToolTraceRecord(
            route=decision.route,
            exposed_tools=decision.trace_record.exposed_tools,
            selected_tool=tool_name,
            selected_adapter=NOT_APPLICABLE,
            descriptor_version=decision.trace_record.descriptor_version,
            descriptor_hash=decision.trace_record.descriptor_hash,
            admission_outcome=decision.outcome,
            cache_status=decision.trace_record.cache_status,
            freshness=decision.trace_record.freshness,
            latency_ms=latency_ms,
        )
        self.trace_records.append(trace)
        return result

    def build_execution_envelope(
        self,
        *,
        route: StockQueryRoute,
        tool_name: str,
        result: Any,
        admission_outcome: str = "allowed",
    ) -> ToolExecutionEnvelope:
        """Build an M2B.2 envelope around an already computed normalized result."""

        capability = self.capability_descriptors.get(tool_name)
        normalized_output = self._coerce_normalized_output(tool_name, result)
        return ToolExecutionEnvelope(
            route=route.value,
            selected_tool=tool_name,
            selected_adapter=NOT_APPLICABLE,
            descriptor_identity=capability.descriptor_hash if capability else tool_name,
            admission_outcome=AdmissionOutcome(admission_outcome),
            normalized_output=normalized_output,
            cache_status=NOT_APPLICABLE,
            freshness_status=(
                normalized_output.source_metadata.freshness_status
                if normalized_output.source_metadata
                else NOT_APPLICABLE
            ),
            warnings=normalized_output.warnings,
            degraded_state_reason=normalized_output.degraded_state.code if normalized_output.degraded_state else None,
            trace_metadata={"descriptor_version": capability.descriptor_version if capability else ""},
        )

    def create_wrapped_tools(
        self,
        *,
        route: StockQueryRoute,
        surface: RouteFilteredToolSurface,
    ) -> Sequence[AgentTool]:
        """Create LangChain-compatible gateway wrappers for exposed tools."""

        return tuple(
            GatewayToolWrapper(
                gateway=self,
                route=route,
                surface=surface,
                tool_name=descriptor.name,
                description=descriptor.purpose,
            )
            for descriptor in surface.exposed_tools
        )

    def trace_completeness_ratio(self) -> float:
        """Return ratio of trace records containing required M2B.1 fields."""

        if not self.trace_records:
            return 1.0
        required = (
            "route",
            "exposed_tools",
            "selected_tool",
            "descriptor_version",
            "descriptor_hash",
            "admission_outcome",
            "latency_ms",
        )
        complete = 0
        for trace in self.trace_records:
            payload = trace.sanitized_dict()
            if all(payload.get(field_name) not in (None, "") for field_name in required):
                complete += 1
        return complete / len(self.trace_records)

    @staticmethod
    def _arguments_valid(capability: ToolCapabilityDescriptor, args: Mapping[str, Any]) -> bool:
        schema = capability.input_schema or {}
        properties = schema.get("properties", {})
        for required in schema.get("required", ()):
            if required not in args or args.get(required) in (None, ""):
                return False
        required_any = schema.get("required_any", ())
        if required_any and not any(all(args.get(field_name) not in (None, "") for field_name in group) for group in required_any):
            return False
        for name, value in args.items():
            spec = properties.get(name)
            if not spec:
                continue
            expected_type = spec.get("type")
            if expected_type == "string" and not isinstance(value, str):
                return False
            if expected_type == "integer" and not isinstance(value, int):
                return False
            if "enum" in spec and value not in spec["enum"]:
                return False
        return True

    @staticmethod
    def _coerce_normalized_output(tool_name: str, result: Any) -> NormalizedOutput:
        if isinstance(result, NormalizedOutput):
            return result
        if isinstance(result, Mapping) and isinstance(result.get("normalized_output"), Mapping):
            payload = result["normalized_output"]
            kind = classify_normalized_output(payload)
            if kind == NormalizedOutputKind.DEGRADED_STATE:
                content = payload.get("content", {})
                return make_degraded_output(
                    code=str(content.get("code", result.get("machine_code", "degraded"))),
                    safe_message=str(content.get("message", "Tool returned a degraded state.")),
                    reason=str(content.get("code", "degraded")),
                    tool_name=tool_name,
                )
            return NormalizedOutput(
                kind=kind,
                content=payload.get("content", {}),
                warnings=tuple(payload.get("warnings", ())),
            )
        return make_degraded_output(
            code="normalization_missing",
            safe_message="Tool result did not include an admitted normalized output.",
            reason="validation_failed",
            tool_name=tool_name,
        )


class GatewayToolWrapper(AgentTool):
    """LangChain-compatible tool wrapper that delegates through ToolGateway."""

    name: str = "gateway_tool"
    description: str = "Gateway-admitted tool wrapper"

    def __init__(
        self,
        *,
        gateway: ToolGateway,
        route: StockQueryRoute,
        surface: RouteFilteredToolSurface,
        tool_name: str,
        description: str,
    ) -> None:
        super().__init__(cache=None, enable_cache=False)
        object.__setattr__(self, "_gateway", gateway)
        object.__setattr__(self, "_route", route)
        object.__setattr__(self, "_surface", surface)
        object.__setattr__(self, "name", tool_name)
        object.__setattr__(self, "description", description)

    def _execute(self, **kwargs: Any) -> Any:
        result = self._gateway.execute_tool(
            route=self._route,
            tool_name=self.name,
            args=kwargs,
            surface=self._surface,
        )
        if isinstance(result, DegradedToolResult):
            return result.to_dict()
        return result
