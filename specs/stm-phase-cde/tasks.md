# Tasks: STM Phase C-E - Management API, Runtime Consistency, and Test Realignment

**Input**: Design documents from `/specs/stm-phase-cde/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, `checklists/`

**Tests**: Tests are mandatory for this feature because the clarified spec includes explicit contract, lifecycle, migration, operator-boundary, and coverage-baseline regression requirements.

**Organization**: Tasks are grouped by user story so each story remains independently implementable and verifiable while preserving the shared OpenAPI and operator-boundary gates required by the constitution.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with the other tasks in the same `parallel-group`
- **[Story]**: User story label for traceability (`[US1]` ... `[US8]`)
- Every task includes the exact file path(s) it changes or validates

## Phase 1: Setup

**Purpose**: Establish the implementation baseline, route inventory, and coverage guardrails before shared backend work begins.

<!-- sequential -->
- [ ] T001 Review and reconcile feature traceability across `specs/stm-phase-cde/spec.md`, `specs/stm-phase-cde/plan.md`, and `specs/stm-phase-cde/checklists/readiness.md` so the implementation backlog preserves the clarified scope.
- [ ] T002 Audit the currently registered public route surface in `src/web/api_server.py` against the legacy contract in `docs/openapi.yaml`, including the existing `/api/sessions/{session_id}/conversation` documentation drift.
- [ ] T003 Capture the pre-change agent-core coverage baseline and add the verification command set to `specs/stm-phase-cde/quickstart.md` for NFR-6.1.3 non-regression tracking.

---

## Phase 2: Foundational

**Purpose**: Deliver the shared contract, validation, and registration groundwork that blocks all user-story implementation.

**⚠️ CRITICAL**: No user-story work should begin until these tasks are complete.

<!-- parallel-group: 1 -->
- [ ] T004 [P] Define shared `limit`/`offset`/`status` parsing helpers for management routes in `src/utils/service_utils.py`.
- [ ] T005 [P] Verify research decisions remain aligned with `specs/stm-phase-cde/research.md`, `specs/stm-phase-cde/data-model.md`, `specs/stm-phase-cde/contracts/management-api.md`, and `specs/stm-phase-cde/contracts/operator-tooling.md` before implementation branches diverge.
- [ ] T006 [P] Add management lifecycle and validation error types aligned to the chat error envelope in `src/services/exceptions.py`.

<!-- sequential -->
- [ ] T007 Wire the management blueprints and any new operator services through `src/services/factory.py` and `src/web/api_server.py`.
- [ ] T008 Reconcile the baseline public API documentation in `docs/openapi.yaml` for existing routes, `conversation_id` chat semantics, constitution-gated OpenAPI sync, and the explicit disposition of legacy `/api/sessions/{session_id}/conversation` documentation.

**Checkpoint**: Shared routing, contract, and OpenAPI gates are defined; user stories can now proceed in priority order.

---

## Phase 3: User Story 1 - Workspace CRUD Endpoints (Priority: P1) 🎯 MVP

**Goal**: Deliver workspace create/list/detail/update/archive endpoints with ownership enforcement and aggregate counts.

**Independent Test**: Create, list, retrieve, update, and archive a workspace over REST; verify cross-user access is rejected and archive cascades are observable in workspace detail payloads.

<!-- parallel-group: 2 -->
- [ ] T009 [P] [US1] Add workspace service and route coverage in `tests/test_workspace_service.py` and `tests/test_api_routes.py`.
- [ ] T010 [P] [US1] Add workspace contract and ownership integration coverage in `tests/integration/test_management_api_contracts.py`.
- [ ] T011 [P] [US1] Extend aggregate-count and archive helpers in `src/data/repositories/workspace_repository.py`.

<!-- sequential -->
- [ ] T012 [US1] Extend workspace CRUD, detail aggregation, and archive orchestration in `src/services/workspace_service.py`.
- [ ] T013 [US1] Implement workspace management routes in `src/web/routes/workspace_routes.py` and register them in `src/web/api_server.py`.
- [ ] T014 [US1] Publish workspace management paths, payloads, and archive action schemas in `docs/openapi.yaml`.

**Checkpoint**: Workspace management is independently testable and documented.

---

## Phase 4: User Story 2 - Session CRUD and Lifecycle Endpoints (Priority: P2)

**Goal**: Deliver nested and direct session management endpoints with lifecycle enforcement, parent validation, and cascade semantics.

**Independent Test**: Create sessions under a workspace, list and retrieve them, update active-session context, close and archive sessions, and verify parent mismatch and closed-session constraints are enforced.

<!-- parallel-group: 3 -->
- [ ] T015 [P] [US2] Add session lifecycle and ownership tests in `tests/test_session_service.py` and `tests/test_api_routes.py`.
- [ ] T016 [P] [US2] Add nested-parent mismatch, closed-session, and archived-workspace integration tests in `tests/integration/test_management_api_contracts.py`.
- [ ] T017 [P] [US2] Extend filter, count, and cascade queries in `src/data/repositories/session_repository.py`.

<!-- sequential -->
- [ ] T018 [US2] Extend session lifecycle and context-mutation validation in `src/services/session_service.py`.
- [ ] T019 [US2] Implement nested and direct session routes in `src/web/routes/session_routes.py` and register them in `src/web/api_server.py`.
- [ ] T020 [US2] Update `docs/openapi.yaml` for session CRUD, close/archive actions, nested parent validation, and the final disposition of legacy `/api/sessions/{session_id}/conversation` documentation.

**Checkpoint**: Session management and lifecycle rules are independently testable.

---

## Phase 5: User Story 3 - Conversation CRUD and Lifecycle Endpoints (Priority: P3)

**Goal**: Deliver nested and direct conversation management endpoints, archive behavior, and history-summary retrieval.

**Independent Test**: Create conversations under a session, list and retrieve them, request summary data, archive them, and verify full hierarchy validation for direct and nested access.

<!-- parallel-group: 4 -->
- [ ] T021 [P] [US3] Add conversation CRUD, archive, and summary tests in `tests/test_conversation_service.py` and `tests/test_api_routes.py`.
- [ ] T022 [P] [US3] Add hierarchy-chain and zero-result pagination integration coverage in `tests/integration/test_management_api_contracts.py`.
- [ ] T023 [P] [US3] Extend conversation list, detail, summary, and archive helpers in `src/data/repositories/conversation_repository.py`.

<!-- sequential -->
- [ ] T024 [US3] Extend conversation hierarchy validation, summary retrieval, and archive-reason behavior in `src/services/conversation_service.py`.
- [ ] T025 [US3] Implement nested and direct conversation routes in `src/web/routes/conversation_routes.py` and register them in `src/web/api_server.py`.
- [ ] T026 [US3] Update `docs/openapi.yaml` for conversation CRUD, history-summary responses, and required hierarchy identifiers.

**Checkpoint**: Conversation management is independently testable and tied to the public contract.

---

## Phase 6: User Story 4 - Cross-Cutting API Behaviors (Priority: P4)

**Goal**: Make the management API behave consistently for pagination, error envelopes, idempotent GETs, archive-over-delete semantics, and public-contract completeness.

**Independent Test**: Validate list pagination, repeated GET stability, error shape parity with chat, and parent archive cascades across the management API surface.

<!-- parallel-group: 5 -->
- [ ] T027 [P] [US4] Add pagination, error-envelope parity, idempotent GET, and atomic archive-cascade integration coverage in `tests/integration/test_management_api_contracts.py`.
- [ ] T028 [P] [US4] Implement shared management pagination and error-response helpers in `src/utils/service_utils.py` and `src/services/exceptions.py`.

<!-- sequential -->
- [ ] T029 [US4] Align archive-over-delete, secure parent-match rejection, and atomic parent-to-descendant archive execution across `src/web/routes/workspace_routes.py`, `src/web/routes/session_routes.py`, `src/web/routes/conversation_routes.py`, `src/services/workspace_service.py`, and `src/services/session_service.py`.
- [ ] T030 [US4] Reconcile `docs/openapi.yaml` against the registered public API surface in `src/web/api_server.py`, including new Phase C paths plus `/api/chat`, `/api/health`, `/api/config`, `/api/models/openai*`, and `/api/users*`.
- [ ] T030A [US4] Add management API latency-budget verification for GET, list, create/update/archive, and cascade archive behavior in `tests/performance/test_management_api_latency.py` and `specs/stm-phase-cde/quickstart.md`.

**Checkpoint**: The public management API behaves consistently and the canonical OpenAPI document is no longer feature-partial.

---

## Phase 7: User Story 5 - Runtime Metadata Tracking in Chat Flow (Priority: P5)

**Goal**: Keep conversation metadata and checkpoint state synchronized through the chat flow while preserving archived-conversation immutability.

**Independent Test**: Send chat messages with `conversation_id`, verify metadata updates become visible within 5 seconds, confirm archived conversations reject new messages, and explicitly cover concurrent archive-versus-message races plus chat-response success when metadata writes fail and drift is surfaced later.

<!-- parallel-group: 6 -->
- [ ] T031 [P] [US5] Add runtime metadata synchronization, archived-conversation rejection, and concurrent archive-versus-message race tests in `tests/test_chat_service.py` and `tests/test_chat_routes.py`.
- [ ] T032 [P] [US5] Add metadata-checkpoint alignment and chat-response-success with metadata-write-failure drift-surfacing regression coverage in `tests/integration/test_stm_runtime_wiring.py` and `tests/integration/test_memory_persistence.py`.
- [ ] T033 [P] [US5] Extend conversation metadata update helpers for counts, tokens, timestamps, and focused symbols in `src/services/conversation_service.py` and `src/data/repositories/conversation_repository.py`.

<!-- sequential -->
- [ ] T034 [US5] Extend chat flow auto-create, archive gating, mixed-write handling, and reconciliation-visible drift emission for metadata write failures in `src/services/chat_service.py` and `src/web/routes/ai_chat_routes.py`.
- [ ] T035 [US5] Update `docs/openapi.yaml` and `specs/stm-phase-cde/quickstart.md` for `conversation_id` chat requests, archived-conversation conflicts, and metadata-visibility verification.

**Checkpoint**: Runtime metadata consistency is independently testable and reflected in the published chat contract.

---

## Phase 8: User Story 6 - Data Reconciliation and Integrity Verification (Priority: P6)

**Goal**: Provide operator-only reconciliation scans that detect hierarchy and checkpoint/metadata anomalies without expanding the public API surface.

**Independent Test**: Seed orphaned and mismatched records, run reconciliation, validate the JSON report, and verify the tooling stays outside public route registration.

<!-- parallel-group: 7 -->
- [ ] T036 [P] [US6] Add reconciliation anomaly-detection coverage in `tests/integration/test_stm_runtime_wiring.py` and `tests/integration/test_memory_persistence.py`.
- [ ] T038 [P] [US6] Implement reconciliation scan, machine-readable report assembly, and structured scan-action logging with `correlation_id` and timestamps in `src/services/runtime_reconciliation_service.py` and `src/services/factory.py`.

<!-- sequential -->
- [ ] T037 [US6] Add reconciliation latency-impact, scan-action logging, and operator-boundary coverage in `tests/performance/test_reconciliation_impact.py`, `tests/integration/test_stm_runtime_wiring.py`, and `tests/security/test_operator_tooling_boundaries.py`.
- [ ] T039 [US6] Implement the operator-only reconciliation entrypoint in `scripts/reconcile_stm_runtime.py`, including distinct scan log emission for `scan_started`, `anomaly_detected`, and `scan_completed` actions.
- [ ] T040 [US6] Align the operator-only boundary across `specs/stm-phase-cde/contracts/operator-tooling.md`, `tests/security/test_operator_tooling_boundaries.py`, and `src/web/api_server.py`.

**Checkpoint**: Reconciliation is independently testable, operator-only, and absent from the public REST surface.

---

## Phase 9: User Story 7 - Legacy Data Migration Tooling (Priority: P7)

**Goal**: Provide additive, dry-run-first, resumable migration for legacy session-keyed checkpoint traffic while keeping mixed traffic working.

**Independent Test**: Run dry-run and resume-capable migration against seeded legacy data, confirm zero destructive writes in dry-run mode, and verify uninterrupted and resumed runs converge.

<!-- parallel-group: 8 -->
- [ ] T041 [P] [US7] Add migration dry-run, resume, and mixed-traffic regression tests in `tests/integration/test_memory_persistence.py` and `tests/security/test_operator_tooling_boundaries.py`.
- [ ] T042 [P] [US7] Implement additive legacy checkpoint promotion in `src/data/migration/legacy_checkpoint_migration.py`.
- [ ] T043 [P] [US7] Implement the operator migration CLI and audit output in `scripts/migrate_legacy_threads.py`.

<!-- sequential -->
- [ ] T044 [US7] Extend legacy stateless and conversation-aware chat compatibility in `src/services/chat_service.py` and `src/web/routes/ai_chat_routes.py`.
- [ ] T045 [US7] Align migration runbook details in `specs/stm-phase-cde/contracts/operator-tooling.md` and `specs/stm-phase-cde/quickstart.md`.

**Checkpoint**: Migration tooling is independently testable, resumable, and aligned with the mixed-traffic contract.

---

## Phase 10: User Story 8 - Test Realignment for Hierarchy, STM, Lifecycle, and Consistency (Priority: P8)

**Goal**: Rewrite and harden the regression suite so hierarchy, STM isolation, lifecycle enforcement, operator boundaries, and coverage baseline become release gates.

**Independent Test**: Run the revised suite, confirm legacy `session_id == thread_id` assumptions are removed, and verify the coverage baseline does not regress.

<!-- parallel-group: 9 -->
- [ ] T046 [P] [US8] Replace legacy `session_id == thread_id` assertions with explicit STM-isolation coverage for same-conversation restore, cross-conversation isolation, resumed checkpoint retrieval, stateless mode, and `conversation_id == thread_id` behavior in `tests/test_agent_memory.py`, `tests/integration/test_stm_runtime_wiring.py`, and `tests/test_chat_routes.py`.
- [ ] T047 [P] [US8] Add hierarchy and lifecycle regression coverage in `tests/integration/test_management_api_contracts.py` and `tests/test_api_routes.py`.
- [ ] T048 [P] [US8] Add public-surface and operator-boundary regression coverage in `tests/security/test_operator_tooling_boundaries.py` and `src/web/api_server.py`.

<!-- sequential -->
- [ ] T049 [US8] Capture and enforce the NFR-6.1.3 coverage-baseline non-regression workflow in `specs/stm-phase-cde/quickstart.md` and `tests/conftest.py`.

**Checkpoint**: Regression coverage now enforces the hierarchy-aware model and the feature’s soft coverage gate.

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Finish the review gates that prove the implementation, contracts, quickstart, and verification commands stay aligned.

<!-- sequential -->
- [ ] T050 Validate that `specs/stm-phase-cde/quickstart.md`, `specs/stm-phase-cde/contracts/management-api.md`, and `docs/openapi.yaml` remain mutually consistent as the executable validation guide, route contract, and published REST document.
- [ ] T051 Run the feature regression and coverage command set from `specs/stm-phase-cde/quickstart.md` across `tests/test_workspace_service.py`, `tests/test_session_service.py`, `tests/test_conversation_service.py`, `tests/test_chat_service.py`, `tests/integration/test_management_api_contracts.py`, `tests/integration/test_stm_runtime_wiring.py`, `tests/security/test_operator_tooling_boundaries.py`, `tests/performance/test_reconciliation_impact.py`, and `tests/performance/test_management_api_latency.py`, including the concurrent archive-versus-message and metadata-write-failure drift scenarios.
- [ ] T052 Re-audit `specs/stm-phase-cde/spec.md`, `specs/stm-phase-cde/plan.md`, `specs/stm-phase-cde/research.md`, `specs/stm-phase-cde/data-model.md`, and `specs/stm-phase-cde/checklists/readiness.md` for final spec-plan-contract alignment before implementation sign-off.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup** has no dependencies and establishes the feature baseline.
- **Phase 2: Foundational** depends on Phase 1 and blocks all user-story work.
- **US1** depends on Phase 2.
- **US2** depends on US1 because session endpoints require stable workspace routing and ownership behavior.
- **US3** depends on US2 because conversation endpoints require stable session lifecycle and parent validation.
- **US4** depends on US1 through US3 because it consolidates shared behavior across the full management API surface.
- **US5** depends on US3 and can proceed once the conversation model and chat route contract are stable.
- **US6** depends on US5 and the completed Phase C hierarchy so reconciliation reads a stable public/runtime model.
- **US7** depends on US6 and US5 because migration relies on reconciliation visibility and mixed-traffic runtime safeguards.
- **US8** starts once Phase C tests exist, but it is only complete after US1 through US7 are complete.
- **Polish** depends on all previous phases.

### User Story Dependency Graph

- `Setup -> Foundational -> US1 -> US2 -> US3 -> US4`
- `US3 -> US5 -> US6 -> US7`
- `US1 + US2 + US3 + US4 + US5 + US6 + US7 -> US8`
- `US8 -> Polish`

### Cross-Artifact Review Gates

- `T001` and `T052` cover `spec.md <-> plan.md <-> readiness.md` alignment.
- `T005` covers `research.md <-> data-model.md <-> contracts/*.md` alignment.
- `T035` and `T050` cover `quickstart.md <-> contracts/management-api.md <-> docs/openapi.yaml` alignment.
- `T040` and `T048` cover `operator-tooling boundaries <-> public API surface` alignment.
- `T008`, `T020`, `T030`, and `T035` enforce the constitution gate that REST work is incomplete while `docs/openapi.yaml` is stale.

---

## Parallel Execution Examples

### Parallel Example: User Story 1

- `parallel-group: 2` -> `T009`, `T010`, `T011`

### Parallel Example: User Story 2

- `parallel-group: 3` -> `T015`, `T016`, `T017`

### Parallel Example: User Story 3

- `parallel-group: 4` -> `T021`, `T022`, `T023`

### Parallel Example: User Story 4

- `parallel-group: 5` -> `T027`, `T028`

### Parallel Example: User Story 5

- `parallel-group: 6` -> `T031`, `T032`, `T033`

### Parallel Example: User Story 6

- `parallel-group: 7` -> `T036`, `T038`
- sequential follow-up -> `T037`, `T039`, `T040`

### Parallel Example: User Story 7

- `parallel-group: 8` -> `T041`, `T042`, `T043`

### Parallel Example: User Story 8

- `parallel-group: 9` -> `T046`, `T047`, `T048`

---

## Implementation Strategy

### MVP First

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Validate workspace CRUD plus the first OpenAPI management contract update before proceeding.

### Incremental Delivery

1. Deliver the Phase C hierarchy in order: US1 -> US2 -> US3 -> US4.
2. Add runtime consistency through US5.
3. Add operator-only reconciliation and migration via US6 and US7.
4. Finish with US8 and Polish so the revised regression and OpenAPI gates become the release criteria.

### Notes

- `docs/openapi.yaml` work is mandatory implementation work for this feature, not optional documentation cleanup.
- The legacy `/api/sessions/{session_id}/conversation` documentation must be explicitly deprecated, replaced, or retained with migration notes; it cannot remain ambiguous.
- NFR-6.1.3 is enforced here as coverage-baseline non-regression, not as a new project-wide target.
- Operator tooling remains outside the public `/api` surface for the entire feature.