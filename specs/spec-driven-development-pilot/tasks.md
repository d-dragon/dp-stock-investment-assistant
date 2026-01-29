# Tasks: FR-3.1 Short-Term Memory (STM)

**Feature**: Short-Term Memory (STM) — Conversation Buffer for Multi-Turn Dialogues  
**Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](../../.specify/specs/1-short-term-memory/spec.md)  
**Generated**: 2026-01-28 | **Estimated**: 20-25 Story Points

---

## Overview

This task file implements FR-3.1 Short-Term Memory, enabling the StockAssistantAgent to maintain multi-turn conversation context within sessions using LangGraph's `MongoDBSaver` checkpointer.

**Key Deliverables**:
- `conversations` collection schema with MongoDB validation and indexes
- `ConversationRepository` extending `MongoGenericRepository`
- `MemoryConfig` frozen dataclass with fail-fast validation (FR-3.1.9, FR-3.1.10)
- `MongoDBSaver` checkpointer integration in LangGraph bootstrap
- `ConversationService` with summarization trigger logic
- Session-aware API routes (`POST /api/chat`, Socket.IO events)
- Comprehensive test coverage (unit, integration, e2e)

**Architecture**:
- Direct 1:1 mapping: `session_id` → `thread_id` (no translation layer)
- Dual collection strategy: `conversations` (app-managed) + `agent_checkpoints` (LangGraph-managed)
- Archive-over-delete policy per ADR-001

---

## Task Summary

| Phase | Tasks | Story Points | Focus Area |
|-------|-------|--------------|------------|
| 1: Setup | 3 | 2 SP | Project structure, config skeleton |
| 2: Foundational (BLOCKING) | 7 | 6-7 SP | Schema, repository, config validation |
| 3: US1 Session-Aware Conversation | 8 | 5-6 SP | Agent checkpointer, session params |
| 4: US2 Session Persistence | 4 | 2-3 SP | Restart recovery, data integrity |
| 5: US3 Stateless Fallback Mode | 3 | 1-2 SP | No-session behavior |
| 6: US4 Memory Content Compliance | 4 | 2 SP | Content filtering, audit |
| 7: US5 Session Recall on Reconnect | 3 | 1-2 SP | Disconnect/reconnect |
| 8: Polish & Documentation | 4 | 2-3 SP | OpenAPI, quickstart, e2e test |
| **Total** | **36** | **20-25 SP** | |

---

## Phase 1: Setup (2 SP)

> **Goal**: Establish project structure and configuration skeleton for STM implementation.

- [X] T001 Create feature directory structure per plan.md project layout
  - Create `src/data/schema/conversations_schema.py` (empty module with docstring)
  - Create `src/data/repositories/conversation_repository.py` (empty module)
  - Create `src/services/conversation_service.py` (empty module)
  - Create `src/utils/memory_config.py` (empty module)

- [X] T002 [P] Add memory configuration section skeleton to `config/config.yaml`
  - Add `langchain.memory` section with all 9 parameters (FR-3.1.9)
  - Parameters: `enabled`, `summarize_threshold`, `max_messages`, `messages_to_keep`, `max_content_size`, `summary_max_length`, `context_load_timeout_ms`, `state_save_timeout_ms`, `checkpoint_collection`, `conversations_collection`
  - Include comments with valid ranges per spec

- [X] T003 [P] Update `config/config_example.yaml` with memory configuration section
  - Mirror structure from T002 with example values
  - Document each parameter purpose

---

## Phase 2: Foundational (BLOCKING) — 6-7 SP

> **Goal**: Build data layer foundation that ALL user stories depend on. **Must complete before any US phase.**

### Schema & Migration

- [X] T004 Create conversations collection JSON schema in `src/data/schema/conversations_schema.py`
  - Define `CONVERSATIONS_SCHEMA` with all 15 fields from data-model.md
  - Include schema validation rules (status enum, ISO dates, etc.)
  - Add `CONVERSATIONS_INDEXES` list (5 indexes including unique session_id)

- [X] T005 [P] Update `src/data/migration/db_setup.py` to create conversations collection
  - Add `setup_conversations_collection(db)` function
  - Create collection with JSON schema validation
  - Create all 5 indexes from schema file
  - Add optional `setup_checkpoints_indexes(db)` for TTL on agent_checkpoints

### Repository Layer

- [X] T006 Implement `ConversationRepository` in `src/data/repositories/conversation_repository.py`
  - Extend `MongoGenericRepository`
  - Implement `get_or_create(session_id, workspace_id, user_id)` method
  - Implement `update_stats(session_id, message_count, total_tokens)` method
  - Implement `set_status(session_id, status)` method with transition validation
  - Implement `archive(session_id)` method (sets archived_at, status)
  - Implement `health_check()` returning (bool, dict)

- [X] T007 [P] Register `ConversationRepository` in `src/data/repositories/factory.py`
  - Add `get_conversation_repository()` method to `RepositoryFactory`
  - Follow singleton pattern consistent with other repositories

### Configuration Layer (FR-3.1.9, FR-3.1.10)

- [X] T008 Implement `MemoryConfig` frozen dataclass in `src/utils/memory_config.py`
  - Create `@dataclass(frozen=True)` with all 9 parameters
  - Implement `__post_init__` validation per FR-3.1.10 ranges
  - Add `_validate_range(field, min, max)` helper method
  - Implement `from_config(config_dict)` class method for YAML loading
  - Raise `ValueError` with actionable message on invalid config (fail-fast)

- [X] T009 [P] Update `src/utils/config_loader.py` to load memory configuration
  - Ensure `langchain.memory` section is loaded from YAML
  - Add environment variable override support for memory parameters

### Tests

- [X] T010 Create unit tests for `ConversationRepository` in `tests/test_conversation_repository.py`
  - Test `get_or_create` creates new document when missing
  - Test `get_or_create` returns existing document
  - Test `update_stats` updates message_count and total_tokens
  - Test `set_status` validates status transitions (active→summarized→archived)
  - Test `set_status` rejects invalid transitions (archived→active)
  - Test `archive` sets archived_at and status=archived
  - Test `health_check` returns healthy status
  - Mock MongoDB collection; no real database needed

- [X] T011 [P] Create unit tests for `MemoryConfig` in `tests/test_memory_config.py`
  - Test default values load correctly
  - Test valid custom values accepted
  - Test invalid `summarize_threshold` < 1000 raises ValueError
  - Test invalid `summarize_threshold` > 10000 raises ValueError
  - Test `messages_to_keep >= max_messages` raises ValueError
  - Test error message includes parameter name and valid range
  - Test `from_config()` loads from YAML dict structure

- [X] T011 [P] Create config validation unit tests in `tests/test_memory_config.py`
  - Test: Invalid `summarize_threshold` (below 1000, above 10000) raises `ValueError`
  - Test: Invalid `max_messages` (below 10, above 200) raises `ValueError`
  - Test: Invalid `messages_to_keep` (below 5, above 50, or >= max_messages) raises `ValueError`
  - Test: Invalid `max_content_size` (below 1024, above 65536) raises `ValueError`
  - Test: Invalid `summary_max_length` (below 100, above 2000) raises `ValueError`
  - Test: Invalid `context_load_timeout_ms` (below 100, above 5000) raises `ValueError`
  - Test: Invalid `state_save_timeout_ms` (below 10, above 500) raises `ValueError`
  - Test: Invalid `checkpoint_collection` (empty string, non-string) raises `ValueError`
  - Test: Invalid `conversations_collection` (empty string, non-string) raises `ValueError`
  - Test: Valid config within all ranges creates `MemoryConfig` successfully
  - Test: `MemoryConfig.from_config()` loads from YAML dict correctly
  - Test: Error messages include parameter name and valid range
  - **Verifies**: FR-3.1.9 (all 9 parameters), FR-3.1.10 (fail-fast validation), SC-8 (100% config compliance)

---

## Phase 3: US1 — Session-Aware Conversation (P1) — 5-6 SP

> **Goal**: Enable multi-turn conversations where agent remembers context from prior exchanges.
>
> **User Story (spec.md P1)**: User initiates conversation with session_id, asks follow-up questions, agent recalls prior context accurately.
>
> **Acceptance Criteria**:
> - Agent references prior exchange accurately (FR-3.1.1)
> - Session context binding demonstrated (FR-3.1.4)
> - Memory contains conversation text but NOT financial data (FR-3.1.8)

### Agent Integration

- [X] T012 [US1] Initialize `MongoDBSaver` checkpointer in `src/core/langgraph_bootstrap.py`
  - Add `create_checkpointer(config)` function using `MemoryConfig`
  - Return `None` if `langchain.memory.enabled=false`
  - Use collection name from `MemoryConfig.checkpoint_collection`
  - Handle connection errors gracefully with logging

- [X] T013 [US1] Modify `StockAssistantAgent.__init__` to accept checkpointer in `src/core/stock_assistant_agent.py`
  - Add optional `checkpointer` parameter to constructor
  - Store as `self._checkpointer` instance attribute
  - Pass checkpointer to LangGraph graph builder if provided

- [X] T014 [US1] Add `session_id` parameter to `process_query()` in `src/core/stock_assistant_agent.py`
  - Add `session_id: Optional[str] = None` parameter
  - Build `config={"configurable": {"thread_id": session_id}}` when session_id provided
  - Pass config to `agent_executor.invoke()` call

- [X] T015 [P] [US1] Add `session_id` parameter to `process_query_streaming()` in `src/core/stock_assistant_agent.py`
  - Mirror pattern from T014 for streaming method
  - Pass config to `agent_executor.stream()` call

### API Integration

- [X] T016 [US1] Modify `POST /api/chat` route in `src/web/routes/ai_chat_routes.py`
  - Extract `session_id` from request JSON (optional field)
  - Validate session_id format (UUID v4) if provided
  - Pass session_id to `agent.process_query(message, session_id=session_id)`
  - Include `session_id` in response JSON

- [X] T017 [P] [US1] Modify Socket.IO `chat_message` event in `src/web/sockets/chat_events.py`
  - Extract `session_id` from event data (optional field)
  - Pass to agent processing method
  - Include in response emission

### Tests

- [X] T018 [US1] Create integration tests for agent memory in `tests/test_agent_memory.py`
  - Test multi-turn conversation: ask question, follow up, verify context recall
  - Test session isolation: two different session_ids have separate contexts
  - Test agent references prior messages accurately (FR-3.1.1)
  - Use mock or test MongoDB instance

- [X] T019 [US1] Create API tests for session-aware chat in `tests/api/test_chat_routes_memory.py`
  - Test `POST /api/chat` with valid session_id returns 200
  - Test response includes echoed session_id
  - Test multi-turn API conversation maintains context
  - Test invalid session_id format returns 400

---

## Phase 4: US2 — Session Persistence Across Restart (P2) — 2-3 SP

> **Goal**: Ensure conversation state survives system restarts without data loss.
>
> **User Story (spec.md P2)**: User has active session with ≥3 messages, system restarts, user reconnects with same session_id, agent demonstrates awareness of prior conversation.
>
> **Acceptance Criteria**:
> - Message history matches 100% after restart (FR-3.1.2)
> - Session identifier correctly binds to stored state (FR-3.1.3)

- [X] T020 [US2] Create persistence integration test in `tests/integration/test_memory_persistence.py`
  - Test: Create session, add 3+ messages, simulate restart (reinitialize agent), verify context restored
  - Test: Hash comparison of message history pre/post restart (100% match)
  - Test: Verify checkpoint data survives across agent instances

- [X] T021 [US2] Implement conversation metadata tracking in `src/services/conversation_service.py`
  - Create `ConversationService` class with `ConversationRepository` dependency
  - Implement `track_message(session_id, role, content)` method
  - Update message_count and total_tokens in conversation document
  - Register in `ServiceFactory`

- [X] T022 [P] [US2] Add service factory registration in `src/services/factory.py`
  - Add `get_conversation_service()` method
  - Wire `ConversationRepository` dependency

- [X] T023 [US2] Create service unit tests in `tests/test_conversation_service.py`
  - Test `track_message` updates conversation stats
  - Test conversation lookup by session_id
  - Mock repository; no real database needed

---

## Phase 5: US3 — Stateless Fallback Mode (P3) — 1-2 SP

> **Goal**: Agent functions without session tracking when no session_id is provided.
>
> **User Story (spec.md P3)**: Client sends query WITHOUT session_id, agent responds normally, no conversation record persisted.
>
> **Acceptance Criteria**:
> - Agent responds normally without session_id (FR-3.1.6)
> - No conversation data persisted to database
> - Subsequent queries have no memory of prior exchange

- [X] T024 [US3] Create stateless mode tests in `tests/test_agent_memory.py`
  - Test: Query without session_id returns valid response
  - Test: No checkpoint data created when session_id omitted
  - Test: Two sequential queries without session_id have no context carryover

- [X] T025 [US3] Verify backward compatibility in API routes
  - Test: `POST /api/chat` without session_id field returns 200
  - Test: Response omits `session_id` field when not provided (backward compatible)
  - Test: session_id included in response when provided
  - Test: Invalid session_id format returns 400
  - Test: Explicit `session_id: null` treated as stateless

- [X] T026 [US3] Add API contract test in `tests/api/test_chat_routes_memory.py`
  - Test: Omitted session_id treated as stateless (`test_chat_without_session_id_still_works`)
  - Test: Explicit `session_id: null` treated as stateless (`test_chat_with_null_session_id_treated_as_not_provided`)
  - NOTE: Tests already exist in this file (15 tests passing)

---

## Phase 6: US4 — Memory Content Compliance (P4) — 2 SP

> **Goal**: Verify memory stores only allowed content types (conversation text, no financial data).
>
> **User Story (spec.md P4)**: Tools return stock prices, ratios, news; stored memory contains zero financial data.
>
> **Acceptance Criteria**:
> - Zero price values in stored data (FR-3.1.7)
> - Zero financial ratios or calculated metrics (FR-3.1.7)
> - Tool outputs stored as references only, not raw data (FR-3.1.8)

- [X] T027 [US4] Create content compliance validation helper in `src/utils/memory_config.py`
  - Add `ContentValidator` class (or methods in MemoryConfig)
  - Implement `scan_prohibited_patterns(content)` returning list of violations
  - Patterns: `$[0-9]+`, `[0-9]+%`, P/E ratio patterns, price patterns
  - Return empty list if compliant

- [X] T028 [US4] Create compliance audit tests in `tests/test_conversation_service.py`
  - Test: Conversation with tool invocation stores response text only
  - Test: Agent response "I found the price is $150" → "$150" NOT in checkpoint
  - Test: Stored messages pass content compliance scan

- [X] T029 [P] [US4] Add compliance integration test in `tests/integration/test_memory_persistence.py`
  - Test: Full conversation flow with tool calls
  - Test: Inspect checkpoint data for prohibited patterns
  - Test: Audit scan returns zero violations

- [X] T030 [US4] Document compliance verification in quickstart.md
  - Add section on memory compliance testing
  - Include example audit query commands

---

## Phase 7: US5 — Session Recall on Disconnection (P5) — 1-2 SP

> **Goal**: User can resume conversation after temporary disconnection.
>
> **User Story (spec.md P5)**: User has active conversation, network drops, user reconnects with same session_id, agent resumes with context awareness.
>
> **Acceptance Criteria**:
> - Valid session_id restores conversation state when status=active (FR-3.1.5)
> - First response after reconnect references prior context

- [X] T031 [US5] Create reconnection integration test in `tests/integration/test_memory_persistence.py`
  - Test: Simulate disconnect (destroy agent instance)
  - Test: Reconnect with same session_id
  - Test: First response demonstrates context awareness
  - Test: Message count accurate after reconnect

- [X] T032 [US5] Test archived session handling
  - Test: Attempt to resume archived session
  - Test: System returns 409 Conflict with clear message
  - Test: Archived session history still readable (GET endpoint)

- [X] T033 [US5] Add Socket.IO reconnection test in `tests/api/test_chat_routes_memory.py`
  - Test: Disconnect Socket.IO client, reconnect, resume session
  - Test: Context maintained across WebSocket reconnection

---

## Phase 8: Polish & Documentation — 2-3 SP

> **Goal**: Finalize documentation, API contracts, and end-to-end validation.

- [X] T034 Update OpenAPI specification in `docs/openapi.yaml`
  - Add `session_id` parameter to `POST /api/chat` request schema
  - Add `conversation` object to response schema
  - Document all error responses (400, 403, 404, 409, 503)
  - Add `GET /sessions/{session_id}/conversation` endpoint

- [X] T035 [P] Create developer quickstart guide in `specs/spec-driven-development-pilot/quickstart.md`
  - Prerequisites (MongoDB, config setup)
  - How to enable memory feature
  - Example API calls with session_id
  - Troubleshooting common issues

- [X] T036 Create end-to-end multi-turn test in `tests/integration/test_memory_persistence.py`
  - Full user scenario: 5-turn conversation with follow-ups
  - Verify context accuracy ≥95% (SC-1)
  - Verify persistence reliability 100% (SC-2)
  - Benchmark load time < 500ms (SC-7)

- [X] T037 [P] Performance benchmark test
  - Measure `graph.get_state()` latency against `context_load_timeout_ms` config
  - Measure state save time against `state_save_timeout_ms` config
  - Assert both under configured thresholds
  - Log benchmark results for CI tracking

---

## Dependencies & Execution Order

### Critical Path

```
Phase 1 (Setup)
    │
    ▼
Phase 2 (Foundational) ─── BLOCKING ───┬───┬───┬───┬───┐
    │                                  │   │   │   │   │
    ▼                                  ▼   ▼   ▼   ▼   ▼
Phase 3 (US1)                       Phase Phase Phase Phase Phase
Session-Aware                       4     5     6     7     8
Conversation                        (US2) (US3) (US4) (US5) Polish
```

### Task Dependencies

| Task | Depends On | Rationale |
|------|------------|-----------|
| T004-T011 | T001-T003 | Schema/repo need project structure |
| T012-T019 | T006, T008 | Agent integration needs repository and config |
| T020-T023 | T006, T012-T014 | Persistence needs repository and checkpointer |
| T024-T026 | T012-T014 | Stateless mode tests need agent integration |
| T027-T030 | T006, T021 | Compliance needs service layer |
| T031-T033 | T012-T017 | Reconnection tests need full API integration |
| T034-T037 | All prior phases | Polish after implementation complete |

### Parallel Opportunities by Phase

**Phase 2 (Foundational)**:
- T004 + T005 can run parallel (schema vs migration)
- T008 + T009 can run parallel (MemoryConfig vs config_loader)
- T010 + T011 can run parallel (repo tests vs config tests)

**Phase 3 (US1)**:
- T014 + T015 can run parallel (sync vs streaming methods)
- T016 + T017 can run parallel (REST vs Socket.IO routes)

**Phase 4+ (User Stories)**:
- After Phase 2 completes, US3-US5 can proceed in parallel with US1/US2
- US4 (Compliance) has no dependencies on US1-US3 implementation

---

## Independent Test Criteria Per User Story

| User Story | Independent Verification |
|------------|-------------------------|
| **US1** (Session-Aware) | Multi-turn conversation test passes with context recall |
| **US2** (Persistence) | Hash comparison pre/post restart shows 100% match |
| **US3** (Stateless) | Query without session_id succeeds, no data persisted |
| **US4** (Compliance) | Audit scan of stored data returns zero violations |
| **US5** (Reconnection) | Reconnect test shows context maintained |

---

## Implementation Strategy

### MVP Scope (Recommended)

**Phase 1 + Phase 2 + Phase 3 (US1)** = Minimum viable STM feature

- Users can have multi-turn conversations
- Context maintained within session
- Backward compatible (stateless still works)

### Incremental Delivery

1. **Sprint 1**: Phase 1 + Phase 2 (Foundation) → PR #1
2. **Sprint 2**: Phase 3 (US1 Session-Aware) → PR #2 (feature usable)
3. **Sprint 3**: Phase 4-5 (US2 Persistence, US3 Stateless) → PR #3
4. **Sprint 4**: Phase 6-7 (US4 Compliance, US5 Reconnect) + Phase 8 → PR #4

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| MongoDBSaver compatibility | Phase 2 includes integration test with real MongoDB |
| Performance regression | SC-7 benchmark test in Phase 8 |
| Memory leaks | Archive-over-delete policy; TTL on checkpoints |
| Config drift | Frozen MemoryConfig; fail-fast validation |

---

## Validation Checklist

Before marking complete, verify:

- [ ] All 10 functional requirements (FR-3.1.1 - FR-3.1.10) implemented
- [ ] All 5 user scenarios (P1-P5) have passing tests
- [ ] Constitution Article III (Memory Boundaries) compliant
- [ ] Configuration validation catches all invalid values (FR-3.1.10)
- [ ] No hardcoded operational parameters (FR-3.1.9)
- [ ] OpenAPI specification updated
- [ ] 80%+ test coverage on new code
