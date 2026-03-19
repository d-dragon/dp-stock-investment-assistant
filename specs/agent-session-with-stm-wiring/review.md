# Pre-Implementation Review

**Feature**: STM Domain Model Refactor and Service-Layer Restructuring  
**Artifacts reviewed**: spec.md, plan.md, tasks.md, checklists/implementation.md, analysis.md  
**Review model**: GPT-5.3-Codex (cross-model review)  
**Generating model**: Claude Opus 4.6 (Phases 1-6)  
**Date**: 2026-03-18

## Summary

| Dimension | Verdict | Key Observation |
|-----------|---------|-----------------|
| Spec-Plan Alignment | **PASS** | All 22 FRs map to plan steps. §10.1-§10.4 decisions are consistent. Deferred items (FR-019, US5) agree across all artifacts. |
| Plan-Tasks Completeness | **PASS** | All 16 plan steps map to ≥1 task. No orphan tasks. T011 (exceptions) lacks an explicit plan step but is covered in Project Structure. |
| Dependency Ordering | **WARN** | Phases 3 and 4 are serialized in the task graph but could run in parallel per the phase dependency diagram — conservative but suboptimal. |
| Parallelization Correctness | **WARN** | Parallel-group 3 (T009, T010, T011) has a hidden semantic dependency: T009's lifecycle enforcement needs `InvalidLifecycleTransitionError` defined in T011. |
| Feasibility & Risk | **WARN** | 3 tasks (T004, T009, T012) are large (8-11 sub-items each). 4 test files with `session_id` references are not explicitly scoped in any task—only caught by T025 catchall. |
| Standards Compliance | **PASS** | Follows BaseService, MongoGenericRepository, ServiceFactory, Protocol-based DI. Constitution checked and clean. |
| Implementation Readiness | **WARN** | Several ambiguities flagged in checklist remain unresolved: `context_overrides` structure, merge strategy, inheritance timing (snapshot vs live). Agent's `process_query_structured` currently lacks `session_id`—task says "rename" but means "add". |

**Overall**: **READY WITH WARNINGS**

## Findings

### Critical (FAIL — must fix before implementing)

None.

### Warnings (WARN — recommend fixing, can proceed)

**W-R1: Parallel-group 3 has a hidden cross-file dependency (T009 ↔ T011)**

T009 (conversation_service.py) sub-item 8 needs to raise `InvalidLifecycleTransitionError` for state machine enforcement (FR-015a). This exception class is created by T011 (exceptions.py), which runs in the same parallel group. If T009 executes before T011, the import will fail.

- **Location**: tasks.md Phase 3, parallel-group 3
- **Recommendation**: Either (a) move T011 to run before parallel-group 3 (sequential, after T008), or (b) split T011 into two parts — exception creation (before group 3) and renaming (in group 3), or (c) add a note that T009 implementer must define the exception inline if T011 hasn't run yet.

**W-R2: Four test files with `session_id` references not scoped in any explicit task**

Grep of the test suite reveals 11 files containing `session_id`. Seven are explicitly listed in tasks T017-T024, but four are not:

| File | `session_id` Occurrences | In Tasks? |
|------|-------------------------|-----------|
| tests/api/test_chat_routes_memory.py | 30+ | **No** — Heavy usage, needs full rework |
| tests/test_api_routes.py | Unknown | **No** |
| tests/test_chat_routes.py | Unknown | **No** |
| tests/test_additional_repositories.py | Unknown | **No** |

T025 ("run full test suite and fix remaining import errors") is the only catch-all, but `test_chat_routes_memory.py` alone requires 30+ `session_id` → `conversation_id` replacements across test names, fixtures, assertions, and mock signatures — far beyond "import error fixes."

- **Location**: tasks.md Phase 6-7
- **Recommendation**: Add an explicit task (e.g., T025a) or expand T025's scope description to enumerate these 4 files. At minimum, `test_chat_routes_memory.py` needs its own task given the volume of changes. This was flagged as I4 in analysis.md but remains open.

**W-R3: Phase 3 and Phase 4 are unnecessarily serialized at the task level**

The phase dependency diagram correctly shows Phase 3 (US1) and Phase 4 (US2) running in parallel — both depend only on Phase 2:

```
Phase 2 ──► Phase 3 (US1: T009, T010, T011)
Phase 2 ──► Phase 4 (US2: T012)
```

But the task dependency graph serializes them: `T009/T010/T011 → T012`. Verified: T012 (SessionService) depends on `session_repository` (T005), `workspace_repository` (existing), and `conversation_repository` (T006) — all from Phase 2. It does NOT depend on ConversationService changes (T009). T012 imports from `protocols.py` (T008) for the `SessionProvider` it implements, not from `conversation_service.py`.

- **Location**: tasks.md Task Dependency Graph
- **Impact**: Serialization adds unnecessary latency. T012 could join parallel-group 3.
- **Recommendation**: Move T012 into parallel-group 3 (which would become a group of 4 — split into two groups of 2, or accept a group of 4 if tooling allows).

**W-R4: Three tasks are over-large (>8 sub-items each)**

| Task | Sub-items | Estimated LOC | Risk |
|------|-----------|---------------|------|
| T004 (conversations schema) | 8 | ~100-150 | Schema + indexes + default doc fn |
| T009 (conversation service) | 10 | ~150-200 | New methods + renames + cache + lifecycle |
| T012 (session service) | 11 | ~200-250 | Entire new service class creation |

Per feasibility guidelines, tasks touching >3 files or >200 LOC should be flagged. T009 and T012 are near or above that threshold.

- **Recommendation**: Consider splitting T009 into "rename existing methods" and "add new methods" (two tasks, same file). T012 is a new file creation so splitting is less natural, but could separate CRUD methods from lifecycle/context methods.

**W-R5: Agent `process_query_structured` task description is misleading**

T010 sub-item 3 says: "rename `session_id` parameter to `conversation_id` (note: current signature lacks session_id — add it)". The current source confirms:

```python
def process_query_structured(self, query: str, *, provider: Optional[str] = None) -> AgentResponse:
```

No `session_id` parameter exists. The parenthetical note is accurate but the primary verb "rename" is wrong — it should say "add `conversation_id` parameter". An implementer reading quickly could miss the parenthetical and skip the method.

- **Location**: tasks.md T010 sub-item 3
- **Recommendation**: Reword to "Add `conversation_id` parameter to `process_query_structured()` (not present in current signature)."

**W-R6: Unresolved checklist ambiguities that could block implementation**

Several checklist items remain unchecked and represent genuine implementation ambiguities:

| CHK | Question | Impact |
|-----|----------|--------|
| CHK005 | `context_overrides` allowed keys/structure? | Implementer must decide schema — free-form vs. typed |
| CHK028 | Merge strategy for session context + conversation overrides? | Deep merge vs. shallow override affects behavior |
| CHK046 | Inheritance timing — snapshot at creation or live read? | Major behavioral difference for context updates |
| CHK048 | Conflict resolution when conversation overrides same key as session? | Silently override? Error? |
| CHK050 | `focused_symbols` — additive to session symbols or replacement? | Array merge semantics |

- **Location**: checklists/implementation.md
- **Recommendation**: Resolve at least CHK028 (merge strategy) and CHK046 (inheritance timing) before implementation, as they fundamentally shape the ConversationService and ChatService implementations. The others can be decided during implementation if a "start simple" principle is applied.

### Observations (informational)

**O-1: T011 lacks a dedicated plan step**

T011 (update exceptions.py) is in the plan's Project Structure as "MODIFY" (added per W7 resolution), but there is no explicit "Step N.M — Update exceptions.py" in the plan's Implementation Phases section. The task was generated as a cross-cutting concern. This is fine but creates a minor traceability gap.

**O-2: SC-002 ("zero regression") is aspirational given the deliberate API break**

SC-002 says "All existing tests that pass before the refactor continue to pass after migration." But Decision §10.1 deliberately breaks the API — every test that calls `session_id` will fail until updated. SC-002 is really measuring "zero regression after test updates are complete" rather than "tests pass without modification." The analysis.md CHK062 flags this. Recommendation: clarify SC-002's language.

**O-3: W4 (governing doc staleness) is a real downstream risk**

`AGENT_MEMORY_TECHNICAL_DESIGN.md` and `LANGCHAIN_AGENT_ARCHITECTURE_AND_DESIGN.md` will contain stale `session_id` references after implementation. Analysis.md defers this to post-implementation. Acceptable, but a follow-up task should be created promptly to avoid developer confusion.

**O-4: `sessions` collection handling in migration is ambiguous**

Plan Step 1.6 (T007) specifies dropping `conversations` and `agent_checkpoints` collections. The `sessions` collection schema is also changing (status rename "open"→"active", new fields). T007 does not mention dropping/recreating `sessions`. If existing session records have `status: "open"` (current enum), they'll fail schema validation after the enum change to `"active"`. This is likely handled by the fact that it's dev data, but should be explicit.

**O-5: Analysis.md's self-assessment is thorough**

The two-round analysis caught and resolved 12 findings (C1, W1-W7, W-NEW-1–5). Only W4 (doc staleness) remains open and is appropriately deferred. The coverage matrix is 100% for FR→task mapping. This is high-quality self-analysis.

## Recommended Actions

- [ ] **Fix W-R1**: Resolve parallel-group 3 dependency by making T011 sequential before the group, or documenting the cross-file dependency for implementers
- [ ] **Fix W-R2**: Add explicit task(s) for the 4 unlisted test files with `session_id` references (especially `test_chat_routes_memory.py`)
- [ ] **Consider W-R3**: Relax T012's dependency to allow parallel execution with T009/T010/T011
- [ ] **Consider W-R4**: Split T009 (10 sub-items) into rename + new methods tasks
- [ ] **Fix W-R5**: Reword T010 sub-item 3 from "rename" to "add"
- [ ] **Resolve W-R6**: Decide CHK028 (merge strategy) and CHK046 (inheritance timing) before implementation begins
- [ ] **Clarify O-2**: Update SC-002 language to say "after all test updates are complete"
- [ ] **Clarify O-4**: State explicitly whether `sessions` collection is dropped+recreated or migrated in-place in T007

---

## Re-Run Addendum (2026-03-18)

Requested remediation set was applied across spec/plan/tasks/checklists and re-reviewed.

### Requested Items Status

- W-R1: **RESOLVED** — T011 is now sequential prerequisite before parallel-group 3.
- W-R2: **RESOLVED** — explicit tasks added for previously unscoped test files (T027-T030).
- W-R3: **RESOLVED** — T012 moved into parallel-group 3 (dependency relaxed).
- W-R4: **RESOLVED (requested scope)** — T009 split into smaller units via T026 and T032.
- W-R5: **RESOLVED** — T010 wording corrected to "add conversation_id" for `process_query_structured()`.
- W-R6: **RESOLVED** — merge and inheritance timing decisions defined and recorded (CHK028/046/048/050 marked resolved).
- O-2: **RESOLVED** — SC-002 clarified to post-test-update behavioral regression target.
- O-4: **RESOLVED** — migration now explicitly includes sessions drop/recreate in plan + T007.

### Final Re-Run Verdict

**READY WITH WARNINGS**

Remaining warnings are non-blocking precision/documentation gaps (detailed open checklist items), not contradictions in the core design artifacts.

---

## Post-Implementation Verification (Phase 9)

**Date**: 2026-03-19  
**Iteration**: 2 (re-verification after E1-E5 remediation + F1 fix)

### Previous Findings Resolution

| ID | Finding | Severity | Status |
|----|---------|----------|--------|
| E1 | close_session cascading archive to children | HIGH | **RESOLVED** — cascade only on `target_status == "archived"` |
| E2 | active→archived skip allowed | HIGH | **RESOLVED** — `_VALID_TRANSITIONS["active"] = {"closed"}` only |
| E3 | archive_reason was "session_closed" | MEDIUM | **RESOLVED** — uses `"session_archived"` |
| E4 | `_load_conversation_context` absent in ChatService | MEDIUM | **RESOLVED** — method added with session→conversation merge |
| E5 | No workspace validation in create_session | MEDIUM | **RESOLVED** — `workspace_repository.get_by_id()` validation added |
| — | `self._now()` AttributeError | BUG | **RESOLVED** — replaced with `datetime.now(timezone.utc)` |
| F1 | `"session_archived"` missing from schema enum | MEDIUM | **RESOLVED** — added to conversations_schema.py |

### Remaining Findings (LOW — deferred)

| ID | Finding | Severity | Notes |
|----|---------|----------|-------|
| F2 | `archive_by_session_id()` default param stale (`"session_closed"`) | LOW | Harmless — caller always passes explicit value |
| F3 | Test file named `test_session_service_lifecycle.py` vs task ref | LOW | Intentional — name better reflects content |
| F4 | Session CRUD unit tests (get/list/context) not covered | LOW | Tested indirectly; can add post-merge |

### Metrics

| Metric | Value |
|--------|-------|
| Tasks completed | 32 / 32 (100%) |
| Requirement coverage | 17 / 17 active FRs |
| Files verified | 27 source + test files |
| Previous findings resolved | 7 / 7 |
| Remaining findings | 3 LOW (non-blocking) |

### Verdict

**PASS** — All CRITICAL, HIGH, and MEDIUM issues resolved. Ready for Phase 10 (Tests).
