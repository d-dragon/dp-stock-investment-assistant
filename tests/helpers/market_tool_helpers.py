"""Assertion helpers for market tool-system tests."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from core.tools.normalization import (
    NormalizedOutput,
    NormalizedOutputKind,
    contains_blocked_prompt_payload,
    has_complete_market_attribution,
)


def assert_market_attribution(output: NormalizedOutput) -> None:
    assert output.kind == NormalizedOutputKind.EVIDENCE_FACT
    assert has_complete_market_attribution(output.source_metadata)
    assert output.freshness_metadata.get("provider_id")
    assert output.freshness_metadata.get("freshness_status")


def assert_visualization_only(output: NormalizedOutput) -> None:
    assert output.kind == NormalizedOutputKind.VISUALIZATION_PROVENANCE
    assert output.content["canonical_evidence"] is False
    assert output.source_metadata is not None
    assert output.source_metadata.provider_class == "visualization"


def assert_no_raw_payload(value: Mapping[str, Any]) -> None:
    assert not contains_blocked_prompt_payload(value)


def assert_route_metrics(metrics: Mapping[str, Any], *, minimum: float = 0.85) -> None:
    assert metrics["accuracy"] >= minimum
    assert metrics["precision"] >= minimum
    assert metrics["recall"] >= minimum


def assert_all_outputs_safe(outputs: Sequence[NormalizedOutput]) -> None:
    for output in outputs:
        assert_no_raw_payload(output.to_dict())
