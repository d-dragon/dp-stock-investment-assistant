"""Disabled-by-default mutation receipt contracts for M2B.2."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Mapping, Optional

from .normalization import DegradedReason, NormalizedOutput, NormalizedOutputKind, make_degraded_output, stable_output_id, utc_now_iso


class MutationKind(str, Enum):
    WORKFLOW_MUTATION = "workflow_mutation"


class MutationSubtype(str, Enum):
    INTERNAL_STATE_MUTATION = "internal_state_mutation"


class MutationStatus(str, Enum):
    DISABLED = "disabled"
    BLOCKED = "blocked"
    APPROVED_TEST_ONLY = "approved_test_only"
    COMPLETED = "completed"


SYMBOL_MUTATION_ACTIONS = {
    "upsert_symbol",
    "merge_alias",
    "update_tags",
    "update_coverage",
    "retire_symbol",
}


@dataclass(frozen=True)
class MutationReceipt:
    """Audit shape for future approved state-changing tool actions."""

    mutation_id: str
    target_record: str
    action: str
    before_summary: Mapping[str, Any]
    after_summary: Mapping[str, Any]
    actor_or_route: str
    approval_status: MutationStatus | str
    audit_metadata: Mapping[str, Any]
    timestamp: str
    result: str
    mutation_kind: MutationKind = MutationKind.WORKFLOW_MUTATION
    mutation_subtype: MutationSubtype = MutationSubtype.INTERNAL_STATE_MUTATION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mutation_id": self.mutation_id,
            "target_record": self.target_record,
            "action": self.action,
            "before_summary": dict(self.before_summary),
            "after_summary": dict(self.after_summary),
            "actor_or_route": self.actor_or_route,
            "approval_status": self.approval_status.value if isinstance(self.approval_status, Enum) else self.approval_status,
            "audit_metadata": dict(self.audit_metadata),
            "timestamp": self.timestamp,
            "result": self.result,
            "mutation_kind": self.mutation_kind.value,
            "mutation_subtype": self.mutation_subtype.value,
        }

    def to_normalized_output(self) -> NormalizedOutput:
        return NormalizedOutput(
            kind=NormalizedOutputKind.MUTATION_RECEIPT,
            content=self.to_dict(),
            warnings=() if self.approval_status == MutationStatus.COMPLETED else (str(self.approval_status),),
        )


def is_symbol_mutation_action(action: str) -> bool:
    return str(action) in SYMBOL_MUTATION_ACTIONS


def disabled_mutation_receipt(
    *,
    action: str,
    target_record: str,
    actor_or_route: str = "tool-system-m2b.2",
    audit_metadata: Optional[Mapping[str, Any]] = None,
) -> MutationReceipt:
    """Create an audit receipt for a disabled production mutation request."""

    payload = {
        "action": action,
        "target_record": target_record,
        "actor_or_route": actor_or_route,
        "status": MutationStatus.DISABLED.value,
    }
    return MutationReceipt(
        mutation_id=stable_output_id("mutation", payload),
        target_record=target_record,
        action=action,
        before_summary={},
        after_summary={},
        actor_or_route=actor_or_route,
        approval_status=MutationStatus.DISABLED,
        audit_metadata=dict(audit_metadata or {"reason": "m2b2_default_disabled"}),
        timestamp=utc_now_iso(),
        result="disabled_by_default",
    )


def guard_symbol_mutation(
    *,
    action: str,
    target_record: str,
    actor_or_route: str = "tool-system-m2b.2",
    allow_test_only: bool = False,
) -> NormalizedOutput:
    """Return a disabled degraded outcome unless explicitly test-approved."""

    if allow_test_only:
        receipt = MutationReceipt(
            mutation_id=stable_output_id("mutation", {"action": action, "target": target_record, "test": True}),
            target_record=target_record,
            action=action,
            before_summary={},
            after_summary={"test_only": True},
            actor_or_route=actor_or_route,
            approval_status=MutationStatus.APPROVED_TEST_ONLY,
            audit_metadata={"scope": "test_only"},
            timestamp=utc_now_iso(),
            result="receipt_only_no_production_write",
        )
        return receipt.to_normalized_output()
    receipt = disabled_mutation_receipt(action=action, target_record=target_record, actor_or_route=actor_or_route)
    degraded = make_degraded_output(
        code=DegradedReason.MUTATION_DISABLED.value,
        safe_message="Symbol-store mutation requests are disabled by default in M2B.2.",
        reason=DegradedReason.MUTATION_DISABLED,
        route=actor_or_route,
        tool_name="stock_symbol",
    )
    content = dict(degraded.content)
    content["mutation_receipt"] = receipt.to_dict()
    return NormalizedOutput(
        kind=NormalizedOutputKind.DEGRADED_STATE,
        content=content,
        degraded_state=degraded.degraded_state,
        warnings=(DegradedReason.MUTATION_DISABLED.value,),
    )
