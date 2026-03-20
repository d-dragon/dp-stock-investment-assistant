# Phase C–E Requirement Analysis Report

> **Document Type**: Requirement Analysis  
> **Date**: March 19, 2026  
> **Scope**: Phases C (Management API Delivery), D (Runtime Consistency and Reconciliation), E (Test Realignment and Hardening)  
> **Governing Roadmap**: [AGENTIC_APP_WITH_STM_INTEGRATION_ROADMAP.md](../High-level%20Design/AGENTIC_APP_WITH_STM_INTEGRATION_ROADMAP.md)  
> **Target SRS**: [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md)

---

## 1. Purpose

This report analyzes functional and non-functional requirements derived from Phases C, D, and E of the STM Integration Roadmap, cross-referenced with [AGENT_MEMORY_TECHNICAL_DESIGN.md](./AGENT_MEMORY_TECHNICAL_DESIGN.md) and [LANGCHAIN_AGENT_ARCHITECTURE_AND_DESIGN.md](./LANGCHAIN_AGENT_ARCHITECTURE_AND_DESIGN.md). It identifies gaps in the current SRS (v2.1) and proposes specific additions and revisions.

---

## 2. Baseline Assessment

### 2.1 What Phase A and B Delivered

Phases A (Domain and Schema Alignment) and B (Service-Layer Refactor) completed the following:

| Deliverable | Status | Evidence |
|-------------|--------|----------|
| Target domain model frozen (workspace → session → conversation → thread) | ✅ Done | SRS v2.1 glossary, AGENT_MEMORY_TECHNICAL_DESIGN v1.3 |
| Normalized identifiers (conversation_id, session_id, workspace_id, thread_id) | ✅ Done | conversations_schema.py, sessions_schema.py |
| Schema consistency (type-aligned FKs, unique constraints on conversation_id/thread_id) | ✅ Done | Schema files with UUID v4 patterns and proper indexes |
| SessionService introduced | ✅ Done | src/services/session_service.py with full lifecycle |
| ConversationService refactored for session-parented conversations | ✅ Done | src/services/conversation_service.py |
| ChatService made conversation-aware | ✅ Done | src/services/chat_service.py with validation and context loading |
| Agent runtime uses conversation_id → thread_id mapping | ✅ Done | stock_assistant_agent.py process_query_streaming |

### 2.2 What Remains Undelivered

| Gap | Roadmap Phase | Impact |
|-----|---------------|--------|
| No REST management endpoints for workspace, session, or conversation | Phase C | Frontend cannot manage hierarchy; only chat endpoint exists |
| Conversation metadata not tracked during real chat flow | Phase D | Metadata (message_count, total_tokens) can drift from checkpointer state |
| No integrity checks or reconciliation tooling | Phase D | Orphan conversations, checkpoint-metadata misalignment not detectable |
| No migration tooling for legacy session-scoped data | Phase D | Historical data may be inconsistent with new model |
| Integration tests still partially assert old session_id == thread_id model | Phase E | Tests may block correct implementation or mask regressions |
| No tests for management API workflows | Phase E | New API surface has zero coverage |

---

## 3. Phase C: Management API Delivery — Requirement Analysis

### 3.1 Functional Requirements

Phase C introduces REST management endpoints for the workspace-session-conversation hierarchy. The service and repository layers already exist; only the HTTP surface is missing.

#### 3.1.1 Workspace Management API

| Requirement | Description | Priority | SRS Status |
|-------------|-------------|----------|------------|
| List workspaces for authenticated user | GET endpoint returning user's workspaces | P1 | **Not in SRS** — FR-5.1.7 mentions "management endpoints" but has no specifics |
| Create workspace | POST endpoint with name, description | P1 | Not in SRS |
| Get workspace details | GET by workspace_id with aggregate stats | P1 | Not in SRS |
| Update workspace metadata | PATCH for name, description | P2 | Not in SRS |
| Archive or deactivate workspace | POST archive action with cascade policy | P2 | Not in SRS |

#### 3.1.2 Session Management API

| Requirement | Description | Priority | SRS Status |
|-------------|-------------|----------|------------|
| Create session under workspace | POST with workspace_id, title, optional seed context | P0 | Not in SRS |
| Get session by session_id | GET returning session with context fields | P0 | Not in SRS |
| List sessions in workspace | GET with filtering by status | P0 | Not in SRS |
| Update session context | PATCH for assumptions, pinned_intent, focused_symbols | P1 | Not in SRS |
| Close session | POST action transitioning status to closed | P1 | Not in SRS |
| Archive session | POST action transitioning status to archived with cascade to conversations | P1 | Not in SRS |

#### 3.1.3 Conversation Management API

| Requirement | Description | Priority | SRS Status |
|-------------|-------------|----------|------------|
| Create conversation under session | POST with session_id, optional title | P0 | Not in SRS |
| Get conversation by conversation_id | GET returning metadata, stats, status | P0 | Not in SRS |
| List conversations in session | GET with filtering by status | P0 | Not in SRS |
| Archive conversation | POST action transitioning to archived | P1 | Not in SRS |
| Get conversation history summary | GET returning summary and message stats | P2 | Not in SRS |

#### 3.1.4 Cross-Cutting API Requirements

| Requirement | Description | Priority | SRS Status |
|-------------|-------------|----------|------------|
| Hierarchical navigation | Nested resource patterns (workspace → sessions → conversations) | P1 | FR-5.1.7 partially covers |
| Parent boundary validation | Every management request validates parent ownership chain | P0 | FR-5.1.8 covers the principle |
| Consistent error responses | Management APIs use same error shape as chat APIs | P0 | ERR-1 covers |
| Archive semantics over delete | No hard delete for any entity; archive with audit | P0 | FR-3.2.9 covers conversations; workspace/session need equivalent |
| Lifecycle transition rules | Enforce valid state transitions (active→closed→archived) | P1 | FR-3.2.8 covers conversations; session/workspace need equivalent |

### 3.2 Non-Functional Requirements

| Category | Requirement | Priority | SRS Status |
|----------|-------------|----------|------------|
| **Performance** | Management API response time < 500ms for list operations, < 200ms for single-resource GET | P1 | **Not in SRS** — NFR-1 only covers agent query latency |
| **Authorization** | Management APIs enforce user ownership at every hierarchy level | P0 | NFR-4.1.3 partially covers |
| **Pagination** | List endpoints support cursor-based or offset pagination | P1 | Not in SRS |
| **Idempotency** | Create operations return existing resource if duplicate detected | P2 | Not in SRS |
| **Observability** | Management API calls logged with correlation ID | P1 | NFR-5.1.1 covers queries but not management actions explicitly |

### 3.3 Impact on Current SRS

- **FR-5 (API Integration)**: Needs a new sub-section FR-5.3 for Management API with specific endpoint requirements.
- **IR-1 (REST API Contract)**: Needs expanded interface requirements for management payloads.
- **NFR-1 (Performance)**: Needs management API latency targets.
- **AC (Acceptance Criteria)**: Needs new AC-5 section for management API verification.

---

## 4. Phase D: Runtime Consistency and Reconciliation — Requirement Analysis

### 4.1 Functional Requirements

Phase D addresses the gap between the checkpointer (live STM truth) and conversation metadata (application-managed sidecar). It also introduces integrity verification and migration tooling.

#### 4.1.1 Conversation Metadata Tracking in Chat Flow

| Requirement | Description | Priority | SRS Status |
|-------------|-------------|----------|------------|
| Track user turns in metadata | On each user message, update message_count and last_activity_at | P0 | FR-3.2.6 states the principle but does not require runtime wiring |
| Track assistant turns in metadata | On each assistant response, update message_count and total_tokens | P0 | FR-3.2.6 states the principle |
| Ensure conversation exists before chat | Auto-create or validate conversation record before agent invocation | P0 | **Partially covered** — ChatService validates but wiring incomplete |
| Refresh focused symbols | Update conversation-level focused_symbols when agent detects new securities | P1 | Not in SRS |
| Enforce archive immutability in chat flow | Reject chat messages targeting archived conversations | P0 | FR-3.2.10 covers |

#### 4.1.2 Data Integrity and Reconciliation

| Requirement | Description | Priority | SRS Status |
|-------------|-------------|----------|------------|
| Detect orphan conversations | Identify conversations missing parent sessions | P1 | **Not in SRS** |
| Detect orphan sessions | Identify sessions missing parent workspaces | P1 | Not in SRS |
| Detect checkpoint-metadata misalignment | Identify checkpoints without conversation records and vice versa | P1 | Not in SRS |
| Reconciliation report generation | Produce machine-readable report of data anomalies | P1 | Not in SRS |
| Self-healing for recoverable anomalies | Automatically link orphaned records where mapping is unambiguous | P2 | Not in SRS |

#### 4.1.3 Data Migration

| Requirement | Description | Priority | SRS Status |
|-------------|-------------|----------|------------|
| Promote legacy session_id-based threads | Convert historical session_id thread keys into conversation records | P1 | Not in SRS |
| Migration dry-run capability | Preview migration impact without writing changes | P1 | Not in SRS |
| Migration audit trail | Record all migration actions for traceability | P1 | Not in SRS |
| Backward-compatible operation during migration | System continues to serve both legacy and new-model requests | P0 | FR-5.1.5 covers stateless fallback but not migration compatibility |

### 4.2 Non-Functional Requirements

| Category | Requirement | Priority | SRS Status |
|----------|-------------|----------|------------|
| **Data Integrity** | Metadata and checkpoint state eventually consistent within 5s | P0 | NFR-2.3.2 covers |
| **Data Integrity** | No data loss during migration (zero checkpoint orphaning) | P0 | **Not in SRS** |
| **Data Integrity** | Reconciliation runs without blocking production traffic | P1 | Not in SRS |
| **Observability** | Reconciliation and migration actions logged with correlation ID | P1 | Not in SRS |
| **Reliability** | Migration supports incremental execution (resumable after failure) | P1 | Not in SRS |
| **Security** | Migration and reconciliation tools require elevated permission | P1 | Not in SRS |

### 4.3 Impact on Current SRS

- **FR-3 (Conversation Memory)**: Needs strengthened language in FR-3.2.6 to require runtime metadata tracking, not just metadata existence.
- **New FR-7 or FR-3.6**: Needs new requirements for data integrity, reconciliation, and migration.
- **NFR-2 (Reliability)**: Needs data migration reliability requirements.
- **NFR-5 (Observability)**: Needs migration/reconciliation logging requirements.
- **AC (Acceptance Criteria)**: Needs new AC-6 section for consistency verification.

---

## 5. Phase E: Test Realignment and Hardening — Requirement Analysis

### 5.1 Functional Requirements (Test Scenarios as Requirements)

Phase E does not introduce new system behavior but formalizes the required test scenarios as acceptance criteria to enforce the correct architecture.

#### 5.1.1 Hierarchy Tests

| Test Scenario | Validates | Priority | SRS Coverage |
|---------------|-----------|----------|--------------|
| One workspace owns multiple sessions | FR-3.2.1 hierarchy | P0 | AC-2.6 partially |
| One session owns multiple conversations | FR-3.2.4 | P0 | AC-2.6 partially |
| Conversation resources isolated under session and workspace | FR-3.2.7 | P0 | AC-4.2 partially |

#### 5.1.2 STM Tests

| Test Scenario | Validates | Priority | SRS Coverage |
|---------------|-----------|----------|--------------|
| Same conversation restores same thread context | FR-3.1.2, FR-3.2.3 | P0 | AC-2.2 covers |
| Two conversations in same session do not share memory | FR-3.2.3, FR-3.2.4 | P0 | AC-2.6 covers |
| Resumed conversation retrieves prior checkpoint | FR-3.1.5 | P0 | AC-2.2 covers |
| Stateless mode works without conversation context | FR-3.1.6 | P0 | AC-2.5 covers |

#### 5.1.3 Lifecycle Tests

| Test Scenario | Validates | Priority | SRS Coverage |
|---------------|-----------|----------|--------------|
| Archived conversation rejects new messages | FR-3.2.10 | P0 | **Not explicitly in AC** |
| Closed/archived session constrains new conversation creation | Session lifecycle | P1 | **Not in AC** |
| Cross-workspace and cross-session access rejected | FR-3.2.7, FR-3.4.6 | P0 | AC-4.2 partially |

#### 5.1.4 Consistency Tests

| Test Scenario | Validates | Priority | SRS Coverage |
|---------------|-----------|----------|--------------|
| Metadata and checkpoint aligned after message flow | FR-3.2.6, NFR-2.3.2 | P0 | **Not in AC** |
| Migration preserves retrievable STM history | Migration integrity | P1 | **Not in AC** |
| Orphan detection identifies inconsistent records | Reconciliation | P1 | **Not in AC** |

### 5.2 Non-Functional Requirements

| Category | Requirement | Priority | SRS Status |
|----------|-------------|----------|------------|
| **Maintainability** | Integration test suite covers all hierarchy invariants | P0 | NFR-6.1.3 sets 80% coverage target |
| **Maintainability** | Management API endpoints have ≥ 80% test coverage | P1 | Not specifically stated |
| **Maintainability** | Backward compatibility tests prevent regression on stateless mode | P0 | Not specifically stated |

### 5.3 Impact on Current SRS

- **AC section**: Needs significant expansion with AC-5 (Management API), AC-6 (Consistency), AC-7 (Lifecycle).
- **Traceability Matrix**: Needs update to map new ACs to new FRs.

---

## 6. Gap Summary and SRS Update Plan

### 6.1 New Functional Requirements Needed

| Proposed ID | Title | Source Phase | Description |
|-------------|-------|-------------|-------------|
| **FR-5.3** | Management API — Workspace | Phase C | CRUD endpoints for workspace resources |
| **FR-5.4** | Management API — Session | Phase C | CRUD and lifecycle endpoints for session resources |
| **FR-5.5** | Management API — Conversation | Phase C | CRUD and lifecycle endpoints for conversation resources |
| **FR-7** | Data Integrity and Operational Tooling | Phase D | Reconciliation, migration, and runtime metadata synchronization |

### 6.2 Existing FR Amendments Needed

| FR ID | Change | Reason |
|-------|--------|--------|
| FR-3.2.6 | Strengthen to require runtime metadata synchronization during chat flow | Phase D makes metadata tracking operational, not just structural |
| FR-5.1.7 | Replace generic "management endpoints" with reference to new FR-5.3–5.5 | Phase C delivers specific endpoints |

### 6.3 New Non-Functional Requirements Needed

| Proposed ID | Title | Description |
|-------------|-------|-------------|
| NFR-1.4 | Management API Latency | Response time targets for CRUD operations |
| NFR-2.4 | Data Migration Reliability | Zero data loss, resumable, dry-run capable |
| NFR-2.5 | Reconciliation Safety | Non-blocking, auditable, idempotent |

### 6.4 New Acceptance Criteria Needed

| Proposed ID | Title | Key Scenarios |
|-------------|-------|---------------|
| AC-5 | Management API Functionality | CRUD for workspace, session, conversation; lifecycle transitions |
| AC-6 | Data Consistency | Metadata-checkpoint alignment; orphan detection; migration integrity |
| AC-7 | Lifecycle Enforcement | Archive immutability; cascade on session close; cross-boundary rejection |

### 6.5 Other SRS Section Updates

| Section | Change |
|---------|--------|
| **Definitions (1.3)** | Add Management API, Reconciliation, Migration, Cascade Archive terms |
| **Open Issues (10)** | Resolve OI-5 (CRUD policy) since Phase C defines it; add new OI for migration window and reconciliation schedule |
| **Traceability Matrix (6)** | Expand to cover AC-5 through AC-7 |
| **Interface Requirements (7)** | Add IR-1.8 through IR-1.12 for management API contract specifics |
| **Revision History (11)** | Add v2.2 entry |

---

## 7. Requirement Dependencies

```
Phase A (Done) ──► Phase B (Done) ──► Phase C ──► Phase D ──► Phase E
                                        │            │            │
                                        │            │            ▼
                                        │            │     Test Realignment
                                        │            │     (validates C+D)
                                        │            ▼
                                        │     Runtime Consistency
                                        │     (requires C endpoints)
                                        ▼
                                  Management APIs
                                  (requires A+B services)
```

Phase C is executable immediately — service and repository layers from Phase B are ready. Phase D can begin in parallel for metadata tracking (which only depends on chat flow, not management APIs), but reconciliation tooling should follow Phase C completion. Phase E should begin alongside Phase D to validate each increment.

---

## 8. Conclusion

The current SRS (v2.1) correctly models the conversation-scoped STM domain but underspecifies the management API surface, runtime consistency guarantees, and operational tooling requirements that Phases C–E demand. The proposed SRS updates add **4 new FR sub-sections**, **3 new NFR entries**, **3 new acceptance criteria groups**, and corresponding interface and traceability updates — all derived directly from the roadmap increments and validated against the current codebase state.

---

*End of Analysis Report*
