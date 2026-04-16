# Specification Analysis Report — STM Domain Model Refactor

**Feature**: `agent-session-with-stm-wiring` | **Date**: 2025-07-18 | **Re-analysis**: 2026-03-18 | **Status**: Pre-implementation analysis

---

## Findings Table (Original Round)

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| **C1** | Consistency | ~~**CRITICAL**~~ **RESOLVED** | spec.md SC-006 vs plan.md Decision §10.2 | SC-006 struck and replaced with clean-slate success criterion. | ~~Formally strike or amend SC-006 in spec.md.~~ Done. |
| **W1** | Inconsistency | ~~**WARNING**~~ **RESOLVED** | spec.md FR-009 vs plan.md Step 2.2 vs tasks.md T012 | **Decision**: Enforce sequential `active→closed→archived` for sessions. Plan Step 2.2 and T012 updated to remove `active→archived` skip. | Done. |
| **W2** | Underspecification | ~~**WARNING**~~ **RESOLVED** | plan.md §Schema Changes vs AGENT_MEMORY_TECHNICAL_DESIGN.md | `archived_at` and `archive_reason` added to plan Step 1.3 schema table, Step 1.3 instructions, and tasks.md T004. | Done. |
| **W3** | Underspecification | ~~**WARNING**~~ **RESOLVED** | plan.md §Schema Changes vs AGENT_MEMORY_TECHNICAL_DESIGN.md | **Decision**: Keep `focused_symbols` on conversations as thread-local refinement (per tech design). Added to plan schema table, Step 1.3, and T004. | Done. |
| **W4** | Divergence | **WARNING — DEFERRED** | plan.md §Step 2.5 + §Step 2.7 vs AGENT_MEMORY_TECHNICAL_DESIGN.md + ARCHITECTURE_DESIGN.md | **Governing docs will become stale**: Plan removes `session_id` from agent/API entry points (Decision §10.1). Both governing docs still show `session_id: Optional[str]` in API contracts and agent method signatures. The divergence is intentional and documented but the governing docs are not updated. | Add a post-implementation task to update AGENT_MEMORY_TECHNICAL_DESIGN.md §API Contracts and ARCHITECTURE_DESIGN.md §5-6 to reflect the deliberate API break. |
| **W5** | Inconsistency | ~~**WARNING**~~ **RESOLVED** | spec.md §Assumptions vs AGENT_MEMORY_TECHNICAL_DESIGN.md | **Decision**: UUID v4 (strict) is canonical for `conversation_id`. Spec and plan already use UUID v4. Tech design to be updated post-implementation (W4). | Done. |
| **W6** | Underspecification | ~~**WARNING**~~ **RESOLVED** | spec.md §Key Entities vs plan.md §Schema Changes | `linked_symbol_ids` added to plan Step 1.2 schema table, Step 1.2 instructions, and T003. | Done. |
| **W7** | Coverage Gap | ~~**WARNING**~~ **RESOLVED** | tasks.md T011 vs plan.md §Project Structure | `src/services/exceptions.py` added to plan's project structure with status MODIFY. | Done. |
| **I1** | Terminology | **INFO** | plan.md §Index Changes vs AGENT_MEMORY_TECHNICAL_DESIGN.md | **Index naming inconsistency**: Plan uses `idx_conversations_session_id` and `idx_conversations_thread_id`; tech design uses `idx_conversations_session` and `idx_conversations_thread`. | Adopt one convention. Recommend the plan's more descriptive names (with `_id` suffix). |
| **I2** | Underspecification | **INFO** | AGENT_MEMORY_TECHNICAL_DESIGN.md vs plan.md | **`user_id` not in tech design's `required` array**: Tech design's conversations `required` list is `["conversation_id", "session_id", "workspace_id", "created_at"]` — missing `user_id`. Plan correctly makes `user_id` required. | Plan's stricter requirement is better. Update tech design if it's to remain the reference. |
| **I3** | Underspecification | **INFO** | AGENT_MEMORY_TECHNICAL_DESIGN.md vs plan.md | **`metadata` and `total_tokens` fields**: Tech design includes `metadata` (object) and `total_tokens` (int) in target conversations schema. Plan doesn't explicitly address these. Likely already exist in current schema. | Verify current `conversations_schema.py` includes these fields. If not, add to plan or document as deferred. |
| **I4** | Coverage | **INFO** | tasks.md T025 | **Unlisted test files may break**: Workspace contains `test_chat_routes.py`, `test_api_routes.py`, `test_agent.py` that likely reference `session_id` but are not explicitly listed in plan Phase 3 or tasks Phase 6 for updates. T025 serves as catch-all but is imprecise. | Consider enumerating all files containing `session_id` references in a pre-implementation grep, and adding them to T025's scope description. |
| **I5** | Underspecification | **INFO** | plan.md §Schema Changes | **`summary_up_to_message` field**: Tech design includes this field for summarization boundary tracking. Not in plan schema changes. Expected since summarization mechanism is out of scope, but the field stub may be needed for future compatibility. | Document as intentionally deferred. If field already exists in current schema, preserve it. |

---

## Re-Analysis Findings (Round 2 — 2026-03-18)

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| **W-NEW-1** | Duplication | ~~**WARNING**~~ **RESOLVED** | spec.md Key Entities | Duplicate Conversation entity (two bullets with overlapping attributes). | ~~Merge into single canonical definition.~~ Done — merged, keeping full attributes from bullet 1 + lifecycle prose from bullet 2. |
| **W-NEW-2** | Consistency | ~~**WARNING**~~ **RESOLVED** | spec.md FR-006 | FR-006 text said "preserves historical thread identifiers by promoting" — contradicted Decision §10.2 (clean-slate). | ~~Strike and replace with clean-slate wording.~~ Done — FR-006 struck and replaced. |
| **W-NEW-3** | Consistency | ~~**WARNING**~~ **RESOLVED** | spec.md US3 Scenario 2 | US3 Scenario 2 described promote-in-place migration — contradicted §10.2. | ~~Strike and replace with clean-slate validation scenario.~~ Done — scenario struck and replaced. |
| **W-NEW-4** | Consistency | ~~**WARNING**~~ **RESOLVED** | spec.md Assumptions (2 items) | (a) Promote-in-place assumption contradicted §10.2. (b) Backward-compat shim assumption contradicted §10.1. | ~~Replace both.~~ Done — both assumptions struck and replaced. |
| **W-NEW-5** | Consistency | ~~**WARNING**~~ **RESOLVED** | spec.md Edge Cases | Edge case described promote-in-place migration failure handling — meaningless under clean-slate. | ~~Replace with clean-slate failure scenario.~~ Done — edge case struck and replaced. |

---

## Coverage Summary

| Spec Requirement | Has Plan Step? | Has Task? | Task IDs | Notes |
|------------------|---------------|-----------|----------|-------|
| FR-001 (Domain model hierarchy) | ✅ Data Model | ✅ | T002–T007 | Aggregate outcome of all schema work |
| FR-002 (conversation_id as STM key) | ✅ Step 1.3 | ✅ | T004, T010 | |
| FR-003 (Type normalization) | ✅ Steps 1.1–1.3 | ✅ | T002, T003, T004 | |
| FR-004 (Sessions schema) | ✅ Step 1.2 | ✅ | T003 | `linked_symbol_ids` added (W6 resolved) |
| FR-005 (Conversations indexes) | ✅ Step 1.3 | ✅ | T004 | |
| FR-006 (Migration path) | ✅ Step 1.6 | ✅ | T007 | Clean-slate per §10.2 |
| FR-007 (SessionService ops) | ✅ Step 2.2 | ✅ | T012 | |
| FR-008 (Workspace ownership) | ✅ Step 2.2 | ✅ | T012 | |
| FR-009 (Lifecycle transitions) | ✅ Step 2.2 | ✅ | T012 | active→archived discrepancy (W1) |
| FR-009a (Session context) | ✅ Step 2.2 | ✅ | T012 | |
| FR-009b (Cascade behavior) | ✅ Step 2.2 | ✅ | T012 | |
| FR-010 (ConversationService refactor) | ✅ Step 2.3 | ✅ | T009 | |
| FR-011 (Conversation CRUD) | ✅ Step 2.3 | ✅ | T009 | |
| FR-011a (Context inheritance) | ✅ Step 2.3 | ✅ | T009 | |
| FR-011b (Context refinement) | ✅ Step 2.3 | ✅ | T009 | |
| FR-012 (ChatService conversation-aware) | ✅ Step 2.4 | ✅ | T013 | |
| FR-012a (Session context loading) | ✅ Step 2.4 | ✅ | T013 | |
| FR-012b (Context isolation) | ✅ Step 2.4 | ✅ | T013 | |
| FR-013 (AgentProvider protocol) | ✅ Step 2.5 | ✅ | T010 | |
| FR-014 (ServiceFactory) | ✅ Step 2.6 | ✅ | T014 | |
| FR-015 (Protocols update) | ✅ Step 2.1 | ✅ | T008 | |
| FR-015a (Conversation state machine) | ✅ Step 2.3 | ✅ | T009 | |
| FR-016 (Archive immutability) | ✅ Steps 2.2–2.3 | ✅ | T009, T012 | `archived_at`/`archive_reason` added (W2 resolved) |
| FR-017 (Stateless mode) | ✅ Steps 2.5, 2.7 | ✅ | T010, T015 | |
| FR-018 (Memory never stores facts) | ✅ Constitution Check | — | — | Design constraint, no task needed |
| FR-019 (Backward compat) | ✅ DEFERRED | ✅ DEFERRED | — | Consistent across artifacts |

---

## SRS External Alignment

| SRS Section | Requirement IDs | Coverage in Spec | Gaps |
|-------------|----------------|-----------------|------|
| FR-3.1 (Short-Term Memory) | FR-3.1.1 – FR-3.1.8 | ✅ All 8 covered | None |
| FR-3.2 (Hierarchical Conv Mgmt) | FR-3.2.1 – FR-3.2.10 | ✅ All 10 covered | None |
| FR-3.4 (Session Context) | FR-3.4.1 – FR-3.4.7 | ✅ All 7 covered | None |

---

## Constitution Alignment

None. All seven ADR-001 principles validated in plan's Constitution Check table. No violations detected.

---

## Unmapped Tasks

None. All 25 tasks (T001–T025) trace to spec FRs, plan steps, or legitimate cross-cutting concerns (setup, test catchall).

---

## Known Issues Validation

| Issue | Status | Detail |
|-------|--------|--------|
| **CHK064: SC-006 vs §10.2** | ✅ **RESOLVED** | SC-006 struck in spec.md, replaced with clean-slate criterion. CHK064 marked resolved in checklist. |
| **session_id in API contracts vs API break** | ⚠️ **Documented divergence** | Tech design shows `session_id: Optional[str]` in API contracts; plan Decision §10.1 removes it entirely. Flow is internally consistent — session_id is derived from conversation's FK. Governing docs need post-implementation update. **(W4)** |
| **Tech design schema fields not in plan** | ✅ **RESOLVED** | `archived_at`, `archive_reason`, and `focused_symbols` added to plan and tasks. `metadata`, `total_tokens`, `summary_up_to_message` deferred (I3, I5). |

---

## Metrics

| Metric | Value |
|--------|-------|
| Total Functional Requirements | 22 (FR-001 through FR-019, including sub-items) |
| Total Tasks | 25 (T001–T025) |
| Coverage % (FRs with ≥1 task) | **100%** (22/22) |
| SRS Requirements Covered | 25/25 (FR-3.1 + FR-3.2 + FR-3.4) |
| Critical Issues | **0** (C1 resolved) |
| Warning Issues | **1 open** (W4 deferred to post-impl); **11 resolved** (W1–W3, W5–W7, W-NEW-1–5) |
| Info Issues | **5** (I1–I5) |
| Constitution Violations | **0** |
| Deferred Items (consistent) | 2 (FR-019, US5) |
