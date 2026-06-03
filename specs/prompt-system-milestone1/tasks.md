# Tasks: Prompt Compiler Path — Milestone M1 (Prompt Runtime Parity)

**Feature**: `specs/prompt-system-milestone1`
**Branch**: `enhance-agent-prompt-system-followup`
**Date**: 2026-06-03

**Inputs**: [spec.md](./spec.md), [plan.md](./plan.md), [checklists/spec-plan-quality.md](./checklists/spec-plan-quality.md)

**Dependencies**: Python 3.8+, PyYAML (existing transitive), `langchain_core` >=0.3.28, `langsmith` (existing). No new third-party packages.

**Tests**: Follow `tests/conftest.py` fixtures and pytest patterns per `.github/instructions/testing.instructions.md`. Use `MagicMock` for dependency isolation; use Flask test client for API-level integration tests. Test run command: `& .\.venv\Scripts\python.exe -m pytest tests/test_prompt_*.py tests/test_agent_regression.py -v`

---

## Phase 1: Foundation — Shared Types & Directory Structure

**Purpose**: Create the shared dataclasses and directory structure that ALL user stories depend on.

**⚠️ BLOCKING**: No user story can begin until this phase is complete.

- [X] T001 [P] Create `src/prompts/system/` and `src/prompts/skills/` and `src/prompts/experiments/` directory structure per ADR taxonomy (ARCHITECTURE_DESIGN.md §4.5.1.1)
- [X] T002 Define `PromptAsset` dataclass in `src/core/prompt_types.py` with fields: `name`, `version`, `agent_role`, `status`, `locale`, `parity_group`, `variant`, `content` (str), `file_path` (pathlib.Path), `frontmatter` (dict). Use `@dataclass(frozen=True)` per project immutable configuration pattern.
- [X] T003 Define `PromptSelection` dataclass in `src/core/prompt_types.py` with fields: `selected_assets` (List[str]), `prompt_version` (str), `prompt_variant` (str), `selection_mode` (str), `fallback_used` (bool), `degraded_reason` (Optional[str]), `trace_metadata` (dict). Use `@dataclass(frozen=True)`.
- [X] T004 Define `SelectionTuple` typed dict or dataclass in `src/core/prompt_types.py` with all 8 fields per TECHNICAL_DESIGN.md §3.5.2.2: `agent_role` (str), `route` (str, default `"general_chat"`), `locale` (str, default `"en"`), `selection_mode` (str, default `"fixed"`), `requested_version` (Optional[str]), `prompt_experiment_id` (Optional[str]), `workspace_mode` (str, default `"default"`), `env` (str, default `"production"`)

**Checkpoint**: Foundation ready — `src/core/prompt_types.py` exists with all 3 types. All user stories can import from this module.

---

## Phase 2: User Story 1 — Externalize and Version the ReAct Baseline Prompt (P1)

**Goal**: Extract the hardcoded `REACT_SYSTEM_PROMPT` from `stock_assistant_agent.py` into a versioned, frontmatter-annotated markdown asset. The asset uses version-in-frontmatter per ADR taxonomy (ARCHITECTURE_DESIGN.md §4.5.1.1), not version-in-path.

**Independent Test**: (1) Delete the prompt asset, restart — agent falls back to inline constant (safety net before PS-04). (2) Restore asset, run 5-query seed set (`PRICE_CHECK`, `NEWS_ANALYSIS`, `FUNDAMENTALS`, `TECHNICAL_ANALYSIS`, `GENERAL_CHAT`), capture response metadata. (3) Remove `REACT_SYSTEM_PROMPT` from code, restart with only externalized asset, re-run 5 queries. Compare: no structural regression (same section structure, same tool-call pattern, no new safety failures).

### Tests for User Story 1

- [X] T005 [P] [US1] Write regression test fixture in `tests/test_agent_regression.py` that defines the 5-query seed set with expected route classifications and captures raw response content + metadata. Use `pytest.fixture` pattern per testing.instructions.md.
- [X] T006 [P] [US1] Write behavioral parity test in `tests/test_agent_regression.py` — `test_externalized_prompt_behavioral_parity` — that runs the 5-query seed set against the inline `REACT_SYSTEM_PROMPT` baseline, captures response patterns (section structure, tool-call count, safety markers), then runs the same queries against the externalized asset and asserts no structural regression. Mark with `@pytest.mark.slow` for CI segregation.

### Implementation for User Story 1

- [X] T007 [P] [US1] Create `src/prompts/system/react_analyst.md` with frontmatter containing `name: react_analyst_v1`, `version: 1.0.0`, `agent_role: react_analyst`, `status: active`, `variant: baseline`, `locale: en`. Copy the exact content of `StockAssistantAgent.REACT_SYSTEM_PROMPT` verbatim between `---` frontmatter delimiters. No behavioral changes. **Edge case**: version MUST be in frontmatter metadata only (not in directory path or filename per ADR taxonomy). The roadmap's `v1.md` path is superseded — verify no `v1/` directory or `react_analyst_v1.md` filename is created.
- [X] T008 [US1] Add a `prompt_asset_loader` import placeholder in `stock_assistant_agent.py` and add a `_load_system_prompt()` method that reads `src/prompts/system/react_analyst.md` via `pathlib.Path.read_text()`, parses frontmatter with `yaml.safe_load()`, and returns the content body. Keep `REACT_SYSTEM_PROMPT` as fallback when the file is missing (pre-PS-04 safety net). Log INFO with prompt identity on successful load.
  **Note**: This is an intermediate step. Phase 4 (T019) replaces `_load_system_prompt()` with `PromptAssetLoader.resolve()`. The direct file-read approach here provides a safe transition path during M1 observation window per additive evolution principle (Constitution Rule 8).
- [X] T009 [US1] Wire `_load_system_prompt()` into the `create_agent()` call site in `stock_assistant_agent.py` so the agent uses the file content when available and falls back to `REACT_SYSTEM_PROMPT` when not. Add a deprecation comment on `REACT_SYSTEM_PROMPT`: `# DEPRECATED: retained as fallback alias during M1 observation window; remove after PS-04 verification`.

**Checkpoint**: US1 complete — prompt asset exists, agent reads from file with inline fallback. 5-query seed set passes with no structural regression.

---

## Phase 3: User Story 2 — PromptAssetLoader with Fallback Safety (P2)

**Goal**: Implement `PromptAssetLoader` that accepts the full 8-field selection tuple (TECHNICAL_DESIGN.md §3.5.2.2), resolves against a manifest derived from asset directory scanning, and falls back to baseline lineage on failure. At M1 scope, `route`, `locale`, `prompt_experiment_id`, `workspace_mode`, and `env` accept documented defaults; `agent_role`, `requested_version`, and `selection_mode` are the active discriminators.

**Independent Test**: (1) Set `requested_version` to `"2.0.0"` when only `1.0.0` exists — loader returns `1.0.0` baseline with `fallback_used=True`, WARN logged. (2) Feed malformed frontmatter file — loader rejects, falls back to baseline, WARN logged. (3) Remove all assets — loader raises unresolvable-prompt startup error.

### Tests for User Story 2

- [X] T010 [P] [US2] Write unit tests in `tests/test_prompt_asset_loader.py` for `PromptAssetLoader.resolve()` — `test_loader_resolves_exact_version` (happy path), `test_loader_falls_back_on_version_mismatch` (AC-8.2 compliance), `test_loader_falls_back_on_malformed_frontmatter` (FR-1.4.8 compliance), `test_loader_raises_on_baseline_exhaustion`. Use `MagicMock` for file-system isolation. Use `tmp_path` fixture for temp asset files.
- [X] T011 [P] [US2] Write cache behavior test in `tests/test_prompt_asset_loader.py` — `test_loader_caches_by_full_selection_tuple` — verifies that calling `resolve()` twice with the same 8-field tuple hits cache on the second call (mock file system access). Assert cache key contains all 8 fields.
- [X] T012 [P] [US2] Write frontmatter parsing tests in `tests/test_prompt_asset_loader.py` — `test_loader_parses_valid_frontmatter` (valid YAML `---` delimiters), `test_loader_rejects_missing_frontmatter_delimiters`, `test_loader_rejects_malformed_yaml` (unclosed key). Assert fallback + WARN log for invalid cases.

### Implementation for User Story 2

- [X] T013 [P] [US2] Implement `PromptAssetLoader` class in `src/core/prompt_asset_loader.py` with:
  - `__init__(self, prompt_root: pathlib.Path, config: dict, logger: Logger)` — stores root path, loads config, sets up logger
  - `_build_manifest(self) -> Dict[str, List[PromptAsset]]` — scans `prompt_root/system/`, `prompt_root/skills/`, `prompt_root/experiments/` for `.md` files, parses frontmatter, groups by `agent_role`. Missing subdirectories (`skills/`, `experiments/` at M1 scope) are silently skipped — no error raised. Use `pathlib.Path.iterdir()` or `glob()` with `.exists()` guard.
  - `resolve(self, selection: SelectionTuple) -> PromptSelection` — matches selection tuple against manifest, returns `PromptSelection` with `fallback_used=False` on success
  - `_resolve_fallback(self, agent_role: str, failed_version: str, failed_reason: str) -> PromptSelection` — resolves to baseline lineage, logs WARN with failed identity, returns `PromptSelection(fallback_used=True, degraded_reason=...)`
  - Use `yaml.safe_load()` for frontmatter parsing (PyYAML is existing transitive dependency)
- [X] T014 [US2] Implement baseline lineage resolution logic — `_find_baseline_lineage(self, agent_role: str) -> Optional[PromptAsset]` — finds the asset with `status: active` and highest version within that agent_role group. If no active asset found, returns None (triggers unresolvable-prompt error).
- [X] T015 [US2] Implement manifest caching — `_cached_manifest` with TTL from `prompts.registry.refresh_window_seconds` config (default: 300s). Cache key includes manifest version (derived from directory scan timestamp). On cache miss or expired TTL, re-scan and rebuild manifest.
- [X] T016 [US2] Wire `PromptAssetLoader` into `src/core/prompt_types.py` by exporting the class for cross-module imports. Update `prompt_types.py` `__all__` if used.

**Checkpoint**: US2 complete — `PromptAssetLoader` resolves from 8-field tuple, falls back on failure with WARN log, caches parsed frontmatter. All unit tests pass.

---

## Phase 4: US1 Completion — Wire PromptAssetLoader into Agent (PS-04)

**Goal**: Replace `REACT_SYSTEM_PROMPT` as the primary prompt source with `PromptAssetLoader`-resolved content. `REACT_SYSTEM_PROMPT` constant is removed from the primary code path (retained as deprecated import alias during M1 observation window per spec §Edge Cases).

**⚠️ Depends on**: Phase 2 (US1 — prompt asset exists) AND Phase 3 (US2 — loader implemented)

### Tests for PS-04

- [X] T017 [P] Write integration test in `tests/test_prompt_asset_loader.py` — `test_agent_starts_with_loader` — mocks `PromptAssetLoader.resolve()` to return a known `PromptSelection`, creates `StockAssistantAgent` with loader, verifies agent uses loader content as system prompt. Use `MagicMock(spec=PromptAssetLoader)`.
- [X] T018 [P] Write startup-failure test in `tests/test_prompt_asset_loader.py` — `test_agent_startup_fails_on_unresolvable_prompt` — configures loader with missing asset directory, verifies `StockAssistantAgent.__init__` raises `RuntimeError` (or equivalent) with message containing "unresolvable prompt". **Edge case**: covers fallback chain exhaustion (spec §Edge Cases → PS-02/PS-03 fallback chain exhaustion) — when ALL baseline lineages fail to load, the system reports an unresolvable-prompt error rather than synthesizing prompt content.

### Implementation for PS-04

- [X] T019 [US1] Modify `stock_assistant_agent.py` `__init__` to accept an optional `prompt_asset_loader: Optional[PromptAssetLoader] = None` parameter. When provided, call `loader.resolve(SelectionTuple(agent_role="react_analyst", ...))` and use the resolved content as the system prompt. Default to current `REACT_SYSTEM_PROMPT` behavior when loader is None (backward compatibility during M1 window).
- [X] T020 [US1] Remove `REACT_SYSTEM_PROMPT` from the primary `create_agent()` call path. Replace with `self._current_prompt.content` where `_current_prompt` is the `PromptSelection` resolved during `__init__`. Add deprecation warning on first use of the `REACT_SYSTEM_PROMPT` alias.
- [X] T021 [US1] Add INFO-level logging in `stock_assistant_agent.py` `__init__` confirming loaded prompt identity — log `asset_id`, `prompt_version`, `prompt_variant`, `selection_mode`, and `fallback_used` from the resolved `PromptSelection`.

**Checkpoint**: PS-04 complete — agent uses `PromptAssetLoader` as primary prompt source. `REACT_SYSTEM_PROMPT` is deprecated alias. `_load_system_prompt()` from Phase 2 is replaced by loader path.

---

## Phase 5: User Story 3 — Prompts Config Surface and Activation Validation (P2)

**Goal**: Add `prompts.*` configuration namespace to `config/config.yaml` with two-layer validation: structural errors (invalid keys, unsupported modes) block startup; content-resolution errors (non-existent version) fall back with WARN. Per spec M1-FR-009a/M1-FR-009b.

**⚠️ Depends on**: Phase 4 (agent wired with loader)

**Independent Test**: (1) Set `prompts.selection_mode: "invalid_mode"` — startup fails with config error. (2) Set `prompts.system.active_version: "2.0.0"` — agent starts with `1.0.0` baseline, WARN logged. (3) Valid config — clean startup, agent uses configured prompt.

### Tests for User Story 3

- [X] T022 [P] [US3] Write structural validation tests in `tests/test_prompt_config.py` — `test_config_rejects_unsupported_selection_mode` (invalid mode blocks startup with clear error), `test_config_rejects_missing_required_fields` (missing `system.active_version` blocks startup), `test_config_accepts_valid_structure` (valid config passes structural validation). Use Flask test client for app-bootstrap-level tests per testing.instructions.md API route patterns.
- [X] T023 [P] [US3] Write content-resolution tests in `tests/test_prompt_config.py` — `test_config_content_resolution_falls_back_on_unknown_version` (non-existent version allows startup with WARN), `test_config_content_resolution_succeeds_on_valid_version` (existing version allows clean startup). Mock `PromptAssetLoader.resolve()` to control resolution outcomes.

### Implementation for User Story 3

- [X] T024 [P] [US3] Add `prompts.*` namespace to `config/config.yaml` with the following structure (per spec M1-FR-008 and TECHNICAL_DESIGN.md §3.5.8):
  ```yaml
  prompts:
    registry:
      directory: "src/prompts"
      refresh_window_seconds: 300
    system:
      active_role: "react_analyst"
      active_version: "1.0.0"
      variants:
        - name: "baseline"
          version: "1.0.0"
          file: "system/react_analyst.md"
          status: "active"
    selection_mode: "fixed"
    default_locale: "en"
    experiments:
      enabled: false
      active_id: null
  ```
- [X] T025 [US3] Implement config structural validation — add a function `validate_prompts_config(config: dict)` in a new module `src/core/prompt_config.py` (or inline in `prompt_asset_loader.py`). Check: `selection_mode` is one of `fixed`, `forced`, `shadow`, `weighted`; `system.active_role` is non-empty string; `system.active_version` is non-empty string; `registry.directory` exists. Raise `ConfigError` (or `ValueError`) with actionable message on failure. Wire this into the Flask app factory (`api_server.py`) or agent `__init__` startup sequence before any prompt resolution occurs.
- [X] T026 [US3] Wire the two-layer validation into `api_server.py` app factory — after config is loaded, call structural validation. If it fails, abort app creation with clear error. On success, create `PromptAssetLoader` from config and inject into `APIRouteContext` (add `prompt_asset_loader` field to `APIRouteContext`).

**Checkpoint**: US3 complete — config namespace exists, structural validation blocks startup on invalid config, content resolution falls back gracefully. All config tests pass.

---

## Phase 6: User Story 4 — Prompt Identity in Response and Trace Metadata (P2)

**Goal**: Every agent invocation emits `prompt_version`, `prompt_variant`, `prompt_selection_mode`, `fallback_used`, `model_provider`, and `model_name` in response metadata AND LangSmith trace spans. Dual-path design: response metadata always available; LangSmith trace degrades silently when unreachable (M1-NFR-004).

**⚠️ Depends on**: Phase 4 (agent with prompt identity from loader)

**Independent Test**: Send query via chat API, parse `response.metadata` — verify all 6 fields present and non-empty. Repeat for 3 queries with different route classifications. Verify same fields in LangSmith trace when connected.

### Tests for User Story 4

- [X] T027 [P] [US4] Write response metadata integration tests in `tests/test_prompt_metadata.py` — `test_response_metadata_includes_all_prompt_fields` — uses Flask test client to POST a chat message, parses `response.metadata`, asserts `prompt_version`, `prompt_variant`, `prompt_selection_mode`, `fallback_used`, `model_provider`, `model_name` are non-empty strings/booleans. Per spec AC-8.1.
- [X] T028 [P] [US4] Write LangSmith-independence test in `tests/test_prompt_metadata.py` — `test_response_metadata_populated_regardless_of_langsmith` — mocks `langsmith.Client` to raise `ConnectionError`, sends chat query, asserts response metadata still contains all 6 fields. Per M1-NFR-004.
- [X] T029 [P] [US4] Write metadata-with-fallback test in `tests/test_prompt_metadata.py` — `test_response_metadata_shows_fallback` — configures loader to use non-existent version (triggering fallback), sends query, asserts `response.metadata.fallback_used` is `True` and `degraded_reason` is non-empty. Per spec User Story 4 AC-3.
- [X] T030 [P] [US4] Write stateless-request metadata test in `tests/test_prompt_metadata.py` — `test_stateless_request_receives_metadata` — sends query without `conversation_id`, asserts metadata fields present. Per spec §Edge Cases → PS-05 metadata on stateless requests.

### Implementation for User Story 4

- [X] T031 [US4] Add `_inject_prompt_metadata()` method to `StockAssistantAgent` that reads the resolved `PromptSelection` and current model info, returns a dict with `prompt_version`, `prompt_variant`, `prompt_selection_mode`, `fallback_used`, `model_provider`, `model_name`. Call this at the end of `process_query()` / `process_query_streaming()` and merge into the response dict's `metadata` key.
- [X] T032 [US4] Add LangSmith trace tag injection — in the agent invocation path, after resolving the prompt, call `RunnableConfig(tags={...})` with `prompt_version`, `prompt_variant`, `prompt_selection_mode`, `agent_role`, `model_provider`, `model_name`. Wrap in try/except so LangSmith failures are silently caught (log at DEBUG level only). Per spec M1-FR-011.
- [X] T033 [US4] Ensure the metadata dict flows through the SSE/WebSocket streaming path — in `service_utils.py` `batched()` or the streaming generator in `ai_chat_routes.py`, append metadata as a final JSON object field named `"metadata"` containing `prompt_version`, `prompt_variant`, `prompt_selection_mode`, `fallback_used`, `model_provider`, `model_name`. The metadata field is additive and does not change the REST response schema (OpenAPI contract unchanged per spec Out-of-Scope). Verify metadata is present in both REST JSON response and SSE streaming terminal frame.

**Checkpoint**: US4 complete — response metadata always populated, LangSmith traces tagged when available, fallback indicators work. All metadata tests pass.

---

## Phase 7: Polish, Regression & Long-Lived Doc Synchronization

**Purpose**: Cross-cutting concerns that affect the entire feature — regression validation, document sync, traceability refresh, and cleanup.

- [X] T034 [P] Update `docs/domains/agent/TECHNICAL_DESIGN.md` §3.5 (Prompt Realization and Guardrails) — promote M1 implementation details: mark `PromptAssetLoader` as implemented (not planned), add implementation notes matching the 8-field selection tuple per §3.5.2.2, and update the component diagram to reflect implemented status for the Loader component.
- [X] T035 [P] Update `docs/domains/agent/ARCHITECTURE_DESIGN.md` §4.8.2 (Planned Prompt Architecture) — update the `PromptAssetLoader` boundary status from "Proposed" to "Implemented - M1" and add a note about the 8-field selection tuple and default values for future-oriented fields.
- [X] T036 [P] Update `docs/domains/agent/SRS_SPEC_TRACEABILITY.md` — add reverse-trace entries for M1-mapped SRS items (FR-1.4.5, FR-1.4.6, FR-1.4.8, FR-1.4.16, NFR-5.2.5–5.2.9, NFR-6.2.3, AC-8.1, AC-8.2) referencing `specs/prompt-system-milestone1/spec.md` and `specs/prompt-system-milestone1/tasks.md`.
- [X] T037 [P] Update `specs/spec-traceability.yaml` — change `prompt-system-milestone1` `mapping_status` from `mapped` to `verified` after all tests pass. Add `tasks.md` to `evidence_paths` and `review.md` placeholder.
- [X] T038 [P] Update `specs/spec-sync-status.md` — add delivery status entry for M1 with feature path, coverage metrics, and evidence links.
- [X] T039 [P] Add deprecation comment to `src/core/langchain_adapter.py` `PromptBuilder` class noting it is non-authoritative for prompt composition — the `PromptAssetLoader` + future `PromptAssembler` path is the canonical prompt composition path (per plan §Project Structure).
- [X] T040 Run the full M1 test suite — `& .\.venv\Scripts\python.exe -m pytest tests/test_prompt_asset_loader.py tests/test_prompt_metadata.py tests/test_prompt_config.py tests/test_agent_regression.py -v` — verify 100% pass rate. Record results in `specs/prompt-system-milestone1/review.md`.
- [X] T041 Run the existing backend regression suite — `& .\.venv\Scripts\python.exe -m pytest tests/ -v --ignore=tests/test_prompt_asset_loader.py --ignore=tests/test_prompt_metadata.py --ignore=tests/test_prompt_config.py --ignore=tests/test_agent_regression.py` — verify no regressions introduced by M1 changes.
- [X] T042 Run the checklist from `checklists/spec-plan-quality.md` against the final implementation — verify all 44 items pass or have documented justification for any non-applicable items. Record results in `specs/prompt-system-milestone1/review.md`.

**Checkpoint**: All M1 changes implemented, tests pass (100%), long-lived docs synchronized, traceability refreshed, no regressions in existing suite.

---

## Dependencies & Execution Order

### Phase Dependency Graph

```
Phase 1 (Foundation)
    │
    ├─────────────────┐
    ▼                 ▼
Phase 2 (US1)    Phase 3 (US2)
    │                 │
    └────────┬────────┘
             ▼
      Phase 4 (PS-04 — Wire Loader into Agent)
             │
       ┌─────┴─────┐
       ▼           ▼
  Phase 5      Phase 6
  (US3 —      (US4 —
   Config)    Metadata)
       │           │
       └─────┬─────┘
             ▼
      Phase 7 (Polish & Sync)
```

### Blocking Dependencies

| Phase | Blocks | Reason |
|-------|--------|--------|
| Phase 1 (Foundation) | All Phases 2–7 | `prompt_types.py` types required by loader, agent, config, metadata |
| Phase 2 (US1 — Prompt Asset) | Phase 4 (PS-04) | Agent needs externalized asset before it can switch to file-based prompt |
| Phase 3 (US2 — Loader) | Phase 4 (PS-04), Phase 5 (US3), Phase 6 (US4) | Loader required for agent prompt resolution, config content validation, metadata extraction |
| Phase 4 (PS-04 — Wire Loader) | Phase 5 (US3), Phase 6 (US4) | Agent must use loader before config can control it, and before metadata can be extracted from PromptSelection |
| Phase 5 (US3 — Config) | — | Independent user-visible increment after Phase 4 |
| Phase 6 (US4 — Metadata) | — | Independent user-visible increment after Phase 4 |
| Phase 7 (Polish & Sync) | All Phases 2–6 | Sync artifacts must reflect final implementation state |

### Parallel Opportunities

- **Phase 1**: T001 (directories), T002–T004 (types) — all [P] can run in parallel
- **Phase 2 + Phase 3**: Full parallel execution — US1 creates prompt asset + basic file reader (T005–T009); US2 implements loader component (T010–T016). No file conflicts.
- **Within Phase 2**: T005 (test fixture) and T007 (prompt asset file) — [P], no dependencies
- **Within Phase 3**: T010–T012 (tests) and T013–T016 (implementation) — tests can be written first (test-first), then implementation. T013 and T014 share the same file — must be sequential.
- **Within Phase 4**: T017–T018 (tests) and T019–T021 (implementation) — tests first, then implementation
- **Phase 5 + Phase 6**: Can run in parallel after Phase 4 — US3 and US4 touch different files (config vs metadata)
- **Within Phase 5**: T022–T023 (tests) [P], T024 (config file) [P], T025 (validation) depends on T024
- **Within Phase 6**: T027–T030 (tests) [P], T031–T033 (implementation) sequential
- **Phase 7**: T034–T039 — all [P], touch different sync artifacts. T040–T042 must run last.

### Suggested MVP Scope

**Minimum Viable Product**: Phases 1 + 2 + 3 (US1 + US2)
- Externalized prompt asset + basic file reader (with inline fallback)
- `PromptAssetLoader` component with baseline fallback
- 8-field selection tuple signature (with defaults for future fields)
- All US1 + US2 tests passing
- No config surface, no metadata, no agent swap yet
- Allows manual verification that externalized prompt behaves identically to hardcoded

**Full M1 Delivery**: Phases 1–7
- Agent uses `PromptAssetLoader` as primary prompt source
- Config surface with two-layer validation
- Response metadata + LangSmith trace tags
- All long-lived docs synchronized, traceability refreshed

### Per-Phase Execution Notes

- **Test-first**: Within each phase, write tests before implementation per spec AC requirements
- **File ownership**: `src/core/prompt_types.py` is the single source of truth for PromptAsset/PromptSelection/SelectionTuple types — do not duplicate type definitions
- **Cross-phase imports**: Phase 4 imports from Phase 3's `prompt_asset_loader.py`; Phase 5 and 6 import from Phase 4's modified `stock_assistant_agent.py`
- **Rollback safety**: Keep `REACT_SYSTEM_PROMPT` constant until Phase 4 is verified (M1 observation window). Only remove the alias after Phase 7 regression suite passes.
