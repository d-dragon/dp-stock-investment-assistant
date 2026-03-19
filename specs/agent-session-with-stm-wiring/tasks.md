# Tasks: STM Domain Model Refactor and Service-Layer Restructuring

**Input**: Design documents from `specs/agent-session-with-stm-wiring/`
**Prerequisites**: plan.md (required), spec.md (required)
**Branch**: `agent-session-with-stm-wiring`

**Organization**: Tasks follow plan Decision §10.4 (schema first, then services). Phase 2 (Foundational) covers all schema/repository/migration work (FR-003–FR-006). Phases 3–5 cover service-layer restructuring organized by user story. Phase 6 updates tests. User Story 5 is **DEFERRED** per plan Decision §10.1 (deliberate API break).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks in same group)
- **[Story]**: Which user story this task belongs to (US1, US2, US4)
- `<!-- parallel-group: N -->` marks groups of up to 3 tasks for concurrent fleet execution
- `<!-- sequential -->` marks tasks that must run in strict order

---

## Phase 1: Setup

**Purpose**: No new project setup required — existing project, existing branch. Verify prerequisites.

<!-- sequential -->
- [x] T001 Verify branch `agent-session-with-stm-wiring` is checked out and all source files listed in plan.md §Project Structure exist at expected paths. No changes — read-only validation.

---

## Phase 2: Foundational — Schema, Repositories, and Migration

**Purpose**: Establish correct data contracts before any service code changes (Plan Decision §10.4). Covers FR-003 (type normalization), FR-004 (sessions schema), FR-005 (conversations identity refactor), FR-006 (clean-slate migration). This phase corresponds to spec User Story 3 (Schema and Identity Normalization).

**⚠ CRITICAL**: No service-layer work (Phases 3–5) can begin until this phase is complete.

### Schema Files

<!-- parallel-group: 1 -->
- [x] T002 [P] Normalize `user_id` type from `objectId` to `string` in `WORKSPACES_SCHEMA` and update `get_workspaces_validation()` in `src/data/schema/workspaces_schema.py` (FR-003). Change the `bsonType` of `user_id` from `"objectId"` to `"string"`.

- [x] T003 [P] Extend sessions schema in `src/data/schema/sessions_schema.py` (FR-003, FR-004, FR-009, FR-009a): (1) Add `session_id` field — `bsonType: "string"`, UUID v4 pattern `^[0-9a-f]{8}-...`, add to `required` array. (2) Change `workspace_id` bsonType from `"objectId"` to `"string"`. (3) Add `user_id` field — `bsonType: "string"`. (4) Rename status enum value `"open"` → `"active"`, add `"archived"` to enum. (5) Add context fields: `assumptions` (string|null), `pinned_intent` (string|null), `focused_symbols` (array of strings). (5a) Add `linked_symbol_ids` field — `bsonType: "array"`, items `"string"` — linked symbol references for session scope (W6). (6) Add index `idx_sessions_session_id` (session_id, unique) to `SESSIONS_INDEXES`. (7) Add a `get_sessions_indexes()` helper function if missing.

- [x] T004 [P] Refactor conversations schema in `src/data/schema/conversations_schema.py` (FR-002, FR-005): (1) Add `conversation_id` field — `bsonType: "string"`, UUID v4 pattern, add to `required`. (2) Add `thread_id` field — `bsonType: "string"`, add to `required`. (3) Change `session_id` from required+unique to required+non-unique (remove from unique index, keep in required). (4) Change `workspace_id` and `user_id` from `["string", "null"]` to `"string"` (make required, add to `required` array). (5) Remove `session_assumptions` and `pinned_intent` properties (moved to session). (6) Add `context_overrides` (bsonType: ["object", "null"]) and `conversation_intent` (bsonType: ["string", "null"]). (6a) Add `focused_symbols` (bsonType: "array", items "string") — thread-local symbol refinement inheriting from session (W3). (6b) Add `archived_at` (bsonType: ["date", "null"]) and `archive_reason` (bsonType: ["string", "null"], enum: ["user_closed", "inactivity", "workspace_archived", null]) — archival metadata (W2, FR-016). (7) Update `CONVERSATIONS_INDEXES`: drop `idx_conversations_session_id_unique`, add `idx_conversations_conversation_id` (unique), `idx_conversations_thread_id` (unique), `idx_conversations_session_id` (non-unique), `idx_conversations_hierarchy_status` (workspace_id + session_id + status, compound). (8) Update `get_default_conversation_document()` to accept `conversation_id` and `thread_id` parameters, remove `session_assumptions`/`pinned_intent` defaults.

### Repository Files

<!-- parallel-group: 2 -->
- [x] T005 [P] Refactor `src/data/repositories/session_repository.py` (FR-004): (1) Remove all `ObjectId(workspace_id)` calls — use string directly in queries. (2) Add `find_by_session_id(session_id: str) -> Optional[Dict]` method. (3) Add `update_status(session_id: str, status: str) -> Optional[Dict]` method. (4) Add `find_by_workspace(workspace_id: str, status: Optional[str] = None) -> List[Dict]` method using string comparison. (5) Update `get_by_workspace_id()` to use string instead of `ObjectId()`. (6) Update `get_by_status()` to use string instead of `ObjectId()`. (7) Rename `get_active_sessions()` to query `"active"` instead of `"open"`.

- [x] T006 [P] Refactor `src/data/repositories/conversation_repository.py` (FR-002, FR-005, FR-010, FR-011): (1) Add `find_by_conversation_id(conversation_id: str) -> Optional[Dict]` method. (2) Keep existing `find_by_session_id()` but change return type to `List[Dict]` (returns multiple, non-unique). (3) Add `create_conversation(conversation_id: str, session_id: str, workspace_id: str, user_id: str, thread_id: str) -> Optional[Dict]` explicit create method — validates `thread_id == conversation_id`. (4) Update `get_or_create()` to use `conversation_id` as the unique key instead of `session_id`. (5) Update `update_activity()` to accept `conversation_id` instead of `session_id`. (6) Update `archive()` and `set_status()` to accept `conversation_id` instead of `session_id`. (7) Add `find_by_session_id_list(session_id: str) -> List[Dict]` for listing conversations under a session. (8) Update `exists_by_session_id()` → add `exists_by_conversation_id()`.

### Migration

<!-- sequential -->
- [x] T007 Update clean-slate migration in `src/data/migration/db_setup.py` (FR-006, Decision §10.2): (1) Add logic to drop `conversations` collection before recreation. (2) Add logic to drop `sessions` collection before recreation to remove stale enum/type records. (3) Add logic to drop LangGraph checkpoint collections (`agent_checkpoints` and any write-ahead collections). (4) Log warnings at WARNING level about data loss during drop with affected collection names. (5) Ensure recreated collections use updated schemas and indexes from T003 and T004. (6) Make migration idempotent — safe to re-run.

**Checkpoint**: All schema, repository, and migration changes are complete. Data contracts are stable. Service-layer work can now begin.

---

## Phase 3: User Story 1 — Conversation-Scoped Agent Memory (Priority: P1) 🎯 MVP

**Goal**: Decouple agent memory from session identity to conversation identity. `conversation_id` becomes the canonical STM key; `thread_id == conversation_id`. Each conversation gets its own independent agent memory thread.

**Independent Test**: Create two conversations under one session, send messages in each, verify agent memory is isolated per conversation. Verify stateless mode (no conversation_id) still works.

### Protocols (prerequisite for all service changes)

<!-- sequential -->
- [x] T008 [US1] Update `src/services/protocols.py` (FR-013, FR-015, FR-015a): (1) In `AgentProvider` protocol — rename `session_id` parameter to `conversation_id` in `process_query()`, `process_query_streaming()`, and `process_query_structured()`. (2) Update `ConversationProvider` protocol — rename `get_conversation(session_id)` to `get_conversation(conversation_id: str)`, update docstrings to reference conversation_id. (3) Add new `SessionProvider` protocol with methods: `get_session(session_id: str) -> Optional[Dict]` and `get_session_context(session_id: str) -> Optional[Dict]`. Make it `@runtime_checkable`.

### Exception Contract Prerequisite

<!-- sequential -->
- [x] T011 [US1] Update `src/services/exceptions.py`: (1) Rename `ArchivedSessionError` → `ArchivedConversationError` — update `session_id` attribute to `conversation_id`, update error message text. (2) Rename `SessionNotFoundError` → `ConversationNotFoundError` — update `session_id` attribute to `conversation_id`. (3) Add `InvalidLifecycleTransitionError(ServiceError)` with `entity_type`, `current_status`, `target_status` attributes for lifecycle state machine violations (FR-009, FR-015a).

### Service + Agent (independent files, can parallelize)

<!-- parallel-group: 3 -->
- [x] T009 [P] [US1] Refactor core conversation identity methods in `src/services/conversation_service.py` (FR-010, FR-011, FR-015a): (1) Rename `track_message(session_id, ...)` → `track_message(conversation_id, ...)` — update all internal references. (2) Rename `get_conversation(session_id)` → `get_conversation(conversation_id)`. (3) Add `create_conversation(session_id: str, workspace_id: str, user_id: str) -> Optional[Dict]` — generates `conversation_id` via `uuid.uuid4()`, sets `thread_id == conversation_id`, calls repository `create_conversation()`. (4) Add `list_conversations(session_id: str) -> List[Dict]` — list by parent session. (5) Rename `archive_conversation(session_id)` → `archive_conversation(conversation_id)`. (6) Update lifecycle transitions to enforce state machine: active→summarized, active→archived, summarized→archived (FR-015a) and raise `InvalidLifecycleTransitionError` from T011.

- [x] T010 [P] [US1] Refactor `src/core/stock_assistant_agent.py` (FR-013): (1) In `process_query()` — rename `session_id` parameter to `conversation_id`. (2) In `process_query_streaming()` — rename `session_id` parameter to `conversation_id`. (3) In `process_query_structured()` — add `conversation_id` parameter (current signature lacks session/thread identity parameter). (4) In `_process_with_react()` — rename `session_id` → `conversation_id`, build `invoke_config` with `thread_id: conversation_id`. (5) In `_stream_with_react_async()` — rename `session_id` → `conversation_id`. (6) Agent remains unaware of session/workspace hierarchy — only receives `conversation_id` as thread identity.

- [x] T012 [P] [US2] Create `src/services/session_service.py` (FR-007, FR-008, FR-009, FR-009a, FR-009b): (1) Class `SessionService(BaseService)` with constructor accepting `session_repository`, `workspace_repository` (for ownership validation), `conversation_repository` (for cascade archive), `cache: Optional[CacheBackend]`. (2) `create_session(workspace_id, user_id, title, **kwargs)` — validate workspace exists via workspace_repository, generate `session_id` via `uuid.uuid4()`, insert with status `"active"`. (3) `get_session(session_id)` — lookup by session_id with cache. (4) `list_sessions(workspace_id, status_filter=None)` — list by workspace. (5) `update_session(session_id, updates: Dict)` — update metadata fields. (6) `close_session(session_id)` — enforce `active→closed` only, no new conversations allowed after close. (7) `archive_session(session_id)` — enforce `closed→archived` only (sequential lifecycle per W1 decision; no `active→archived` skip), cascade archive all child conversations via conversation_repository. (8) `get_session_context(session_id)` — return `{assumptions, pinned_intent, focused_symbols}` dict. (9) `update_session_context(session_id, assumptions=None, pinned_intent=None, focused_symbols=None)` — partial update of context fields. (10) `health_check()` — standard `_dependencies_health_report()` with required `session_repository`. (11) Define `SESSION_CACHE_TTL = 300` class attribute.

<!-- sequential -->
- [x] T026 [US1] Complete context-focused enhancements in `src/services/conversation_service.py` (FR-011a, FR-011b): (1) Add `get_conversation_with_context(conversation_id: str) -> Optional[Dict]`. (2) Add `update_context_overrides(conversation_id: str, overrides: Dict) -> bool`. (3) Implement merge strategy for inherited context per spec clarifications: load session context at request time (live read), then apply conversation `context_overrides` as shallow key overwrite; if `focused_symbols` exists in overrides, it replaces inherited `focused_symbols` for that conversation only.

- [x] T032 [US1] Complete conversation cache-key refactor in `src/services/conversation_service.py` (FR-010): update remaining cache key helpers from session_id to conversation_id, including `_conversation_cache_key()` and `_invalidate_conversation_cache()`, and verify all call sites use conversation-scoped keys.

**Checkpoint**: ConversationService uses conversation_id, agent uses conversation_id as thread_id, protocols define canonical contracts. Conversation-scoped memory isolation is in place.

---

## Phase 4: User Story 2 — Session Lifecycle Management (Priority: P2)

**Goal**: Sessions become business grouping containers with lifecycle states (active→closed→archived) and reusable context (assumptions, pinned_intent, focused_symbols) that child conversations inherit.

**Independent Test**: Create sessions under a workspace, transition through lifecycle states, verify lifecycle constraints enforce on child conversations. Verify session context retrieval.

<!-- sequential -->

- [x] T031 [US2] Validate and finalize `SessionService` behavior after implementation (FR-007, FR-008, FR-009, FR-009a, FR-009b): confirm lifecycle guards, cascade archive behavior, context get/update semantics, cache usage, and dependency health report behavior remain aligned with spec.

**Checkpoint**: SessionService provides full lifecycle management. Sessions store and retrieve reusable context.

---

## Phase 5: User Story 4 — Service-Layer Conversation-Aware Chat Flow (Priority: P4)

**Goal**: Wire conversation identity and session context into the runtime chat path. ChatService resolves conversation, validates ownership, loads session context, invokes agent with conversation's thread_id.

**Independent Test**: Send chat messages through ChatService and verify conversation metadata updates, session context availability, and cross-boundary isolation.

### ChatService + Factory (sequential — dependency chain)

<!-- sequential -->
- [x] T013 [US4] Refactor `src/services/chat_service.py` (FR-012, FR-012a, FR-012b, FR-017): (1) Add `session_provider: Optional[SessionProvider]` constructor parameter (import from protocols). (2) Rename `_validate_session_not_archived(session_id)` → `_validate_conversation_active(conversation_id)` — validate conversation exists, status is active or summarized, validate conversation belongs to expected workspace via hierarchy. (3) Add `_load_conversation_context(conversation_id: str) -> Optional[Dict]` method — load session context via SessionProvider, merge with conversation-level `context_overrides`, return merged dict. (4) Update `stream_chat_response()` — rename `session_id` parameter to `conversation_id`, pass to agent as `conversation_id` when present. (5) Update `process_chat_query()` — rename `session_id` to `conversation_id`. (6) Update `process_chat_query_structured()` — add `conversation_id` parameter. (7) Preserve FR-017 stateless path: if `conversation_id` is absent, bypass conversation/session persistence validation and process without checkpoint persistence. (8) Replace all `ArchivedSessionError` references with `ArchivedConversationError` import.

- [x] T014 [US4] Update `src/services/factory.py` (FR-014): (1) Add import for `SessionService` from `services.session_service`. (2) Add `get_session_service() -> SessionService` public builder. (3) Add `_build_session_service()` private builder — wire `session_repository`, `workspace_repository`, `conversation_repository` from RepositoryFactory, inject `cache`. (4) Update `_build_chat_service()` — add `session_provider=self.get_session_service()` to ChatService constructor call. (5) Register `"session_service"` in `_services` dict for singleton caching.

### API Entry Points (parallel — different files, both depend on T013)

<!-- parallel-group: 4 -->
- [x] T015 [P] [US4] Refactor `src/web/routes/ai_chat_routes.py` (Decision §10.1, FR-017): (1) Rename `session_id` parameter to `conversation_id` in request body extraction. (2) Update UUID v4 validation to use `conversation_id` field name when provided. (3) Pass `conversation_id` to `stream_chat_response()` and `process_chat_query()`. (4) Update response body — include `conversation_id` for stateful flows; keep stateless responses valid when `conversation_id` is omitted. (5) Update `ArchivedSessionError` catch → `ArchivedConversationError` with updated response field names (`conversation_id` instead of `session_id`, code `CONVERSATION_ARCHIVED`). (6) Update all log messages from `session=` to `conversation=`. (7) Update request JSON docstring to document `conversation_id` replacing `session_id` while preserving stateless operation when not supplied.

- [x] T016 [P] [US4] Refactor `src/web/sockets/chat_events.py` (Decision §10.1, FR-017): (1) Rename `session_id` extraction to `conversation_id` in `handle_chat_message()`. (2) Update UUID v4 validation to use `conversation_id` when present. (3) Pass `conversation_id` to agent via `process_query()`. (4) Update response payload — echo `conversation_id` for stateful flows; allow stateless flow when absent. (5) Update `SocketIOContext` dataclass if agent method signatures changed. (6) Update all debug/error log messages from `session_id=` to `conversation_id=`.

**Checkpoint**: Full chat flow uses conversation_id end-to-end. Session context is loaded and merged. API contract is updated (deliberate break).

---

## Phase 6: Test Updates

**Purpose**: Update existing tests for conversation_id identity model and add tests for new SessionService. Plan Phase 3.

### Schema + New Service Tests

<!-- parallel-group: 5 -->
- [x] T017 [P] Update `tests/test_conversations_schema.py`: Validate updated conversations schema — `conversation_id` required, `thread_id` required, `session_id` non-unique, `workspace_id`/`user_id` required not nullable, `session_assumptions`/`pinned_intent` removed, `context_overrides` and `conversation_intent` added. Validate index changes (unique conversation_id, unique thread_id, non-unique session_id, compound hierarchy_status).

- [x] T018 [P] Update `tests/test_conversation_repository.py`: (1) Replace all `session_id`-based lookups with `conversation_id`-based lookups. (2) Test `find_by_conversation_id()`, `create_conversation()`, updated `get_or_create()`. (3) Test `find_by_session_id()` returns `List[Dict]` (multiple). (4) Test `update_activity()` and `archive()` with `conversation_id`. (5) Test `exists_by_conversation_id()`.

- [x] T019 [P] Create `tests/test_session_service.py`: (1) Test `create_session()` — workspace ownership validation, UUID generation, status defaults to `"active"`. (2) Test `get_session()`, `list_sessions()` — basic CRUD. (3) Test lifecycle transitions: active→closed (success), closed→archived (success), archived→active (reject), closed→active (reject). (4) Test `archive_session()` cascade — verify child conversations archived. (5) Test `get_session_context()` and `update_session_context()` — partial updates, retrieval. (6) Test `health_check()` contract. Use protocol-based mocking for repositories.

### Service + Integration Tests

<!-- parallel-group: 6 -->
- [x] T020 [P] Update `tests/test_conversation_service.py`: (1) Replace all `session_id` calls with `conversation_id`. (2) Test `create_conversation()` — UUID generation, `thread_id == conversation_id`, session context inheritance stub. (3) Test `list_conversations(session_id)`. (4) Test `update_context_overrides()`. (5) Test lifecycle state machine: active→summarized, active→archived, summarized→archived (success), archived→active (reject).

- [x] T021 [P] Update `tests/test_chat_service.py`: (1) Replace `session_id` with `conversation_id` in all test methods. (2) Test `_validate_conversation_active()` — active passes, summarized passes, archived raises `ArchivedConversationError`. (3) Test session context loading via mock `SessionProvider`. (4) Test context merge (session context + conversation overrides). (5) Test streaming and non-streaming flows with `conversation_id`. (6) Verify `SessionNotFoundError`→`ConversationNotFoundError` handling.

- [x] T022 [P] Update `tests/test_agent_memory.py`: (1) Replace `session_id` parameter with `conversation_id` in all agent calls. (2) Test `conversation_id` → `thread_id` mapping in invoke config. (3) Test stateless mode (`conversation_id=None`) still works.

<!-- parallel-group: 6b -->
- [x] T027 [P] Update `tests/api/test_chat_routes_memory.py` for API break compatibility (W-R2): replace `session_id` request/response usage with `conversation_id`, update fixtures/mocks/assertions for conversation-scoped memory behavior, and preserve stateless-mode coverage.

- [x] T028 [P] Update `tests/test_api_routes.py` for conversation-scoped API contracts (W-R2): replace endpoint payload/response/session assertions from `session_id` to `conversation_id` and align error-code assertions for archived conversation handling.

- [x] T029 [P] Update `tests/test_chat_routes.py` for route-level parameter migration (W-R2): replace `session_id` extraction/validation assertions with `conversation_id`, and align route logging/message expectations.

<!-- sequential -->
- [x] T030 Update `tests/test_additional_repositories.py` for repository-level identity changes (W-R2): replace legacy `session_id` unique-key assumptions with `conversation_id` unique-key plus non-unique session FK expectations.

**Checkpoint**: All unit tests pass with conversation_id identity model. New SessionService has full test coverage.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Integration tests, documentation, and final validation.

<!-- parallel-group: 7 -->
- [x] T023 [P] Update integration tests if they exist: `tests/integration/test_stm_runtime_wiring.py` (conversation_id thread mapping) and `tests/integration/test_memory_persistence.py` (multi-conversation isolation). If files don't exist, skip.

- [x] T024 [P] Update `tests/test_sessions_schema.py` (if exists) or create it: Validate extended sessions schema — `session_id` required+unique, `workspace_id` is string not objectId, `user_id` added, status enum includes `"active"`, `"closed"`, `"archived"`. Validate context fields (`assumptions`, `pinned_intent`, `focused_symbols`). Validate new index `idx_sessions_session_id`.

<!-- sequential -->
- [x] T025 Run full test suite (`pytest -v`) and fix any remaining failures caused by the session_id→conversation_id migration across the codebase, including files covered in T027-T030. Verify zero behavioral regressions after all planned test updates are complete.

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
  └──► Phase 2 (Foundational: Schema + Repos + Migration) ◄── BLOCKS ALL SERVICE WORK
         └──► Phase 3 (US1: Conversation-Scoped Memory)
         │       └──► Phase 5 (US4: Chat Flow) ◄── depends on US1 + US2
         └──► Phase 4 (US2: Session Lifecycle)
                 └──► Phase 5 (US4: Chat Flow) ◄── depends on US1 + US2
                         └──► Phase 6 (Tests)
                                 └──► Phase 7 (Polish)
```

### Task Dependency Graph

```
T001 (verify)
  └──► T002, T003, T004  ← parallel-group: 1 (3 schema files)
         └──► T005, T006  ← parallel-group: 2 (2 repo files)
                └──► T007 (migration, sequential)
                       └──► T008 (protocols, sequential — prerequisite)
                              └──► T011 (exceptions, sequential prerequisite)
                                     └──► T009, T010, T012  ← parallel-group: 3 (conv service core, agent, session service)
                                            └──► T026 (conversation context merge/finalization, sequential)
                                                   └──► T032 (conversation cache-key refactor, sequential)
                                                          └──► T031 (session lifecycle/context validation, sequential)
                                                                 └──► T013 (chat service, sequential)
                                                                        └──► T014 (factory, sequential)
                                                                               └──► T015, T016  ← parallel-group: 4 (API entry points)
                                                                                      └──► T017, T018, T019  ← parallel-group: 5
                                                                                             └──► T020, T021, T022  ← parallel-group: 6
                                                                                                    └──► T027, T028, T029  ← parallel-group: 6b
                                                                                                           └──► T030 (sequential)
                                                                                                                  └──► T023, T024  ← parallel-group: 7
                                                                                                                         └──► T025 (full suite)
```

### Parallel Opportunities Summary

| Group | Tasks | Files | Can Fan Out |
|-------|-------|-------|-------------|
| 1 | T002, T003, T004 | workspaces_schema, sessions_schema, conversations_schema | 3 agents |
| 2 | T005, T006 | session_repository, conversation_repository | 2 agents |
| 3 | T009, T010, T012 | conversation_service, stock_assistant_agent, session_service | 3 agents |
| 4 | T015, T016 | ai_chat_routes, chat_events | 2 agents |
| 5 | T017, T018, T019 | test_conversations_schema, test_conversation_repo, test_session_service | 3 agents |
| 6 | T020, T021, T022 | test_conversation_service, test_chat_service, test_agent_memory | 3 agents |
| 6b | T027, T028, T029 | test_chat_routes_memory, test_api_routes, test_chat_routes | 3 agents |
| 7 | T023, T024 | integration tests, test_sessions_schema | 2 agents |

---

## Implementation Strategy

### MVP First (Phase 2 + Phase 3 = US1)

1. Complete Phase 2: Foundational (schema contracts stable)
2. Complete Phase 3: US1 — Conversation-Scoped Agent Memory
3. **STOP and VALIDATE**: Two conversations under one session have isolated agent memory
4. Stateless mode (no conversation_id) still works

### Incremental Delivery

1. Phase 2 (Foundational) → Schema contracts stable
2. Phase 3 (US1) → Conversation-scoped memory works → **MVP testable**
3. Phase 4 (US2) → Session lifecycle + context inheritance works
4. Phase 5 (US4) → Full chat flow wired end-to-end → **Feature complete**
5. Phase 6 (Tests) → All tests updated and passing
6. Phase 7 (Polish) → Integration tests, final validation

---

## Notes

- **Deliberate API break** (Decision §10.1): No `session_id` shim. Stateful callers provide `conversation_id`; missing `conversation_id` follows FR-017 stateless mode.
- **Clean-slate migration** (Decision §10.2): `sessions`, `conversations`, and `agent_checkpoints` collections are dropped and recreated. No production data exists.
- **Schema first** (Decision §10.4): All Phase 2 tasks MUST complete before any Phase 3+ work.
- SC-006 (legacy data accessible) — **RESOLVED**: SC-006 struck in spec.md and replaced with clean-slate success criterion per C1 remediation.
- [P] tasks = different files, no dependencies within same parallel group
- Commit after each task or logical group
- Stop at any checkpoint to validate independently
