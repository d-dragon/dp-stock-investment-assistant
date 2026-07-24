# Tasks: Agent Structured Outputs & Route-Adapted Response Tools

**Input**: Design documents from `specs/003-agent-structured-outputs/`  
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [quickstart.md](quickstart.md), [contracts/openapi-chat-response.yaml](contracts/openapi-chat-response.yaml)

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`)
- Every task includes exact repository file paths.

---

## Governance Task Requirements

Generated tasks MUST include exact file paths for all governance work that applies to the feature:

- Update `specs/spec-traceability.yaml` when SRS scope, evidence paths, coverage status, or lifecycle status changes.
- Update public contracts when behavior changes. Current REST contract authority is `docs/openapi.yaml`.
- Add or update long-lived docs only for stable knowledge that belongs in `docs/`, and cite exact section-level anchors.
- Regenerate sync reports with `python scripts/sync_spec_status.py --gate` after traceability or feature status changes.
- Validate repository-relative markdown links and section-level anchor references.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and prerequisite structure verification

- [x] T001 Verify project environment dependencies (Pydantic v2, LangChain 0.3+, LangGraph 0.2+) and feature directory structure in `specs/003-agent-structured-outputs/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core schemas and response tools that MUST be complete before user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 [P] Define `ResponseStatus`, `StockQueryRoute`, polymorphic `AgentStructuredOutput`, domain schemas (`StockAnalysisResponse`, `RecommendationResponse`, `GeneralChatResponse`), and `AgentResponse` envelope in `src/core/types.py`
- [x] T003 [P] Register control-plane response tools (`submit_stock_analysis`, `submit_recommendation`, `submit_general_chat`) under `RiskClass.BOUNDED_NON_MUTATING` with `return_direct=True` in `src/core/tools/response_tools.py` and `src/core/tools/registry.py`

**Checkpoint**: Core Pydantic schemas and response tools ready — user story implementation can begin.

---

## Phase 3: User Story 1 - Typed Structured Output Generation via Route-Adapted Response Tools (Priority: P1) 🎯 MVP

**Goal**: Deliver typed, machine-readable structured JSON response payloads (`AgentStructuredOutput`) matching domain Pydantic schemas via route-adapted response tools during single-turn ReAct reasoning with 0% extra prompt token cost overhead ([SRS v2.9 FR-1.2.5, FR-1.2.6, AC-10.1, AC-10.2, AC-10.3](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#125-structured-output-generation)).

**Independent Test**: Execute `pytest tests/unit/test_structured_output.py` and `pytest tests/integration/test_chat_structured_flow.py -k "test_happy_path"` to verify that `StockAssistantAgent.process_query_structured()` returns `AgentResponse.structured_content` containing a validated `StockAnalysisResponse` object with `status == ResponseStatus.SUCCESS`.

### Implementation for User Story 1

- [x] T004 [P] [US1] Create unit tests for Pydantic schema validation and response tool registration in `tests/unit/test_structured_output.py`
- [x] T005 [US1] Implement route-filtered tool surface injection in `StockAssistantAgent._build_tool_surface_for_query()` in `src/core/stock_assistant_agent.py`
- [x] T006 [US1] Implement `StockAssistantAgent.process_query_structured()` to bind matching route response tool and extract `AgentStructuredOutput` direct payloads with `return_direct=True` in `src/core/stock_assistant_agent.py`

**Checkpoint**: User Story 1 fully functional — single-turn ReAct reasoning emits typed JSON with 0% token overhead.

---

## Phase 4: User Story 2 - Out-of-Band Fallback Formatter & Graceful Degradation (Priority: P2)

**Goal**: Extract structured JSON out-of-band via `model.with_structured_output()` when models emit plain markdown text without calling response tools, falling back gracefully to `ResponseStatus.PARTIAL` on extraction errors or timeouts ([SRS v2.9 FR-1.2.7, AC-10.4, ERR-1.4](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#127-two-stage-service-layer-post-processing-formatter)).

**Independent Test**: Execute `pytest tests/unit/test_fallback_formatter.py` to verify that simulated plain text outputs trigger `ChatService._extract_structured_response()`, returning `AgentResponse` with `structured_content` populated and degrading to `status = ResponseStatus.PARTIAL` without raising exceptions.

### Implementation for User Story 2

- [x] T007 [P] [US2] Create unit tests for two-stage service-layer fallback formatter and execution timeout degradation in `tests/unit/test_fallback_formatter.py`
- [x] T008 [US2] Implement `ChatService._extract_structured_response()` two-stage fallback formatter enforcing 10.0s timeout budget (`agent.structured_output.fallback_timeout_seconds: 10.0`) calling `model.with_structured_output()` in `src/services/chat_service.py`
- [x] T009 [US2] Implement fallback degradation handler in `StockAssistantAgent.process_query_structured()` returning `ResponseStatus.PARTIAL` and raw text when fallback extraction fails in `src/core/stock_assistant_agent.py`

**Checkpoint**: User Stories 1 AND 2 operate independently — model non-compliance degrades safely without thread crashes.

---

## Phase 5: User Story 3 - Checkpointer State Hygiene & Transport Edge Serialization (Priority: P3)

**Goal**: Exclude heavy `AgentStructuredOutput` JSON payloads from MongoDB `agent_checkpoints` short-term memory serialization while suppressing raw JSON tokens on REST SSE and WebSocket streaming edges ([SRS v2.9 FR-1.2.8, AC-10.5, IR-1.14, IR-3.11](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#128-stm-checkpointer-state-hygiene-and-payload-exclusion)).

**Independent Test**: Execute `pytest tests/integration/test_chat_structured_flow.py -k "test_checkpointer_exclusion or test_api_chat_structured"` to verify `agent_checkpoints` stores raw `BaseMessage` arrays without Pydantic payloads, and REST SSE streams filter out JSON tool argument tokens.

### Implementation for User Story 3

- [x] T010 [P] [US3] Create integration tests for checkpointer payload exclusion and transport edge streaming token suppression in `tests/integration/test_chat_structured_flow.py`
- [x] T011 [US3] Update `ChatService._record_message_metadata()` to update `last_turn_metadata` and append summary frames (`route_kind`, `structured_status`, `schema_version`) to the `turns` array in the `conversations` MongoDB collection in `src/services/chat_service.py`
- [x] T012 [US3] Implement raw JSON tool argument streaming token suppression and discrete `structured_completion` event frame emission in `src/web/routes/ai_chat_routes.py` and `src/web/sockets/chat_events.py`

**Checkpoint**: Checkpointer state hygiene verified and transport edge streaming delivers clean chat bubbles.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation updates, contract synchronization, traceability refresh, and validation gates

- [x] T013 [P] Update REST contract component schema in `docs/openapi.yaml` to include `structured_content` and `ResponseStatus` matching `specs/003-agent-structured-outputs/contracts/openapi-chat-response.yaml`
- [x] T014 [P] Update `specs/spec-traceability.yaml` with SRS v2.9 `FR-1.2.5`–`FR-1.2.9`, `AC-10`, `IR-1.14`, `IR-3.11`, `ERR-1.4` mappings, evidence paths, and `Implemented` status
- [x] T015 [P] Update technical design realization in `docs/domains/agent/TECHNICAL_DESIGN.md#31-agent-runtime-and-orchestration` with section-level anchors
- [x] T016 Execute all runnable validation scenarios in `specs/003-agent-structured-outputs/quickstart.md`
- [x] T017 Run `python scripts/sync_spec_status.py --gate` and commit regenerated `specs/spec-sync-status.md` plus reverse traceability output
- [x] T018 Validate repository-relative markdown links and section-level anchor references across all feature artifacts

---

## Phase 7: Convergence

**Purpose**: Close gaps identified during post-implementation convergence assessment — the fallback formatter is not wired into production paths, and Pydantic model/contract schemas diverge from the spec and data model.

- [x] T019 Wire `ChatService._extract_structured_response()` into the fallback degradation path in `StockAssistantAgent.process_query_structured()` so that when the model emits plain text without calling a response tool, the service-layer formatter (`model.with_structured_output()`) is invoked before returning `ResponseStatus.PARTIAL` per FR-004/FR-1.2.7/AC-10.4 (missing)
- [x] T020 Align `ResponseStatus` enum between `src/core/types.py` and `docs/openapi.yaml` — add `FAILED` value to code enum and document `FALLBACK`/`ERROR` in OpenAPI contract to eliminate bidirectional schema mismatch per FR-001 (contradicts)
- [x] T021 Reconcile `AgentStructuredOutput` implementation in `src/core/types.py` with data-model.md: add shared base Pydantic model with `schema_version`, `route_kind` (`StockQueryRoute` enum), `timestamp` fields, or update data-model.md to reflect the Union pattern used (contradicts)
- [x] T022 Reconcile `GeneralChatResponse` field naming between `src/core/types.py` (`message`, `topics_covered`) and spec/data-model.md (`topic`, `summary`) — align one direction with tests per data-model.md §1.3 (contradicts)
- [x] T023 Reconcile `RecommendationResponse` field naming between `src/core/types.py` (`recommendation`, `thesis`) and spec/data-model.md (`action`, `rationale`) — align one direction with tests per data-model.md §1.3 (contradicts)
- [x] T024 Improve SSE JSON tool argument token filtering in `ChatService.stream_chat_response()` at `src/services/chat_service.py` to handle multi-chunk streaming boundary cases and avoid false positives on legitimate text per FR-008/IR-1.14 (partial)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user story implementation
- **User Stories (Phases 3–5)**: Depend on Foundational phase completion
  - Sequential priority order: US1 (P1 MVP) → US2 (P2 Fallback) → US3 (P3 Hygiene & Transport Edge)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational (Phase 2) — No dependencies on other stories
- **User Story 2 (P2)**: Starts after Foundational (Phase 2) — Integrates with US1 `process_query_structured()`
- **User Story 3 (P3)**: Starts after Foundational (Phase 2) — Integrates with US1 response output boundary

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational)
2. Complete Phase 3 (User Story 1)
3. **STOP and VALIDATE**: Run `pytest tests/unit/test_structured_output.py`
4. Deploy MVP single-turn ReAct response tool structured outputs

### Incremental Delivery

1. Setup + Foundational → Core Pydantic schemas & response tools ready
2. User Story 1 → Single-turn ReAct response tool outputs (0% token overhead)
3. User Story 2 → Out-of-band fallback formatter (resilience against model non-compliance)
4. User Story 3 → Checkpointer hygiene & SSE/WebSocket streaming token suppression
5. Polish & Sync → OpenAPI contract sync, traceability update, and gate validation
