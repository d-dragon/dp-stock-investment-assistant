---

description: "Task list for Prompt Compiler Path — Milestone M2 (Route-Aware Skills)"
---

# Tasks: Prompt Compiler Path — Milestone M2 (Route-Aware Skills)

**Input**: Design documents from `specs/prompt-system-milestone2/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included — plan targets 15+ PromptAssembler tests, 5+ manifest tests, 3+ regression tests.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- Backend Python: `src/`, `tests/` at repository root
- Single project repository

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create directory structure and update configuration shared across all user stories

- [X] T001 Create `src/prompts/skills/routes/` directory for route-skill prompt assets
- [X] T002 Add `prompts.route_contexts.*` configuration block to `config/config.yaml` with `enabled`, `directory`, `supported_routes`, and `dynamic_controls.allowed_fields`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data types and manifest extension that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 [P] Add `CompiledPrompt` frozen dataclass to `src/core/prompt_types.py` with fields: `compiled_text`, `segment_manifest`, `prompt_version`, `prompt_variant`, `trace_metadata`
- [X] T004 [P] Add `SegmentType` enum to `src/core/prompt_types.py` with 7 members: `SHARED_POLICY`, `ROLE_PROMPT`, `ROUTE_SKILL`, `MEMORY_CONTEXT`, `EVIDENCE`, `TASK_FRAMING`, `OUTPUT_CONTRACT`
- [X] T005 [P] Add `SegmentEntry` frozen dataclass to `src/core/prompt_types.py` with fields: `type: SegmentType`, `source_path: str`, `authority_level: int`
- [X] T006 Extend `PromptAssetLoader._build_manifest()` in `src/core/prompt_asset_loader.py` to scan `skills/routes/` subdirectory as a fourth scan path alongside `system/`, `skills/`, `experiments/`
- [X] T007 Add `route_scope` frontmatter validation in `PromptAssetLoader._parse_asset_file()` (`src/core/prompt_asset_loader.py`): verify `route_scope` values against `StockQueryRoute.__members__`, skip invalid values with WARN-level logging
- [X] T008 Add `route_scope` field to `PromptAsset` frontmatter parsing in `PromptAssetLoader._parse_asset_file()` (`src/core/prompt_asset_loader.py`) — parse list, default to empty list if missing

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel

---

## Phase 3: User Story 1 — Route-Context Prompt Assets for All 8 Route Categories (Priority: P1) 🎯 MVP

**Goal**: Create 8 frontmatter-annotated route-skill prompt assets under `src/prompts/skills/routes/` and verify the manifest builder discovers them keyed by `(agent_role, route_scope)`.

**Independent Test**: Create a route-skill asset for `PRICE_CHECK` — verify manifest builder includes it under correct `agent_role` and `route_scope`. Create all 8 — verify manifest contains 8 entries. Create one with invalid frontmatter — verify WARN + skip. This can be tested solely through `PromptAssetLoader` unit tests without any agent dependency.

**SRS mapping**: FR-1.4.7 (Route-Specific Prompt Context)

### Implementation for User Story 1

- [X] T009 [P] [US1] Create `src/prompts/skills/routes/price_check.md` with frontmatter (`name`, `version`, `agent_role: react_analyst`, `route_scope: ["PRICE_CHECK"]`, `status: active`, `variant: baseline`) and route-specific behavioral content
- [X] T010 [P] [US1] Create `src/prompts/skills/routes/news_analysis.md` with frontmatter (`route_scope: ["NEWS_ANALYSIS"]`) and route-specific behavioral content
- [X] T011 [P] [US1] Create `src/prompts/skills/routes/portfolio.md` with frontmatter (`route_scope: ["PORTFOLIO"]`) and route-specific behavioral content
- [X] T012 [P] [US1] Create `src/prompts/skills/routes/technical_analysis.md` with frontmatter (`route_scope: ["TECHNICAL_ANALYSIS"]`) and route-specific behavioral content
- [X] T013 [P] [US1] Create `src/prompts/skills/routes/fundamentals.md` with frontmatter (`route_scope: ["FUNDAMENTALS"]`) and route-specific behavioral content
- [X] T014 [P] [US1] Create `src/prompts/skills/routes/ideas.md` with frontmatter (`route_scope: ["IDEAS"]`) and route-specific behavioral content
- [X] T015 [P] [US1] Create `src/prompts/skills/routes/market_watch.md` with frontmatter (`route_scope: ["MARKET_WATCH"]`) and route-specific behavioral content
- [X] T016 [P] [US1] Create `src/prompts/skills/routes/general_chat.md` with frontmatter (`route_scope: ["GENERAL_CHAT"]`) and route-specific behavioral content

### Tests for User Story 1

- [X] T017 [P] [US1] Add route-skill manifest test to `tests/test_prompt_asset_loader.py`: verify `_build_manifest()` discovers route-skill assets under `skills/routes/` and keys them by `(agent_role, route_scope)`
- [X] T018 [P] [US1] Add route-skill validation test to `tests/test_prompt_asset_loader.py`: verify invalid `route_scope` value (e.g. `["INVALID_ROUTE"]`) logs WARN and skips the file
- [X] T019 [P] [US1] Add route-skill missing-directory test to `tests/test_prompt_asset_loader.py`: verify missing `skills/routes/` directory is silently skipped (no error, consistent with M1 `experiments/` behavior)
- [X] T020 [P] [US1] Add route-skill full-manifest test to `tests/test_prompt_asset_loader.py`: verify all 8 route-skill assets are discoverable and the manifest contains 8 entries across correct route scopes

---

## Phase 4: User Story 2 — PromptAssembler with Route-Aware Composition (Priority: P1)

**Goal**: Implement `PromptAssembler` that composes a deterministic `CompiledPrompt` from `PromptSelection`, route result, and runtime context. Wire into agent invocation path when `route_contexts.enabled: true`. Handle missing-skill degradation, dynamic controls rejection, and metadata emission.

**Independent Test**: (1) Configure agent with a `PRICE_CHECK` route skill — verify compiled prompt contains shared policy + role prompt + route skill (via metadata). (2) Configure with 5 of 8 route skills — verify missing route produces `missing_route_skills` in metadata and coherent response. (3) Test with and without route skills — verify metadata includes `route` and `route_skill_used`.

**SRS mapping**: FR-1.4.7, FR-1.4.11, FR-1.4.16, NFR-5.2.8, AC-8.5, AC-8.8, AC-8.11

**Depends on**: Phase 2 (data types + manifest extension), US1 (route-skill assets for route content resolution)

### Tests for User Story 2

- [X] T021 [P] [US2] Add PromptAssembler assembly-order test to `tests/test_prompt_assembler.py`: verify `compile()` produces all 7 segments in correct order per TECHNICAL_DESIGN.md §3.5.2.3
- [X] T022 [P] [US2] Add PromptAssembler missing-skill degradation test to `tests/test_prompt_assembler.py`: verify missing route skill produces `missing_route_skills` in `trace_metadata` and `compiled_text` contains only shared policy + role prompt
- [X] T023 [P] [US2] Add PromptAssembler all-skills-missing test to `tests/test_prompt_assembler.py`: verify `route_contexts.enabled: true` with zero route-skill assets degrades gracefully (same as M1 baseline)
- [X] T024 [P] [US2] Add PromptAssembler dynamic-controls-rejection test to `tests/test_prompt_assembler.py`: verify unknown dynamic control fields are dropped, recorded in `dropped_dynamic_fields`, and not elevated into `compiled_text`
- [X] T025 [P] [US2] Add PromptAssembler segment-classification test to `tests/test_prompt_assembler.py`: verify `segment_manifest` entries have correct `SegmentType`, `source_path`, and `authority_level` values
- [X] T026 [P] [US2] Add PromptAssembler performance benchmark test to `tests/test_prompt_assembler.py`: verify `compile()` completes in <50ms for a typical input (decorated with `@pytest.mark.performance`)

### Implementation for User Story 2

- [X] T027 [US2] Implement `PromptAssembler` class in `src/core/prompt_assembler.py` with `compile(selection: PromptSelection, route: StockQueryRoute, runtime_context: Optional[Dict] = None) -> CompiledPrompt` — deterministic assembly order per TECHNICAL_DESIGN.md §3.5.2.3 with `\n---\n` segment delimiters
- [X] T028 [US2] Implement route-skill resolution inside `PromptAssembler.compile()`: look up route skill from the manifest using `selection` + `route`, handle missing skill gracefully (skip segment, record gap in `trace_metadata.missing_route_skills`, set `route_skill_used: false`)
- [X] T029 [US2] Implement dynamic controls allowlist in `PromptAssembler`: validate `runtime_context` fields against `config["prompts"]["dynamic_controls"]["allowed_fields"]`, drop unrecognized fields, record in `trace_metadata.dropped_dynamic_fields`
- [X] T030 [US2] Implement `SegmentType` classification in `PromptAssembler`: classify each segment as `SHARED_POLICY`, `ROLE_PROMPT`, `ROUTE_SKILL`, `MEMORY_CONTEXT`, `EVIDENCE`, `TASK_FRAMING`, or `OUTPUT_CONTRACT` — produce `segment_manifest` in `CompiledPrompt` output
- [X] T031 [US2] Implement `SegmentEntry` authority levels: `SHARED_POLICY`=1, `ROLE_PROMPT`=2, `ROUTE_SKILL`=3, `MEMORY_CONTEXT`=4, `EVIDENCE`=5, `TASK_FRAMING`=6, `OUTPUT_CONTRACT`=7
- [X] T032 [US2] Wire `PromptAssembler` into `StockAssistantAgent` (`src/core/stock_assistant_agent.py`): add `prompt_assembler` parameter to `__init__`, integrate into `_load_system_prompt()` when `route_contexts.enabled: true`
- [X] T033 [US2] Add route context emit to agent response metadata and LangSmith trace tags: `route`, `route_skill_used`, `selected_skills`, `prompt_selection_mode` in `StockAssistantAgent._inject_prompt_metadata()` (`src/core/stock_assistant_agent.py`)
- [X] T034 [P] [US2] Update `APIRouteContext` in `src/web/routes/shared_context.py` if route context config needs to be available to routes

### Integration Tests for User Story 2

- [X] T035 [US2] Add agent route-aware integration test to `tests/test_agent_regression.py`: verify agent with `route_contexts.enabled: true` and `PRICE_CHECK` route skill emits correct metadata (`route`, `route_skill_used: true`)
- [X] T036 [US2] Add agent route-aware degraded test to `tests/test_agent_regression.py`: verify agent with `route_contexts.enabled: true` but missing route skills still produces coherent response with `route_skill_used: false`
- [X] T037 [US2] Add agent route-aware disabled test to `tests/test_agent_regression.py`: verify agent with `route_contexts.enabled: false` preserves M1 behavior unchanged
- [X] T038 [US2] Add agent authority-separation test to `tests/test_agent_regression.py`: inject route-skill content containing counter-policy safety instructions — verify agent refusal posture is unchanged and shared policy remains authoritative per FR-1.4.11 (maps to SC-M2-04)

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Verification, documentation sync, and traceability updates

### Verification

- [X] T039 Run full test suite (`pytest -v --tb=short`) — verify all M1 tests (29) plus all M2 tests pass with zero failures
- [X] T040 Run config validation — verify `config/config.yaml` loads correctly with new `prompts.route_contexts.*` section using `python -c "from utils.config_loader import ConfigLoader; ConfigLoader.load_config()"`

### Long-Lived Document Sync

- [X] T041 Update `docs/domains/agent/TECHNICAL_DESIGN.md` §3.5.2 — mark `PromptAssembler` as implemented (M2), update M2+ note to clarify PromptAssembler delivered, ResponseGuardrailMiddleware deferred to M3
- [X] T042 Update `docs/domains/agent/ARCHITECTURE_DESIGN.md` §4.8.2 — update PromptAssembler status from "proposed for M2+" to "Implemented — M2", add spec reference to `specs/prompt-system-milestone2/spec.md`
- [X] T043 Update `docs/domains/agent/SRS_SPEC_TRACEABILITY.md` — update FR-1.4.7 from `clarified` to `implemented`, FR-1.4.11 from `clarified` to `implemented`, AC-8.5/AC-8.8/AC-8.11 from `unmapped` to `implemented`, add `specs/prompt-system-milestone2/spec.md` as linked spec for each

### Traceability Sync

- [X] T044 Update `specs/spec-traceability.yaml` — update M2 `mapping_status` from `planned` to `implemented`, add evidence paths (tasks.md, checklists, test files)
- [X] T045 Update `specs/spec-sync-status.md` — update M2 derived status from `planned` to `implemented`, add task completion count

---

## Dependency Graph

```
Phase 1 (Setup)
  └─ T001 (create routes dir)
  └─ T002 (config update)
        │
Phase 2 (Foundational)
  ├─ T003 (CompiledPrompt)
  ├─ T004 (SegmentType enum)
  ├─ T005 (SegmentEntry)
  ├─ T006 (manifest scan extension) ────┐
  ├─ T007 (route_scope validation) ─────┤
  └─ T008 (route_scope parsing) ────────┤
        │                               │
Phase 3: US1 ───────────────────────────┤
  ├─ T009-T016 (8 route-skill assets) ──┤
  └─ T017-T020 (US1 tests) ─────────────┘
        │
Phase 4: US2
  ├─ T021-T026 (US2 tests: run after T027-T031 are coded)
  ├─ T027-T031 (PromptAssembler core)
  ├─ T032 (agent wiring: depends on T027 + M1 agent)
  ├─ T033 (metadata emit: depends on T032)
  └─ T035-T038 (agent integration tests: depend on T032)
        │
Phase 5 (Polish)
  ├─ T039-T040 (verification)
  ├─ T041-T043 (doc sync)
  └─ T044-T045 (traceability sync)
```

## Parallel Execution Opportunities

| Parallel Group | Tasks | Condition |
|----------------|-------|-----------|
| P-group A | T003, T004, T005 | All independent — different dataclasses/enums in same file |
| P-group B | T009-T016 | All independent — each route-skill asset is a separate file |
| P-group C | T017-T020 | All independent — distinct test cases in same test file |
| P-group C | T021-T026 | All independent — distinct test cases in same test file |
| P-group D | T040, T041, T042 | All independent — different long-lived docs |
| P-group E | T043, T044 | Independent YAML/markdown updates |

## Implementation Strategy

1. **MVP** (Minimum Phase 3): Create 3 route-skill assets (PRICE_CHECK, NEWS_ANALYSIS, GENERAL_CHAT) to validate the manifest extension and route_scope validation work. Remaining 5 assets can follow once pattern is proven.
2. **Core PromptAssembler** (Phase 4): Implement `compile()` with shared policy → role prompt → route skill assembly first. Add memory context, evidence, task framing, output contract as subsequent segments. Missing-skill degradation is built-in from the start.
3. **Agent wiring** (T032-T033): Do last — depends on PromptAssembler being complete and tested in isolation.
4. **Doc sync** (Phase 5): Batch all sync tasks together after all tests pass.
