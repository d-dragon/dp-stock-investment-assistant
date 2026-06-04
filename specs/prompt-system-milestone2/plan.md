# Implementation Plan: Prompt Compiler Path — Milestone M2 (Route-Aware Skills)

**Branch**: `prompt-system-milestone2` | **Date**: 2026-06-04 | **Spec**: `specs/prompt-system-milestone2/spec.md`

**Input**: Feature specification from `specs/prompt-system-milestone2/spec.md` — backlog items PS-07 (Route-Context Prompt Assets) and PS-08 (PromptAssembler + Route-Aware Composition).

**Prerequisite check**: M1 (Prompt Runtime Parity) is complete — `PromptAssetLoader` with 8-field `SelectionTuple`, externalized `react_analyst.md` asset, `prompts.*` config surface, response metadata. Verified per `specs/prompt-system-milestone1/review.md`.

## Summary

Implement route-aware prompt composition along the planned prompt compiler path (`PromptAssetLoader → PromptAssembler → [M3: ResponseGuardrailMiddleware]`). Two backlog items:

- **PS-07** (P1, FR-1.4.7): Extend `PromptAssetLoader._build_manifest()` to scan `skills/routes/` and author 8 frontmatter-annotated route-skill markdown assets (one per `StockQueryRoute` category). Route-skill assets are keyed in the manifest by `(agent_role, route_scope)`. Invalid `route_scope` values are skipped with WARN-level logging. Missing `skills/routes/` directory is silently ignored.

- **PS-08** (P1, FR-1.4.7, FR-1.4.11, FR-1.4.16, NFR-5.2.8): Implement `PromptAssembler` that consumes `PromptSelection` (from M1's `PromptAssetLoader`) and a normalized route result, composes one `CompiledPrompt` with deterministic assembly order (per TECHNICAL_DESIGN.md §3.5.2.3: shared policy → always-active skills → route-specific skill → bounded memory context → evidence → task framing → output contract), handles missing-skill degradation with trace metadata, and wires into the agent invocation path when `route_contexts.enabled: true`.

**Gate**: Do not enable experiment modes until route-aware composition is stable and traceable.

## Technical Context

**Language/Version**: Python 3.13+ (matching project baseline)

**Primary Dependencies**:
- `langchain-core>=0.3.28` — base prompt templates (for `@dynamic_prompt` or standalone composition)
- `yaml` (PyYAML) — frontmatter parsing (already used by M1)
- `pathlib` — file system scanning (already used by M1)
- Existing M1 infrastructure: `PromptAssetLoader` (`src/core/prompt_asset_loader.py`), `PromptAsset`/`PromptSelection`/`SelectionTuple` (`src/core/prompt_types.py`)

**Storage**: Filesystem only — prompt assets under `src/prompts/skills/routes/`. Manifest is in-memory with TTL-based refresh (existing `refresh_window_seconds` in config). No database or cache changes.

**Testing**: pytest (existing harness with `conftest.py`, `pytest.ini`, `pytest-mock`). Tests follow M1 patterns: `MagicMock` for external deps, `tmp_path` for prompt asset filesystem fixtures, `mocker.patch` for `CacheBackend` and M1 prompt loader. Target: 15+ tests for PromptAssembler, 5+ extended manifest tests, 3+ agent regression tests.

**Target Platform**: Linux containers (API server), Windows dev (local). Python runtime.

**Project Type**: Backend agent extension — new components added to `src/core/`, existing components extended in `src/web/`.

**Performance Goals**:
- Prompt assembly: <50ms per request (deterministic in-memory composition — segment ordering is a series of string concatenations)
- Route-skill manifest lookup: <5ms (in-memory dict lookup after manifest build)

**Constraints**:
- Must NOT weaken shared safety policy (FR-1.4.11 — route skills can narrow task framing only)
- Must NOT reclassify routes — `PromptAssembler` admits the router result as-is
- Must NOT synthesize substitute instructions for missing route skills
- Must preserve M1 behavior when `route_contexts.enabled: false`
- Manifest builder must silently skip missing `skills/routes/` directory (consistent with M1 behavior for `experiments/`)
- Invalid or unknown `route_scope` values in frontmatter must be skipped with WARN-level logging (validated against canonical 8-route set from `StockQueryRoute` enum)
- Dynamic control fields must be validated against an approved allowlist; unrecognized fields dropped and traced

**Scale/Scope**: 8 route-skill markdown assets, 1 new component (`PromptAssembler`), 1 new frozen dataclass (`CompiledPrompt`), 1 config extension (`prompts.route_contexts.*`), 1 agent integration point.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [X] **Governing artifacts identified**: SRS (FR-1.4.7, FR-1.4.11, FR-1.4.16, NFR-5.2.8, AC-8.5, AC-8.8, AC-8.11), `ARCHITECTURE_DESIGN.md` §4.8.2, `TECHNICAL_DESIGN.md` §3.5.2.3/§3.5.4, `PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md` §Milestone Gates, ADR-AGENT-002 (Skills pattern), ADR-AGENT-003 (Externalized assets)
- [X] **Artifact ownership confirmed**: delivery-scoped work in `specs/prompt-system-milestone2/`, long-lived doc syncs in `docs/domains/agent/`
- [X] **Required sync targets listed**: `TECHNICAL_DESIGN.md` §3.5.2, `ARCHITECTURE_DESIGN.md` §4.8.2, `SRS_SPEC_TRACEABILITY.md`, `spec-traceability.yaml`, `spec-sync-status.md`, `config/config.yaml`, `docs/openapi.yaml` (if metadata shapes change)
- [X] **Affected architecture layers**: Agent (PromptAssembler, route-skill assets), Backend (config surface). No infrastructure, frontend, or data layer changes.
- [X] **Validation strategy**: pytest unit tests for `PromptAssembler` (assembly order, missing-skill degradation, dynamic controls rejection, segment classification), extended `PromptAssetLoader` manifest tests for `skills/routes/` scanning, agent regression tests for route-aware composition integration.
- [X] **No backward-incompatible changes**: M2 is additive — M1 behavior preserved when `route_contexts.enabled: false`. Config addition is optional (new section under existing `prompts.*` namespace).

## Project Structure

### Documentation (this feature)

```text
specs/prompt-system-milestone2/
├── spec.md                  # Feature specification
├── plan.md                  # This file (/speckit.plan command output)
├── research.md              # Phase 0 output
├── data-model.md            # Phase 1 output
├── quickstart.md            # Phase 1 output
├── contracts/               # Phase 1 output
├── checklists/
│   └── requirements.md      # Quality gate checklist
└── tasks.md                 # Task breakdown (/speckit.tasks command)
```

### Source Code — Files to Create

```text
src/prompts/skills/routes/           # NEW — route-skill asset directory (subdir under existing skills/)
├── price_check.md                   # NEW — PRICE_CHECK route skill
├── news_analysis.md                 # NEW — NEWS_ANALYSIS route skill
├── portfolio.md                     # NEW — PORTFOLIO route skill
├── technical_analysis.md            # NEW — TECHNICAL_ANALYSIS route skill
├── fundamentals.md                  # NEW — FUNDAMENTALS route skill
├── ideas.md                         # NEW — IDEAS route skill
├── market_watch.md                  # NEW — MARKET_WATCH route skill
└── general_chat.md                  # NEW — GENERAL_CHAT route skill

src/core/
└── prompt_assembler.py              # NEW — PromptAssembler class

tests/
└── test_prompt_assembler.py         # NEW — PromptAssembler unit tests
```

### Source Code — Files to Modify

```text
src/core/
├── prompt_types.py                  # MODIFY — add CompiledPrompt (frozen dataclass), SegmentType enum, SegmentEntry
├── prompt_asset_loader.py           # MODIFY — extend _build_manifest() to scan skills/routes/, add route_scope frontmatter validation
└── stock_assistant_agent.py         # MODIFY — wire PromptAssembler in _load_system_prompt() when route_contexts.enabled: true

config/config.yaml                   # MODIFY — add prompts.route_contexts.* and prompts.dynamic_controls.* blocks

src/web/
├── api_server.py                    # MODIFY — pass route result to agent for PromptAssembler integration
└── routes/shared_context.py         # MODIFY — add route_contexts config reference (if needed)

tests/
├── test_prompt_asset_loader.py      # MODIFY — add route-skill manifest scanning tests (4 new tests for T017-T020)
├── test_agent_regression.py         # MODIFY — add route-aware agent tests (4 new tests for T035-T038)
└── conftest.py                      # MODIFY — add PromptAssembler test fixtures for all M2 test files
```

## Complexity Tracking

No constitution violations — M2 is additive, follows established M1 patterns (same frontmatter conventions, same manifest caching, same WARN-level fallback logging), and does not introduce backward-incompatible changes or cross-boundary complexity. All existing tests remain green.

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [ ] Governing artifacts identified: relevant SRS items, architecture or technical design,
  ADRs, contracts, runbooks, or existing feature specs.
- [ ] Artifact ownership confirmed: long-lived updates belong in `docs/`, delivery-scoped work
  belongs in `specs/`, and Spec Kit runtime or tooling changes belong in `.specify/`.
- [ ] Required sync targets listed up front: `docs/openapi.yaml`,
  `specs/spec-traceability.yaml`, `specs/spec-sync-status.md`, affected reverse-trace docs,
  technical design docs, and runbooks as applicable.
- [ ] Affected architecture layers, dependency seams, and migration or rollback implications are
  documented.
- [ ] Validation strategy is defined with executable evidence where possible: tests,
  diagnostics, type or lint checks, health checks, trace metadata, or migration verification.
- [ ] Any necessary complexity or backward-incompatible change is explicitly justified.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
