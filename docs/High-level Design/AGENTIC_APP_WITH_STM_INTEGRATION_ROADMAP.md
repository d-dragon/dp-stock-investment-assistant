# Agentic Application With STM Integration Roadmap

> Document Type: Research Report and Technical Roadmap  
> Status: Draft for Architecture Review  
> Date: 2026-03-17  
> Scope: Workspace, Session, Conversation, and STM integration model for the LangChain-based agentic application  
> Repository: dp-stock-investment-assistant

## 1. Purpose

This document consolidates the current development status of the agentic application's Short-Term Memory integration and defines a technical roadmap for evolving the system toward a consistent domain model where:

- one workspace contains multiple sessions,
- one session contains multiple conversations,
- one conversation maps 1:1 to the agent checkpointer thread,
- MongoDB persists workspace, session, conversation, and checkpoint data consistently,
- REST APIs provide management workflows and CRUD-style interfaces across the hierarchy.

This report is intended to serve as a technical reference for architecture review, implementation planning, and subsequent API and schema changes.

## 2. Research Scope and Inputs

The findings in this report were derived from the following categories of artifacts already present in the repository.

### 2.1 Reviewed Architecture and Requirements Documents

- `docs/langchain-agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md`
- `docs/langchain-agent/AGENT_MEMORY_TECHNICAL_DESIGN.md`
- `docs/domains/agent/decisions/AGENT_ARCHITECTURE_DECISION_RECORDS.md`
- `docs/langchain-agent/LANGCHAIN_AGENT_ARCHITECTURE_AND_DESIGN.md`
- `docs/langchain-agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md`
- `specs/spec-driven-development-pilot/data-model.md`

### 2.2 Reviewed Runtime and Persistence Artifacts

- `src/core/stock_assistant_agent.py`
- `src/core/langgraph_bootstrap.py`
- `src/web/api_server.py`
- `src/web/routes/ai_chat_routes.py`
- `src/web/sockets/chat_events.py`
- `src/services/chat_service.py`
- `src/services/conversation_service.py`
- `src/services/workspace_service.py`
- `src/services/factory.py`
- `src/data/repositories/workspace_repository.py`
- `src/data/repositories/session_repository.py`
- `src/data/repositories/conversation_repository.py`
- `src/data/schema/workspaces_schema.py`
- `src/data/schema/sessions_schema.py`
- `src/data/schema/conversations_schema.py`
- `src/data/schema/agent_checkpoints_schema.py`
- `src/data/schema/schema_manager.py`

### 2.3 Reviewed Test Artifacts

- `tests/integration/test_stm_runtime_wiring.py`
- `tests/integration/test_memory_persistence.py`
- `tests/test_chat_service.py`
- `tests/test_conversation_service.py`

## 3. Executive Summary

The current STM integration is implemented and operational, but it is built around a narrower identity model than the target business workflow now requires.

The existing implementation treats `session_id` as the single stateful identifier for both business workflow and agent execution. In practical terms, the current design assumes:

- a workspace can contain multiple sessions,
- a session is effectively the active conversation container,
- the session identifier is passed directly to LangGraph as `thread_id`,
- the `conversations` collection stores metadata using `session_id` as its unique key,
- tests, technical design documents, and runtime behavior all reinforce this 1:1 mapping.

This approach is internally consistent for session-scoped STM. However, it does not support the desired domain model where one session can own multiple distinct conversations, each with an independent agent memory thread.

The primary architectural conclusion is therefore:

**The system does not merely need additional CRUD endpoints. It needs a controlled identity-model refactor where conversation becomes the agent execution unit and session becomes a business grouping unit above it.**

## 4. Current Development Status

## 4.1 What Is Already Implemented

The current codebase already contains the core technical building blocks required for STM integration.

### 4.1.1 LangGraph Checkpointer Wiring

Short-Term Memory is already wired into the agent through LangGraph's MongoDB-backed checkpointer.

- `src/core/langgraph_bootstrap.py` creates a `MongoDBSaver` checkpointer when STM is enabled.
- `src/core/stock_assistant_agent.py` passes the identifier supplied as `session_id` into LangGraph as `thread_id` when a checkpointer is available.
- `src/web/api_server.py` initializes the checkpointer and injects it into the agent during server startup.

This means the durable memory mechanism itself already exists and is not merely speculative or planned work.

### 4.1.2 Stateful Chat Entry Points

Both REST and Socket.IO entry points already accept `session_id`.

- `src/web/routes/ai_chat_routes.py` validates `session_id` and forwards it to `ChatService`.
- `src/web/sockets/chat_events.py` accepts `session_id` and forwards it directly into agent processing.

This confirms that STM is already exposed through runtime interfaces, albeit only using the current session-scoped identity model.

### 4.1.3 Separate Persistence Concepts Already Exist

The persistence layer already separates workspace, session, and conversation collections.

- workspaces are modeled and persisted,
- sessions are modeled and persisted,
- conversations are modeled and persisted,
- agent checkpoints are stored separately through LangGraph.

The schema setup process in `src/data/schema/schema_manager.py` already provisions these collections. Therefore, the problem is not the absence of persistence structures. The problem is the semantic alignment and consistency contract between them.

### 4.1.4 Service and Repository Foundations Exist

The repository layer already includes:

- `WorkspaceRepository`
- `SessionRepository`
- `ConversationRepository`

The service layer already includes:

- `WorkspaceService`
- `ConversationService`
- `ChatService`

These components provide a solid implementation base. However, the hierarchy is only partially orchestrated, and session lifecycle logic is not yet elevated into a dedicated service.

## 4.2 What Is Partially Implemented

### 4.2.1 Conversation Metadata Model Exists but Is Not Fully Operational

The `conversations` collection was introduced as application-managed metadata separate from LangGraph checkpoints. The schema includes useful fields such as:

- status,
- message_count,
- total_tokens,
- summary,
- focused_symbols,
- session_assumptions,
- pinned_intent,
- last_activity_at.

The `ConversationService` can create or update this metadata through `track_message()` and archive workflow methods.

However, the normal chat flow does not currently invoke this service to persist message activity during actual user interaction. In the current runtime path:

- `ChatService` validates whether the referenced conversation is archived,
- the agent executes using the checkpointer,
- conversation metadata tracking is not consistently updated on user and assistant turns.

As a result, the checkpointer is currently the live STM truth for runtime memory, while the `conversations` collection functions more like a partially wired metadata sidecar.

### 4.2.2 Workspace Service Is Present but Not Yet Hierarchy-Oriented

`WorkspaceService` already supports workspace listing, creation, deletion, and summary behavior. It also references session and watchlist repositories. However, it does not yet provide a complete workflow for:

- session creation under a workspace,
- session ownership validation,
- nested conversation management,
- aggregate lifecycle reporting across the workspace hierarchy.

This service is a useful foundation, but not yet the full orchestration layer required by the target model.

## 4.3 What Is Missing

### 4.3.1 Session-Oriented Management Workflow

There is no dedicated `SessionService` that owns session creation, status transitions, or session-level orchestration. This is a notable gap because the target model elevates session from a simple stored record into a first-class management unit.

### 4.3.2 CRUD API Surface for the Hierarchy

The registered API blueprints currently cover:

- health,
- chat,
- models,
- user.

There is no REST management surface for:

- workspaces,
- sessions,
- conversations.

Therefore, the application does not yet expose the management workflow requested by the target use case.

### 4.3.3 Consistent Identity Model Across Domain and Agent Memory

The current implementation does not distinguish clearly between:

- business session identity,
- business conversation identity,
- agent thread identity.

This is the central blocker preventing the desired model from being implemented cleanly.

## 5. Current Architectural Constraint

## 5.1 Existing Identity Assumption

The current implementation is based on the following invariant:

`session_id == conversation identifier == LangGraph thread_id`

This invariant appears in several layers simultaneously.

### 5.1.1 Documentation Layer

The STM technical design, architecture documents, and spec-driven data model all describe a 1:1 mapping between session and conversation and a direct mapping from `session_id` to `thread_id`.

### 5.1.2 Schema Layer

The `conversations` schema uses `session_id` as its required unique business key.

### 5.1.3 Repository Layer

`ConversationRepository` uses `find_by_session_id()` and `get_or_create(session_id=...)` as primary operations.

### 5.1.4 Runtime Layer

The agent runtime builds `config={"configurable": {"thread_id": session_id}}` when STM is enabled.

### 5.1.5 Test Layer

Integration tests explicitly verify that multiple requests sharing the same `session_id` share the same `thread_id` and STM state.

## 5.2 Why This Constraint Now Conflicts With the Target Model

The desired model is:

- one workspace contains multiple sessions,
- one session contains multiple conversations,
- one conversation maps 1:1 with the agent checkpointer thread.

Under that target model, `session_id` can no longer be used as the LangGraph `thread_id`, because a single session may need to own multiple memory-isolated conversations.

Therefore, the system must change from:

- **session-scoped memory**

to:

- **conversation-scoped memory within a session-scoped business workflow**

This is a domain identity refactor, not a surface API addition.

## 6. Data and Schema Findings

## 6.1 Positive Findings

The codebase already persists workspace, session, and conversation concepts independently and provisions them through the schema manager. This lowers implementation risk because the architecture does not need to introduce entirely new persistence areas.

## 6.2 Schema Inconsistencies

Several inconsistencies must be resolved before the hierarchy can be managed reliably.

### 6.2.1 Session Schema Does Not Match the STM Spec Narrative

The spec-driven STM data model references a session business identifier used as the STM-facing key. The actual `sessions` schema, however, does not define an explicit `session_id` string field or user ownership field. It stores:

- `workspace_id` as ObjectId,
- `title`,
- `status`,
- `linked_symbol_ids`,
- timestamps.

This makes the session collection insufficient as an authoritative workflow boundary for identity propagation unless it is expanded.

### 6.2.2 Foreign Key Type Inconsistency

The following type mismatch exists today:

- `workspaces.user_id` is ObjectId,
- `sessions.workspace_id` is ObjectId,
- `conversations.workspace_id` is string or null,
- `conversations.user_id` is string or null.

This will complicate:

- ownership validation,
- workspace isolation,
- joins or cross-collection lookups,
- REST resource consistency.

### 6.2.3 Conversation Schema Encodes the Old Identity Model

The `conversations` schema currently uses `session_id` as the unique key. Under the target architecture, conversation should have its own identifier and should reference session as a parent. The uniqueness boundary should move to `conversation_id` or `thread_id`, not remain on `session_id`.

## 6.3 Persistence Consistency Observation

The collection set is present, but the system does not yet enforce a strict invariant such as:

- every conversation belongs to one valid session,
- every session belongs to one valid workspace,
- every conversation thread belongs to exactly one conversation,
- no checkpoint thread exists without a corresponding conversation metadata record,
- no active conversation exists without a valid parent session and workspace.

This invariant should become part of the design contract before the management workflow is expanded.

## 7. Target Architecture

## 7.1 Recommended Canonical Domain Model

The following model is recommended as the canonical design target.

### 7.1.1 Workspace

Workspace is the top-level business container.

Responsibilities:

- ownership boundary,
- collaboration boundary,
- isolation boundary for sessions and conversations,
- aggregate reporting container.

### 7.1.2 Session

Session is the business workflow container within a workspace.

Responsibilities:

- group related work over a bounded analysis period,
- represent a named investigation, initiative, or review cycle,
- contain multiple conversations over the same analytical context,
- support lifecycle transitions such as active, closed, archived.

### 7.1.3 Conversation

Conversation is the atomic agent interaction container within a session.

Responsibilities:

- one continuous thread of memory-aware exchange,
- one independent STM state lineage,
- one checkpointer thread,
- one metadata record in the `conversations` collection.

### 7.1.4 Thread Identity

`thread_id` should map 1:1 with conversation identity, not session identity.

This implies:

- `conversation_id == thread_id` is acceptable and recommended,
- `session_id` becomes a parent foreign key, not the STM execution key.

## 7.2 Target Relationship Diagram

```text
Workspace (1)
  -> Session (N)
       -> Conversation (N)
            -> Agent Checkpoint Thread (1:1)
```

This relationship model provides the separation required for:

- multiple independent discussion threads within one session,
- resumable STM on a conversation basis,
- richer management APIs,
- clearer auditability and lifecycle management.

## 8. Suggested Increment Outline

This section expands the recommended implementation path in a technical manner and preserves all critical points from the earlier assessment.

## 8.1 Increment 1: Freeze the Target Domain Model Before Implementation

The first and most important increment is not code. It is establishing a single canonical definition of the target hierarchy.

### Why this increment is necessary

The current repository contains multiple design documents that consistently reinforce the old invariant `session_id -> thread_id`. If implementation begins without first updating the design contract, subsequent changes will be inconsistent across:

- architecture documentation,
- persistence design,
- runtime APIs,
- tests,
- migration logic.

### Required outcome

The project should explicitly standardize the following decisions:

- a workspace owns many sessions,
- a session owns many conversations,
- a conversation owns one agent thread,
- `conversation_id` is the stateful runtime identity used for STM,
- `session_id` is no longer the direct thread identity.

### Deliverables

- revised ERD,
- updated technical design narrative,
- revised glossary for workspace, session, conversation, thread,
- updated acceptance criteria for STM and workflow management.

### Key recommendation

Do not expose new CRUD endpoints before this model is frozen. Otherwise, the API contract will prematurely encode a relationship model that is already known to be incomplete.

## 8.2 Increment 2: Normalize Identifiers Across Workspace, Session, and Conversation

The second increment is identity normalization.

### Why this increment is necessary

The current collections use a mixture of Mongo `_id`, ObjectId foreign keys, and string identifiers. STM runtime currently depends on a string `session_id`, while the sessions collection itself is not fully aligned with that model. This creates ambiguity in both persistence and API design.

### Target identity strategy

Each business resource should have a stable external identifier.

Recommended business identifiers:

- `workspace_id`
- `session_id`
- `conversation_id`
- `thread_id`

Recommended persistence rule:

- Mongo `_id` remains the storage key,
- business identifiers are explicit fields for API usage and cross-collection references.

### Recommended mapping

- `workspace.workspace_id` uniquely identifies the workspace,
- `session.session_id` uniquely identifies the session,
- `conversation.conversation_id` uniquely identifies the conversation,
- `conversation.thread_id` equals `conversation_id`.

### Benefits

- removes ambiguity between database identity and API identity,
- simplifies migration and tracing,
- supports future external integrations,
- avoids overloading `session_id` with two incompatible meanings.

## 8.3 Increment 3: Fix Schema Consistency Before Adding Workflow Logic

The third increment is schema repair and normalization.

### Why this increment is necessary

Without schema consistency, any higher-level workflow will rely on fragile assumptions, manual type coercion, and incomplete ownership validation.

### Required schema improvements

#### Sessions collection

Add or normalize fields such as:

- `session_id`
- `workspace_id`
- `user_id`
- `title`
- `status`
- timestamps

This will allow sessions to function as first-class business resources rather than lightweight records.

#### Conversations collection

Refactor fields to include:

- `conversation_id`
- `session_id`
- `workspace_id`
- `user_id`
- `thread_id`
- `status`
- metadata fields already present today

#### Uniqueness constraints

Move the primary uniqueness rule from `session_id` to `conversation_id` or `thread_id`.

#### Type consistency

Standardize how cross-collection references are stored. The project should choose one coherent strategy for parent-child references across workspaces, sessions, and conversations.

### Benefits

- cleaner repository contracts,
- reliable authorization and isolation checks,
- easier querying and reporting,
- simpler migration and test setup.

## 8.4 Increment 4: Introduce a Dedicated SessionService and Upgrade ConversationService

The fourth increment is service-layer restructuring.

### Why this increment is necessary

The current service layer has a partial hierarchy. Workspace behavior exists. Conversation behavior exists. Chat behavior exists. Session orchestration does not yet exist as a dedicated service.

This creates an architectural hole because the desired business workflow depends on session being a managed aggregate rather than just a stored document.

### Recommended service responsibilities

#### WorkspaceService

- manage workspace CRUD,
- list sessions under a workspace,
- produce workspace-level summaries,
- enforce ownership and isolation boundaries.

#### SessionService

- create, get, list, update, close, and archive sessions,
- validate workspace ownership,
- enumerate conversations within a session,
- enforce session lifecycle rules.

#### ConversationService

- create and manage conversations within a session,
- maintain metadata,
- archive conversations,
- expose conversation lookup by `conversation_id` and `thread_id`,
- support consistency validation with parent session and workspace.

#### ChatService

- resolve conversation context,
- validate that the conversation is active and belongs to the intended session and workspace,
- invoke the agent using `thread_id`,
- record metadata updates on each turn.

### Benefits

- strong separation of concerns,
- clearer ownership of lifecycle logic,
- better testability,
- easier extension for future policies and auditing.

## 8.5 Increment 5: Move Chat Runtime From Session-Aware to Conversation-Aware STM

This increment is the runtime heart of the refactor.

### Why this increment is necessary

The current chat path still treats `session_id` as the STM key. Under the target model, the chat runtime must instead operate on conversation identity.

### Target runtime flow

1. client submits `conversation_id`,
2. ChatService resolves the conversation record,
3. ChatService validates the conversation belongs to the expected session and workspace,
4. ChatService uses `conversation.thread_id` to invoke the agent,
5. LangGraph loads and saves STM for that conversation thread,
6. ChatService updates metadata for both user and assistant turns.

### Important design rule

The agent itself should remain unaware of higher-level business grouping beyond the thread identity. Session and workspace semantics should be resolved in the service layer before invocation.

### Benefits

- true support for multiple conversations per session,
- memory isolation between conversations,
- simpler future support for conversation branching or cloning,
- reduced coupling between business workflow and LangGraph state.

## 8.6 Increment 6: Expose CRUD APIs by Hierarchy

This increment introduces the management surface explicitly requested for the agentic application.

### Why this increment is necessary

Persistent hierarchy without management APIs leaves the design operationally incomplete. Users and dependent frontends need clear interfaces for managing workspaces, sessions, and conversations.

### Recommended REST structure

The following endpoint families are a practical baseline:

- `/api/workspaces`
- `/api/workspaces/{workspace_id}`
- `/api/workspaces/{workspace_id}/sessions`
- `/api/sessions/{session_id}`
- `/api/sessions/{session_id}/conversations`
- `/api/conversations/{conversation_id}`
- `/api/conversations/{conversation_id}/archive`

### CRUD expectations

#### Workspace

- create workspace,
- get workspace,
- list workspaces for a user,
- update workspace,
- remove or archive workspace according to policy.

#### Session

- create session under workspace,
- get session,
- list sessions in workspace,
- update session metadata,
- close or archive session.

#### Conversation

- create conversation under session,
- get conversation,
- list conversations in session,
- update conversation metadata if allowed,
- archive conversation.

### Recommendation on deletion semantics

Given the existing ADR and memory design, archival semantics are safer than hard deletion for conversations. Hard delete may still be introduced later under explicit compliance and data-retention requirements.

## 8.7 Increment 7: Wire Conversation Metadata Tracking Into the Real Chat Path

This increment is required to make the `conversations` collection operationally meaningful.

### Why this increment is necessary

Today, the metadata service exists but is not part of the main interaction lifecycle. That means the metadata record can become stale or absent even while the LangGraph checkpoint contains the actual conversational state.

### Required behavior

During chat processing, the application should:

- ensure the conversation record exists,
- record the user turn,
- record the assistant turn,
- update counters and timestamps,
- refresh focused symbols and other session-conversation metadata,
- enforce archive immutability.

### Design implication

The system should treat checkpoint state and conversation metadata as two coordinated but distinct persistence layers:

- checkpoint for actual STM graph state,
- conversation record for searchable, manageable, auditable application metadata.

### Benefits

- accurate management APIs,
- reliable dashboards and summaries,
- easier archival and retention workflows,
- better audit and troubleshooting visibility.

## 8.8 Increment 8: Add Consistency Checks, Reconciliation, and Migration Support

This increment addresses operational safety.

### Why this increment is necessary

The repository already contains STM data and tests based on the previous identity model. A clean transition requires controlled migration and integrity verification.

### Migration concerns

Existing session-based checkpoint threads should not be discarded or silently orphaned. The system needs a strategy to transform legacy records into the new structure.

### Recommended migration principle

Preserve historical thread identifiers by promoting them into conversation identifiers where possible. This minimizes data loss and avoids unnecessary checkpoint rekeying.

### Reconciliation capabilities to add

- detect conversations missing parent sessions,
- detect sessions missing parent workspaces,
- detect checkpoints without conversation records,
- detect conversation records without checkpoints where STM should exist,
- generate repairable reports for data anomalies.

### Benefits

- safer rollout,
- easier operational support,
- lower risk of state drift,
- better long-term maintainability.

## 8.9 Increment 9: Rewrite and Expand the Test Strategy Around the New Canonical Invariant

This increment ensures the refactor is governed by the correct behavior, not the obsolete one.

### Why this increment is necessary

The current integration tests actively assert the older `session_id == thread_id` behavior. If not rewritten, they will either block correct implementation or incentivize compatibility shortcuts that preserve the wrong architecture.

### Required test scenarios

#### Hierarchy tests

- one workspace can own multiple sessions,
- one session can own multiple conversations,
- conversation resources are isolated under their session and workspace.

#### STM tests

- same conversation restores the same thread context,
- two conversations within the same session do not share memory,
- resumed conversation retrieves prior checkpoint state,
- stateless mode still works when no conversation context is supplied.

#### Lifecycle tests

- archived conversation rejects new messages,
- closed or archived session prevents or constrains new conversation creation according to policy,
- cross-workspace and cross-session access is rejected.

#### Consistency tests

- metadata and checkpoint state remain aligned after message flow,
- migration preserves retrievable STM history,
- orphan detection identifies inconsistent records.

### Benefits

- architecture is enforced through tests,
- regression risk is reduced,
- rollout can be staged with confidence.

## 9. Recommended Delivery Phasing

The following phased delivery order is recommended.

### Phase A: Domain and Schema Alignment

Focus:

- finalize target domain model,
- normalize identifiers,
- repair schemas,
- define migration and compatibility strategy.

### Phase B: Service-Layer Refactor

Focus:

- introduce `SessionService`,
- refactor `ConversationService`,
- make `ChatService` conversation-aware,
- move workflow validation into services.

### Phase C: Management API Delivery

Focus:

- add workspace, session, and conversation CRUD endpoints,
- support archive and listing workflows,
- expose hierarchical navigation.

### Phase D: Runtime Consistency and Reconciliation

Focus:

- wire metadata writes into chat runtime,
- add integrity checks,
- implement migration and repair tooling.

### Phase E: Test Realignment and Hardening

Focus:

- rewrite old invariant tests,
- add coverage for the new hierarchy,
- validate backward compatibility where intentionally preserved.

## 10. Risks and Technical Considerations

## 10.1 Backward Compatibility Risk

Existing callers currently understand STM in terms of `session_id`. Moving to conversation-aware STM will require a compatibility decision:

- transitional support for legacy `session_id`,
- or a deliberate API break with migration plan.

## 10.2 Data Migration Risk

Historical checkpoints and metadata may not align cleanly once the new relationship model is introduced. A migration report and dry-run capability are strongly recommended.

## 10.3 Authorization and Isolation Risk

Because type consistency across `workspace_id`, `session_id`, and `user_id` is not yet standardized, authorization checks may become fragile unless identity normalization is completed first.

## 10.4 Partial Refactor Risk

The highest-risk implementation path is to add CRUD endpoints without first changing the identity model. That approach would create API surface area around an architecture that is already known to be insufficient.

## 11. Final Recommendation

The project should treat this initiative as an architectural evolution of STM integration, not simply as management endpoint expansion.

The most important design decision is to redefine the memory boundary so that:

- session is a business workflow container,
- conversation is the STM container,
- conversation maps 1:1 to agent thread state.

Once this identity model is established, the remaining work becomes straightforward and can proceed in an orderly manner through schema alignment, service refactor, management APIs, runtime consistency updates, and revised tests.

## 12. Proposed Next Technical Step

The next concrete engineering step should be the production of a follow-up design package containing:

- a revised entity relationship diagram,
- normalized collection contracts,
- endpoint definitions for workspace, session, and conversation management,
- a compatibility and migration strategy for legacy session-bound STM,
- an implementation task breakdown by phase.

That design package should be approved before schema or API changes begin.