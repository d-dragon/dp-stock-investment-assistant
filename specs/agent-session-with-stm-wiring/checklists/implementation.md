# Implementation Requirements Quality Checklist: STM Domain Model Refactor and Service-Layer Restructuring

**Purpose**: Validate that spec and plan requirements are clear, complete, consistent, and unambiguous enough for a developer to implement the STM domain model refactor and service-layer restructuring without guesswork.
**Created**: 2026-03-17
**Feature**: [spec.md](../spec.md) | [plan.md](../plan.md)
**Focus**: Schema normalization (Phase A) + service-layer restructuring (Phase B)
**Depth**: Standard — implementation readiness for pre-production codebase
**Audience**: Implementing developer and PR reviewer

---

## Schema & Identity Normalization (Phase A)

- [ ] CHK001 - Are all type changes for `workspace_id` exhaustively listed across every affected collection and index? [Completeness, Plan §Step 1.1–1.3]
- [ ] CHK002 - Is the UUID v4 regex pattern for `conversation_id` and `session_id` explicitly specified, or only referenced by convention? [Clarity, Spec §Assumptions]
- [ ] CHK003 - Are the exact indexes to DROP vs ADD enumerated for both `conversations` and `sessions` collections? [Completeness, Plan §Index Changes]
- [ ] CHK004 - Is the `thread_id == conversation_id` invariant enforced at schema validation level or only by application code? [Ambiguity, Spec §FR-002]
- [x] CHK005 - Are the `context_overrides` object's allowed keys and structure defined, or is it a free-form object? [Clarity, Plan §Step 1.3] — **Resolved 2026-03-18**: defined as a free-form object with shallow key overwrite semantics; `focused_symbols` is treated as a replacement key when present.
- [ ] CHK006 - Is the `conversation_intent` field's relationship to `context_overrides` specified — are they independent or nested? [Clarity, Plan §Step 1.3]
- [ ] CHK007 - Is the MongoDB schema validation level (`strict` vs `moderate` vs `warn`) explicitly specified for each collection after migration? [Clarity, Plan §Risk Mitigations]
- [ ] CHK008 - Are the `assumptions`, `pinned_intent`, and `focused_symbols` field types and constraints (max length, array item type) defined beyond basic type? [Clarity, Plan §Step 1.2]
- [ ] CHK009 - Is the `status` enum rename from `"open"` to `"active"` defined as a schema-only change, or does it require data migration of existing session records? [Ambiguity, Plan §Step 1.2]
- [ ] CHK010 - Are required vs optional fields explicitly marked for the conversations schema post-refactor (e.g., is `context_overrides` nullable or absent-by-default)? [Completeness, Plan §Step 1.3]
- [ ] CHK011 - Is the compound index `idx_conversations_hierarchy_status` field order specified (which field first matters for query performance)? [Clarity, Plan §Index Changes]

## Migration Strategy (Clean-Slate)

- [ ] CHK012 - Are ALL LangGraph-managed collections to be dropped explicitly listed (checkpoints, writes, write-ahead logs)? [Completeness, Plan §Step 1.6]
- [ ] CHK013 - Is the migration idempotent — can it be safely re-run without side effects? [Gap]
- [ ] CHK014 - Are the exact collection names for LangGraph checkpoint storage specified (they vary by MongoDBSaver configuration)? [Clarity, Plan §Step 1.6]
- [ ] CHK015 - Is the migration ordering defined relative to schema validation application — drop first, then apply validation, or simultaneous? [Ambiguity, Plan §Step 1.6]
- [ ] CHK016 - Are warnings/logs for data loss during clean-slate migration specified with enough detail (log level, message format, affected counts)? [Clarity, Plan §Step 1.6]
- [x] CHK017 - Does the migration account for the `sessions` collection — is it dropped, preserved, or migrated in place? [Gap, Plan §Step 1.6] — **Resolved 2026-03-18**: clean-slate migration drops and recreates `sessions`, `conversations`, and LangGraph checkpoint collections.

## Service Layer — SessionService (Phase B)

- [ ] CHK018 - Is "workspace ownership validation" in `create_session()` defined — does it check user_id ownership of workspace_id, or just workspace existence? [Ambiguity, Spec §FR-008]
- [ ] CHK019 - Are the exact error types/codes for lifecycle transition violations specified (e.g., attempting closed → active)? [Gap, Spec §FR-009]
- [ ] CHK020 - Is the cascade behavior of `archive_session()` fully specified — does it archive conversations synchronously or asynchronously? [Ambiguity, Spec §FR-009b]
- [ ] CHK021 - Are race conditions addressed for concurrent archive + message operations beyond the edge case prose? [Coverage, Spec §Edge Cases]
- [ ] CHK022 - Is the `health_check()` contract for SessionService specified — what dependencies does it report on? [Gap, Plan §Step 2.2]
- [ ] CHK023 - Is the `update_session()` method's allowed update fields bounded, or can any field be updated? [Clarity, Plan §Step 2.2]
- [ ] CHK024 - Is the `update_session_context()` method's behavior on partial updates defined — does omitting `pinned_intent` clear it or leave it unchanged? [Ambiguity, Plan §Step 2.2]

## Service Layer — ConversationService Refactor

- [ ] CHK025 - Is the `create_conversation()` method's session status validation specified — can conversations be created under closed sessions? [Completeness, Spec §FR-009b]
- [ ] CHK026 - Are the conversation lifecycle state transitions (active → summarized → archived) consistent between spec FR-015a and plan Step 2.3? [Consistency, Spec §FR-015a, Plan §Step 2.3]
- [ ] CHK027 - Is the session context inheritance mechanism in `create_conversation()` specified — are fields copied or referenced? [Ambiguity, Spec §FR-011a]
- [x] CHK028 - Is the `get_conversation_with_context()` merge strategy defined — does conversation override win, or is it a deep merge? [Clarity, Plan §Step 2.3] — **Resolved 2026-03-18**: shallow key overwrite, conversation overrides win over session base for matching keys.
- [ ] CHK029 - Are cache key format changes from `session_id` to `conversation_id` enumerated for all affected keys? [Completeness, Plan §Step 2.3]
- [ ] CHK030 - Is the `list_conversations(session_id)` return order specified (by creation date, last activity, or unordered)? [Gap, Plan §Step 2.3]
- [ ] CHK031 - Are the `track_message()` method's metadata update fields (`message_count`, `last_activity_at`) specified for both user and assistant turns? [Clarity, Spec §FR-012]

## Service Layer — ChatService Refactor

- [ ] CHK032 - Is the `_validate_conversation_active()` method's behavior for "summarized" status defined — is it treated as active for messaging purposes? [Ambiguity, Spec §FR-015a, Plan §Step 2.4]
- [ ] CHK033 - Is "validate conversation belongs to expected workspace via hierarchy" specified — does ChatService receive workspace_id from the caller or derive it? [Clarity, Plan §Step 2.4]
- [ ] CHK034 - Is the merged context dict structure for agent prompt injection defined — keys, nesting, format? [Gap, Plan §Step 2.4]
- [ ] CHK035 - Is the `session_provider` dependency marked Optional — what happens when it's None (no session context loaded)? [Clarity, Plan §Step 2.4]
- [ ] CHK036 - Are error responses for conversation validation failures specified with HTTP status codes and response body format? [Gap, Spec §Edge Cases]

## Protocol & DI Updates

- [ ] CHK037 - Is the `AgentProvider` protocol's `conversation_id` parameter Optional or required — does stateless mode pass None? [Ambiguity, Spec §FR-013, FR-017]
- [ ] CHK038 - Does the `ConversationProvider` protocol define return types for `get_conversation()` — Dict, Optional[Dict], or a typed dataclass? [Clarity, Plan §Protocol Updates]
- [ ] CHK039 - Is the `SessionProvider` protocol's `get_session_context()` return type defined — plain dict, TypedDict, or dataclass? [Clarity, Plan §Protocol Updates]
- [ ] CHK040 - Are protocol method signatures consistent between plan §Protocol Updates and plan §Step 2.1? [Consistency, Plan §Protocol Updates vs §Step 2.1]
- [ ] CHK041 - Is the import strategy for protocols specified — does ChatService import SessionProvider from protocols.py, not session_service.py? [Clarity, Plan §Risk Mitigations]

## Lifecycle State Machine

- [ ] CHK042 - Are all valid session state transitions exhaustively listed — is active → archived directly allowed, or must it go through closed? [Completeness, Spec §FR-009]
- [ ] CHK043 - Are conversation state transitions (FR-015a) consistent with session cascade behavior (FR-009b) — can a cascaded archive skip the summarized state? [Consistency, Spec §FR-009b vs FR-015a]
- [ ] CHK044 - Is the "summarized" conversation state's impact on messaging clearly defined — can users send new messages to a summarized conversation? [Ambiguity, Spec §FR-015a, Clarifications]
- [ ] CHK045 - Is the immutability constraint for archived conversations defined beyond "no new messages" — can metadata fields (title, tags) be updated? [Clarity, Spec §FR-016]

## Context Inheritance & Isolation

- [x] CHK046 - Is the inheritance timing defined — does a conversation snapshot session context at creation, or read it live on each message? [Ambiguity, Spec §FR-011a] — **Resolved 2026-03-18**: context is loaded live at request/message processing time.
- [ ] CHK047 - Does the spec define what happens to inherited context when session context is updated after conversation creation? [Gap, Spec §FR-011a]
- [x] CHK048 - Is the `context_overrides` merge strategy defined for conflicts — e.g., conversation overrides `pinned_intent` while session also has it? [Clarity, Spec §FR-011b] — **Resolved 2026-03-18**: conflict resolution uses shallow overwrite (conversation value wins).
- [ ] CHK049 - Is session context isolation across workspaces an explicit requirement or implied — are there cross-workspace access controls defined? [Clarity, Spec §FR-012b]
- [x] CHK050 - Are the focused_symbols array semantics defined — are they additive to session symbols, or do they replace them in conversation overrides? [Ambiguity, Spec §FR-011b] — **Resolved 2026-03-18**: replacement semantics for conversation override value.

## Stateless Mode & Backward Compatibility

- [x] CHK051 - Is stateless mode behavior (FR-017) fully specified for the post-refactor API — does it bypass conversation validation entirely? [Completeness, Spec §FR-017] — **Resolved 2026-03-18**: yes, missing `conversation_id` follows stateless processing and bypasses conversation/session persistence validation.
- [x] CHK052 - Is the API entry point's handling of missing `conversation_id` clearly defined — 400 error, or stateless pass-through? [Ambiguity, Plan §Step 2.7, Spec §FR-017] — **Resolved 2026-03-18**: stateless pass-through when `conversation_id` is absent; 400 applies only to malformed UUID when `conversation_id` is provided.
- [ ] CHK053 - Are the exact request/response body schemas for the refactored chat endpoint documented? [Gap, Plan §Step 2.7]
- [ ] CHK054 - Is the Socket.IO event payload change (session_id → conversation_id) documented with the exact event name and payload structure? [Clarity, Plan §Step 2.7]

## API Entry Points

- [x] CHK055 - Is the `ai_chat_routes.py` request body schema change specified — is `conversation_id` required, optional, or conditional? [Ambiguity, Plan §Step 2.7] — **Resolved 2026-03-18**: `conversation_id` is optional/conditional (`required` only for stateful memory flows).
- [x] CHK056 - Are error responses for invalid/missing `conversation_id` defined with status codes? [Gap, Spec §Edge Cases] — **Resolved 2026-03-18**: missing `conversation_id` is valid (stateless); invalid format when provided returns 400; unknown but well-formed `conversation_id` returns 404.
- [ ] CHK057 - Is the streaming response format affected by the refactor, or does only the input contract change? [Clarity, Plan §Step 2.7]

## Agent Integration

- [ ] CHK058 - Is the `stock_assistant_agent.py` refactor limited to parameter renaming, or does the agent need to handle context injection? [Clarity, Plan §Step 2.5]
- [ ] CHK059 - Is the agent's "unawareness" of session/workspace hierarchy an explicit contract or just a current design — should it be enforced? [Clarity, Spec §FR-013]
- [ ] CHK060 - Are all three agent methods (`process_query`, `process_query_streaming`, `process_query_structured`) listed for the conversation_id rename? [Completeness, Plan §Step 2.5]

## Testing Requirements

- [ ] CHK061 - Are test scenarios for multi-conversation memory isolation (SC-001) defined with specific assertion criteria? [Measurability, Spec §SC-001]
- [ ] CHK062 - Is "zero regression" (SC-002) achievable given the deliberate API break — are affected test files enumerated? [Consistency, Spec §SC-002 vs Decision §10.1]
- [ ] CHK063 - Are performance regression criteria (SC-003) quantified — what response time thresholds define "no regression"? [Measurability, Spec §SC-003]
- [x] CHK064 - Is SC-006 (legacy data accessible after migration) consistent with Decision §10.2 (clean-slate drop)? **RESOLVED**: SC-006 struck in spec.md, replaced with clean-slate criterion. [Conflict, Spec §SC-006 vs Plan §Decision 10.2]
- [ ] CHK065 - Are session context inheritance tests (SC-009, SC-010) specified with concrete assertion patterns? [Measurability, Spec §SC-009, SC-010]
- [ ] CHK066 - Are integration test dependencies (MongoDB, Redis) specified — do tests use mocks/stubs or require running services? [Gap, Plan §Phase 3]

## Cross-Cutting Concerns

- [ ] CHK067 - Are error handling requirements defined for each service method — what exceptions are thrown vs caught? [Gap]
- [ ] CHK068 - Is logging strategy specified for the new SessionService — log levels, context fields, sensitive data exclusions? [Gap]
- [ ] CHK069 - Are cache TTL values defined for session and conversation cache entries? [Gap]
- [ ] CHK070 - Is the ServiceFactory singleton behavior for `get_session_service()` explicitly stated — lazy init, thread safety? [Clarity, Plan §Step 2.6]
- [ ] CHK071 - Are timestamp fields (`created_at`, `updated_at`, `last_activity_at`) specified for UTC format consistency? [Gap]
- [ ] CHK072 - Is the `user_id` validation approach defined — is it trusted from the request context or validated against the users collection? [Gap, Spec §FR-008]

## Dependencies & Assumptions

- [ ] CHK073 - Is the assumption that "no production data exists" documented as a precondition for the clean-slate migration? [Traceability, Plan §Decision 10.2]
- [ ] CHK074 - Is the MongoDBSaver checkpoint collection naming convention documented — does it depend on configuration? [Assumption, Plan §Step 1.6]
- [ ] CHK075 - Are LangGraph version constraints specified — does the refactor depend on specific MongoDBSaver API behavior? [Gap]
- [ ] CHK076 - Is the phase ordering (schema first, services second) enforced by task dependencies or just by convention? [Clarity, Plan §Decision 10.4]

## Notes

- Items reference spec sections as `[Spec §FR-XXX]` or `[Spec §SC-XXX]` and plan sections as `[Plan §Step X.Y]` or `[Plan §Decision X.Y]`.
- `[Gap]` indicates a requirement area not currently covered in spec or plan.
- `[Ambiguity]` indicates a requirement that could be interpreted multiple ways.
- `[Conflict]` indicates potential inconsistency between spec sections.
- `[Consistency]` checks alignment between related requirements.
- CHK064 **RESOLVED**: SC-006 struck in spec.md and replaced with clean-slate success criterion per analysis C1 remediation.
