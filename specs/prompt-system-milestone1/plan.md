# Implementation Plan: Prompt Compiler Path — Milestone M1 (Prompt Runtime Parity)

**Branch**: `enhance-agent-prompt-system-followup` | **Date**: 2026-06-03 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/prompt-system-milestone1/spec.md`

## Summary

Milestone M1 externalizes the current hardcoded ReAct system prompt from `stock_assistant_agent.py` into a versioned, frontmatter-annotated markdown asset at `src/prompts/system/react_analyst.md` (per ADR taxonomy), implements a `PromptAssetLoader` with baseline-fallback safety, adds a `prompts.*` configuration namespace with two-layer validation, and wires prompt identity (version, variant, selection mode, provider, model) into response metadata and LangSmith trace spans. Backlog items PS-01 through PS-06 of the prompt compiler path are in scope; route-context skills (PS-07/PS-08 → M2), evaluation harness (PS-09/PS-10 → M3), and experiment modes (PS-11 → M4 / PS-12 → M5) are excluded.

## Technical Context

**Language/Version**: Python 3.8+ (project baseline; Python 3.11 recommended)

**Primary Dependencies**: 
- `PyYAML` (or `ruamel.yaml`) for frontmatter parsing — already present via project config stack
- `langchain_core` >=0.3.28 (existing — for `RunnableConfig` metadata injection)
- `langsmith` (existing — for trace metadata tags)
- No new third-party packages required for M1

**Storage**: 
- Prompt assets: file system under `src/prompts/system/` (following ADR taxonomy from ARCHITECTURE_DESIGN.md §4.5.1.1)
- Prompt manifest: derived from asset directory scanning; no dedicated manifest file required at M1 scope (single asset)
- Metadata: emitted in `response.metadata` (in-memory) and LangSmith trace spans (optional external channel)
- Configuration: `config/config.yaml` `prompts.*` namespace

**Testing**: 
- `pytest` (existing project framework)
- Integration tests: Flask test client for API-level verification of response metadata fields
- Unit tests: `PromptAssetLoader` resolution, fallback, frontmatter parsing (no external dependencies)
- Fault-injection tests: missing/malformed prompt assets, invalid config values
- Regression tests: 5-query seed set comparison (pre/post externalization) across 8 route categories
- No new test frameworks required

**Target Platform**: Linux container (Docker), Windows development host. No changes to deployment topology.

**Project Type**: Backend agent runtime enhancement — Python package under `src/core/`, config under `config/`, prompt assets under `src/prompts/`

**Performance Goals**: 
- Prompt asset loading: < 50ms added to startup time (M1-NFR-002)
- Trace metadata emission: < 10ms per request (M1-NFR-003)
- No regression in existing NFR-1.1.1–1.1.6 latency targets

**Constraints**:
- Prompt asset path must follow ADR taxonomy: `system/react_analyst.md` (version in frontmatter, not directory nesting) per ARCHITECTURE_DESIGN.md §4.5.1.1
- `PromptAssetLoader` must not own route classification, tool execution, or model invocation (ARCHITECTURE_DESIGN.md §4.8.2, Development View package boundaries)
- Compiler path components must be additive — existing `src/prompts/` legacy files and `REACT_SYSTEM_PROMPT` alias may remain during M1 observation window (Architecture Synthesis: additive evolution principle)
- Two-layer validation: structural config errors (invalid keys, unsupported modes) block startup; content-resolution errors (non-existent version) fall back with WARN (per PS-03 scope definition)
- LangSmith must not become a hard runtime dependency; response metadata is the primary always-available test path (M1-NFR-004)
- Full 8-field selection tuple per TECHNICAL_DESIGN.md §3.5.2.2: `agent_role`, `route`, `locale`, `selection_mode`, `requested_version`, `prompt_experiment_id`, `workspace_mode`, `env`. At M1, 3 fields (`agent_role`, `requested_version`, `selection_mode`) are active discriminators; the remaining 5 fields MUST accept documented defaults and MUST be wired in the resolver signature for M2+-ready expansion.

**Scale/Scope**: Single-agent ReAct runtime. One baseline prompt asset. One config namespace. No multi-agent or route-context changes.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Governing artifacts identified**: SRS FR-1.4.5, FR-1.4.6, FR-1.4.8, FR-1.4.16, NFR-5.2.5–5.2.9, NFR-6.2.3, AC-8.1, AC-8.2, AC-8.7 (scope-awareness only — deferred to M4); ARCHITECTURE_DESIGN.md §4.5.1.1, §4.8.2, §4.5; PROMPT_SYSTEM_RESEARCH_PROPOSAL.md §Proposed Prompt Asset Model, §Versioning Model; PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md §2A.2, §Execution Backlog Mirror; Constitution v2.1.0 §Document Referencing, §Spec Kit Lifecycle Obligations
- [x] **Artifact ownership confirmed**: Delivery-scoped artifacts in `specs/prompt-system-milestone1/`. Long-lived doc updates to `docs/domains/agent/TECHNICAL_DESIGN.md` §3.5 and `docs/domains/agent/ARCHITECTURE_DESIGN.md` §4.8.2 are sync targets. `.specify/` is not used as governed delivery evidence store.
- [x] **Required sync targets listed**: `docs/domains/agent/TECHNICAL_DESIGN.md` §3.5, `docs/domains/agent/ARCHITECTURE_DESIGN.md` §4.8.2, `docs/domains/agent/SRS_SPEC_TRACEABILITY.md`, `specs/spec-traceability.yaml`, `specs/spec-sync-status.md`, `config/config.yaml`
- [x] **Affected architecture layers**: Agent runtime (`stock_assistant_agent.py`), new `PromptAssetLoader` component (under `src/core/`), config layer (`config/config.yaml`), prompt assets (`src/prompts/system/`). No changes to routes, services, repositories, transport, or deployment layers.
- [x] **Validation strategy defined**: Unit tests for loader resolution and fallback. Integration tests for response metadata fields. Fault-injection tests for missing/malformed assets and invalid config. 5-query seed set for behavioral regression. Dual-path response-metadata verification (always available) + LangSmith trace audit (when connected).
- [x] **Complexity justified**: Two-layer config validation (structural vs content-resolution) adds minimal complexity justified by the need to distinguish operator config errors from deployment version gaps. No backward-incompatible changes. Existing `REACT_SYSTEM_PROMPT` constant retained as deprecated alias during M1 window for safe rollback.

## Project Structure

### Documentation (this feature)

```text
specs/prompt-system-milestone1/
├── spec.md              # Feature specification (current file)
├── plan.md              # This file — implementation plan
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output — PromptSelection, PromptAsset schema
└── tasks.md             # Phase 2 output (generated by /speckit.tasks)
```

### Source Code — Affected Files

```text
# NEW files
src/core/prompt_asset_loader.py    # PromptAssetLoader: resolve, cache, fallback
src/core/prompt_types.py           # PromptSelection, PromptAsset dataclasses

# MODIFIED files
src/core/stock_assistant_agent.py  # Replace REACT_SYSTEM_PROMPT with loader path (PS-04)
src/core/langchain_adapter.py      # Document: isolate legacy PromptBuilder as non-authoritative
src/web/api_server.py              # Inject PromptAssetLoader into APIRouteContext

# NEW prompt asset
src/prompts/system/react_analyst.md  # Externalized baseline prompt with frontmatter

# MODIFIED config
config/config.yaml                    # Add prompts.* namespace (PS-03)

# TEST files
tests/test_prompt_asset_loader.py    # Unit: resolution, fallback, frontmatter parsing
tests/test_prompt_metadata.py        # Integration: response metadata fields, trace tags
tests/test_prompt_config.py          # Integration: structural validation, content fallback
tests/test_agent_regression.py       # Regression: 5-query seed set comparison
```

**Structure Decision**: Single-project layout (Option 1). All Python source under `src/`. Prompt assets under `src/prompts/system/` per ADR taxonomy. Tests under `tests/`. No frontend, IaC, or multi-project structure changes.

## Complexity Tracking

> No constitution violations detected. Complexity justification below documents deliberate design choices.

| Choice | Why Needed | Simpler Alternative Rejected Because |
|--------|------------|--------------------------------------|
| Two-layer config validation (structural error blocks startup; content error falls back) | Distinguishes operator config mistakes (invalid selection_mode) from deployment version gaps (version not found yet) | Single-layer "fail on any error" would force operators to deploy a matching prompt asset before changing config, creating circular dependency between config and asset deployment |
| Both response metadata AND LangSmith trace metadata | Response metadata is always available (CI, local dev, prod); LangSmith traces provide richer offline analysis | Metadata-only without traces would lose cross-session filtering and evaluation integration; traces-only would break CI/local testing |
| Frontmatter YAML for prompt metadata instead of separate manifest file | Self-contained assets; no secondary file to keep in sync; loader scans directory once | Separate manifest file would require synchronization discipline that M1 scale does not warrant |
| Version in frontmatter, not directory path | ADR taxonomy authority (ARCHITECTURE_DESIGN.md §4.5.1.1); version-as-path would force directory restructure on every version bump | `v1.md` style path was in the original roadmap but conflicts with the canonical architecture; resolved via explicit edge-case documentation in spec.md |
