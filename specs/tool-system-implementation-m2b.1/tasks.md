---
description: "Task list for Tool Contract and Gateway Baseline - M2B.1"
---

# Tasks: Tool Contract and Gateway Baseline - M2B.1

**Input**: Design documents from `specs/tool-system-implementation-m2b.1/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`, `contracts/`, `checklists/requirements.md`, `checklists/requirements-alignment.md`

**Tests**: Included. This feature requires test-first tasks plus explicit test execution tasks for descriptor inventory, route-filtered surfaces, gateway admission, runtime compatibility, safe trace metadata, explicit `NFR-6.1.3`/`NFR-6.1.4` coverage gates, and sync verification.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently after the shared foundation is complete.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches a different file or has no dependency on incomplete tasks.
- **[Story]**: Required only for user-story phases.
- Every task names an exact file path or executable artifact path.

## Path Conventions

- Backend Python source: `src/`
- Backend tests: `tests/`
- Feature artifacts: `specs/tool-system-implementation-m2b.1/`
- Long-lived docs and sync artifacts: `docs/`, `specs/spec-traceability.yaml`, `specs/spec-sync-status.md`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the M2B.1 implementation and test surfaces without changing runtime behavior.

- [ ] T001 Create `tests/test_tool_gateway_m2b1.py` with shared pytest fixtures for `ToolRegistry`, mock cache, mock data manager, mock symbol repository, and all `StockQueryRoute` values
- [ ] T002 [P] Create `src/core/tools/descriptors.py` module scaffold for M2B.1 capability and policy descriptors
- [ ] T003 [P] Create `src/core/tools/surface.py` module scaffold for route-filtered tool surface construction
- [ ] T004 [P] Create `src/core/tools/gateway.py` module scaffold for thin gateway admission, degraded states, and trace metadata
- [ ] T005 Update `src/core/tools/__init__.py` to export the M2B.1 descriptor, surface, and gateway symbols after the modules exist

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define shared data structures and validation primitives used by all user stories.

**Critical**: No user story implementation can begin until this phase is complete.

- [ ] T006 [P] Define descriptor enums and dataclasses in `src/core/tools/descriptors.py` for `ToolCapabilityDescriptor`, `ToolPolicyDescriptor`, baseline inventory state, exposure status, license mode, risk class, and mutation policy
- [ ] T007 [P] Define `RouteSurfaceRequest` and `RouteFilteredToolSurface` dataclasses in `src/core/tools/surface.py` with fields from `specs/tool-system-implementation-m2b.1/data-model.md`
- [ ] T008 [P] Define `GatewayAdmissionDecision`, `ToolTraceRecord`, and `DegradedToolResult` dataclasses in `src/core/tools/gateway.py` with fields from `specs/tool-system-implementation-m2b.1/contracts/gateway-admission-trace-contract.md`
- [ ] T009 Implement deterministic canonical descriptor hashing in `src/core/tools/descriptors.py` that excludes generated hash fields from the canonical hash input
- [ ] T010 Implement descriptor validation helpers in `src/core/tools/descriptors.py` for missing descriptors, duplicate tool names, malformed fields, forbidden model-visible fields, descriptor drift, and policy/capability mismatch
- [ ] T011 Add foundational import and dataclass construction tests in `tests/test_tool_gateway_m2b1.py` for `src/core/tools/descriptors.py`, `src/core/tools/surface.py`, and `src/core/tools/gateway.py`

**Checkpoint**: Foundation ready. Descriptor, surface, and gateway code can now be tested independently.

---

## Phase 3: User Story 1 - Existing Tools Have Governed Descriptors (Priority: P1) MVP

**Goal**: `StockSymbolTool`, `TradingViewTool`, and `ReportingTool` each have reviewed capability and policy descriptors while current registry-backed behavior remains compatible.

**Independent Test**: Run only descriptor-focused tests in `tests/test_tool_gateway_m2b1.py`; verify all three baseline tools have safe capability descriptors, internal policy descriptors, descriptor hashes, disabled/non-exposed placeholder status where applicable, and no model-visible internal policy leakage.

**SRS mapping**: `M2B1-FR-001`, `M2B1-FR-002`, `M2B1-FR-003`, `M2B1-FR-004`, `M2B1-FR-009`, `M2B1-FR-010`, `M2B1-FR-014`, `M2B1-FR-018`; `SC-001`, `SC-002`, `SC-005`, `SC-010`.

### Tests for User Story 1

- [ ] T012 [US1] Add descriptor inventory tests in `tests/test_tool_gateway_m2b1.py` verifying `StockSymbolTool`, `TradingViewTool`, and `ReportingTool` each have capability and policy descriptors with descriptor version and hash
- [ ] T013 [US1] Add model-visible descriptor safety tests in `tests/test_tool_gateway_m2b1.py` verifying capability descriptors exclude credentials, credential owner, provider fallback rules, parser limits, internal license policy, timeout internals, provider details, and raw gateway traces
- [ ] T014 [US1] Add placeholder and scaffold descriptor tests in `tests/test_tool_gateway_m2b1.py` verifying `TradingViewTool` is disabled/non-exposed and `ReportingTool` scaffold status is explicit unless policy admits a non-mutating route
- [ ] T015 [US1] Add descriptor integrity tests in `tests/test_tool_gateway_m2b1.py` verifying hash drift, policy/capability mismatch, missing descriptor, and duplicate tool name fail closed

### Implementation for User Story 1

- [ ] T016 [US1] Implement baseline descriptor inventory in `src/core/tools/descriptors.py` for `stock_symbol`, `tradingview`, and `reporting` using the exact baseline expectations from `specs/tool-system-implementation-m2b.1/contracts/tool-descriptor-contract.md`
- [ ] T017 [US1] Implement `get_baseline_tool_descriptors()` and descriptor lookup helpers in `src/core/tools/descriptors.py` keyed by current tool names from `src/core/tools/stock_symbol.py`, `src/core/tools/tradingview.py`, and `src/core/tools/reporting.py`
- [ ] T018 [US1] Implement `validate_descriptor_inventory()` in `src/core/tools/descriptors.py` to return machine-detectable validation outcomes for missing, invalid, drifted, disabled, and non-exposed descriptors
- [ ] T019 [US1] Preserve descriptor compatibility seams in `src/core/tools/base.py` by keeping descriptor support outside `_execute()` and cache contract behavior
- [ ] T020 [US1] Preserve registry execution compatibility in `src/core/tools/registry.py` by keeping descriptor and gateway metadata outside registration and invocation semantics
- [ ] T021 [US1] Preserve `StockSymbolTool` execution compatibility in `src/core/tools/stock_symbol.py` by keeping descriptor support outside current tool behavior
- [ ] T022 [US1] Preserve `TradingViewTool` placeholder compatibility in `src/core/tools/tradingview.py` by keeping disabled and non-exposed descriptor state outside current runtime behavior
- [ ] T023 [US1] Preserve `ReportingTool` execution compatibility in `src/core/tools/reporting.py` by keeping descriptor support outside the current non-mutating behavior

**Checkpoint**: US1 complete. Descriptor inventory is complete and current tool behavior is unchanged.

---

## Phase 4: User Story 2 - Route-Filtered Tool Exposure Before Agent Invocation (Priority: P1)

**Goal**: The assistant receives only route-eligible, descriptor-valid, policy-admitted, enabled tools before each ReAct invocation.

**Independent Test**: Run route-surface tests for `price_check`, `technical_analysis`, `fundamentals`, `market_watch`, `portfolio`, `news_analysis`, `ideas`, and `general_chat`; verify unsupported routes expose no scaffolded substitute and internal filter reasons are retained outside the model-visible surface.

**SRS mapping**: `M2B1-FR-005`, `M2B1-FR-006`, `M2B1-FR-015`, `M2B1-FR-016`; `SC-003`, `SC-010`.

**Depends on**: Phase 2 and US1 descriptor inventory.

### Tests for User Story 2

- [ ] T024 [US2] Add route fixture tests in `tests/test_tool_gateway_m2b1.py` verifying all eight `StockQueryRoute` values produce the expected M2B.1 tool surface
- [ ] T025 [US2] Add filtering tests in `tests/test_tool_gateway_m2b1.py` verifying disabled, internal-only, feature-flag-blocked, context-blocked, risk-blocked, and license-blocked tools are hidden
- [ ] T026 [US2] Add unsupported-route tests in `tests/test_tool_gateway_m2b1.py` verifying routes without admitted M2B.1 tools expose an empty tool list instead of scaffolded or unrelated substitutes
- [ ] T027 [US2] Add provider-adapter isolation tests in `tests/test_tool_gateway_m2b1.py` verifying provider adapter names and filter reasons do not appear in model-visible descriptor fields
- [ ] T028 [US2] Add agent wiring tests in `tests/test_tool_gateway_m2b1.py` verifying `StockAssistantAgent` builds the filtered tool surface before calling the ReAct invocation path

### Implementation for User Story 2

- [ ] T029 [US2] Implement `ToolSurfaceBuilder` in `src/core/tools/surface.py` with inputs from `RouteSurfaceRequest` and outputs from `RouteFilteredToolSurface`
- [ ] T030 [US2] Implement route, locale, feature flag, available context, registry enablement, descriptor integrity, model visibility, risk class, and license filtering in `src/core/tools/surface.py`
- [ ] T031 [US2] Implement `surface_hash`, exposed tool descriptor versions, hidden tool names, and internal filter reasons in `src/core/tools/surface.py`
- [ ] T032 [US2] Add optional `stock_query_router` and `tool_surface_builder` dependencies to `StockAssistantAgent.__init__()` in `src/core/stock_assistant_agent.py` while preserving current defaults
- [ ] T033 [US2] Add per-query route classification and tool-surface construction to `StockAssistantAgent.process_query()`, `StockAssistantAgent.process_query_structured()`, and `StockAssistantAgent.process_query_streaming()` in `src/core/stock_assistant_agent.py`
- [ ] T034 [US2] Update `StockAssistantAgent._build_agent_executor()` or a new per-turn executor helper in `src/core/stock_assistant_agent.py` to pass only the filtered tool list to `create_agent()` using the existing single ReAct runtime pattern

**Checkpoint**: US2 complete. ReAct receives a route-filtered tool surface before model invocation.

---

## Phase 5: User Story 3 - Gateway Admission Blocks Unsafe Tool Calls (Priority: P1)

**Goal**: Selected tool calls pass through a thin in-process admission boundary before registry-backed execution.

**Independent Test**: Submit allowed and denied fixture calls through `ToolGateway`; verify allowed calls execute exactly once through `ToolRegistry`, denied calls do not execute the underlying tool, and all denials produce machine-detectable degraded states.

**SRS mapping**: `M2B1-FR-007`, `M2B1-FR-008`, `M2B1-FR-009`, `M2B1-FR-010`, `M2B1-FR-011`, `M2B1-FR-017`; `SC-004`, `SC-005`, `SC-009`.

**Depends on**: Phase 2 and US1 descriptors. Final agent wiring depends on the US2 route-surface outputs.

### Tests for User Story 3

- [ ] T035 [US3] Add allowed-call gateway tests in `tests/test_tool_gateway_m2b1.py` verifying an admitted `stock_symbol` call executes through the current `ToolRegistry` path exactly once
- [ ] T036 [US3] Add denial tests in `tests/test_tool_gateway_m2b1.py` for unknown tool, unexposed tool, disallowed route-tool combination, invalid arguments, blocked risk class, unclear license posture, missing timeout budget, and exceeded timeout budget
- [ ] T037 [US3] Add descriptor drift and policy mismatch admission tests in `tests/test_tool_gateway_m2b1.py` verifying drifted capability or policy descriptors block exposure or execution
- [ ] T038 [US3] Add provider, cache, and freshness admission tests in `tests/test_tool_gateway_m2b1.py` verifying applicable failures degrade and non-applicable fields are marked safely as `not_applicable`
- [ ] T039 [US3] Add degraded result contract tests in `tests/test_tool_gateway_m2b1.py` verifying denied calls return stable machine codes, safe messages, `execute_underlying_tool=false`, and internal trace records

### Implementation for User Story 3

- [ ] T040 [US3] Implement `ToolGateway.evaluate_admission()` in `src/core/tools/gateway.py` for selected tool, route-tool match, descriptor integrity, registry state, argument validity, risk class, license posture, freshness state, provider or cache state, and timeout budget
- [ ] T041 [US3] Implement argument schema validation in `src/core/tools/gateway.py` using the selected tool capability descriptor input schema before any underlying tool execution
- [ ] T042 [US3] Implement deny-by-default policy outcomes in `src/core/tools/gateway.py` for missing descriptors, descriptor drift, route mismatch, disabled/non-exposed tool state, license uncertainty, unsupported risk, provider/cache/freshness failure, and timeout breach
- [ ] T043 [US3] Implement registry-backed allowed execution in `src/core/tools/gateway.py` by invoking the existing registered `CachingTool` from `src/core/tools/registry.py` without replacing `ToolRegistry`
- [ ] T044 [US3] Implement LangChain-compatible gateway wrapper creation in `src/core/tools/gateway.py` so the ReAct model sees admitted wrappers while execution still flows through the registry-backed tool instance
- [ ] T045 [US3] Wire `ToolGateway` into `StockAssistantAgent` filtered tool construction in `src/core/stock_assistant_agent.py` without introducing a remote service or second agent runtime

**Checkpoint**: US3 complete. Unsafe tool calls fail closed before execution.

---

## Phase 6: User Story 4 - Runtime Compatibility and Auditability (Priority: P1)

**Goal**: Preserve the current ReAct execution model while adding internal trace records for exposed tools, selected tools, descriptor identities, admission outcomes, latency, cache/freshness status, warnings, and degraded states.

**Independent Test**: Run compatibility and trace fixtures at the shared agent/tool boundary; verify registry-backed execution remains in use, no second runtime or remote gateway is introduced, at least 95% of governed runs have required trace fields, and public surfaces expose only safe degraded-state or warning metadata.

**SRS mapping**: `M2B1-FR-011`, `M2B1-FR-012`, `M2B1-FR-013`, `M2B1-FR-016`, `M2B1-FR-017`; `SC-002`, `SC-006`, `SC-007`, `SC-008`, `SC-009`, `SC-010`.

**Depends on**: US2 route-surface outputs and US3 gateway admission.

### Tests for User Story 4

- [ ] T046 [US4] Add runtime compatibility tests in `tests/test_tool_gateway_m2b1.py` verifying allowed tool calls still use `ToolRegistry`, `CachingTool`, and the current `create_agent()` ReAct pattern
- [ ] T047 [US4] Add trace completeness tests in `tests/test_tool_gateway_m2b1.py` verifying at least 95% of governed tool runs include required `ToolTraceRecord` fields and conditionally applicable fields are populated or marked `not_applicable`
- [ ] T048 [US4] Add trace secrecy tests in `tests/test_tool_gateway_m2b1.py` verifying traces exclude secrets, credentials, raw provider policy details, raw provider payloads, raw HTML/PDF content, and sensitive user data
- [ ] T049 [US4] Add public metadata safety tests in `tests/test_tool_gateway_m2b1.py` verifying public response metadata contains only safe degraded-state status or warning categories and no internal gateway trace details
- [ ] T050 [US4] Add performance and route-reduction tests in `tests/test_tool_gateway_m2b1.py` marked `@pytest.mark.performance` verifying route-surface construction plus gateway admission stays under 50 ms for representative non-provider flows and filtered surfaces reduce model-visible tool candidates by at least 20% versus the unfiltered M2B.1 baseline inventory where the baseline has more than one candidate

### Implementation for User Story 4

- [ ] T051 [US4] Implement internal `ToolTraceRecord` creation and latency measurement in `src/core/tools/gateway.py` and `src/core/tools/surface.py`
- [ ] T052 [US4] Implement safe trace sanitization in `src/core/tools/gateway.py` to remove secrets, credentials, sensitive user data, raw provider policy, raw payloads, and parser internals
- [ ] T053 [US4] Add internal trace propagation to `StockAssistantAgent.process_query_structured()` metadata in `src/core/stock_assistant_agent.py` while keeping raw trace records out of public REST, SSE, and WebSocket payloads
- [ ] T054 [US4] Add safe degraded-state and warning summary helper in `src/core/tools/gateway.py` for optional public metadata when existing response surfaces already support safe metadata
- [ ] T055 [US4] Preserve Socket.IO lifecycle parity as out of scope by keeping M2B.1 verification focused on shared agent/tool boundary tests in `tests/test_tool_gateway_m2b1.py`

**Checkpoint**: US4 complete. Runtime behavior is compatible and internal traces are auditable.

---

## Phase 7: Verification, Documentation, and Sync

**Purpose**: Execute feature verification, reconcile docs only after implementation evidence exists, and regenerate sync reports.

### Test Execution

- [ ] T056 Run descriptor validation tests with `pytest tests/test_tool_gateway_m2b1.py -k descriptor -q` and record results in `specs/tool-system-implementation-m2b.1/review.md`
- [ ] T057 Run route-surface validation tests with `pytest tests/test_tool_gateway_m2b1.py -k route_surface -q` and record results in `specs/tool-system-implementation-m2b.1/review.md`
- [ ] T058 Run gateway-admission validation tests with `pytest tests/test_tool_gateway_m2b1.py -k gateway_admission -q` and record results in `specs/tool-system-implementation-m2b.1/review.md`
- [ ] T059 Run trace, safety, and performance validation tests with `pytest tests/test_tool_gateway_m2b1.py -k "trace or public_metadata or performance" -q` and record results in `specs/tool-system-implementation-m2b.1/review.md`
- [ ] T060 Run compatibility tests with `pytest tests/test_tools.py tests/test_stock_query_router.py tests/test_agent_regression.py -q` and record results in `specs/tool-system-implementation-m2b.1/review.md`
- [ ] T061 Run touched agent-core coverage gate for `NFR-6.1.3` with `pytest tests/test_tool_gateway_m2b1.py tests/test_stock_query_router.py tests/test_agent_regression.py --cov=src/core/stock_assistant_agent.py --cov=src/core/stock_query_router.py --cov-fail-under=80 -q` and record results in `specs/tool-system-implementation-m2b.1/review.md`
- [ ] T062 Run tool-layer coverage gate for `NFR-6.1.4` with `pytest tests/test_tool_gateway_m2b1.py tests/test_tools.py --cov=src/core/tools --cov-fail-under=70 -q` and record results in `specs/tool-system-implementation-m2b.1/review.md`
- [ ] T063 Run repository coverage baseline with `pytest tests/ --cov=src --cov-fail-under=56 -q` and record results in `specs/tool-system-implementation-m2b.1/review.md`

### Documentation and Contract Sync

- [ ] T064 Update `specs/tool-system-implementation-m2b.1/quickstart.md` if final executable verification commands differ from the implemented test layout
- [ ] T065 Update `specs/spec-traceability.yaml` with final implementation evidence paths, task completion status, and lifecycle status after all implementation tasks are complete
- [ ] T066 Update `docs/domains/agent/TECHNICAL_DESIGN.md` and `docs/domains/agent/ARCHITECTURE_DESIGN.md` only after verification if stable M2B.1 realization details need promotion from `specs/tool-system-implementation-m2b.1/`
- [ ] T067 Confirm `docs/openapi.yaml` remains unchanged for M2B.1 or update it only if safe public degraded-state or warning metadata changes a public REST contract
- [ ] T068 Validate section-level anchors referenced from `specs/tool-system-implementation-m2b.1/spec.md`, `specs/tool-system-implementation-m2b.1/plan.md`, `specs/tool-system-implementation-m2b.1/tasks.md`, and `docs/domains/agent/SRS_SPEC_TRACEABILITY.md`
- [ ] T069 Run `python scripts/sync_spec_status.py --gate` to regenerate `specs/spec-sync-status.md` and `docs/domains/agent/SRS_SPEC_TRACEABILITY.md`
- [ ] T070 Run post-implementation Spec Kit verification and write final findings to `specs/tool-system-implementation-m2b.1/review.md` before marking the feature verified

---

## Dependencies and Execution Order

### Phase Dependencies

- **Phase 1**: No dependencies.
- **Phase 2**: Depends on Phase 1.
- **US1**: Depends on Phase 2.
- **US2**: Depends on Phase 2 and US1 descriptors.
- **US3**: Core gateway admission depends on US1 descriptors; final agent wiring depends on US2 route surface outputs.
- **US4**: Depends on US2 route surface and US3 gateway admission.
- **Phase 7**: Depends on all selected user stories.

### User Story Dependencies

- **US1** is the MVP and prerequisite for every later story because route filtering and admission require reviewed descriptors.
- **US2** can start once US1 descriptor validation is available.
- **US3** core gateway logic can start once US1 descriptors are available; `StockAssistantAgent` gateway wiring completes only after US2 produces route-surface outputs.
- **US4** can start once US2 and US3 expose traceable route-surface and gateway outcomes.

### Within Each User Story

- Write tests first and verify they fail for the missing behavior before implementation.
- Implement data structures before builders and gateway logic.
- Wire `StockAssistantAgent` after descriptor, surface, and gateway unit tests pass.
- Run the story-specific verification command before advancing to the next dependent story.

---

## Parallel Execution Examples

### Foundation

```text
Task: "T006 Define descriptor enums and dataclasses in src/core/tools/descriptors.py"
Task: "T007 Define RouteSurfaceRequest and RouteFilteredToolSurface dataclasses in src/core/tools/surface.py"
Task: "T008 Define GatewayAdmissionDecision, ToolTraceRecord, and DegradedToolResult dataclasses in src/core/tools/gateway.py"
```

### After US1 Descriptor Contracts Exist

```text
Task: "T029 Implement ToolSurfaceBuilder in src/core/tools/surface.py"
Task: "T040 Implement ToolGateway.evaluate_admission() in src/core/tools/gateway.py"
```

### Verification

```text
Task: "T056 Run descriptor validation tests with pytest tests/test_tool_gateway_m2b1.py -k descriptor -q"
Task: "T057 Run route-surface validation tests with pytest tests/test_tool_gateway_m2b1.py -k route_surface -q"
Task: "T058 Run gateway-admission validation tests with pytest tests/test_tool_gateway_m2b1.py -k gateway_admission -q"
```

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete US1 descriptor tests and descriptor inventory.
3. Run `pytest tests/test_tool_gateway_m2b1.py -k descriptor -q`.
4. Stop and validate that current `tests/test_tools.py` still passes before route filtering begins.

### Incremental Delivery

1. Add US1 descriptors without changing execution behavior.
2. Add US2 route-filtered surfaces before ReAct invocation.
3. Add US3 gateway admission around registry-backed execution.
4. Add US4 trace, safety, compatibility, and performance evidence.
5. Run full feature verification and sync.

### Scope Guardrails

- Do not add provider-backed model-visible tools.
- Do not enable generic web fetch.
- Do not implement symbol-store mutation.
- Do not persist reports or artifacts.
- Do not implement full `ToolExecutionEnvelope`, normalized outputs, or `ToolContextPack`.
- Do not treat M2B.1 as closing Socket.IO lifecycle parity.

---

## Requirement Coverage Matrix

| Requirement | Covered by tasks |
|-------------|------------------|
| `M2B1-FR-001` | T001, T002, T005, T012, T016, T019, T020, T021, T022, T023, T060 |
| `M2B1-FR-002` | T002, T006, T012, T016, T017 |
| `M2B1-FR-003` | T010, T013, T052 |
| `M2B1-FR-004` | T012, T016, T018 |
| `M2B1-FR-005` | T001, T003, T007, T024, T029, T030, T032, T033, T034, T050 |
| `M2B1-FR-006` | T003, T025, T026, T027, T030, T031 |
| `M2B1-FR-007` | T004, T008, T035, T036, T038, T040, T041, T042 |
| `M2B1-FR-008` | T004, T036, T039, T042, T043, T044 |
| `M2B1-FR-009` | T009, T015, T031, T037, T051 |
| `M2B1-FR-010` | T009, T015, T037, T042 |
| `M2B1-FR-011` | T032, T035, T043, T044, T045, T046, T060 |
| `M2B1-FR-012` | T008, T011, T047, T051, T053, T056, T057, T058, T059 |
| `M2B1-FR-013` | T011, T048, T052, T059 |
| `M2B1-FR-014` | T014, T016, T064, T067 |
| `M2B1-FR-015` | T007, T026, T030, T031 |
| `M2B1-FR-016` | T028, T055, T056, T057, T058, T059, T061, T062, T063, T068, T070 |
| `M2B1-FR-017` | T049, T054, T067 |
| `M2B1-FR-018` | T006, T008, T064, T065, T066, T068, T069 |
