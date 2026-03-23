# Feature Specification: STM Phase C-E — Management API, Runtime Consistency, and Test Realignment

**Feature Branch**: `stm-phase-cde`  
**Created**: 2026-03-20  
**Status**: Clarified  
**Input**: Derived from SRS v2.2 (FR-5.3–5.6, FR-7, NFR-1.4, NFR-2.4–2.5, AC-5–7, IR-1.8–1.13), Phase CDE Requirement Analysis, STM Integration Roadmap (Increments 6–9), and Phase A-B feature spec (`agent-session-with-stm-wiring`)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Workspace CRUD Endpoints (Priority: P1)

A user opens the application and manages their workspaces: creating new workspaces for different investment themes, listing all their workspaces, viewing workspace details with aggregate statistics, updating workspace metadata, and archiving workspaces they no longer need. All operations enforce that the user can only access workspaces they own.

**Why this priority**: Workspaces are the root of the hierarchy. Without workspace management endpoints, there is no entry point for users to organize sessions and conversations through the API. Every other management story depends on workspaces being addressable.

**Independent Test**: Create, list, retrieve, update, and archive workspaces via REST API calls. Verify ownership enforcement by attempting to access another user's workspace.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** the user creates a workspace with a name and description, **Then** the system returns a workspace record with workspace_id, name, description, status "active", and a creation timestamp. *(FR-5.3.2)*
2. **Given** a user with multiple workspaces, **When** the user lists their workspaces, **Then** the system returns all workspaces owned by that user with id, name, description, status, and session count; an empty list is returned if none exist. *(FR-5.3.1)*
3. **Given** a valid workspace_id owned by the user, **When** the user retrieves workspace details, **Then** the response includes workspace metadata plus aggregate session count and active conversation count. *(FR-5.3.3)*
4. **Given** a non-archived workspace, **When** the user updates the name or description, **Then** only the provided fields are changed and the updated workspace is returned. *(FR-5.3.4)*
5. **Given** an active workspace, **When** the user archives it, **Then** the workspace status transitions to "archived", all child sessions and conversations also transition to "archived", and no new sessions or conversations can be created under it. *(FR-5.3.5, FR-5.6.3)*
6. **Given** a workspace owned by a different user, **When** the requesting user attempts any operation on it, **Then** the system returns 403 or 404. *(FR-5.3.6)*

---

### User Story 2 — Session CRUD and Lifecycle Endpoints (Priority: P2)

A user creates analysis sessions within a workspace, seeds them with analytical context (assumptions, pinned intent, focused symbols), reviews and updates that context over time, closes sessions when the investigation is complete, and archives sessions for long-term record keeping. Closing a session allows continued messaging in existing conversations but blocks new conversation creation. Archiving cascades immutability to all child conversations.

**Why this priority**: Sessions are the organizational container between workspace and conversation. Without session endpoints, users cannot group related conversations, manage analytical context, or enforce lifecycle policies on groups of related work. Depends on workspace endpoints (P1) for hierarchy validation.

**Independent Test**: Create sessions under a workspace, transition through lifecycle states (active → closed → archived), verify that lifecycle constraints cascade correctly to child conversations.

**Acceptance Scenarios**:

1. **Given** an active workspace, **When** a user creates a session with a title and optional seed context, **Then** the system returns a session record with session_id, parent workspace_id, status "active", and creation timestamp. *(FR-5.4.1)*
2. **Given** a valid session_id, **When** the user retrieves the session, **Then** the response includes session metadata, status, assumptions, pinned_intent, focused_symbols, and conversation count. *(FR-5.4.2)*
3. **Given** a workspace with multiple sessions, **When** the user lists sessions with an optional status filter, **Then** the system returns a paginated list of sessions with id, title, status, and conversation count. *(FR-5.4.3)*
4. **Given** an active session, **When** the user updates assumptions, pinned_intent, or focused_symbols, **Then** the updated session is returned and changes are available to subsequent conversation context loading. *(FR-5.4.4)*
5. **Given** an active session, **When** the user closes it, **Then** the session status transitions to "closed"; existing conversations remain in their current state; new conversation creation under this session is blocked. *(FR-5.4.5)*
6. **Given** a closed or active session, **When** the user archives it, **Then** the session status transitions to "archived" and all child conversations also transition to "archived"; no new messages are accepted in any child conversation. *(FR-5.4.6, FR-5.6.3)*
7. **Given** an archived session, **When** the user attempts to transition it to active or closed, **Then** the system rejects the request with a clear error message. *(FR-5.4.7)*
8. **Given** a session belonging to another user's workspace, **When** the requesting user attempts any operation, **Then** the system returns 403 or 404. *(FR-5.4.8)*

---

### User Story 3 — Conversation CRUD and Lifecycle Endpoints (Priority: P3)

A user creates conversations within sessions, views conversation details including metadata and message statistics, lists conversations within a session, archives conversations they have completed, and retrieves conversation history summaries. All operations validate the full ownership chain from user through workspace and session to conversation.

**Why this priority**: Conversations are the leaf of the management hierarchy and the unit that connects to agent memory. Without conversation endpoints, users cannot manage individual conversation records, view status, or archive completed work. Depends on session endpoints (P2) for parent validation.

**Independent Test**: Create conversations under a session, retrieve details, list within session, archive, and verify parent chain validation by attempting cross-hierarchy access.

**Acceptance Scenarios**:

1. **Given** an active session, **When** a user creates a conversation with an optional title and optional seed context (context_overrides), **Then** the system returns a conversation record with conversation_id, thread_id (== conversation_id), parent session_id and workspace_id, status "active", and a creation timestamp. The conversation_id can be used for subsequent chat requests. *(FR-5.5.1)*
2. **Given** a valid conversation_id, **When** the user retrieves the conversation, **Then** the response includes conversation metadata, status, message_count, total_tokens, summary (if summarized), focused_symbols, and parent identifiers. *(FR-5.5.2)*
3. **Given** a session with multiple conversations, **When** the user lists conversations with an optional status filter, **Then** the system returns a paginated list of conversations with id, status, message_count, and last_activity_at. *(FR-5.5.3)*
4. **Given** an active or summarized conversation, **When** the user archives it, **Then** the conversation status transitions to "archived", archive_reason is recorded, and no further messages are accepted. *(FR-5.5.4)*
5. **Given** a conversation with at least one message, **When** the user requests a history summary, **Then** the response includes an AI-generated summary (if available), message_count, total_tokens, focused_symbols, and time range. *(FR-5.5.5)*
6. **Given** a conversation outside the user's ownership chain, **When** the user attempts any management operation, **Then** the system returns 403 or 404. *(FR-5.5.6)*

---

### User Story 4 — Cross-Cutting API Behaviors (Priority: P4)

All management API endpoints share consistent behaviors: paginated list results, archive-over-delete semantics (no hard deletion), cascade archive from parent to descendants, consistent JSON error shapes matching the chat API error format, and idempotent GET operations. These cross-cutting behaviors ensure a predictable and coherent API surface.

**Why this priority**: Without consistent cross-cutting behaviors, the management API is fragmented and unpredictable. These behaviors are essential for production readiness but are secondary to the individual CRUD endpoints being functional. Can be applied incrementally as P1–P3 endpoints are built.

**Independent Test**: Verify pagination on list endpoints with large collections, confirm archive actions cascade correctly, validate error response shapes match the chat API format, and confirm GETs are idempotent.

**Acceptance Scenarios**:

1. **Given** a collection with more than 50 resources, **When** a list endpoint is called, **Then** the response includes items array, total count, and pagination cursor or offset metadata. *(FR-5.6.1, AC-5.7)*
2. **Given** any management delete or removal request, **When** the system processes it, **Then** the resource is marked as archived rather than hard-deleted; the record remains queryable for audit purposes. *(FR-5.6.2)*
3. **Given** a parent resource (workspace or session) being archived, **When** the archive action completes, **Then** all descendant resources are also transitioned to archived status atomically per parent operation. *(FR-5.6.3, AC-5.4)*
4. **Given** an error occurs on any management endpoint, **When** the error response is returned, **Then** it includes error.code, error.message, and error.correlation_id matching the chat API error shape (ERR-1.1). *(FR-5.6.4)*
5. **Given** an unchanged resource, **When** the same GET request is issued multiple times, **Then** the response is identical across retries. *(FR-5.6.5)*
6. **Given** management API operations under normal load, **When** response times are measured, **Then** single-resource GETs complete in < 200ms, lists in < 500ms, create/update/archive in < 500ms, and cascade archive in < 2 seconds (P95). *(NFR-1.4.1–NFR-1.4.4, AC-5.5)*

---

### User Story 5 — Runtime Metadata Tracking in Chat Flow (Priority: P5)

When a user sends a chat message within a conversation, the system ensures the conversation metadata record exists, tracks user and assistant turns by updating message_count, total_tokens, and last_activity_at, refreshes focused symbols when the agent detects new stock symbols, and coordinates checkpoint state with conversation metadata as two distinct but synchronized persistence layers. Archived conversations reject new messages.

**Why this priority**: Without runtime metadata tracking, the conversation metadata maintained by the management API drifts from the actual checkpoint state, making management endpoints unreliable. This is critical for operational consistency but depends on the management API surface being in place to consume the metadata.

**Independent Test**: Send chat messages through a conversation and verify that conversation metadata (message_count, total_tokens, last_activity_at, focused_symbols) is updated accurately after each exchange. Attempt to chat in an archived conversation and verify rejection.

**Acceptance Scenarios**:

1. **Given** a chat request with a conversation_id, **When** the conversation record does not yet exist in the metadata store, **Then** the system auto-creates the record with correct parent references before agent invocation. *(FR-7.1.1)*
2. **Given** a non-archived conversation, **When** a user sends a message, **Then** message_count is incremented by 1 and last_activity_at is updated to the current timestamp; the update is visible via conversation GET endpoint within 5 seconds. *(FR-7.1.2, AC-6.1)*
3. **Given** a non-archived conversation, **When** the agent produces a response, **Then** message_count is incremented by 1 and total_tokens is updated with the estimated token count; visible within 5 seconds. *(FR-7.1.3, AC-6.1)*
4. **Given** a conversation where the agent detects a new stock symbol (e.g., "MSFT") during processing, **When** the response completes, **Then** focused_symbols includes "MSFT" without removing previously tracked symbols. *(FR-7.1.4)*
5. **Given** an archived conversation, **When** a user attempts to send a message, **Then** the system rejects the request with a conflict error indicating the conversation is immutable. *(FR-3.2.10, AC-7.1)*
6. **Given** a chat exchange completes with STM enabled, **When** both checkpoint and metadata writes finish, **Then** checkpoint stores agent graph state and conversation record stores searchable application metadata — both updated in the same request cycle. *(FR-7.1.5)*

---

### User Story 6 — Data Reconciliation and Integrity Verification (Priority: P6)

An operator runs reconciliation scans to detect data anomalies: orphan conversations whose parent sessions are missing, orphan sessions whose parent workspaces are missing, and checkpoint-metadata misalignments where checkpoints exist without conversation records or vice versa. Reconciliation produces a machine-readable report of anomalies with suggested remediations. Scans run without blocking production traffic.

**Why this priority**: Reconciliation is essential for operational safety — detecting drift and data corruption before they become user-visible problems. Lower priority than the runtime tracking that prevents anomalies in the first place, but required for production confidence. Depends on management API (Phase C) being complete so that the hierarchy is fully queryable.

**Independent Test**: Inject orphan records and checkpoint-metadata misalignments into test data, run reconciliation scans, and verify the report correctly identifies all anomalies with appropriate suggested remediations.

**Acceptance Scenarios**:

1. **Given** conversations exist whose session_id references a non-existent session, **When** a reconciliation scan runs, **Then** the report lists all orphan conversation_ids with their invalid session references. *(FR-7.2.1, AC-6.2)*
2. **Given** sessions exist whose workspace_id references a non-existent workspace, **When** a reconciliation scan runs, **Then** the report lists all orphan session_ids with their invalid workspace references. *(FR-7.2.2, AC-6.2)*
3. **Given** checkpoint threads exist without corresponding conversation records (or conversation records exist without matching checkpoints when STM should exist), **When** a reconciliation scan runs, **Then** the report lists unmatched thread_ids in both directions. *(FR-7.2.3, AC-6.3)*
4. **Given** a reconciliation scan completes, **When** the report is generated, **Then** it is machine-readable JSON including anomaly type, affected resource identifiers, and suggested remediation for each finding. *(FR-7.2.4)*
5. **Given** reconciliation is running alongside active chat sessions, **When** chat latency is measured during the scan, **Then** latency increase is less than 5%. *(FR-7.2.5, NFR-2.5.1)*
6. **Given** the same data state, **When** reconciliation is run multiple times, **Then** the report is identical (idempotent). *(NFR-2.5.2)*

---

### User Story 7 — Legacy Data Migration Tooling (Priority: P7)

An operator migrates legacy session_id-based checkpoint threads into the new conversation-scoped model. The migration tool supports dry-run mode to preview changes without writing, produces an audit trail of all actions, can be resumed after interruption without re-processing completed records, preserves all historical checkpoint data (zero data loss), and allows the system to serve both legacy and new-model requests during the migration window.

**Why this priority**: Migration ensures backward compatibility with historical data and prevents orphaned checkpoints. It is lower priority because Phase A-B used clean-slate migration for initial schema setup; this addresses the remaining legacy data from production environments. Depends on the conversation model and reconciliation tooling being in place.

**Independent Test**: Seed a database with legacy session_id-based checkpoint threads, run migration in dry-run mode and verify no writes, run actual migration and verify all threads are promoted to conversation records, interrupt and resume migration to verify incremental behavior, and confirm legacy threads remain accessible via new conversation_id mapping.

**Acceptance Scenarios**:

1. **Given** legacy checkpoint threads keyed by session_id, **When** migration runs, **Then** each thread is promoted to a conversation record with conversation_id derived from the legacy thread_id; checkpoint state remains accessible via the new mapping. *(FR-7.3.1, AC-6.4)*
2. **Given** migration is initiated in dry-run mode, **When** the preview completes, **Then** the report shows the number of records to create, update, or skip; no database writes occur. *(FR-7.3.2, AC-6.5)*
3. **Given** migration is executed, **When** the audit trail is inspected, **Then** every action includes timestamp, action type, source identifier, target identifier, outcome, and correlation_id. *(FR-7.3.3, NFR-2.4.4)*
4. **Given** migration is interrupted after processing 50 of 100 records, **When** migration is resumed, **Then** the 50 completed records are skipped; the remaining 50 are processed; the final state is identical to uninterrupted execution. *(FR-7.3.4)*
5. **Given** migration completes, **When** all pre-migration checkpoint threads are queried, **Then** every thread remains accessible via its new conversation_id mapping; zero checkpoints are orphaned or lost. *(FR-7.3.5, NFR-2.4.1)*
6. **Given** migration is in progress, **When** both legacy stateless requests (without `conversation_id`) and new hierarchy-aware requests are sent, **Then** both types process correctly; the system continues to serve normally during the migration window. *(FR-7.3.6, AC-6.6)*

---

### User Story 8 — Test Realignment for Hierarchy, STM, Lifecycle, and Consistency (Priority: P8)

The existing integration test suite is rewritten and expanded to enforce the correct workspace → session → conversation → thread hierarchy invariants. Tests cover four categories: hierarchy validation (ownership and isolation), STM isolation (per-conversation memory boundaries), lifecycle enforcement (archive immutability, session close/archive cascades, cross-boundary rejection), and data consistency (metadata-checkpoint alignment, migration integrity, orphan detection). Legacy tests that assert the old session_id == thread_id model are replaced.

**Why this priority**: Tests are the final quality gate that enforces the architecture. Without them, regressions can reintroduce the old identity model or break hierarchy invariants. P8 because it validates P1–P7 deliverables rather than adding new user-facing functionality. Should begin alongside Phase D to validate each increment.

**Independent Test**: Run the full test suite and verify all hierarchy, STM, lifecycle, and consistency tests pass; verify legacy session_id == thread_id assertions have been removed or replaced; verify operator-only tooling remains outside the public API surface.

**Acceptance Scenarios**:

1. **Given** the test suite runs, **When** hierarchy tests execute, **Then** they verify: one workspace owns multiple sessions, one session owns multiple conversations, and conversation resources are isolated under their session and workspace. *(AC-2.6, FR-3.2.1, FR-3.2.4, FR-3.2.7)*
2. **Given** the test suite runs, **When** STM tests execute, **Then** they verify: same conversation restores same thread context, two conversations in same session do not share memory, resumed conversation retrieves prior checkpoint, and stateless mode works without conversation context. *(AC-2.2, AC-2.5, AC-2.6)*
3. **Given** the test suite runs, **When** lifecycle tests execute, **Then** they verify: archived conversation rejects new messages, closed/archived session constrains new conversation creation, and cross-workspace/cross-session access is rejected. *(AC-7.1–AC-7.5)*
4. **Given** the test suite runs, **When** consistency tests execute, **Then** they verify: metadata and checkpoint are aligned after message flow, migration preserves retrievable STM history, and orphan detection identifies inconsistent records. *(AC-6.1–AC-6.6)*
5. **Given** the full test suite, **When** security and contract tests execute, **Then** they verify that reconciliation and migration tooling require elevated/operator execution paths and are not exposed through public management API endpoints. *(NFR-2.5.4)*

---

### Edge Cases

- **Concurrent archive and message**: A user sends a message to a conversation at the same time the parent session is being archived. The archive operation takes precedence; the message is rejected if the conversation status has transitioned to archived by the time it is processed.
- **Archive already-archived resource**: A repeated archive request MUST leave the resource and all descendants unchanged in archived state; exact duplicate-request response semantics are not fixed by this feature.
- **Update closed session context**: Updating assumptions, pinned_intent, or focused_symbols on a closed session is rejected; FR-5.4.4 still applies only while the session is active.
- **Create conversation in closed session**: The system rejects with a clear error indicating the session is closed and no new conversations are allowed.
- **Create session in archived workspace**: The system rejects with a clear error indicating the workspace is archived.
- **Cascade archive with mixed statuses**: When a workspace with sessions in mixed states (active, closed, archived) is archived, all non-archived sessions and conversations transition to archived; already-archived resources remain unchanged.
- **Pagination with zero results**: List endpoints return an empty items array, total count of 0, and valid pagination metadata.
- **Invalid parent chain on conversation creation**: Creating a conversation with a session_id that belongs to a different user's workspace returns 403 or 404 without revealing the existence of the session.
- **Reconciliation during heavy traffic**: Reconciliation scans MUST satisfy the non-blocking latency requirement without introducing any mandatory query implementation strategy in this spec.
- **Migration of partially migrated data**: Resuming migration after a partial run correctly skips already-migrated records and processes only remaining ones.
- **Metadata update failure during chat**: If metadata update fails after agent invocation, the chat response is still delivered but the metadata drift is flagged for reconciliation.
- **Orphan with ambiguous parent**: If a reconciliation scan finds an orphan that could belong to multiple parents, it is flagged for manual resolution rather than auto-linked.
- **Dry-run with no legacy data**: Migration dry-run on a database with no legacy records returns a report with zero planned changes.
- **Conversation with thread_id mismatch**: If a conversation record has thread_id != conversation_id, reconciliation flags it as an integrity anomaly.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Phase C: Management API Delivery

**FR-C01**: System MUST provide REST endpoints for workspace management: list user workspaces (GET), create workspace (POST), get workspace details (GET), update workspace metadata (PATCH), and archive workspace (POST action). *(SRS: FR-5.3.1–FR-5.3.5)*

**FR-C02**: All workspace operations MUST validate that the requesting user owns the workspace; unauthorized requests MUST return 403 or 404. *(SRS: FR-5.3.6)*

**FR-C03**: System MUST provide REST endpoints for session management: create session under workspace (POST), get session (GET), list sessions in workspace (GET with status filter), update session context (PATCH), close session (POST action), and archive session (POST action). *(SRS: FR-5.4.1–FR-5.4.6)*

**FR-C04**: Session lifecycle transitions MUST follow the order: active → closed → archived. Reverse transitions MUST NOT be allowed. Invalid transitions MUST be rejected with a clear error message. *(SRS: FR-5.4.7)*

**FR-C05**: All session operations MUST validate that the session belongs to a workspace owned by the requesting user. *(SRS: FR-5.4.8)*

**FR-C06**: System MUST provide REST endpoints for conversation management: create conversation under session (POST, accepting optional title and seed context via context_overrides), get conversation (GET), list conversations in session (GET with status filter), archive conversation (POST action), and get conversation history summary (GET). *(SRS: FR-5.5.1–FR-5.5.5)*

**FR-C07**: All conversation management operations MUST validate the full ownership chain (user → workspace → session → conversation); requests outside the user's hierarchy MUST return 403 or 404. *(SRS: FR-5.5.6)*

**FR-C08**: List endpoints MUST support paginated results with response metadata (total count, pagination cursor or offset). Page size defaults, maximum page size, and sort order are intentionally deferred to planning. *(SRS: FR-5.6.1, IR-1.11)*

**FR-C09**: No management endpoint MUST perform hard deletion; all removal operations MUST transition resources to archived status. *(SRS: FR-5.6.2)*

**FR-C10**: Archiving a parent resource MUST cascade archive status to all descendant resources atomically per parent operation. *(SRS: FR-5.6.3)*

**FR-C11**: Management API errors MUST follow the same JSON error shape as chat API errors, including error.code, error.message, and error.correlation_id. *(SRS: FR-5.6.4, ERR-1.1)*

**FR-C12**: GET operations MUST be idempotent and safe. *(SRS: FR-5.6.5)*

**FR-C13**: Workspace endpoints MUST be rooted at `/api/workspaces` with nested session navigation at `/api/workspaces/{workspace_id}/sessions`. *(SRS: IR-1.8)*

**FR-C14**: Session endpoints MUST support both nested access (`/api/workspaces/{workspace_id}/sessions`) and direct access (`/api/sessions/{session_id}`) with parent validation. For nested routes, the `workspace_id` in the path MUST match the session's stored parent workspace_id; mismatches MUST be rejected rather than silently normalized. *(SRS: IR-1.9)*

**FR-C15**: Conversation endpoints MUST support both nested access (`/api/sessions/{session_id}/conversations`) and direct access (`/api/conversations/{conversation_id}`) with hierarchy validation. For nested routes, the `session_id` in the path MUST match the conversation's stored parent session_id; mismatches MUST be rejected rather than silently normalized. *(SRS: IR-1.10)*

**FR-C16**: Archive action endpoints MUST use POST method (e.g., `POST /api/conversations/{id}/archive`) rather than DELETE. *(SRS: IR-1.12)*

**FR-C17**: Management API responses MUST include workspace_id, session_id, and conversation_id in resource payloads to support client-side hierarchy navigation. *(SRS: IR-1.13)*

#### Phase D: Runtime Consistency and Reconciliation

**FR-D01**: System MUST ensure a conversation metadata record exists before the agent processes a chat message. If the record is missing, it MUST be auto-created with correct parent references. *(SRS: FR-7.1.1)*

**FR-D02**: Each user message accepted for a non-archived conversation MUST increment the conversation's message_count by 1 and update last_activity_at; changes MUST be visible via the conversation GET endpoint within 5 seconds. *(SRS: FR-7.1.2, NFR-2.3.2)*

**FR-D03**: Each assistant response produced for a non-archived conversation MUST increment the conversation's message_count by 1 and update total_tokens with the estimated token count; changes MUST be visible within 5 seconds. *(SRS: FR-7.1.3, NFR-2.3.2)*

**FR-D04**: When the agent detects new stock symbols during processing, the conversation-level focused_symbols MUST be updated to include newly detected symbols without removing previously tracked ones. *(SRS: FR-7.1.4)*

**FR-D05**: Checkpoint state and conversation metadata MUST be treated as coordinated but distinct persistence layers, both updated in the same request cycle. *(SRS: FR-7.1.5)*

**FR-D06**: System MUST detect orphan conversations (missing parent sessions) and orphan sessions (missing parent workspaces) through reconciliation scans. *(SRS: FR-7.2.1, FR-7.2.2)*

**FR-D07**: System MUST detect checkpoint-metadata misalignment: checkpoints without conversation records and conversation records without corresponding checkpoints when STM should exist. *(SRS: FR-7.2.3)*

**FR-D08**: Reconciliation MUST produce a machine-readable JSON report including anomaly type, affected resource identifiers, and suggested remediation. *(SRS: FR-7.2.4)*

**FR-D08a**: Reconciliation scan execution MUST be logged with correlation_id and timestamps for each scan action (start, anomaly detection, completion), per NFR-2.4.4. This is distinct from the reconciliation report output (FR-D08). *(SRS: NFR-2.4.4)*

**FR-D09**: Reconciliation scans MUST execute without blocking production traffic; chat latency increase MUST be < 5% during scans. *(SRS: FR-7.2.5, NFR-2.5.1)*

**FR-D10**: System MUST convert legacy session_id-based checkpoint threads into conversation records with correctly assigned conversation_id and preserved checkpoint accessibility. *(SRS: FR-7.3.1)*

**FR-D11**: Migration MUST support dry-run mode that reports planned changes without database writes. *(SRS: FR-7.3.2)*

**FR-D12**: All migration actions MUST be recorded in an audit log with timestamp, action type, source identifier, target identifier, outcome, and correlation_id. *(SRS: FR-7.3.3, NFR-2.4.4)*

**FR-D13**: Migration MUST support incremental/resumable execution: if interrupted, it MUST continue from the last successful point without re-processing completed records. *(SRS: FR-7.3.4)*

**FR-D14**: Migration MUST NOT discard, overwrite, or orphan any existing checkpoint data (zero data loss). *(SRS: FR-7.3.5, NFR-2.4.1)*

**FR-D15**: System MUST continue to serve both legacy stateless requests (without `conversation_id`) and new hierarchy-aware requests during the migration window. This does not reintroduce the deprecated `session_id == thread_id` caller model. *(SRS: FR-7.3.6)*

#### Phase E: Test Realignment and Hardening

**FR-E01**: Test suite MUST verify hierarchy invariants: one workspace owns many sessions, one session owns many conversations, and conversation resources are isolated under their session and workspace. *(SRS: AC-2.6, AC-5.1, AC-5.2, AC-5.3)*

**FR-E02**: Test suite MUST verify STM isolation: same conversation restores the same thread context, two conversations in the same session do not share memory, a resumed conversation retrieves its prior checkpoint, and stateless mode works without conversation context. *(SRS: AC-2.2, AC-2.5, AC-2.6)*

**FR-E03**: Test suite MUST verify lifecycle enforcement: archived conversations reject new messages, closed or archived sessions constrain new conversation creation according to policy, and cross-workspace and cross-session access is rejected. *(SRS: AC-7.1, AC-7.2, AC-7.3, AC-7.4, AC-7.5)*

**FR-E04**: Test suite MUST verify data consistency: metadata and checkpoint state remain aligned after message flow, migration preserves retrievable STM history, and orphan detection identifies inconsistent records. *(SRS: AC-6.1, AC-6.2, AC-6.3, AC-6.4, AC-6.5, AC-6.6)*

**FR-E05**: Legacy tests asserting `session_id == thread_id` MUST be replaced with tests asserting `conversation_id == thread_id`. *(SRS: FR-3.1.3, FR-3.2.2, FR-3.2.3)*

**FR-E06**: Test suite MUST verify that reconciliation and migration tooling require elevated/operator execution paths and are not exposed through public management API endpoints. *(SRS: NFR-2.5.4)*

---

### Key Entities

- **Workspace**: Root business container. Attributes: workspace_id (string, unique), user_id (string), name, description, status (active/archived), created_at, updated_at. Owns many sessions. Serves as ownership and isolation boundary for all descendants.

- **Session**: Business workflow container within a workspace. Attributes: session_id (string, unique), workspace_id (FK), user_id (string), title, status (active/closed/archived), assumptions, pinned_intent, focused_symbols, linked_symbol_ids, created_at, updated_at. Owns many conversations and holds reusable analytical context inherited by child conversations. Lifecycle: active → closed (blocks new conversations, existing messaging continues) → archived (cascades immutability to all children).

- **Conversation**: Atomic agent interaction container within a session. Maps 1:1 to an agent checkpoint thread. Attributes: conversation_id (string, unique), session_id (FK), workspace_id (FK), user_id (string), thread_id (== conversation_id), status (active/summarized/archived), message_count, total_tokens, summary, context_overrides, conversation_intent, focused_symbols, archived_at, archive_reason, last_activity_at, created_at, updated_at. Owns STM state and optional thread-local refinement of inherited session context. `summarized` remains resumable and management-visible; only `archived` is immutable.

- **Reconciliation Report**: Output artifact from integrity scans. Attributes: report_id, timestamp, anomalies array (each with type, affected_ids, suggested_remediation), scan_duration, total_scanned. Reporting is detection-only for this feature and does not itself mutate data.

- **Migration Audit Entry**: Log record for migration actions. Attributes: timestamp, action_type (create/skip/error), source_id, target_id, outcome, correlation_id.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

**SC-001**: All workspace CRUD operations (create, list, get, update, archive) are accessible via REST API and return correct responses matching the SRS interface contracts (IR-1.8, IR-1.13).

**SC-002**: All session CRUD and lifecycle operations (create, list, get, update context, close, archive) enforce parent-workspace validation and lifecycle transition rules (active → closed → archived only).

**SC-003**: All conversation CRUD and lifecycle operations (create, list, get, archive, history summary) enforce full ownership chain validation (user → workspace → session → conversation).

**SC-004**: Cascade archive from workspace propagates to all child sessions and conversations; from session propagates to all child conversations. Zero descendant resources remain in non-archived state after parent archive.

**SC-005**: Management API response times meet NFR-1.4 targets: single-resource GET < 200ms, list < 500ms, create/update/archive < 500ms, cascade archive < 2 seconds (P95).

**SC-006**: After each chat exchange, conversation metadata (message_count, total_tokens, last_activity_at) accurately reflects the exchange within 5 seconds.

**SC-007**: Reconciliation scan correctly identifies orphan conversations, orphan sessions, and checkpoint-metadata misalignments in a seeded test database with known anomalies, producing a complete JSON report.

**SC-008**: Reconciliation scans complete without degrading production chat latency by more than 5%.

**SC-009**: Legacy thread migration converts all session_id-based checkpoints to conversation records with zero data loss — every pre-migration checkpoint remains accessible via its new conversation_id mapping.

**SC-010**: Migration dry-run accurately reports planned changes without writing to the database.

**SC-011**: Migration is resumable: after interruption, restarted migration skips completed records and produces a final state identical to uninterrupted execution.

**SC-012**: During migration, both legacy stateless requests (without `conversation_id`) and new hierarchy-aware requests process successfully.

**SC-013**: All hierarchy, STM, lifecycle, and consistency tests pass in the rewritten test suite; legacy `session_id == thread_id` assertions are fully replaced by `conversation_id == thread_id` assertions.

**SC-014**: Reconciliation and migration tooling are executable only through elevated/operator paths and are not reachable through public management API endpoints.

**SC-015**: Archived conversations reject new chat messages; archived sessions reject new conversation creation; all immutability constraints are enforced.

---

## Out of Scope

- **Frontend changes**: No React UI updates are included. Frontend adaptation will follow the API surface defined in this feature.
- **Conversation summarization mechanism**: The "summarized" conversation state is honored by lifecycle rules, but the LLM summarization trigger, scheduling, and summary generation logic are not implemented in this feature.
- **Auto-healing reconciliation**: Reconciliation detects and reports anomalies only. Repair execution, including auto-heal mode or operator-invoked mutation of hierarchy/checkpoint data, is out of scope; the report may only suggest remediation.
- **Rate limiting**: Management API rate limiting is not included; assumed to be handled by infrastructure.
- **WebSocket management events**: Real-time notification of management actions via WebSocket is out of scope.
- **Multi-user workspace sharing**: Workspaces are single-owner; workspace sharing or team access is not included.
- **API versioning**: No `/api/v2/` prefix is introduced; endpoints are added to the existing `/api/` namespace.

---

## Assumptions

- Phase A-B deliverables are complete and stable: domain model (workspace → session → conversation → thread), normalized identifiers, schema consistency, SessionService, ConversationService, ChatService (conversation-aware), and agent runtime (conversation_id → thread_id mapping) are all in place.
- Phase B provides the primary service and repository foundation for Phase C, but this feature may still require route-layer contracts and minimal supporting service or validation updates to satisfy FR-5.3 through FR-5.6 exactly.
- The dependency chain is: Phase C can start immediately; Phase D metadata tracking can begin in parallel with Phase C (depends on chat flow, not management API); Phase D reconciliation should follow Phase C completion; Phase E should begin alongside Phase D to validate each increment.
- Archive-over-delete semantics apply universally: no hard deletion for any hierarchical resource.
- Session lifecycle: active → closed → archived. Conversation lifecycle: active → summarized → archived. Only forward transitions are permitted.
- Business identifiers (workspace_id, session_id, conversation_id) use UUID v4 format, consistent with Phase A-B schema conventions.
- Clean-slate migration was used for Phase A-B initial schema setup. Phase D migration tooling addresses legacy production data that predates the Phase A-B schema changes.
- Reconciliation and migration tools require elevated permissions and are not exposed via public API endpoints (NFR-2.5.4).
- Open issue OI-6 (migration window/rollback strategy) will be resolved during Phase D planning.
- Open issue OI-7 (reconciliation schedule/alerting thresholds) will be resolved during Phase D planning.
- Open issue OI-8 (pagination defaults — page size, max page size, sort order) will be resolved during Phase C planning.
- NFR-6.1.3 (agent core test coverage ≥ 80%) is a standing quality gate mapped to this feature. Phase E test realignment MUST NOT regress agent core test coverage below the existing baseline. This is a soft constraint — Phase E does not own the 80% target but must preserve it.

---

## References

| Document | Path | Relevance |
|----------|------|-----------|
| SRS v2.2 | `docs/langchain-agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md` | Authoritative requirements: FR-5.3–5.6, FR-7, NFR-1.4, NFR-2.4–2.5, AC-5–7, IR-1.8–1.13, OI-6–8 |
| Phase CDE Requirement Analysis | `docs/langchain-agent/PHASE_CDE_REQUIREMENT_ANALYSIS.md` | Gap analysis, baseline assessment, SRS update plan |
| STM Integration Roadmap | `docs/High-level Design/AGENTIC_APP_WITH_STM_INTEGRATION_ROADMAP.md` | Increments 6–9 (management API, metadata tracking, reconciliation, test strategy) |
| Phase A-B Feature Spec | `specs/agent-session-with-stm-wiring/spec.md` | Companion feature — delivered foundation this spec builds upon |
| Agent Memory Technical Design | `docs/langchain-agent/AGENT_MEMORY_TECHNICAL_DESIGN.md` | Checkpoint and STM persistence design |
| SRS Spec Traceability | `docs/langchain-agent/SRS_SPEC_TRACEABILITY.md` | Bidirectional trace between SRS items and spec artifacts |

---

## Clarifications

### Session 2026-03-20

- Q: Which request-contract details are fixed now versus deferred to planning? → A: Phase C fixes pagination capability, pagination metadata, and status filtering for list endpoints, plus GET idempotency. Default page size, maximum page size, sort order, and duplicate POST response semantics remain planning decisions; implementations MUST NOT assume built-in deduplication for create or archive requests.
- Q: How are closed and archived sessions different in practice? → A: `closed` is a growth restriction only: session reads remain allowed, existing non-archived conversations may still exchange messages, but new conversation creation and session-context mutation are rejected. `archived` is terminal for the session subtree: the session cannot be mutated, all child conversations are archived, and no further messages are accepted.
- Q: How should the `summarized` conversation state be treated by management and runtime flows? → A: `summarized` is still a valid non-archived conversation state. Management endpoints return it as-is, and runtime/chat flows may resume it; only `archived` makes a conversation immutable.
- Q: What traffic compatibility is required during legacy migration? → A: Mixed traffic means legacy stateless chat requests without `conversation_id` continue to work while conversation-scoped requests succeed for migrated and not-yet-migrated records. It does not restore the deprecated `session_id == thread_id` caller behavior.
- Q: What is the reconciliation boundary for this feature? → A: Reconciliation in Phase D is scan-and-report only. It identifies anomalies and suggests remediation, but it does not mutate workspace/session/conversation records or checkpoint data as part of the scan.

### Session 2026-03-20 (SRS v2.2 cross-check)

- Q: Does FR-C06 / User Story 3 account for seed context per FR-5.5.1? → A: No — added "optional seed context (context_overrides)" to FR-C06 and User Story 3 scenario 1 to match SRS FR-5.5.1.
- Q: Does FR-D12 / User Story 7 include correlation_id per NFR-2.4.4? → A: No — added correlation_id to FR-D12 audit log attributes and User Story 7 scenario 3 to satisfy NFR-2.4.4.
- Q: Is reconciliation action logging (distinct from report output) required per NFR-2.4.4? → A: Yes — added FR-D08a requiring reconciliation scan execution logging with correlation_id and timestamps, separate from the report (FR-D08).
- Q: How should NFR-6.1.3 (agent core ≥ 80% coverage) be reflected? → A: Added as a standing quality gate soft constraint in Assumptions. Phase E must not regress the existing agent core coverage baseline; the 80% target itself is a project-wide gate, not a Phase E deliverable.
- Q: Are FR-3.1.3, FR-3.2.2, FR-3.2.3, FR-3.2.7, FR-3.2.8 missing from the traceability YAML? → A: Yes — these SRS items are explicitly referenced by Phase E requirements (FR-E01, FR-E03, FR-E05) in the spec body but absent from `mapped_srs_items` in `specs/spec-traceability.yaml`. Noted for separate YAML fix.
