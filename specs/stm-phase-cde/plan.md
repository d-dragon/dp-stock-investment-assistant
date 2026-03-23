# Implementation Plan: STM Phase C-E - Management API, Runtime Consistency, and Test Realignment

**Branch**: `stm-phase-cde` | **Date**: 2026-03-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/stm-phase-cde/spec.md`

## Summary

Deliver Phase C, D, and E on top of the existing Phase A-B STM hierarchy by extending the current Flask blueprint, service factory, and repository layers rather than introducing a parallel stack. The plan adds management REST endpoints for workspace, session, and conversation lifecycle; makes runtime conversation metadata and checkpoint state operationally consistent; introduces operator-only reconciliation and migration tooling for legacy checkpoint traffic; and realigns the test suite so hierarchy, lifecycle, migration, and security invariants become enforced regression gates.

The plan enforces full clarified-spec coverage with an explicit traceability matrix in this document that maps every user story, functional requirement, success criterion, edge case, planning decision, and operator/security constraint to named workstreams and design artifacts. Where the implementation belongs in a later execution phase, the matrix still assigns the owning workstream and affected repository modules.

## Technical Context

**Language/Version**: Python 3.8+  
**Primary Dependencies**: Flask blueprints, Flask-SocketIO, PyMongo repositories, Redis-backed `CacheBackend`, LangGraph `MongoDBSaver`, pytest  
**Storage**: MongoDB 5.0 (`workspaces`, `sessions`, `conversations`, `agent_checkpoints`, supporting audit/report collections if added), Redis 6.2 cache  
**Testing**: pytest unit, integration, API contract, lifecycle, migration, and performance-sensitive regression suites  
**Target Platform**: Docker Compose local development and AKS-hosted Flask API in production  
**Project Type**: Web service with public REST API, Socket.IO chat, and internal operator tooling  
**Performance Goals**: SC-005 API P95 targets, SC-006 metadata visibility within 5 seconds, SC-008 reconciliation latency impact below 5 percent  
**Constraints**: No hard delete; preserve `conversation_id -> thread_id` mapping; no public exposure of reconciliation/migration tooling; mixed legacy and hierarchy-aware traffic must work during migration; NFR-6.1.3 remains a soft non-regression gate; no frontend changes in this phase  
**Existing Public API Surface**: Registered public routes currently include `/api/health`, `/api/chat`, `/api/config`, `/api/models/openai*`, and `/api/users*`; `docs/openapi.yaml` must be reconciled against this baseline before and during Phase C contract expansion because it still documents legacy session-oriented chat semantics.  
**Scale/Scope**: 8 user stories across Phase C/D/E, 39 functional requirements, 15 success criteria, 14 explicit edge cases, and a completed set of planning decisions captured below and carried through to task generation

## Constitution Check

*GATE: Pass before Phase 0 research. Re-checked after Phase 1 design.*

### Pre-Phase 0 Gate

| Check | Status | Notes |
|-------|--------|-------|
| Memory never stores facts | PASS | Phase D metadata updates stay limited to identifiers, counts, timestamps, status, symbols, and summaries already allowed by the STM model. No financial facts are introduced into memory state. |
| Repository pattern preserved | PASS | Management API, reconciliation, and migration are planned as service and repository extensions under `src/services` and `src/data/repositories`; no ad-hoc DB access in routes. |
| Immutable route context preserved | PASS | New management blueprints are planned under `src/web/routes` and will be wired through `APIRouteContext` and `ServiceFactory`, matching current API server conventions. |
| Backward compatibility addressed | PASS | Mixed-traffic migration compatibility is explicitly planned through additive migration and legacy stateless path preservation; no deprecated `session_id == thread_id` caller contract is reintroduced. |
| Logging over print | PASS | Reconciliation and migration contracts require structured logs with `correlation_id` and timestamps for scan and migration actions. |
| Test-before-merge | PASS | Phase E is a first-class workstream and includes route, lifecycle, migration, operator-path, and coverage-baseline verification. |
| Security first | PASS | Operator-only tooling is kept outside public `/api` routes and receives explicit authorization-path testing. |

### Post-Phase 1 Re-Check

| Check | Status | Notes |
|-------|--------|-------|
| Layered architecture retained | PASS | Design routes work through existing `WorkspaceService`, `SessionService`, `ConversationService`, `ChatService`, plus targeted consistency/operator services only where gaps remain. |
| Simplicity maintained | PASS | The plan avoids greenfield subsystems: management endpoints extend existing blueprints/service factory; operator entrypoints reuse the repo's `scripts/` pattern and internal Python modules. |
| Quality gates remain enforceable | PASS | Coverage matrix, operator tooling contracts, quickstart validation, and test realignment define measurable verification before tasking. |

## Project Structure

### Documentation (this feature)

```text
specs/stm-phase-cde/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── management-api.md
│   └── operator-tooling.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
docs/
└── openapi.yaml                            # Project-scoped REST contract that must be updated with Phase C endpoints and chat contract changes

src/
├── web/
│   ├── api_server.py                         # Register new management blueprints
│   └── routes/
│       ├── shared_context.py                # Reuse immutable DI context
│       ├── ai_chat_routes.py                # Extend runtime metadata and mixed-traffic handling
│       ├── workspace_routes.py              # Planned Phase C workspace endpoints
│       ├── session_routes.py                # Planned Phase C nested/direct session endpoints
│       └── conversation_routes.py           # Planned Phase C nested/direct conversation endpoints
├── services/
│   ├── factory.py                           # Wire any added management or operator services
│   ├── workspace_service.py                 # Extend for details, update, archive cascade
│   ├── session_service.py                   # Extend for parent validation, filters, close/archive policy
│   ├── conversation_service.py              # Extend for list/detail/summary/archive/consistency helpers
│   ├── chat_service.py                      # Phase D metadata synchronization and archive enforcement
│   ├── exceptions.py                        # Consistent lifecycle and validation errors
│   └── protocols.py                         # Protocol updates only if new service dependencies are required
├── data/
│   ├── repositories/
│   │   ├── workspace_repository.py          # Aggregate counts, archive/update support
│   │   ├── session_repository.py            # Filters, counts, cascade helpers, parent checks
│   │   ├── conversation_repository.py       # Summary lookup, pagination, metadata anomaly queries
│   │   └── factory.py                       # Reuse singleton wiring
│   ├── migration/
│   │   ├── db_setup.py                      # Schema/index alignment if needed
│   │   └── legacy_checkpoint_migration.py   # Planned reusable migration module
│   └── schema/
│       ├── workspaces_schema.py
│       ├── sessions_schema.py
│       ├── conversations_schema.py
│       └── agent_checkpoints_schema.py
├── utils/
│   └── service_utils.py                     # Shared pagination/response helpers if needed
└── scripts/
    ├── reconcile_stm_runtime.py             # Planned operator-only reconciliation entrypoint
    └── migrate_legacy_threads.py            # Planned operator-only migration entrypoint

tests/
├── test_workspace_service.py
├── test_session_service.py
├── test_conversation_service.py
├── test_chat_service.py
├── test_api_routes.py
├── test_chat_routes.py
├── integration/
│   ├── test_stm_runtime_wiring.py
│   ├── test_memory_persistence.py
│   └── test_management_api_contracts.py
├── performance/
│   └── test_reconciliation_impact.py
└── security/
    └── test_operator_tooling_boundaries.py
```

**Structure Decision**: Extend the existing backend service rather than creating a new API surface. Public management behaviors remain in Flask blueprints under `src/web/routes`, business rules stay in current service classes where practical, data queries remain in repositories, and operator-only reconciliation/migration execution follows the existing `scripts/` operational pattern backed by internal modules under `src/services` or `src/data/migration`.

## Planning Decisions Resolved in Phase 0

| Topic | Decision | Why This Plan Uses It |
|-------|----------|------------------------|
| Pagination defaults, max, sort order (OI-8 / FR-C08) | Offset-based pagination with `limit` and `offset`; default `limit=25`; maximum `limit=100`; workspace/session lists sort by `updated_at desc`; conversation lists sort by `last_activity_at desc`, with `updated_at desc` tie-breaker. | Fits the current Flask + repository pattern, is easy to test for idempotent GET behavior, and avoids introducing cursor complexity during the initial management API rollout. |
| Nested parent-match validation (FR-C14, FR-C15) | Nested routes validate path parent IDs against stored parent IDs and reject mismatches with the same not-found/error envelope used for out-of-hierarchy access. No silent normalization. | Preserves security boundaries without leaking resource existence and directly addresses the clarified nested-route edge case. |
| Closed vs archived session behavior | `closed` blocks new conversation creation and session-context mutation but still allows reads and messaging in existing non-archived conversations; `archived` is terminal and archives descendants. | Matches clarified spec semantics and avoids conflating growth restriction with immutability. |
| Summarized conversation semantics | `summarized` remains a resumable, listable, retrievable non-archived state; archive rules and message rejection apply only to `archived`. | Prevents runtime or management flows from accidentally treating summary as terminal state. |
| Reconciliation schedule and alert thresholds (OI-7) | Operator can run reconciliation on demand at any time; production baseline is hourly scheduled scans plus mandatory pre-migration and post-migration scans. Alerting is critical for any orphan or thread mismatch outside an active migration window, warning for repeated findings across 2 consecutive scans during migration, and critical for measured latency impact at or above 5 percent. | Converts a deferred decision into an actionable operations contract while preserving the scan-and-report-only scope. |
| Migration window and rollback strategy (OI-6) | Migration is additive and resumable. The migration window remains open until a dry-run shows zero remaining legacy records and 2 consecutive reconciliation scans are clean. Rollback means stop new migration runs, keep legacy stateless handling enabled, preserve original checkpoints, and suppress destructive cleanup until post-window sign-off. | Satisfies zero data loss, mixed-traffic compatibility, and operator safety without requiring a risky hard rollback of already-promoted metadata. |
| NFR-6.1.3 soft constraint | Phase E owns baseline measurement and non-regression enforcement for agent-core coverage, not the project-wide 80 percent target itself. | Keeps the plan aligned with the clarified assumption while still making coverage preservation testable. |

## Workstreams

### WS-C1 - Workspace Management API

- Deliver `GET /api/workspaces`, `POST /api/workspaces`, `GET /api/workspaces/{workspace_id}`, `PATCH /api/workspaces/{workspace_id}`, and `POST /api/workspaces/{workspace_id}/archive`.
- Extend `WorkspaceService` and `WorkspaceRepository` for aggregate session/conversation counts, ownership checks, update semantics, and archive cascade orchestration.
- Ensure response payloads include `workspace_id` and aggregate statistics required by User Story 1 and SC-001.

### WS-C2 - Session Management API and Lifecycle Enforcement

- Deliver nested and direct session routes under `/api/workspaces/{workspace_id}/sessions` and `/api/sessions/{session_id}` plus `POST /close` and `POST /archive` action routes.
- Reuse `SessionService` for lifecycle state machine enforcement and extend it where necessary for status-filtered pagination, parent ownership checks, and update restrictions.
- Explicitly handle closed-vs-archived semantics, archived-workspace rejection, mixed-status cascade archive, and nested parent mismatch validation.

### WS-C3 - Conversation Management API, Summary Retrieval, and Hierarchy Validation

- Deliver nested and direct conversation routes under `/api/sessions/{session_id}/conversations` and `/api/conversations/{conversation_id}` plus `POST /archive` and `GET /summary`.
- Extend `ConversationService` and `ConversationRepository` for status-filtered pagination, summary retrieval, archive reason capture, direct and nested parent-chain validation, and parent IDs in all payloads.
- Preserve `summarized` conversations as resumable, management-visible resources while keeping archive immutability strict.

### WS-C4 - Shared Management API Contract, Error Shape, and Performance Envelope

- Introduce shared route/helper behavior for pagination metadata, status filter parsing, consistent error envelopes, safe/idempotent GET handling, and archive-over-delete semantics.
- Keep route registration in `api_server.py` and dependency access through `APIRouteContext` and `ServiceFactory`.
- Begin with a public-API inventory pass against the registered blueprints so the canonical contract covers both existing endpoints (`/api/health`, `/api/chat`, `/api/config`, `/api/models/openai*`, `/api/users*`) and new Phase C management endpoints.
- Update public contract documentation and the project-scoped OpenAPI document at `docs/openapi.yaml` so Phase C route additions and any affected chat/runtime request or response changes are reflected in the canonical REST contract.
- Reconcile existing OpenAPI drift as part of Phase C planning and execution, including the move from legacy `session_id` chat semantics to `conversation_id`, current archived-conversation conflict behavior, and the disposition of any legacy `/api/sessions/{session_id}/conversation` documentation that no longer matches the intended public surface.
- Phase 5 task generation MUST include explicit work items for `docs/openapi.yaml` updates, review, and verification against implemented route behavior; this is not optional documentation cleanup.

### WS-D1 - Runtime Metadata Consistency in Chat Flow

- Extend `ai_chat_routes.py`, `ChatService`, and `ConversationService` so a conversation metadata record exists before agent execution, user and assistant turns update counts/timestamps/tokens, focused symbols are merged, and archived conversations reject messaging.
- Preserve mixed traffic by allowing legacy stateless requests during the migration window without reintroducing `session_id == thread_id` semantics.
- Treat checkpoint and metadata persistence as coordinated but distinct writes, and feed residual write failures into reconciliation rather than dropping the chat response.

### WS-D2 - Reconciliation Scan, Report, and Execution Logging

- Implement operator-only reconciliation logic that detects orphan sessions, orphan conversations, missing checkpoint metadata pairs, missing checkpoint records, and `thread_id != conversation_id` anomalies.
- Emit machine-readable JSON reports and separate structured scan logs with `correlation_id`, timestamps, counts, and suggested remediations.
- Design scan execution to be read-heavy, chunked, and schedulable so chat latency impact stays within SC-008 and FR-D09.

### WS-D3 - Legacy Migration, Auditability, and Mixed-Traffic Safety

- Implement an additive, resumable migration that promotes legacy session-keyed checkpoint threads to conversation metadata without losing checkpoint accessibility.
- Provide dry-run preview, execution audit log, resume cursor/state, and post-run validation hooks using reconciliation.
- Keep legacy stateless requests and new hierarchy-aware requests functioning throughout the migration window, and define cleanup/rollback conditions explicitly.

### WS-E1 - Public API and Lifecycle Test Realignment

- Replace legacy route and service assertions with hierarchy-aware tests covering workspace/session/conversation CRUD, nested parent validation, lifecycle transitions, archive cascades, payload IDs, and error shape parity.
- Add direct tests for the clarified edge cases: closed session update rejection, conversation creation in closed sessions, session creation in archived workspaces, zero-result pagination, and repeated archive behavior.

### WS-E2 - Runtime Consistency, Operator Boundary, and Coverage Hardening

- Add regression tests for metadata/checkpoint alignment, reconciliation anomaly detection, migration dry-run and resume behavior, mixed-traffic compatibility, operator-only execution paths, and archived conversation immutability.
- Track agent-core coverage baseline during Phase E to prevent violating the NFR-6.1.3 soft constraint.

## Sequencing and Parallelization

### Sequence

1. Finalize Phase C/D planning decisions and contracts in `research.md`, `data-model.md`, and `contracts/`.
2. Implement WS-C4 shared contract helpers first so WS-C1, WS-C2, and WS-C3 use one pagination, error, and validation model.
3. Execute WS-C1, WS-C2, and WS-C3 in parallel after shared contract alignment, because the existing service classes already split by domain.
4. Start WS-D1 in parallel with Phase C endpoint delivery because it depends on chat flow and conversation services rather than on public management routes.
5. Start WS-E1 as soon as the Phase C route contracts are stable; do not defer route contract testing until the end.
6. After Phase C routing and lifecycle semantics are stable, execute WS-D2 reconciliation.
7. Execute WS-D3 migration after WS-D2 establishes detection/reporting and while WS-D1 mixed-traffic compatibility remains active.
8. Close with WS-E2 performance, migration, operator-boundary, and coverage non-regression verification.

### Parallelizable Work

- WS-C1, WS-C2, and WS-C3 are parallelizable after WS-C4 defines shared response/error/pagination behavior.
- WS-D1 can run in parallel with WS-C1 through WS-C3.
- WS-E1 can run in parallel with Phase C implementation and continue incrementally.
- WS-D2 report design can begin before full implementation to lock operator contracts, but scan logic should follow Phase C data-read stability.
- WS-D3 dry-run and audit path design can proceed while WS-D2 is implemented, but actual migration execution logic depends on reconciliation outputs and mixed-traffic guardrails from WS-D1.

## Risks and Mitigations

| Risk | Why It Matters | Mitigation in This Plan |
|------|----------------|-------------------------|
| Existing services do not fully satisfy exact management API contracts | Phase A-B foundation is present, but route-layer and service method gaps can cause scope creep. | WS-C1 through WS-C4 are scoped around extending current services first, and `contracts/management-api.md` fixes exact behaviors before tasks are written. |
| Cascade archive is hard to keep atomic across parent and descendants | Parent archive semantics drive SC-004 and several edge cases. | WS-C2 and WS-C3 explicitly own archive orchestration, repeated-archive idempotence, and mixed-status descendants; tests in WS-E1 validate zero non-archived descendants post-archive. |
| Runtime metadata writes can drift from checkpoint writes under partial failure | This is the core operational risk of Phase D. | WS-D1 preserves chat delivery, records residual drift for reconciliation, and WS-D2 scans for resulting anomalies. |
| Reconciliation scans can degrade chat traffic | FR-D09 and SC-008 create a hard operational guardrail. | WS-D2 constrains scans to chunked read patterns with schedule thresholds defined in research; WS-E2 adds performance verification. |
| Migration can break mixed traffic or silently orphan data | FR-D10 through FR-D15 and SC-009 through SC-012 depend on safe promotion. | WS-D3 uses additive dry-run-first migration, audit logging, resume state, pre/post reconciliation, and explicit rollback rules. |
| Legacy `session_id == thread_id` assertions remain in test code | This would undermine the Phase A-B identity model and block reliable regression coverage. | WS-E1 and WS-E2 explicitly replace those assertions with `conversation_id == thread_id` checks and operator-path tests. |

## Coverage Matrix

### User Stories to Workstreams

| Spec Item | Covered By | Handling |
|-----------|------------|----------|
| User Story 1 | WS-C1, WS-C4, WS-E1 | Workspace CRUD, ownership enforcement, aggregate details, archive cascade, contract tests. |
| User Story 2 | WS-C2, WS-C4, WS-E1 | Session CRUD, lifecycle transitions, close-vs-archive semantics, parent validation, cascade tests. |
| User Story 3 | WS-C3, WS-C4, WS-E1 | Conversation CRUD, nested/direct hierarchy validation, archive reason, summary retrieval, parent chain tests. |
| User Story 4 | WS-C4, WS-E1 | Pagination, archive-over-delete, cascade behavior, error shape parity, idempotent GETs, performance assertions. |
| User Story 5 | WS-D1, WS-E2 | Metadata auto-create, message/token updates, focused symbol merges, archived-message rejection, coordinated writes. |
| User Story 6 | WS-D2, WS-E2 | Orphan and mismatch detection, JSON report contract, idempotent scans, non-blocking execution. |
| User Story 7 | WS-D3, WS-E2 | Dry-run, additive migration, audit trail, resumability, zero-loss promotion, mixed-traffic compatibility. |
| User Story 8 | WS-E1, WS-E2 | Hierarchy, STM isolation, lifecycle, consistency, operator-path, and legacy-assertion replacement coverage. |

### Functional Requirements to Workstreams

| Requirement IDs | Covered By | Planned Handling |
|-----------------|------------|------------------|
| FR-C01, FR-C02, FR-C13, FR-C17 | WS-C1, WS-C4, WS-E1 | Public workspace endpoints rooted at `/api/workspaces`, ownership enforcement, payload IDs, list/detail/update/archive contracts. |
| FR-C03, FR-C04, FR-C05, FR-C14 | WS-C2, WS-C4, WS-E1 | Nested and direct session endpoints, lifecycle order enforcement, parent-workspace validation, nested path mismatch rejection. |
| FR-C06, FR-C07, FR-C15, FR-C16 | WS-C3, WS-C4, WS-E1 | Nested and direct conversation endpoints, full ownership chain checks, POST archive action, summary endpoint, session-path mismatch rejection. |
| FR-C08, FR-C11, FR-C12 | WS-C4, WS-E1 | Offset pagination contract, chat-shaped error responses, safe/idempotent GET behavior, zero-result pagination handling, synchronized `docs/openapi.yaml` contract updates, and reconciliation of pre-existing public endpoint documentation with actual registered routes. |
| FR-C09, FR-C10 | WS-C2, WS-C3, WS-C4, WS-E1 | Archive-over-delete semantics and parent-to-descendant archive cascade. |
| FR-D01, FR-D02, FR-D03, FR-D04, FR-D05 | WS-D1, WS-E2 | Auto-create conversation metadata, per-turn counters/timestamps/tokens, focused symbol accumulation, coordinated checkpoint/metadata cycle. |
| FR-D06, FR-D07, FR-D08, FR-D08a, FR-D09 | WS-D2, WS-E2 | Reconciliation anomaly detection, JSON report generation, structured scan action logging, non-blocking scan design and verification. |
| FR-D10, FR-D11, FR-D12, FR-D13, FR-D14, FR-D15 | WS-D3, WS-D1, WS-E2 | Additive legacy migration, dry-run preview, audit logging with `correlation_id`, resumability, zero-loss preservation, mixed-traffic support during the migration window. |
| FR-E01, FR-E02, FR-E03, FR-E04, FR-E05, FR-E06 | WS-E1, WS-E2 | Hierarchy, STM isolation, lifecycle, consistency, identity-model realignment, and operator-only boundary regression coverage. |

### Success Criteria to Workstreams

| Success Criteria | Covered By | Planned Verification |
|------------------|------------|----------------------|
| SC-001 | WS-C1, WS-E1 | Workspace CRUD route tests and contract verification. |
| SC-002 | WS-C2, WS-E1 | Session lifecycle and parent-validation tests. |
| SC-003 | WS-C3, WS-E1 | Conversation CRUD and full ownership chain tests. |
| SC-004 | WS-C2, WS-C3, WS-E1 | Cascade archive tests at workspace and session boundaries. |
| SC-005 | WS-C4, WS-E2 | Quickstart verification and targeted performance checks for GET/list/mutate/archive latency goals. |
| SC-006 | WS-D1, WS-E2 | Chat-flow metadata visibility checks within 5 seconds. |
| SC-007 | WS-D2, WS-E2 | Seeded anomaly reconciliation tests against JSON report output. |
| SC-008 | WS-D2, WS-E2 | Reconciliation latency-impact tests and alert thresholds. |
| SC-009 | WS-D3, WS-E2 | Zero-loss migration validation against pre-migration checkpoint accessibility. |
| SC-010 | WS-D3, WS-E2 | Dry-run proves planned changes without writes. |
| SC-011 | WS-D3, WS-E2 | Interrupted-and-resumed migration equivalence tests. |
| SC-012 | WS-D1, WS-D3, WS-E2 | Mixed legacy stateless and hierarchy-aware traffic tests during migration. |
| SC-013 | WS-E1, WS-E2 | Full suite passes with `conversation_id == thread_id` assertions replacing legacy assumptions. |
| SC-014 | WS-D2, WS-D3, WS-E2 | Operator-only tooling boundary tests and no public management exposure. |
| SC-015 | WS-C2, WS-C3, WS-D1, WS-E1 | Archived-message rejection and archived/closed creation constraints. |

### Existing Public API and OpenAPI Reconciliation

| Existing Surface Item | Covered By | Planned Handling |
|-----------------------|------------|------------------|
| `/api/health` | WS-C4, WS-E1 | Retain in `docs/openapi.yaml` and verify it remains registered and unchanged unless intentionally revised. |
| `/api/chat` | WS-C4, WS-D1, WS-E2 | Update canonical contract from legacy `session_id` wording to conversation-aware request/response semantics, including archived-conversation conflict behavior and metadata visibility expectations. |
| `/api/config` | WS-C4 | Keep documented alongside Phase C additions so OpenAPI remains a full public API document rather than a feature-only appendix. |
| `/api/models/openai*` | WS-C4 | Preserve and verify existing model-management paths in the contract while adding new management endpoints. |
| `/api/users*` | WS-C4 | Preserve and verify existing user endpoints in the contract while adding new management endpoints. |
| Legacy `/api/sessions/{session_id}/conversation` documentation | WS-C4, WS-E1 | Decide explicitly whether to deprecate, replace, or retain this documented surface based on the actual registered routes and migration policy; tasks must not leave it ambiguous in `docs/openapi.yaml`. |

### Edge Cases, Assumptions, and Operator/Security Constraints

| Item | Covered By | Handling |
|------|------------|----------|
| Concurrent archive and message | WS-D1, WS-C2, WS-C3, WS-E2 | Archive state wins at request processing time; chat rejects if conversation is archived before message acceptance completes. |
| Archive already-archived resource | WS-C2, WS-C3, WS-E1 | Repeated archive remains a no-op on archived state and descendants; duplicate POST semantics are documented as non-deduplicated but safe. |
| Update closed session context | WS-C2, WS-E1 | Closed session blocks context mutation while remaining readable. |
| Create conversation in closed session | WS-C2, WS-C3, WS-E1 | Route/service validation rejects creation with clear lifecycle error. |
| Create session in archived workspace | WS-C1, WS-C2, WS-E1 | Workspace lifecycle validation blocks child creation. |
| Cascade archive with mixed statuses | WS-C2, WS-C3, WS-E1 | Non-archived descendants transition; already-archived descendants remain unchanged. |
| Pagination with zero results | WS-C4, WS-E1 | Responses still return `items`, `total`, `limit`, and `offset` metadata. |
| Invalid parent chain on conversation creation | WS-C3, WS-C4, WS-E1 | Reject using secure not-found/error envelope without leaking parent existence. |
| Reconciliation during heavy traffic | WS-D2, WS-E2 | Read-only chunked scans plus latency impact testing and threshold-based alerting. |
| Migration of partially migrated data | WS-D3, WS-E2 | Resume cursor and skip logic make repeated runs safe and deterministic. |
| Metadata update failure during chat | WS-D1, WS-D2, WS-E2 | Deliver chat response, record drift for reconciliation, do not hide failure from operational logs. |
| Orphan with ambiguous parent | WS-D2, WS-E2 | Report as manual remediation only; no auto-linking in this feature. |
| Dry-run with no legacy data | WS-D3, WS-E2 | Dry-run returns zero planned changes and zero writes. |
| Conversation with thread_id mismatch | WS-D2, WS-E2 | Reconciliation flags integrity anomaly explicitly. |
| Assumption: Phase A-B foundation exists and should be reused | WS-C1 through WS-D3 | Plan extends current `WorkspaceService`, `SessionService`, `ConversationService`, `ChatService`, repositories, and route registration. |
| Assumption: Phase C may require minimal service/validation updates | WS-C1 through WS-C4 | Explicitly assigned to service-extension workstreams rather than treated as out of scope. |
| Assumption: Phase D metadata tracking may run in parallel with Phase C | WS-D1 | Sequencing section preserves this parallel path. |
| Assumption: Reconciliation is scan-and-report only | WS-D2 | Operator contract excludes repair execution. |
| Assumption: Reconciliation and migration require elevated/operator paths | WS-D2, WS-D3, WS-E2 | Contract and security tests keep tooling outside public `/api` endpoints. |
| OI-6 migration window and rollback strategy | WS-D3 | Resolved in planning decisions and operator tooling contract. |
| OI-7 reconciliation schedule and alerting thresholds | WS-D2 | Resolved in planning decisions and operator tooling contract. |
| OI-8 pagination defaults, max page size, sort order | WS-C4 | Resolved in planning decisions and management API contract. |
| NFR-6.1.3 soft coverage constraint | WS-E2 | Coverage baseline measurement and non-regression are mandatory task outputs. |

## Phase Outputs

### Phase 0 - Research

- `research.md` resolves all planning-level decisions deferred by the spec: pagination defaults and limits, nested mismatch behavior, summarized and closed-session semantics in runtime/API flows, reconciliation schedule and thresholds, migration window and rollback rules, and coverage-baseline handling.

### Phase 1 - Design and Contracts

- `data-model.md` captures lifecycle state machines, invariants, consistency rules, anomaly/report entities, and migration run-state design.
- `contracts/management-api.md` defines the public REST surface, payload contracts, pagination metadata, and error shape rules.
- `contracts/operator-tooling.md` defines internal-only reconciliation and migration contracts, logging/audit requirements, and execution boundaries.
- `quickstart.md` defines how implementation should be validated locally without changing frontend code.
- `docs/openapi.yaml` is a mandatory implementation-adjacent deliverable for Phase C and must be called out explicitly in downstream tasks as the project-scoped REST contract to keep in sync with route changes.
- The OpenAPI work includes reconciliation of the already-registered public API surface, not only new Phase C endpoints, so existing chat/config/model/user contracts remain accurate while management endpoints are introduced.

## Complexity Tracking

No constitution violations or extra complexity exemptions are required for this plan.
