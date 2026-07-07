"""M2B.2 tests for request-scoped retention and disabled mutations."""

from __future__ import annotations

import pytest

from core.tools.context import (
    RetainedDerivative,
    assemble_tool_context_pack,
    no_source_degraded_output,
    reject_whole_pack_persistence,
    validate_retained_derivative,
    visualization_provenance_output,
)
from core.tools.mutation_receipts import (
    MutationReceipt,
    MutationStatus,
    disabled_mutation_receipt,
    guard_symbol_mutation,
)
from core.tools.normalization import NormalizedOutputKind, SourceMetadata, make_system_record_output
from tests.fixtures.tool_system_m2b2.symbols import InMemorySymbolRepository, SYMBOL_RECORDS


def test_retained_derivative_requires_source_lineage():
    output = make_system_record_output(SYMBOL_RECORDS[0])
    pack = assemble_tool_context_pack(
        request_id="request-1",
        route="price_check",
        normalized_outputs=(output,),
    )

    derivative = pack.retained_derivative_candidates()[0]
    assert validate_retained_derivative(derivative) is True
    assert derivative.to_dict()["source_metadata"]["provider_id"] == "internal_symbol_store"


def test_full_tool_context_pack_is_not_persistable_wholesale():
    pack = assemble_tool_context_pack(
        request_id="request-1",
        route="price_check",
        normalized_outputs=(make_system_record_output(SYMBOL_RECORDS[0]),),
    )

    assert reject_whole_pack_persistence(pack) is True
    assert reject_whole_pack_persistence(pack.prompt_projection()) is True
    assert reject_whole_pack_persistence(pack.retained_derivative_candidates()[0].to_dict()) is False


def test_missing_source_uses_no_source_degraded_reason():
    output = no_source_degraded_output(route="price_check", tool_name="stock_symbol")
    derivative = RetainedDerivative(
        derivative_id="retained:no-source",
        derivative_type="GeneratedArtifact",
        degraded_state=output.degraded_state,
        metadata={"artifact_reference": "report-1"},
    )

    assert derivative.to_dict()["degraded_state"]["code"] == "no_source_available"


def test_visualization_provenance_is_not_canonical_evidence():
    output = visualization_provenance_output(visualization_url="https://www.tradingview.com/chart/FPT")

    assert output.kind == NormalizedOutputKind.VISUALIZATION_PROVENANCE
    assert output.content["canonical_evidence"] is False
    assert output.source_metadata.provider_class == "visualization"


@pytest.mark.parametrize(
    "action",
    ["upsert_symbol", "merge_alias", "update_tags", "update_coverage", "retire_symbol"],
)
def test_symbol_mutations_disabled_by_default(action):
    output = guard_symbol_mutation(action=action, target_record="FPT")

    assert output.kind == NormalizedOutputKind.DEGRADED_STATE
    assert output.degraded_state.code == "mutation_disabled"
    assert output.content["mutation_receipt"]["approval_status"] == "disabled"


def test_mutation_receipt_required_fields():
    receipt = disabled_mutation_receipt(action="upsert_symbol", target_record="FPT")
    payload = receipt.to_dict()

    for field in (
        "mutation_id",
        "target_record",
        "action",
        "before_summary",
        "after_summary",
        "actor_or_route",
        "approval_status",
        "audit_metadata",
        "timestamp",
        "result",
    ):
        assert field in payload
    assert payload["mutation_kind"] == "workflow_mutation"
    assert payload["mutation_subtype"] == "internal_state_mutation"


def test_default_mutation_request_does_not_call_repository_write_path():
    repo = InMemorySymbolRepository()
    output = guard_symbol_mutation(action="upsert_symbol", target_record="FPT")

    assert output.degraded_state.code == "mutation_disabled"
    assert repo.write_calls == []


def test_test_only_mutation_receipt_fixture_does_not_claim_production_write():
    output = guard_symbol_mutation(action="update_tags", target_record="FPT", allow_test_only=True)

    assert output.kind == NormalizedOutputKind.MUTATION_RECEIPT
    assert output.content["approval_status"] == "approved_test_only"
    assert output.content["result"] == "receipt_only_no_production_write"


def test_retained_derivative_rejects_raw_payload_metadata():
    derivative = RetainedDerivative(
        derivative_id="bad",
        derivative_type="GeneratedArtifact",
        source_metadata=SourceMetadata(provider_id="fixture"),
        metadata={"raw_provider_payload": {"secret": True}},
    )

    with pytest.raises(ValueError, match="raw payloads"):
        derivative.to_dict()
