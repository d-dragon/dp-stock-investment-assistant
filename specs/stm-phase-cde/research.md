# Research: STM Phase C-E

## Decision 1: Pagination Contract for Management Endpoints

- Decision: Use offset-based pagination with `limit` and `offset` query parameters for all list endpoints. Default `limit` is 25, maximum `limit` is 100. Workspace and session lists sort by `updated_at desc`; conversation lists sort by `last_activity_at desc` with `updated_at desc` tie-breaker.
- Rationale: The current Flask blueprint and repository stack already favors explicit query arguments and deterministic list behavior. Offset pagination is simpler to implement and verify in the existing repositories, keeps GET requests idempotent, and is sufficient for the management surfaces in this phase.
- Alternatives considered: Cursor pagination was rejected for this phase because it would add route, repository, and client complexity without a demonstrated current need. A page-number model was rejected because offset maps more directly to Mongo skip/limit behavior and existing test patterns.

## Decision 2: Parent-Match Validation on Nested Routes

- Decision: Nested session and conversation routes must compare the path parent identifier with the stored parent identifier and reject mismatches using the same secure not-found/error envelope used for out-of-hierarchy access.
- Rationale: The clarified spec requires rejection rather than silent normalization, and the repository already treats hierarchy as the isolation boundary. Reusing the same secure envelope avoids leaking whether a resource exists under a different parent.
- Alternatives considered: Returning a distinct mismatch-specific error was rejected because it leaks cross-hierarchy existence. Silently normalizing to the stored parent was rejected because it violates FR-C14 and FR-C15.

## Decision 3: Closed vs Archived Session Policy

- Decision: `closed` sessions are readable but immutable for context updates and block new conversation creation; existing non-archived conversations continue to accept chat. `archived` sessions are terminal for the subtree and archive all child conversations.
- Rationale: This exactly matches the clarified spec and cleanly separates a growth restriction from a terminal immutability state. It also minimizes disruption for ongoing conversations while keeping lifecycle semantics testable.
- Alternatives considered: Treating `closed` like `archived` was rejected because it would contradict the clarified behavior and unnecessarily block ongoing conversations. Allowing session-context updates while closed was rejected because it weakens lifecycle meaning and conflicts with the edge-case clarification.

## Decision 4: Summarized Conversation Semantics

- Decision: `summarized` remains a resumable, retrievable, listable non-archived state for management and runtime flows. Only `archived` conversations are immutable.
- Rationale: The spec explicitly clarifies that summarized conversations remain management-visible and resumable. That behavior must be preserved in both route contracts and chat/runtime handling.
- Alternatives considered: Treating `summarized` as terminal was rejected because it breaks clarified runtime semantics. Collapsing `summarized` into `active` was rejected because it loses useful lifecycle metadata already represented in the data model.

## Decision 5: Reconciliation Execution Schedule and Alert Thresholds

- Decision: Reconciliation runs on demand for operators at any time and is scheduled hourly in production, plus immediately before and after migration executions. Alerting is critical for any orphan session, orphan conversation, checkpoint-only thread, conversation-only metadata record, or `thread_id != conversation_id` anomaly outside an active migration window. During migration, repeated anomalies across 2 consecutive scans raise warnings; latency impact at or above 5 percent is always critical.
- Rationale: This schedule gives operators frequent visibility without turning reconciliation into a continuous background burden. The threshold model respects the migration window while still escalating true integrity problems.
- Alternatives considered: A purely manual schedule was rejected because it leaves too much drift undetected between operator interventions. A near-real-time schedule was rejected because it risks violating the non-blocking latency requirement for little added value in this phase.

## Decision 6: Migration Window and Rollback Strategy

- Decision: The migration is additive, dry-run-first, and resumable. The migration window remains open until dry-run reports zero remaining legacy records and 2 consecutive reconciliation scans are clean. Rollback means halting further migration runs, keeping legacy stateless handling enabled, preserving original checkpoint records, and deferring any cleanup of legacy compatibility code until after sign-off.
- Rationale: This preserves zero data loss, keeps mixed traffic working, and avoids the risk of trying to reverse already-promoted metadata records during an incident. It fits the repo's script-based operational model and the clarified mixed-traffic requirement.
- Alternatives considered: A destructive promote-and-delete strategy was rejected because it violates the safety profile of FR-D14. An immediate hard cutover was rejected because it breaks FR-D15 mixed-traffic compatibility.

## Decision 7: Operator-Only Execution Boundary

- Decision: Reconciliation and migration remain outside the public `/api` namespace and are exposed only through operator-run scripts backed by internal service or migration modules.
- Rationale: The clarified spec and NFR-2.5.4 require elevated execution paths and prohibit public management API exposure for these operations. The repository already uses `scripts/` for operational tooling, making this the most consistent pattern.
- Alternatives considered: Internal admin-only HTTP endpoints were rejected for this phase because they unnecessarily enlarge the public server surface and create additional auth requirements. Embedding reconciliation in public management endpoints was rejected because it violates operator-only scope.

## Decision 8: Test and Coverage Guard Strategy

- Decision: Phase E will track the pre-change baseline for agent-core coverage and fail verification if the baseline regresses, while replacing all legacy `session_id == thread_id` assertions with `conversation_id == thread_id` assertions.
- Rationale: The clarified spec treats NFR-6.1.3 as a soft non-regression constraint for this feature. That means the plan must preserve current coverage expectations without incorrectly expanding Phase E into a generalized coverage-improvement initiative.
- Alternatives considered: Ignoring coverage baseline was rejected because it leaves the soft constraint unenforced. Treating Phase E as the owner of the entire 80 percent project target was rejected because the spec explicitly says it is not a Phase E deliverable.