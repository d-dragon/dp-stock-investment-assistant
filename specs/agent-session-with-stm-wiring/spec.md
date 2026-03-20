# Feature Specification: STM Domain Model Refactor and Service-Layer Restructuring

**Feature Branch**: `agent-session-with-stm-wiring`  
**Created**: 2026-03-17  
**Status**: Verified  
**Input**: User description: "Implement the domain model refactor and service-layer restructuring for STM (Short-Term Memory) integration as defined in the AGENTIC_APP_WITH_STM_INTEGRATION_ROADMAP.md"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Conversation-Scoped Agent Memory (Priority: P1)

A user starts a chat within a session and each new conversation gets its own independent agent memory thread. When the user sends messages within the same conversation, the agent recalls prior context from that conversation only. Messages in a different conversation under the same session do not bleed into each other's memory.

**Why this priority**: This is the core architectural change — decoupling agent memory from session identity to conversation identity. Without this, the entire multi-conversation-per-session model is impossible. Every other story depends on this identity shift being correct.

**Independent Test**: Can be fully tested by creating two conversations under one session, sending messages in each, and verifying that agent memory is isolated per conversation. Delivers the fundamental guarantee that conversation is the STM boundary.

**Acceptance Scenarios**:

1. **Given** a session exists with no conversations, **When** a user starts a new conversation and sends a message, **Then** the system creates a conversation record, assigns a unique conversation_id, uses that conversation_id as thread_id for the agent, and the agent processes the message with fresh memory state.
2. **Given** two active conversations exist under the same session, **When** the user sends a message in conversation A referencing "AAPL", then sends a message in conversation B asking "what stock did I mention?", **Then** the agent in conversation B has no knowledge of the AAPL mention from conversation A.
3. **Given** a conversation with prior message history, **When** the user resumes the conversation after a period of inactivity, **Then** the agent retrieves the prior checkpoint state using the conversation's thread_id and continues with full context from that conversation.
4. **Given** no conversation_id is provided (stateless mode), **When** the user sends a chat message, **Then** the system processes the message without any persistent memory, maintaining backward compatibility with the stateless flow.

---

### User Story 2 - Session Lifecycle Management (Priority: P2)

A user creates, lists, closes, and archives sessions within a workspace. Sessions serve as business grouping containers for related conversations and hold reusable session context such as assumptions, pinned intent, and symbol focus that child conversations can inherit.

**Why this priority**: Sessions are the organizational unit between workspace and conversation. Without session lifecycle management, there is no business grouping above conversation and no way to enforce policies on groups of related work.

**Independent Test**: Can be fully tested by creating sessions under a workspace, transitioning them through lifecycle states (active → closed → archived), and verifying that lifecycle constraints are enforced on child conversations.

**Acceptance Scenarios**:

1. **Given** a workspace exists, **When** a user creates a new session with a title, **Then** the system creates a session record owned by that workspace with status "active" and returns a unique session_id.
2. **Given** an active session, **When** the user closes the session, **Then** the session status transitions to "closed", existing active conversations within it remain fully operational (users can still send and receive messages), but no new conversations can be created under the closed session.
3. **Given** a closed session, **When** the user archives the session, **Then** the session status transitions to "archived" and all child conversations are also archived, becoming immutable.
4. **Given** an archived session, **When** the user attempts to create a new conversation or send a message to any conversation within it, **Then** the system rejects the request.
5. **Given** a workspace with multiple sessions, **When** the user lists sessions, **Then** the system returns all sessions owned by that workspace.
6. **Given** an active session stores reusable assumptions, pinned intent, and focused symbols, **When** a user starts a new conversation under that session, **Then** the conversation inherits that session context without requiring the user to restate it.

---

### User Story 3 - Schema and Identity Normalization (Priority: P3)

The system uses consistent identifier types and naming across workspaces, sessions, and conversations. Cross-collection references use the same data type. Every conversation has its own conversation_id as the primary key, with session_id as a parent foreign key instead of the unique business key.

**Why this priority**: Without consistent identifiers and schema alignment, ownership validation, authorization checks, and cross-collection queries are fragile. This is foundational plumbing that all higher-level features depend on for correctness.

**Independent Test**: Can be fully tested by verifying schema validation rules, creating records across all three collections, and confirming that cross-collection lookups resolve correctly with consistent types.

**Acceptance Scenarios**:

1. **Given** the updated schema is applied, **When** a conversation record is created, **Then** it contains conversation_id (unique), session_id (parent FK), workspace_id, user_id, thread_id (equals conversation_id), and status fields with consistent types.
2. ~~**Given** existing session-based conversation data, **When** a migration runs, **Then** legacy records where session_id was the unique key are transformed so that session_id becomes a parent FK and conversation_id becomes the new unique key, preserving the original session_id value as the conversation_id for backward compatibility.~~ **REPLACED per Decision §10.2 (clean-slate migration)**: **Given** the clean-slate migration has run, **When** the system inspects the conversations collection, **Then** the collection exists with the correct schema (conversation_id unique, session_id non-unique FK, thread_id == conversation_id) and indexes, containing zero legacy records.
3. **Given** the sessions schema, **When** a session record is created, **Then** it contains session_id (explicit business identifier), workspace_id, user_id, and status fields.
4. **Given** cross-collection references, **When** workspace_id is stored in sessions or conversations, **Then** the data type is consistent (string) across all collections.

---

### User Story 4 - Service Layer Conversation-Aware Chat Flow (Priority: P4)

When a user sends a chat message, the ChatService resolves the conversation by conversation_id, validates it belongs to the expected session and workspace, loads inherited session context plus any conversation-specific refinements, invokes the agent using the conversation's thread_id, and updates conversation metadata after both user and assistant turns.

**Why this priority**: This wires the identity refactor into the actual runtime chat path, making conversation metadata operationally meaningful rather than a disconnected sidecar.

**Independent Test**: Can be fully tested by sending chat messages through the service layer and verifying that conversation metadata is updated after each exchange and that session-scoped context is available inside sibling conversations without leaking STM history across them.

**Acceptance Scenarios**:

1. **Given** an active conversation, **When** a user sends a message through ChatService, **Then** ChatService resolves the conversation record by conversation_id, confirms status is "active", uses conversation.thread_id to invoke the agent, and updates message_count and last_activity_at after both user and assistant turns.
2. **Given** a conversation belonging to session S1 in workspace W1, **When** a request arrives claiming the conversation belongs to a different session or workspace, **Then** ChatService rejects the request with an appropriate error.
3. **Given** an archived conversation, **When** a user attempts to send a message, **Then** ChatService returns a conflict error indicating the conversation is archived and immutable.
4. **Given** a session stores a pinned intent and focused symbols, **When** a conversation under that session is resumed, **Then** ChatService loads that session context for the conversation before invoking the agent.
5. **Given** a conversation refines the inherited session context for its own thread, **When** a sibling conversation in the same session is processed, **Then** the sibling receives the base session context but not the first conversation's thread-local refinement.

---

### User Story 5 - Backward Compatibility for Session-Based Callers (Priority: P5) **[DEFERRED]**

> **Note**: Deferred per plan Decision §10.1 (deliberate API break). No transitional shim is built in this iteration. Callers must provide `conversation_id` directly.

Existing callers that pass session_id instead of conversation_id continue to work during a transition period. The system interprets a bare session_id as a reference to the default or most recent conversation within that session, or creates one if none exists.

**Why this priority**: Prevents breaking existing integrations and tests during the migration period. Lower priority because it is a transitional concern, not the target architecture.

**Independent Test**: Can be fully tested by sending chat requests using only session_id (no conversation_id) and verifying that the system resolves to a valid conversation and processes the message correctly.

**Acceptance Scenarios**:

1. **Given** a caller sends a chat request with session_id but no conversation_id, **When** the system receives the request, **Then** it looks up or creates a default conversation under that session and processes the message using that conversation's thread_id.
2. **Given** legacy data where session_id was used as thread_id, **When** the migration has run, **Then** the legacy thread_id is preserved as the conversation_id so that prior checkpoint state remains accessible.

---

### Edge Cases

- What happens when a conversation_id is provided that does not exist in the database? The system returns a 404 error.
- What happens when a session is archived while a user has an active streaming response in a child conversation? The in-flight response completes, but subsequent messages are rejected.
- What happens when a user attempts to create a conversation under a session they do not own? The system rejects with a 403 error after workspace ownership validation.
- How does the system handle simultaneous requests to archive a session and send a message to a child conversation? The archive operation takes precedence; the message is rejected if the conversation status has transitioned to archived by the time it is processed.
- ~~What happens if the migration encounters a conversation record whose session_id does not map to any existing session? The migration logs a warning and creates the conversation_id from the session_id value, leaving session_id as a dangling reference for manual reconciliation.~~ **REPLACED per Decision §10.2**: What happens if the clean-slate migration encounters pre-existing data in the target collections? The migration drops the collections and recreates them with the new schema; no legacy data is preserved.
- What happens when a session has reusable context and a conversation applies a thread-local refinement? The refinement applies only to that conversation thread; sibling conversations continue to inherit the base session context.

## Requirements *(mandatory)*

### Functional Requirements

#### Phase A: Domain and Schema Alignment

- **FR-001**: System MUST adopt a domain model where one workspace owns many sessions, one session owns many conversations, and one conversation maps 1:1 to a LangGraph agent checkpoint thread.
- **FR-002**: System MUST use conversation_id as the primary STM key instead of session_id; thread_id MUST equal conversation_id; session_id MUST become a parent foreign key on conversations.
- **FR-003**: System MUST fix type inconsistencies so that workspace_id, user_id, and session_id use a consistent data type (string) across workspaces, sessions, and conversations collections.
- **FR-004**: Sessions schema MUST include explicit session_id (string, unique business identifier), user_id, and workspace_id fields.
- **FR-005**: Conversations schema MUST replace the session_id unique index with a conversation_id unique index, add session_id as a non-unique parent FK, and add thread_id equal to conversation_id.
- **FR-006**: ~~System MUST provide a migration path for existing session-based STM data that preserves historical thread identifiers by promoting them into conversation identifiers.~~ **REPLACED per Decision §10.2 (clean-slate migration)**: System MUST execute a clean-slate migration that drops existing conversation/checkpoint data and recreates empty collections with the new schema and indexes.

#### Phase B: Service-Layer Refactor

- **FR-007**: System MUST introduce a SessionService with operations: create, get, list (by workspace), update, close, and archive sessions.
- **FR-008**: SessionService MUST validate workspace ownership when creating or modifying sessions.
- **FR-009**: SessionService MUST enforce lifecycle transitions: active → closed → archived. Reverse transitions MUST NOT be allowed.
- **FR-009a**: SessionService MUST store and retrieve session-scoped reusable context including assumptions, pinned intent, and focused symbols so that conversations under the same session can reuse the same analytical context.
- **FR-009b**: When a session transitions to "closed", existing active conversations MUST remain fully operational (messaging allowed), but no new conversations can be created. When a session transitions to "archived", all child conversations MUST also transition to "archived".
- **FR-010**: ConversationService MUST be refactored to use conversation_id-based lookups instead of session_id-based lookups, with session_id retained as a parent FK for filtering.
- **FR-011**: ConversationService MUST support creating conversations under a session, listing conversations by session_id, and looking up conversations by conversation_id.
- **FR-011a**: New and resumed conversations MUST inherit the owning session's stored assumptions, pinned intent, and focused symbols as default context.
- **FR-011b**: ConversationService MUST support conversation-level refinement of inherited session context without mutating the base session context or affecting sibling conversations.
- **FR-012**: ChatService MUST resolve conversation context by conversation_id, validate that the conversation belongs to the expected session and workspace, use conversation.thread_id to invoke the agent, and track metadata (message_count, last_activity_at) on each turn.
- **FR-012a**: ChatService MUST load session-scoped context for the resolved conversation and apply any conversation-specific refinements before invoking the agent.
- **FR-012b**: Session context and conversation refinements MUST remain isolated to the owning session and conversation; they MUST NOT leak across workspace or session boundaries.
- **FR-013**: AgentProvider protocol MUST accept conversation_id instead of session_id for thread_id mapping. The agent itself MUST remain unaware of business grouping above thread_id.
- **FR-014**: ServiceFactory MUST be updated to wire SessionService with its dependencies.
- **FR-015**: protocols.py MUST define a SessionProvider protocol and update the ConversationProvider protocol to use conversation_id instead of session_id.
- **FR-015a**: Conversation lifecycle transitions MUST follow the state machine: active → summarized, active → archived, summarized → archived. Reverse transitions MUST NOT be allowed. The "summarized" state indicates that a conversation summary exists for context compaction and later resume; it does not by itself invalidate the conversation thread.

#### Cross-Cutting Constraints

- **FR-016**: Archived conversations MUST remain immutable — no new messages, no status changes except through administrative reconciliation.
- **FR-017**: Stateless mode (no conversation_id provided) MUST continue to function, processing messages without persistent memory.
- **FR-018**: Memory MUST never store facts (Constitution Article I compliance).
- **FR-019**: ~~System MUST support backward compatibility for callers using session_id during a transition period, by resolving session_id to a default conversation when conversation_id is absent.~~ **DEFERRED** — Per plan Decision §10.1 (deliberate API break), no backward-compat shim is built in this iteration.

### Key Entities

- **Workspace**: Top-level business container. Owns many sessions. Attributes: workspace_id, user_id, title, status, timestamps. Serves as ownership and isolation boundary.
- **Session**: Business workflow container within a workspace. Owns many conversations and the reusable analytical context shared across them. Attributes: session_id, workspace_id, user_id, title, status (active/closed/archived), assumptions, pinned_intent, focused_symbols, linked_symbol_ids, timestamps. Represents a named investigation or review cycle.
- **Conversation**: Atomic agent interaction container within a session. Maps 1:1 to an agent checkpoint thread. Attributes: conversation_id, session_id, workspace_id, user_id, thread_id (== conversation_id), status (active/summarized/archived), message_count, total_tokens, summary, context_overrides, conversation_intent, focused_symbols (thread-local refinement per tech design), archived_at, archive_reason, last_activity_at, timestamps. Owns STM state and optional thread-local refinement of inherited session context.
  - **Lifecycle transitions**: active → summarized (triggered when an LLM-generated summary exists for context compaction), active → archived (via explicit action or parent session archive cascade), summarized → archived. No reverse transitions. The "summarized" state indicates an LLM-generated summary exists and can be injected when the conversation resumes. The summarization mechanism itself is out of scope for this feature; only the state contract and inheritance semantics are defined here.
- **Agent Checkpoint Thread**: LangGraph-managed checkpoint state for one conversation. Identified by thread_id. Not directly managed by application services — managed by LangGraph checkpointer.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Two conversations created under the same session maintain fully isolated agent memory — a fact mentioned in one conversation is never recalled in the other.
- **SC-002**: After all planned test updates for the session_id→conversation_id API break are complete, all previously passing behaviors continue to pass (zero behavioral regression).
- **SC-003**: A conversation resumed after inactivity retrieves its prior checkpoint state within the same response time as before the refactor (no performance regression).
- **SC-004**: Session lifecycle transitions (active → closed → archived) correctly cascade constraints to child conversations, verified by attempting disallowed operations after each transition.
- **SC-005**: Stateless chat requests (no conversation_id) continue to produce correct responses, maintaining feature parity with the pre-refactor behavior.
- **SC-006**: ~~Legacy session-based STM data is fully accessible after migration — no orphaned checkpoints, no lost conversation history.~~ **REPLACED per Decision §10.2 (clean-slate migration)**: Clean-slate migration completes without errors; empty collections have correct schema and indexes.
- **SC-007**: Cross-collection identifier types are uniform, verified by schema validation passing on all records without type coercion warnings.
- **SC-008**: Conversation metadata (message_count, last_activity_at) is accurately updated after every chat exchange, verified by inspecting the conversation record after a round-trip message.
- **SC-009**: A new or resumed conversation under a session receives the session's stored assumptions, pinned intent, and focused symbols without requiring the user to restate them.
- **SC-010**: A conversation-specific refinement changes behavior only for that conversation thread; sibling conversations in the same session continue to receive the base session context unchanged.

## Out of Scope

This feature covers **Phase A (Domain and Schema Alignment)** and **Phase B (Service-Layer Refactor)** from the AGENTIC_APP_WITH_STM_INTEGRATION_ROADMAP.md only. The following phases are explicitly out of scope:

- **Phase C (Management API Delivery)**: REST CRUD endpoints for workspaces, sessions, and conversations. No new route blueprints are added in this feature.
- **Phase D (Runtime Consistency and Reconciliation)**: Reconciliation tooling, orphan detection utilities, and data integrity repair scripts beyond the initial migration.
- **Phase E (Test Realignment and Hardening)**: Comprehensive rewriting of old-invariant tests is out of scope. This feature adds tests for new behavior but does not rewrite the full existing test suite.
- **Conversation summarization mechanism**: The "summarized" status is defined as a valid conversation state, but the LLM summarization trigger, scheduling, and summary generation logic are not implemented in this feature.
- **Frontend changes**: No React UI changes are included. Frontend adaptation will follow the API surface defined in Phase C.

## Assumptions

- ~~The migration strategy will promote existing session_id values to conversation_id values (1:1 mapping for legacy data), meaning each legacy session becomes a session with exactly one conversation.~~ **REPLACED per Decision §10.2**: The migration strategy uses clean-slate drop+recreate; no legacy data is preserved.
- The "archived" status for sessions is an addition to the current schema which only defines "open" and "closed" — this is an intentional extension.
- workspace_id standardization to string type is acceptable because the repository layer already handles ObjectId-to-string conversion; this change formalizes that pattern at the schema level.
- Agent checkpoint data stored by LangGraph does not need to be migrated — checkpoint thread_id keys match the conversation_id values produced by the migration.
- ~~The backward compatibility shim (session_id → default conversation resolution) is a transitional mechanism and will be deprecated in a future release.~~ **REPLACED per Decision §10.1**: No backward compatibility shim is provided; callers must provide conversation_id directly.
- Business identifiers (conversation_id, session_id) use UUID v4 format, consistent with the existing conversations schema pattern (`^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$`). Generated via Python's `uuid.uuid4()`. MongoDB `_id` (ObjectId) remains the storage key; business identifiers are explicit string fields for API usage and cross-collection references.

## Clarifications

### Session 2026-03-17

- Q: What is the explicit scope boundary for this feature? → A: Phase A (Domain and Schema Alignment) and Phase B (Service-Layer Refactor) only. Phases C (CRUD APIs), D (Reconciliation), and E (Test Rewriting) are out of scope.
- Q: What are the valid conversation lifecycle state transitions? → A: active → summarized (LLM summary exists for context compaction), active → archived (explicit or cascade), summarized → archived. No reverse transitions. Summarization does not by itself terminate the conversation; it preserves resumable context. The summarization mechanism itself is out of scope.
- Q: When a session is closed, can users still send messages to existing conversations? → A: Yes. Closed sessions block new conversation creation only. Existing active conversations remain fully operational. This distinguishes "closed" (soft growth restriction) from "archived" (full immutability).
- Q: How are business identifiers (conversation_id, session_id) generated? → A: UUID v4 format, matching existing schema convention. MongoDB _id remains ObjectId; business IDs are explicit string fields.
- Q: Is the session "closed" vs "archived" cascade behavior different for child conversations? → A: Yes. Closing a session does not cascade to conversations (they remain active). Archiving a session cascades: all child conversations transition to archived.
- Q: Where does reusable analytical context belong? → A: Session-level assumptions, pinned intent, and focused symbols belong to the session and are inherited by child conversations. Conversation-specific refinements remain thread-local and do not mutate the base session context.

### Session 2026-03-18

- Q: When should inherited session context be loaded for conversation processing — snapshot at conversation creation or live at request time? → A: **Live read at request time**. New and resumed conversations load current session context when processed; behavior is not snapshot-at-creation.
- Q: How are session context and conversation `context_overrides` merged? → A: Use **shallow key overwrite**: start with session context, then apply conversation `context_overrides` keys on top.
- Q: How should `focused_symbols` overrides behave? → A: If `focused_symbols` is present in `context_overrides`, it **replaces** inherited session `focused_symbols` for that conversation thread only (no sibling/session mutation).
