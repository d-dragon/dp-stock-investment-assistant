# Phase 7 Review: stm-phase-cde

| Dimension | Verdict | Issues |
|-----------|---------|--------|
| Spec-plan alignment | WARN | One internal plan summary is stale about unresolved planning decisions. |
| Plan-tasks completeness and requirement coverage | PASS | The task set now covers the clarified runtime and verification requirements, including the previously missing failure-path tests. |
| Dependency ordering and parallelization correctness | WARN | One parallel group still contains a same-file test collision. |
| Contract precision and OpenAPI-readiness | WARN | List payloads are fixed, but several mutating management endpoints still do not declare explicit response payloads. |
| Quickstart and verification readiness | PASS | Quickstart now includes the management latency verification expected by the task set. |
| Constitution and operator-boundary compliance | PASS | Operator tooling remains outside the public API surface and the OpenAPI sync gate is consistently called out. |
| Implementation readiness and residual risk | WARN | The remaining issues are narrow and non-architectural, but they should be cleaned up to reduce avoidable ambiguity during implementation. |

## Overall Verdict

READY WITH WARNINGS

The prior Phase 6 blockers are resolved. No blocking design failure remains. The artifact set is close enough to proceed, but there are still a few documentation and task-graph ambiguities worth fixing before implementation starts.

## Findings

1. R1. The management contract is improved but still not fully OpenAPI-ready for mutating endpoints. [specs/stm-phase-cde/contracts/management-api.md#L80-L92](specs/stm-phase-cde/contracts/management-api.md#L80-L92) defines workspace PATCH and archive behavior without stating the returned payload shape, and [specs/stm-phase-cde/contracts/management-api.md#L116-L156](specs/stm-phase-cde/contracts/management-api.md#L116-L156) does the same for session create, update, close, and archive. That is workable for engineers, but it still leaves response-schema decisions inferential when the feature explicitly treats OpenAPI synchronization as a constitutional gate.

2. R2. Parallelization is still incorrect for reconciliation tasks. [specs/stm-phase-cde/tasks.md#L150-L153](specs/stm-phase-cde/tasks.md#L150-L153) marks T036 and T037 as parallel even though both modify the same integration test file. That is a real same-file conflict, so the parallel marker is misleading and will cause churn if two implementers follow it literally.

3. R3. The plan still contains a stale scale/scope statement. [specs/stm-phase-cde/plan.md#L23](specs/stm-phase-cde/plan.md#L23) says there are 3 open planning decisions that must be resolved before task generation, while [specs/stm-phase-cde/plan.md#L129](specs/stm-phase-cde/plan.md#L129) already records those decisions as resolved and the feature already has a full task list. This does not block implementation, but it weakens review clarity.

## Prior Remediation Verification

1. Management contract underspecified session-list and conversation-list item payloads: Resolved. Explicit session list item fields are now defined in [specs/stm-phase-cde/contracts/management-api.md#L101-L114](specs/stm-phase-cde/contracts/management-api.md#L101-L114), and explicit conversation list item fields are now defined in [specs/stm-phase-cde/contracts/management-api.md#L173-L189](specs/stm-phase-cde/contracts/management-api.md#L173-L189).

2. Plan said 38 functional requirements instead of 39: Resolved. The plan now states 39 functional requirements at [specs/stm-phase-cde/plan.md#L23](specs/stm-phase-cde/plan.md#L23), matching the addition of FR-D08a in [specs/stm-phase-cde/spec.md#L242](specs/stm-phase-cde/spec.md#L242).

3. Quickstart lacked management API latency verification expected by T030A and T051: Resolved. The quickstart now includes the latency verification step and thresholds in [specs/stm-phase-cde/quickstart.md#L57-L67](specs/stm-phase-cde/quickstart.md#L57-L67), and the task hooks remain present in [specs/stm-phase-cde/tasks.md#L119](specs/stm-phase-cde/tasks.md#L119) and [specs/stm-phase-cde/tasks.md#L206](specs/stm-phase-cde/tasks.md#L206).

4. Tasks did not explicitly name test coverage for concurrent archive-versus-message behavior and chat-response-success with metadata-write-failure drift surfaced later: Resolved. Those behaviors are now explicit in the US5 independent test and tasks at [specs/stm-phase-cde/tasks.md#L129-L135](specs/stm-phase-cde/tasks.md#L129-L135), and again in the final regression gate at [specs/stm-phase-cde/tasks.md#L206](specs/stm-phase-cde/tasks.md#L206).

5. Requirements checklist was stale generic language: Resolved. The checklist now reflects the contract-heavy nature of the feature and explicitly acknowledges contract, quickstart, and OpenAPI obligations in [specs/stm-phase-cde/checklists/requirements.md#L1-L31](specs/stm-phase-cde/checklists/requirements.md#L1-L31).

## Recommended Next Step

Revise specific artifacts, then proceed to implementation.

The needed cleanup is small and localized:
1. Tighten response-schema wording in [specs/stm-phase-cde/contracts/management-api.md](specs/stm-phase-cde/contracts/management-api.md) for mutating endpoints so OpenAPI generation is fully mechanical rather than inferred.
2. Remove or re-sequence the false parallelism in [specs/stm-phase-cde/tasks.md](specs/stm-phase-cde/tasks.md) for T036 and T037.
3. Remove the stale “3 open planning decisions” wording from [specs/stm-phase-cde/plan.md](specs/stm-phase-cde/plan.md).

After that short artifact pass, the feature is ready to implement.

## Post-Review Cleanup

The three warning items above were resolved immediately after this review was issued:

1. `contracts/management-api.md` now declares explicit response payloads for the mutating workspace and session endpoints, removing the remaining OpenAPI inference gap.
2. `tasks.md` now removes the false parallelism between T036 and T037, and its parallel-examples section was updated to match the corrected execution order.
3. `plan.md` no longer says there are unresolved planning decisions before task generation; it now reflects that planning decisions are complete and carried into the task set.

With those cleanup edits applied, the feature is effectively review-complete and ready to proceed to implementation.
