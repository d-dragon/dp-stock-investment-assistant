"""Request-scoped ToolContextPack and retained-derivative helpers for M2B.2."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional, Sequence

from .normalization import (
    DegradedReason,
    DegradedState,
    NormalizedOutput,
    NormalizedOutputKind,
    SourceMetadata,
    contains_blocked_prompt_payload,
    make_degraded_output,
    sanitize_prompt_payload,
    stable_output_id,
)


@dataclass(frozen=True)
class ToolContextPack:
    """Request-scoped normalized context bundle for prompt assembly."""

    request_id: str
    route: str
    normalized_outputs: Sequence[NormalizedOutput]
    citations: Sequence[Mapping[str, Any]] = field(default_factory=tuple)
    artifact_references: Sequence[Mapping[str, Any]] = field(default_factory=tuple)

    @property
    def source_metadata(self) -> Sequence[SourceMetadata]:
        return tuple(output.source_metadata for output in self.normalized_outputs if output.source_metadata)

    @property
    def warnings(self) -> Sequence[str]:
        values = []
        for output in self.normalized_outputs:
            values.extend(output.warnings)
        return tuple(values)

    @property
    def degraded_states(self) -> Sequence[DegradedState]:
        return tuple(output.degraded_state for output in self.normalized_outputs if output.degraded_state)

    @property
    def freshness_metadata(self) -> Sequence[Mapping[str, Any]]:
        return tuple(output.freshness_metadata for output in self.normalized_outputs if output.freshness_metadata)

    def prompt_projection(self) -> Dict[str, Any]:
        """Return a sanitized prompt-facing context projection."""

        payload = {
            "request_id": self.request_id,
            "route": self.route,
            "normalized_outputs": [output.prompt_projection() for output in self.normalized_outputs],
            "citations": list(self.citations),
            "source_metadata": [source.to_dict() for source in self.source_metadata],
            "freshness_metadata": list(self.freshness_metadata),
            "warnings": list(self.warnings),
            "degraded_states": [state.to_dict() for state in self.degraded_states],
            "artifact_references": list(self.artifact_references),
        }
        return sanitize_prompt_payload(payload)

    def retained_derivative_candidates(self) -> Sequence["RetainedDerivative"]:
        """Return retainable derivative metadata without persisting the full pack."""

        derivatives = []
        for output in self.normalized_outputs:
            if output.kind in {
                NormalizedOutputKind.GENERATED_ARTIFACT,
                NormalizedOutputKind.MUTATION_RECEIPT,
                NormalizedOutputKind.VISUALIZATION_PROVENANCE,
                NormalizedOutputKind.SYSTEM_RECORD,
            }:
                derivatives.append(
                    RetainedDerivative(
                        derivative_id=stable_output_id("retained", {"output_id": output.output_id}),
                        derivative_type=output.kind.value,
                        source_metadata=output.source_metadata,
                        degraded_state=output.degraded_state,
                        metadata={"output_id": output.output_id, "route": self.route},
                    )
                )
        return tuple(derivatives)


@dataclass(frozen=True)
class RetainedDerivative:
    """Approved derivative that may outlive one request."""

    derivative_id: str
    derivative_type: str
    source_metadata: Optional[SourceMetadata] = None
    degraded_state: Optional[DegradedState] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def has_lineage_or_degraded_reason(self) -> bool:
        return self.source_metadata is not None or self.degraded_state is not None

    def to_dict(self) -> Dict[str, Any]:
        if not self.has_lineage_or_degraded_reason():
            raise ValueError("RetainedDerivative requires source lineage or a degraded-state reason")
        if contains_blocked_prompt_payload(self.metadata):
            raise ValueError("RetainedDerivative metadata cannot contain raw payloads")
        return {
            "derivative_id": self.derivative_id,
            "derivative_type": self.derivative_type,
            "source_metadata": self.source_metadata.to_dict() if self.source_metadata else None,
            "degraded_state": self.degraded_state.to_dict() if self.degraded_state else None,
            "metadata": sanitize_prompt_payload(dict(self.metadata)),
        }


def assemble_tool_context_pack(
    *,
    request_id: str,
    route: str,
    normalized_outputs: Sequence[NormalizedOutput],
    citations: Sequence[Mapping[str, Any]] = (),
    artifact_references: Sequence[Mapping[str, Any]] = (),
) -> ToolContextPack:
    """Assemble a request-scoped pack and reject unsafe raw content."""

    for output in normalized_outputs:
        if contains_blocked_prompt_payload(output.content):
            raise ValueError("ToolContextPack cannot include raw payloads")
    return ToolContextPack(
        request_id=request_id,
        route=route,
        normalized_outputs=tuple(normalized_outputs),
        citations=tuple(citations),
        artifact_references=tuple(artifact_references),
    )


def reject_whole_pack_persistence(value: Any) -> bool:
    """Return true when the caller attempted to persist a full ToolContextPack."""

    return isinstance(value, ToolContextPack) or (
        isinstance(value, Mapping)
        and "normalized_outputs" in value
        and "request_id" in value
        and "route" in value
    )


def validate_retained_derivative(derivative: RetainedDerivative) -> bool:
    """Validate retained derivative lineage and raw-payload boundaries."""

    derivative.to_dict()
    return True


def visualization_provenance_output(
    *,
    visualization_url: str,
    provider_id: str = "tradingview",
    warning: str = "Visualization provenance is not canonical market evidence.",
) -> NormalizedOutput:
    """Build a visualization provenance output that cannot masquerade as evidence."""

    source = SourceMetadata(
        provider_id=provider_id,
        provider_class="visualization",
        source_url_or_reference=visualization_url,
        warnings=(warning,),
    )
    return NormalizedOutput(
        kind=NormalizedOutputKind.VISUALIZATION_PROVENANCE,
        content={"visualization_url": visualization_url, "canonical_evidence": False},
        source_metadata=source,
        warnings=(warning,),
    )


def no_source_degraded_output(*, route: str, tool_name: str) -> NormalizedOutput:
    """Create a degraded output for retained data with no source lineage."""

    return make_degraded_output(
        code=DegradedReason.NO_SOURCE_AVAILABLE.value,
        safe_message="Source lineage is unavailable for this retained derivative.",
        reason=DegradedReason.NO_SOURCE_AVAILABLE,
        route=route,
        tool_name=tool_name,
    )
