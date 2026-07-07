# Tasks: Internal Symbol and Normalization Backbone - M2B.2

**Input**: Design documents from `specs/tool-system-m2b.2/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, `checklists/requirements.md`, `checklists/requirements-alignment.md`

**Tests**: Required. The feature specification defines independent tests and measurable success criteria for each P1 story. Test tasks must be written before the implementation tasks in each story and should fail before the corresponding implementation is added.

**Organization**: Tasks are grouped by user story so symbol normalization, provider policy, output normalization, request-scoped context, and disabled mutation receipts can each be implemented and verified independently after the shared foundation exists.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches a different file or isolated fixture surface
- **[Story]**: User story label from `spec.md`
- Every task names exact file paths

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare focused M2B.2 test and evidence surfaces without changing runtime behavior.

- [X] T001 Review `specs/tool-system-m2b.2/spec.md`, `specs/tool-system-m2b.2/plan.md`, and `specs/tool-system-m2b.2/checklists/requirements-alignment.md`; record the M2B.2 implementation baseline in `specs/tool-system-m2b.2/review.md`.
- [X] T002 [P] Create shared symbol and provider fixture directory `tests/fixtures/tool_system_m2b2/`.
- [X] T003 [P] Add shared M2B.2 assertion helpers in `tests/helpers/tool_system_m2b2_helpers.py`.
- [X] T004 [P] Create the symbol-normalization test module skeleton in `tests/test_stock_symbol_m2b2.py`.
- [X] T005 [P] Create the provider-policy test module skeleton in `tests/test_provider_policy_m2b2.py`.
- [X] T006 [P] Create the tool-normalization test module skeleton in `tests/test_tool_normalization_m2b2.py`.
- [X] T007 [P] Create the retention and mutation test module skeleton in `tests/test_tool_retention_m2b2.py`.
- [X] T008 Create implementation evidence sections for story gates, compatibility gates, sync gates, and accepted warnings in `specs/tool-system-m2b.2/review.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the internal contracts and preserve the verified M2B.1 tool gateway baseline before any story-specific behavior is implemented.

**Critical**: No user story implementation should begin until this phase is complete.

- [X] T009 [P] Add provider policy module structure in `src/core/tools/provider_policy.py`.
- [X] T010 [P] Add tool normalization module structure in `src/core/tools/normalization.py`.
- [X] T011 [P] Add request-scoped context module structure in `src/core/tools/context.py`.
- [X] T012 [P] Add mutation receipt module structure in `src/core/tools/mutation_receipts.py`.
- [X] T013 Export new M2B.2 internal modules from `src/core/tools/__init__.py` after T009-T012 exist, without exposing providers as model-visible tools.
- [X] T014 Define shared normalized output constants and validation helpers in `src/core/tools/normalization.py`.
- [X] T015 Define shared degraded-state reason constants in `src/core/tools/normalization.py`.
- [X] T016 Preserve M2B.1 descriptor hash/version compatibility while extending internal metadata in `src/core/tools/descriptors.py`.
- [X] T017 Preserve M2B.1 route-filtered surface behavior while preventing provider adapter exposure in `src/core/tools/surface.py`.
- [X] T018 Preserve M2B.1 gateway admission and registry-backed execution behavior while preparing envelope integration in `src/core/tools/gateway.py`.
- [X] T019 Add a no-public-contract-change verification note for `docs/openapi.yaml` in `specs/tool-system-m2b.2/review.md`.
- [X] T020 [P] Add Vietnam symbol and index fixture data in `tests/fixtures/tool_system_m2b2/symbols.py`.
- [X] T021 [P] Add provider descriptor and policy fixture data in `tests/fixtures/tool_system_m2b2/providers.py`.
- [X] T022 [P] Add raw-payload, freshness, and degraded-state fixture data in `tests/fixtures/tool_system_m2b2/payloads.py`.

**Checkpoint**: Foundation ready. M2B.1 gateway behavior remains intact and M2B.2 contracts exist for story work.

---

## Phase 3: User Story 1 - Resolve Internal Symbol Identity (Priority: P1)

**Goal**: Evolve `StockSymbolTool` target behavior toward internal symbol-store lookup, identity normalization, and `SystemRecord` output without owning live quote/history/fundamental retrieval.

**Independent Test**: `python -m pytest tests/test_stock_symbol_m2b2.py -q`

### Tests for User Story 1

- [X] T023 [US1] Add canonical symbol and index identity tests for `FPT`, `HOSE:FPT`, `HNX:SHS`, `UPCOM:BSR`, `VNINDEX`, `VN30`, `HNXINDEX`, and `UPINDEX` in `tests/test_stock_symbol_m2b2.py`.
- [X] T024 [US1] Add ticker-only ambiguity and duplicate-alias degraded-state tests in `tests/test_stock_symbol_m2b2.py`.
- [X] T025 [US1] Add tests proving live quote, history, and fundamental retrieval are not target `StockSymbolTool` responsibilities in `tests/test_stock_symbol_m2b2.py`.
- [X] T026 [US1] Add `SystemRecord` normalized output shape tests for internal symbol-store results in `tests/test_stock_symbol_m2b2.py`.

### Implementation for User Story 1

- [X] T027 [US1] Implement `CanonicalSymbolIdentity` and `InternalSymbolRecord` structures in `src/core/tools/normalization.py`.
- [X] T028 [US1] Add internal symbol-store read helpers around `SymbolRepository` in `src/core/tools/stock_symbol.py`.
- [X] T029 [US1] Refactor lookup and search outputs in `src/core/tools/stock_symbol.py` to use internal symbol-store semantics.
- [X] T030 [US1] Implement list, coverage, exchange, currency, alias, identifier, tag, and index normalization in `src/core/tools/stock_symbol.py`.
- [X] T031 [US1] Implement ambiguous, missing, duplicated, stale, and conflicting symbol degraded states in `src/core/tools/stock_symbol.py`.
- [X] T032 [US1] Classify internal symbol outputs as `SystemRecord` normalized outputs through `src/core/tools/normalization.py`.
- [X] T033 [US1] Block or degrade quote, history, and fundamental actions in `src/core/tools/stock_symbol.py` when they are requested through the evolved symbol tool boundary.
- [X] T034 [US1] Update the `stock_symbol` descriptor purpose, output contract, and compatibility metadata in `src/core/tools/descriptors.py`.
- [X] T035 [US1] Keep Yahoo/DataManager access out of the target symbol-store adapter path in `src/core/tools/stock_symbol.py` while preserving explicitly required legacy compatibility.
- [X] T036 [US1] Run `python -m pytest tests/test_stock_symbol_m2b2.py -q` and record the result in `specs/tool-system-m2b.2/review.md`.
- [X] T037 [US1] Run `python -m pytest tests/test_tool_gateway_m2b1.py -q` and record M2B.1 compatibility in `specs/tool-system-m2b.2/review.md`.
- [X] T038 [US1] Record `SC-002` and `SC-003` fixture coverage evidence in `specs/tool-system-m2b.2/review.md`.

**Checkpoint**: US1 is independently testable and does not claim live market-data ownership.

---

## Phase 4: User Story 2 - Govern Providers Below Tools (Priority: P1)

**Goal**: Add provider descriptors and deterministic provider selection policy below model-visible tools, with fail-closed licensing and production eligibility behavior.

**Independent Test**: `python -m pytest tests/test_provider_policy_m2b2.py -q`

### Tests for User Story 2

- [X] T039 [US2] Add provider descriptor completeness tests in `tests/test_provider_policy_m2b2.py`.
- [X] T040 [US2] Add provider order, fallback eligibility, market-session, freshness, timeout, and degraded-state mapping tests in `tests/test_provider_policy_m2b2.py`.
- [X] T041 [US2] Add tests proving provider adapters are hidden from model-visible tool surfaces in `tests/test_provider_policy_m2b2.py`.
- [X] T042 [US2] Add fail-closed tests for unreviewed licensing, missing credential scope, unclear redistribution posture, and non-production eligibility in `tests/test_provider_policy_m2b2.py`.

### Implementation for User Story 2

- [X] T043 [US2] Implement provider class, data category, license posture, credential owner, and production eligibility enums in `src/core/tools/provider_policy.py`.
- [X] T044 [US2] Implement `ProviderAdapterDescriptor` validation in `src/core/tools/provider_policy.py`.
- [X] T045 [US2] Implement `ProviderSelectionPolicy` and `ProviderSelectionDecision` in `src/core/tools/provider_policy.py`.
- [X] T046 [US2] Implement fail-closed provider admission for licensing, credential scope, redistribution posture, and production eligibility in `src/core/tools/provider_policy.py`.
- [X] T047 [US2] Implement fallback decision metadata and degraded-state mapping in `src/core/tools/provider_policy.py`.
- [X] T048 [US2] Connect provider decision metadata to envelope-ready normalization fields in `src/core/tools/normalization.py`.
- [X] T049 [US2] Verify and adjust `src/core/tools/surface.py` and `src/core/tools/gateway.py` so provider adapters remain hidden below model-visible tool descriptors.
- [X] T050 [US2] Run `python -m pytest tests/test_provider_policy_m2b2.py -q` and record the result in `specs/tool-system-m2b.2/review.md`.
- [X] T051 [US2] Run `python -m pytest tests/test_tool_gateway_m2b1.py tests/test_provider_policy_m2b2.py -q` and record provider-hidden compatibility evidence in `specs/tool-system-m2b.2/review.md`.
- [X] T052 [US2] Record `SC-004` and `SC-005` fixture coverage evidence in `specs/tool-system-m2b.2/review.md`.

**Checkpoint**: US2 is independently testable and provider selection remains internal.

---

## Phase 5: User Story 3 - Normalize Tool Results Before Prompt Use (Priority: P1)

**Goal**: Wrap governed tool calls in execution envelopes, classify outputs into exactly one admitted kind, assemble request-scoped context, and exclude raw payloads before prompt assembly.

**Independent Test**: `python -m pytest tests/test_tool_normalization_m2b2.py -q`

### Tests for User Story 3

- [X] T053 [US3] Add `ToolExecutionEnvelope` required-field tests in `tests/test_tool_normalization_m2b2.py`.
- [X] T054 [US3] Add exactly-one-normalized-output-kind tests for all admitted output kinds in `tests/test_tool_normalization_m2b2.py`.
- [X] T055 [US3] Add raw provider payload, raw web/PDF bytes, scripts, hidden text, untrusted instruction, credential, parser-internal, and raw trace exclusion tests in `tests/test_tool_normalization_m2b2.py`.
- [X] T056 [US3] Add stale, missing-field, provider-down, parser-limited, blocked-license, freshness-unknown, validation-failed, and unsupported-provider degraded-state tests in `tests/test_tool_normalization_m2b2.py`.
- [X] T057 [US3] Add safe public metadata and internal trace metadata separation tests in `tests/test_tool_normalization_m2b2.py`.

### Implementation for User Story 3

- [X] T058 [US3] Implement `NormalizedOutputKind` and `NormalizedOutput` in `src/core/tools/normalization.py`.
- [X] T059 [US3] Implement `SourceMetadata` and freshness metadata helpers in `src/core/tools/normalization.py`.
- [X] T060 [US3] Implement `DegradedState` and machine-detectable degraded reasons in `src/core/tools/normalization.py`.
- [X] T061 [US3] Implement `ToolExecutionEnvelope` in `src/core/tools/normalization.py`.
- [X] T062 [US3] Implement output classification and normalization factories in `src/core/tools/normalization.py`.
- [X] T063 [US3] Implement raw payload quarantine and prompt-safe projection helpers in `src/core/tools/normalization.py`.
- [X] T064 [US3] Implement request-scoped `ToolContextPack` assembly in `src/core/tools/context.py`.
- [X] T065 [US3] Integrate `ToolExecutionEnvelope` and normalized output references into `src/core/tools/gateway.py`.
- [X] T066 [US3] Update `src/core/stock_assistant_agent.py` to consume prompt-safe `ToolContextPack` projections without injecting raw provider or tool payloads.
- [X] T067 [US3] Run `python -m pytest tests/test_tool_normalization_m2b2.py -q` and record the result in `specs/tool-system-m2b.2/review.md`.
- [X] T068 [US3] Run `python -m pytest tests/test_tools.py tests/test_stock_query_router.py tests/test_agent_regression.py -q` and record compatibility evidence in `specs/tool-system-m2b.2/review.md`.
- [X] T069 [US3] Record `SC-006`, `SC-007`, and `SC-008` fixture coverage evidence in `specs/tool-system-m2b.2/review.md`.

**Checkpoint**: US3 is independently testable and no raw payload enters prompt context.

---

## Phase 6: User Story 4 - Preserve Request-Scoped Context and Source Lineage (Priority: P1)

**Goal**: Keep `ToolContextPack` request-scoped, permit only approved retained derivatives, and require source lineage or an explicit no-source degraded reason.

**Independent Test**: `python -m pytest tests/test_tool_retention_m2b2.py -q`

### Tests for User Story 4

- [X] T070 [US4] Add retained derivative source-lineage tests in `tests/test_tool_retention_m2b2.py`.
- [X] T071 [US4] Add tests proving the full `ToolContextPack` is not persisted as conversation memory or durable market truth in `tests/test_tool_retention_m2b2.py`.
- [X] T072 [US4] Add missing-source and no-source degraded-reason tests in `tests/test_tool_retention_m2b2.py`.
- [X] T073 [US4] Add visualization provenance and generated artifact metadata tests that prevent those artifacts from becoming canonical evidence in `tests/test_tool_retention_m2b2.py`.

### Implementation for User Story 4

- [X] T074 [US4] Implement `RetainedDerivative` in `src/core/tools/context.py`.
- [X] T075 [US4] Implement retention guard helpers that reject whole-pack persistence in `src/core/tools/context.py`.
- [X] T076 [US4] Implement source-lineage validation helpers in `src/core/tools/context.py`.
- [X] T077 [US4] Implement visualization provenance and generated artifact metadata projections in `src/core/tools/context.py`.
- [X] T078 [US4] Implement safe retained trace, cache, freshness, warning, and degraded-state metadata subsets in `src/core/tools/context.py`.
- [X] T079 [US4] Verify `src/services/symbols_service.py` and `src/data/repositories/symbol_repository.py` do not persist full request-scoped `ToolContextPack` objects.
- [X] T080 [US4] Run `python -m pytest tests/test_tool_retention_m2b2.py -q` and record the result in `specs/tool-system-m2b.2/review.md`.
- [X] T081 [US4] Record `SC-009` fixture coverage evidence in `specs/tool-system-m2b.2/review.md`.

**Checkpoint**: US4 is independently testable and request-scoped context remains non-durable by default.

---

## Phase 7: User Story 5 - Keep Symbol Mutations Disabled Until Governed (Priority: P1)

**Goal**: Classify symbol-store writes as future workflow mutations, keep them disabled by default, and define mutation receipt shape without enabling production writes.

**Independent Test**: `python -m pytest tests/test_tool_retention_m2b2.py -q -k mutation`

### Tests for User Story 5

- [X] T082 [US5] Add disabled-by-default tests for symbol upsert, alias merge, tag update, coverage update, and retirement marker requests in `tests/test_tool_retention_m2b2.py`.
- [X] T083 [US5] Add `MutationReceipt` required-field tests in `tests/test_tool_retention_m2b2.py`.
- [X] T084 [US5] Add no-durable-write tests for default symbol mutation requests in `tests/test_tool_retention_m2b2.py`.
- [X] T085 [US5] Add test-only or future approved mutation receipt fixture tests in `tests/test_tool_retention_m2b2.py`.

### Implementation for User Story 5

- [X] T086 [US5] Implement mutation kind, mutation status, and `MutationReceipt` structures in `src/core/tools/mutation_receipts.py`.
- [X] T087 [US5] Implement disabled-by-default mutation guards for symbol-store write actions in `src/core/tools/mutation_receipts.py`.
- [X] T088 [US5] Integrate blocked mutation requests with `DegradedState` and `MutationReceipt` normalized output handling in `src/core/tools/normalization.py`.
- [X] T089 [US5] Verify `src/services/symbols_service.py` and `src/data/repositories/symbol_repository.py` write paths are not exposed to model-visible tool execution by default.
- [X] T090 [US5] Run `python -m pytest tests/test_tool_retention_m2b2.py -q -k mutation` and record the result in `specs/tool-system-m2b.2/review.md`.
- [X] T091 [US5] Run `python -m pytest tests/test_stock_symbol_m2b2.py tests/test_provider_policy_m2b2.py tests/test_tool_normalization_m2b2.py tests/test_tool_retention_m2b2.py -q` and record focused M2B.2 evidence in `specs/tool-system-m2b.2/review.md`.
- [X] T092 [US5] Record `SC-010` and `SC-011` fixture coverage evidence in `specs/tool-system-m2b.2/review.md`.

**Checkpoint**: US5 is independently testable and production symbol-store writes remain disabled.

---

## Phase 8: Final Verification, Governance, and Sync

**Purpose**: Prove all story work remains within M2B.2 scope, preserves M2B.1 compatibility, and updates Spec Kit traceability.

- [X] T093 Run `python -m pytest tests/test_tool_gateway_m2b1.py -q` and record M2B.1 regression evidence in `specs/tool-system-m2b.2/review.md`.
- [X] T094 Run `python -m pytest tests/test_stock_symbol_m2b2.py tests/test_provider_policy_m2b2.py tests/test_tool_normalization_m2b2.py tests/test_tool_retention_m2b2.py -q` and record focused M2B.2 evidence in `specs/tool-system-m2b.2/review.md`.
- [X] T095 Run `python -m pytest tests/test_tools.py tests/test_stock_query_router.py tests/test_agent_regression.py -q` and record compatibility evidence in `specs/tool-system-m2b.2/review.md`.
- [X] T096 Run `python -m pytest tests/test_stock_symbol_m2b2.py tests/test_provider_policy_m2b2.py tests/test_tool_normalization_m2b2.py tests/test_tool_retention_m2b2.py --cov=core.tools --cov-report=term-missing --cov-fail-under=56` and record enforced coverage evidence in `specs/tool-system-m2b.2/review.md`.
- [X] T097 Run `python -m pytest tests/test_tool_normalization_m2b2.py tests/test_agent_regression.py --cov=core.tools.context --cov=core.tools.normalization --cov-report=term-missing --cov-fail-under=56` and record enforced prompt-boundary coverage evidence in `specs/tool-system-m2b.2/review.md`.
- [X] T098 Validate `docs/openapi.yaml` has no public contract changes for M2B.2 and record the result in `specs/tool-system-m2b.2/review.md`.
- [X] T099 Validate provider adapters are absent from model-visible descriptors and route surfaces by inspecting `src/core/tools/descriptors.py`, `src/core/tools/surface.py`, and `src/core/tools/gateway.py`; record the result in `specs/tool-system-m2b.2/review.md`.
- [X] T100 Revalidate `specs/tool-system-m2b.2/checklists/requirements-alignment.md` after implementation evidence exists and record any reopened checklist item in `specs/tool-system-m2b.2/review.md`.
- [X] T101 Update `specs/spec-traceability.yaml` with M2B.2 implementation evidence paths, lifecycle status, synchronized documents, and accepted deferrals.
- [X] T102 Run `python scripts/sync_spec_status.py --gate` and confirm regenerated `specs/spec-sync-status.md` plus `docs/domains/agent/SRS_SPEC_TRACEABILITY.md` are current.
- [X] T103 Run `git diff --check` and record whitespace or line-ending findings in `specs/tool-system-m2b.2/review.md`.
- [X] T104 Run `/speckit-validate` for M2B.2 task-to-requirement readiness and record any findings in `specs/tool-system-m2b.2/review.md`.
- [X] T105 Run `/speckit-verify-tasks` and `/speckit-verify-run` after all implementation tasks are complete; record the verification verdict in `specs/tool-system-m2b.2/review.md`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup. Blocks all story implementation.
- **User Story 1 (Phase 3)**: Depends on Foundation. Can be delivered first as the MVP.
- **User Story 2 (Phase 4)**: Depends on Foundation. Can run in parallel with US1 after shared contracts exist.
- **User Story 3 (Phase 5)**: Depends on Foundation and can use outputs from US1/US2 when available, but its normalization primitives are independently testable.
- **User Story 4 (Phase 6)**: Depends on US3 context primitives for full integration; retention tests can be written after Foundation.
- **User Story 5 (Phase 7)**: Depends on US3 normalized output handling for integrated degraded-state receipts; mutation receipt contract tests can be written after Foundation.
- **Final Verification (Phase 8)**: Depends on all desired story phases.

### User Story Dependencies

- **US1**: No dependency on other stories after Foundation.
- **US2**: No dependency on other stories after Foundation.
- **US3**: Depends on Foundation; integrates with US1 and US2 when those story outputs are available.
- **US4**: Depends on US3 `ToolContextPack` and retained derivative primitives.
- **US5**: Depends on US3 degraded-state and normalized output primitives.

### Within Each User Story

- Write tests first and confirm they fail before implementation.
- Define contracts and data structures before integration.
- Preserve M2B.1 compatibility before changing gateway or descriptor behavior.
- Record independent story evidence before moving to final verification.

## Parallel Opportunities

- Setup tasks T002 through T007 can run in parallel.
- Foundation module skeleton tasks T009 through T012 can run in parallel; T013 follows after those modules exist.
- Foundation fixture tasks T020 through T022 can run in parallel.
- Story test tasks that write to the same test file should be sequenced within that file.
- US1 and US2 can proceed in parallel after Foundation.
- US4 and US5 tests can be prepared in parallel after Foundation, but their integrated implementation depends on US3 primitives.

## Parallel Example: US1

```powershell
# Add US1 tests sequentially before implementation because they share one test file:
Task: "T023 canonical symbol and index identity tests in tests/test_stock_symbol_m2b2.py"
Task: "T024 ticker-only ambiguity tests in tests/test_stock_symbol_m2b2.py"
Task: "T025 live market-data exclusion tests in tests/test_stock_symbol_m2b2.py"
Task: "T026 SystemRecord output shape tests in tests/test_stock_symbol_m2b2.py"
```

## Implementation Strategy

### MVP First

1. Complete Setup and Foundation.
2. Complete US1 so internal symbol identity is normalized and independently testable.
3. Run `python -m pytest tests/test_stock_symbol_m2b2.py -q` and `python -m pytest tests/test_tool_gateway_m2b1.py -q`.
4. Stop and review evidence before expanding to provider policy and normalization integration.

### Incremental Delivery

1. US1 establishes internal symbol identity.
2. US2 adds hidden provider policy below tools.
3. US3 wraps tool outcomes and prompt-safe context.
4. US4 adds retention/source-lineage guardrails.
5. US5 defines disabled mutation receipt behavior.
6. Final verification and sync promote the feature only when evidence supports the lifecycle state.

### Team Parallel Strategy

1. One engineer owns Foundation contract modules.
2. One engineer writes US1/US2 tests and fixtures.
3. One engineer writes US3/US4/US5 contract tests.
4. Runtime integration waits until Foundation and the relevant failing tests exist.

## Requirement Coverage Matrix

| Requirement / Criterion | Task IDs |
|-------------------------|----------|
| M2B2-FR-001, SC-001 | T001, T008, T016, T017, T018, T019, T037, T051, T068, T093, T095, T098, T099, T103 |
| M2B2-FR-002, SC-002, SC-003 | T002, T004, T020, T023, T024, T026, T027, T028, T029, T030, T031, T032, T034, T036, T038 |
| M2B2-FR-003 | T025, T033, T035, T036, T038 |
| M2B2-FR-004 | T025, T033, T035, T036, T038 |
| M2B2-FR-005 | T020, T023, T024, T027, T030, T031, T036, T038 |
| M2B2-FR-006 | T026, T027, T032, T034, T036, T038 |
| M2B2-FR-007, SC-004 | T005, T009, T021, T039, T043, T044, T050, T052 |
| M2B2-FR-008, SC-005 | T013, T017, T041, T049, T051, T099 |
| M2B2-FR-009 | T021, T040, T045, T047, T048, T050, T052 |
| M2B2-FR-010 | T021, T042, T046, T047, T050, T052 |
| M2B2-FR-011, SC-006 | T003, T006, T010, T014, T048, T053, T061, T062, T065, T067, T069 |
| M2B2-FR-012 | T014, T054, T058, T062, T067, T069 |
| M2B2-FR-013 | T011, T057, T064, T066, T067, T069, T097 |
| M2B2-FR-014, SC-007 | T022, T055, T063, T066, T067, T069, T097 |
| M2B2-FR-015, SC-008 | T015, T022, T056, T060, T062, T067, T069 |
| M2B2-FR-016 | T022, T059, T060, T070, T072, T076, T078, T080, T081 |
| M2B2-FR-017 | T011, T064, T071, T075, T079, T080, T081 |
| M2B2-FR-018, SC-009 | T007, T070, T071, T072, T073, T074, T075, T076, T077, T078, T080, T081 |
| M2B2-FR-019, SC-010 | T012, T082, T084, T087, T089, T090, T092 |
| M2B2-FR-020, SC-011 | T083, T085, T086, T088, T090, T092 |
| M2B2-FR-021, SC-012 | T019, T033, T035, T098, T100, T101, T104, T105 |
| M2B2-FR-022 | T019, T055, T057, T063, T066, T098, T099, T103 |
| Governance and sync evidence | T001, T008, T019, T036, T037, T038, T050, T051, T052, T067, T068, T069, T080, T081, T090, T091, T092, T093, T094, T095, T096, T097, T098, T099, T100, T101, T102, T103, T104, T105 |

## Independent Test Criteria

- **US1**: `python -m pytest tests/test_stock_symbol_m2b2.py -q`
- **US2**: `python -m pytest tests/test_provider_policy_m2b2.py -q`
- **US3**: `python -m pytest tests/test_tool_normalization_m2b2.py -q`
- **US4**: `python -m pytest tests/test_tool_retention_m2b2.py -q`
- **US5**: `python -m pytest tests/test_tool_retention_m2b2.py -q -k mutation`
- **Regression**: `python -m pytest tests/test_tool_gateway_m2b1.py tests/test_tools.py tests/test_stock_query_router.py tests/test_agent_regression.py -q`
- **Sync**: `python scripts/sync_spec_status.py --gate`

## Notes

- Keep providers below model-visible tools; do not create provider-specific model tools in this milestone.
- Keep `ToolContextPack` request-scoped; do not persist it wholesale.
- Keep production symbol-store writes disabled by default.
- Keep `docs/openapi.yaml` unchanged unless a later governed plan explicitly introduces a public contract change.
- Do not close or promote downstream `TS-06`, TradingView expansion, generic web fetch, report persistence, remote tool admission, or production provider enablement work in M2B.2.
