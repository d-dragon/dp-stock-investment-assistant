# Feature Specification: Prompt Compiler Path — Milestone M1 (Prompt Runtime Parity)

**Feature Directory**: `specs/prompt-system-milestone1`

**Created**: 2026-06-03

**Status**: Implemented

**Input**: Milestone M1 from [PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md §2A.2 Prompt Compiler Path & Controlled Rollout](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#2a2-prompt-compiler-path--controlled-rollout), backlog items `PS-01` through `PS-06` from the [Execution Backlog Mirror](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#execution-backlog-mirror-synced-to-proposal-v18), and the governing SRS sections in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md).

## Governance Context *(mandatory)*

- **Source Authorities**:
  - `SOFTWARE_REQUIREMENTS_SPECIFICATION.md` §FR-1.4.5 (External Prompt Management)
  - `SOFTWARE_REQUIREMENTS_SPECIFICATION.md` §FR-1.4.6 (Prompt Version Identity)
  - `SOFTWARE_REQUIREMENTS_SPECIFICATION.md` §FR-1.4.8 (Prompt Rollback Safety)
  - `SOFTWARE_REQUIREMENTS_SPECIFICATION.md` §FR-1.4.16 (Prompt Segment Classification and Reuse)
  - `SOFTWARE_REQUIREMENTS_SPECIFICATION.md` §NFR-5.2.5–5.2.9 (Prompt Trace Metadata)
  - `SOFTWARE_REQUIREMENTS_SPECIFICATION.md` §NFR-6.2.3 (Versioned Prompt File Assets)
  - `SOFTWARE_REQUIREMENTS_SPECIFICATION.md` §AC-8.1 (Prompt Version Identity Verification)
  - `SOFTWARE_REQUIREMENTS_SPECIFICATION.md` §AC-8.2 (Baseline Fallback Verification)
  - `SOFTWARE_REQUIREMENTS_SPECIFICATION.md` §AC-8.7 (Automatic Rollback Triggering — referenced for scope-awareness; implementation deferred to M4 per PS-11 experiment-mode dependency)
  - `ARCHITECTURE_DESIGN.md` §4.5.1.1 Prompt Asset Layout: Current vs Target (canonical ADR taxonomy: `system/react_analyst.md`, version in frontmatter, not directory nesting)
  - `ARCHITECTURE_DESIGN.md` §4.8.2 Planned Prompt Architecture (PromptAssetLoader → PromptAssembler → ResponseGuardrailMiddleware)
  - `ARCHITECTURE_DESIGN.md` §4.5 Development View (source layout for prompt assets under `src/prompts/system/`, `src/prompts/skills/`, `src/prompts/experiments/`)
  - `PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md` §2A.2 Prompt Compiler Path & Controlled Rollout
  - `PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md` §Execution Backlog Mirror (PS-01 to PS-06)
  - `PROMPT_SYSTEM_RESEARCH_PROPOSAL.md` §Proposed Prompt Asset Model (canonical asset path: `react_analyst.md`, version via frontmatter semver)
  - `PROMPT_SYSTEM_RESEARCH_PROPOSAL.md` §Versioning Model (identifiers: prompt file, prompt name, semantic version, variant label)
  - `PROMPT_SYSTEM_BENCHMARK_REVIEW.md` §4.2, §4.3, §4.6 (External validation)
  - Constitution v2.1.0 §Document Referencing in Spec-Kit Workflows (section-level anchor precision)
  - Constitution v2.1.0 §Spec Kit Lifecycle Obligations (governed artifact delivery)
- **Affected Domains**: Agent (primary), Backend (config surface), Operations (deployment config)
- **Expected Sync Targets**:
  - `docs/domains/agent/TECHNICAL_DESIGN.md` §3.5 Prompt Realization and Guardrails
  - `docs/domains/agent/ARCHITECTURE_DESIGN.md` §4.8.2 Planned Prompt Architecture
  - `docs/domains/agent/SRS_SPEC_TRACEABILITY.md` — reverse-trace for prompt-governance mapping
  - `specs/spec-traceability.yaml` — M1 requirement coverage update
  - `specs/spec-sync-status.md` — delivery status refresh
  - `config/config.yaml` — `prompts.*` config surface addition (PS-03)
- **Out-of-Scope / No-Sync Notes**: Route-context prompt composition (PS-07, PS-08), experiment modes (PS-11), and multi-agent prompt taxonomy (PS-12) are excluded from M1. No OpenAPI changes required. No frontend changes. M2 through M5 milestones will use separate spec-kit features.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Externalize and Version the ReAct Baseline Prompt (Priority: P1)

A prompt maintainer extracts the current hardcoded `REACT_SYSTEM_PROMPT` from `stock_assistant_agent.py` into a versioned, frontmatter-annotated markdown asset at `src/prompts/system/react_analyst.md`. The version is expressed in frontmatter (`version: 1.0.0`), not in the directory path or filename — this follows the canonical ADR taxonomy per [ARCHITECTURE_DESIGN.md §4.5.1.1](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#4511-prompt-asset-layout-current-vs-target) and [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md §Proposed Prompt Asset Model](../../docs/domains/agent/PROMPT_SYSTEM_RESEARCH_PROPOSAL.md#proposed-prompt-asset-model). The agent loads this asset at startup instead of reading the Python string constant. The prompt retains identical behavior to the hardcoded baseline so no functional regression occurs. (Maps to PS-01, PS-04.)

**Why this priority**: The entire prompt compiler path depends on externalized, versioned assets. No downstream work (loader, config, identity, rollback) can function unless the prompt is extracted from source code and accessible as a file-system asset.

**Independent Test**: (1) Delete the extracted prompt asset, restart the agent, and verify the agent falls back to the inline hardcoded constant (this is the M1 safety net before the loader exists). (2) Restore the asset, restart, submit a fixed set of 5 seed queries covering `PRICE_CHECK`, `NEWS_ANALYSIS`, `FUNDAMENTALS`, `TECHNICAL_ANALYSIS`, and `GENERAL_CHAT`. Capture the raw response content and metadata. (3) Permanently remove `REACT_SYSTEM_PROMPT` from the agent code path, restart using only the externalized asset, and re-submit the same 5 queries. Compare response patterns — no structural regression (same section structure, same tool-call pattern, no new safety failures) is required.

**Acceptance Scenarios**:
1. **Given** the hardcoded `REACT_SYSTEM_PROMPT` has been extracted to `src/prompts/system/react_analyst.md` with frontmatter (`name: react_analyst_v1`, `version: 1.0.0`, `agent_role: react_analyst`, `status: active`) **When** `StockAssistantAgent` initializes **Then** it reads the prompt from the file asset. Prior to PS-04, both the file asset and the inline constant are available; after PS-04, only the file asset is used.
2. **Given** the prompt asset has frontmatter `version: 1.0.0` and `variant: baseline` **When** the agent processes a query **Then** the response metadata includes both `prompt_version: "1.0.0"` and `prompt_variant: "baseline"`, and the trace span includes `prompt_version`, `prompt_variant`, and `prompt_selection_mode: "fixed"`. *(FR-1.4.6, NFR-5.2.5)*
3. **Given** `src/prompts/system/react_analyst.md` is present and valid **When** the agent starts **Then** it logs an INFO-level message confirming the loaded prompt identity (`asset_id`, `version`, `variant`) and that `REACT_SYSTEM_PROMPT` is no longer the primary prompt source for the ReAct path.
4. **Given** `REACT_SYSTEM_PROMPT` is removed from the agent code path and only the externalized asset is available **When** the 5-query seed set is submitted **Then** response metadata for all 5 queries shows `prompt_version: "1.0.0"`, `prompt_variant: "baseline"`, `prompt_selection_mode: "fixed"`, `model_provider`, and `model_name`. No query produces a different tool-call pattern or structural failure compared to the pre-migration baseline run. *(FR-1.4.6, NFR-5.2.9)*

*SRS mapping: FR-1.4.5, FR-1.4.6, NFR-6.2.3, AC-8.1, NFR-5.2.9*

---

### User Story 2 — PromptAssetLoader with Fallback Safety (Priority: P2)

The prompt maintainer adds a `PromptAssetLoader` component that sits between configuration and the agent prompt source. The loader accepts an 8-field selection tuple (`agent_role`, `route`, `locale`, `selection_mode`, `requested_version`, `prompt_experiment_id`, `workspace_mode`, `env`) per TECHNICAL_DESIGN.md §3.5.2.2 and resolves it against a prompt manifest derived from the asset directory. At M1 scope, `route`, `locale`, `prompt_experiment_id`, `workspace_mode`, and `env` receive documented default values (e.g., `route: "general_chat"`, `locale: "en"`, `prompt_experiment_id: null`, `workspace_mode: "default"`, `env: "production"`) and are wired for expansion in M2+; `agent_role`, `requested_version`, and `selection_mode` are the active discriminators for the single-asset baseline. Successful resolution returns a `PromptSelection` contract with the selected asset's content and metadata. If the configured asset is missing, malformed (frontmatter parse failure), or fails manifest validation, the loader falls back to the most recent known-good baseline asset, logs a WARN-level event with the failed prompt identity, and returns the baseline `PromptSelection` with `fallback_used: true`. At M1 scope the asset directory contains only the single `react_analyst.md` baseline, so the baseline lineage is that single asset — the fallback path is validated structurally even though the nominal and fallback targets are currently the same file. (Maps to PS-02 for the loader implementation, PS-06 for fallback hardening.)

**Why this priority**: Prompt rollback safety is a P0 requirement (FR-1.4.8). Without a fail-closed loader that resolves to a deterministic baseline on failure, any prompt asset defect would silently widen the agent's prompt authority, crash the agent, or leave the agent with an empty prompt.

**Independent Test**: (1) Set `prompts.system.active_version` to a non-existent version string such as `"v99"`. Restart the agent. Verify the agent starts, uses the baseline prompt, logs a WARN event containing the failed version identifier on stderr or the application log. (2) Create a temporary prompt file at `src/prompts/system/bad_frontmatter.md` whose frontmatter YAML is malformed (e.g., unclosed key). Configure it as the active version. Restart. Verify the loader rejects it, falls back to baseline, and logs WARN with the file path. Clean up the temporary file. (3) Remove the prompt asset entirely. Restart. Verify the loader reports an unresolvable prompt error — M1 raises this as a startup error rather than silently synthesizing content.

**Acceptance Scenarios**:
1. **Given** `PromptAssetLoader.resolve(agent_role="react_analyst", version="2.0.0")` is called with only `1.0.0` available in the manifest **When** `2.0.0` does not exist **Then** the loader returns the `1.0.0` baseline lineage asset and logs a WARN-level event including the failed `version` identifier and the resolved fallback identifier. *(FR-1.4.8, AC-8.2)*
2. **Given** `PromptAssetLoader.resolve()` encounters a prompt file with invalid frontmatter YAML (e.g., unclosed key, missing `---` closing) **When** parsing fails **Then** the loader falls back to the baseline lineage asset and logs WARN with the malformed file path. *(FR-1.4.8)*
3. **Given** the loader successfully resolves a valid prompt asset with frontmatter `version: 1.0.0`, `variant: baseline` **When** the selection completes **Then** it returns a `PromptSelection` contract containing `selected_assets: ["system/react_analyst.md"]`, `prompt_version: "1.0.0"`, `prompt_variant: "baseline"`, `selection_mode: "fixed"`, `fallback_used: false`, and `trace_metadata` with a unique selection ID. *(FR-1.4.16)*
4. **Given** the loader has resolved the baseline lineage after a fallback **When** the `PromptSelection` is consumed by the agent **Then** `PromptSelection.fallback_used` is `true` and `degraded_reason` is a non-empty string explaining the trigger (e.g., "version 2.0.0 not found in manifest"). *(FR-1.4.8)*

*SRS mapping: FR-1.4.8, FR-1.4.16, AC-8.2*

---

### User Story 3 — Prompts Config Surface and Activation Validation (Priority: P2)

An operator configures the prompt system through a dedicated `prompts.*` configuration namespace under `config.yaml`. The configuration defines the prompt directory, selection mode, active role, active version, and variant list, matching the schema from [PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md §Configuration Updates](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#configuration-updates). A two-layer validation approach is used: (1) structural validation at startup catches invalid schema keys, unsupported selection modes, or missing required fields and prevents agent startup with a clear error; (2) content resolution at prompt-load time (handled by `PromptAssetLoader` per User Story 2) catches missing or malformed assets and falls back to baseline with a WARN-level log. This means an operator typing a wrong version string still gets a working agent (baseline fallback), while an operator using a completely invalid config structure gets a startup failure with actionable guidance. (Maps to PS-03.)

**Why this priority**: The `prompts.*` config surface is the control plane for all downstream prompt selection, fallback, experimentation, and rollout. Without explicit validation, misconfigured deployments could activate unintended prompts without detection. The two-layer design ensures that config structural errors are caught early (startup time), while asset resolution errors are handled gracefully (runtime fallback). Depends on PS-01 (asset extraction) and PS-02 (loader) being complete.

**Independent Test**: (1) Configure `prompts.selection_mode: "invalid_mode"`. Start the agent. Verify the agent fails to start with a configuration error explaining valid modes. Correct to `"fixed"`. Restart. Verify clean startup. (2) Configure `prompts.system.active_version: "2.0.0"` when only `1.0.0` exists. Start the agent. Verify the agent starts, uses the `1.0.0` baseline, and logs a WARN with the failed version. (3) Configure `prompts` with a valid structure and version. Start the agent. Verify `stock_assistant_agent.py` reads the active prompt from the prompt directory and version specified in config, not from any hardcoded fallback.

**Acceptance Scenarios**:
1. **Given** `config.yaml` contains a `prompts.*` namespace with `directory: "src/prompts"`, `selection_mode: "fixed"`, `system.active_role: "react_analyst"`, `system.active_version: "1.0.0"`, and `system.variants: [{name: "baseline", version: "1.0.0", file: "system/react_analyst.md", status: "active"}]` **When** the agent starts **Then** the configuration is parsed and validated; the `system.active_version` resolves to an existing asset; the agent activates with the configured prompt. *(NFR-6.2.3, FR-1.4.5)*
2. **Given** `prompts.selection_mode` is set to `"invalid_mode"` (not one of `fixed`, `forced`, `shadow`, or `weighted`) **When** configuration validation runs at startup **Then** the agent reports a configuration error listing the valid modes and does not start. This is a structural validation failure, not a content-resolution fallback. *(FR-1.4.5 config governance)*
3. **Given** `prompts.system.active_version` points to `"2.0.0"` which does not exist in the manifest **When** `PromptAssetLoader` attempts resolution during agent initialization **Then** the loader falls back to the `1.0.0` baseline, the agent starts successfully with baseline content, and a WARN-level event is logged including the failed version `"2.0.0"` and the resolved fallback version `"1.0.0"`. This is a content-resolution fallback, not a startup failure. *(FR-1.4.8, AC-8.2)*

*SRS mapping: FR-1.4.5, FR-1.4.8, NFR-6.2.3, AC-8.2*

---

### User Story 4 — Prompt Identity in Response and Trace Metadata (Priority: P2)

Every agent invocation injects the loaded prompt version, variant, selection mode, and provider metadata into both the agent response metadata and LangSmith trace spans. A system operator can inspect any response or trace and identify which prompt lineage produced it, whether fallback occurred, which model provider and model were used, and what selection mode was active. This makes prompt behavior attributable and diagnostic without requiring deployment-timestamp correlation. (Maps to PS-05.)

**Why this priority**: Traceability of prompt behavior is a P1 requirement (FR-1.4.6, NFR-5.2.5–5.2.9). Without prompt identity and provider metadata, diagnosing which prompt caused a behavioral change requires correlating deployment timestamps with customer reports. `model_provider` and `model_name` must be included per NFR-5.2.9 because prompt behavior varies across providers and model snapshots. Depends on PS-04 (externalized prompt as source of truth).

**Independent Test**: Primary path (always available): Send a query via the chat API. Parse `response.metadata`. Verify `prompt_version`, `prompt_variant`, `prompt_selection_mode`, `model_provider`, and `model_name` are all present and non-empty. Repeat for 3 queries with different route classifications. Secondary path (when LangSmith is connected): Navigate to the LangSmith trace for any of the above queries. Verify the trace's metadata and tags contain the same five fields with matching values. The test passes even if LangSmith is unreachable, as long as the response metadata path succeeds. This dual-path design ensures the test is executable in CI, local dev, and production environments alike.

**Acceptance Scenarios**:
1. **Given** a query is processed by the agent **When** the response is returned **Then** `response.metadata` includes `prompt_version` (semver string), `prompt_variant` (label string), `prompt_selection_mode` (one of `fixed`, `forced`, `shadow`, `weighted`), `fallback_used` (boolean), `model_provider` (string, e.g., `"openai"`), and `model_name` (string, e.g., `"gpt-4"`). All fields are non-empty. *(FR-1.4.6, NFR-5.2.9, AC-8.1)*
2. **Given** the same query **When** a LangSmith trace is created for the agent invocation **Then** the trace metadata includes `prompt_version`, `prompt_variant`, `prompt_selection_mode`, `agent_role`, `model_provider`, and `model_name` tags, matching the values in the response metadata. *(NFR-5.2.5, NFR-5.2.9)*
3. **Given** a fallback occurred during prompt loading **When** the response is returned **Then** `response.metadata.fallback_used` is `true` and `response.metadata.degraded_reason` is a non-empty string explaining the fallback trigger (e.g., `"version 2.0.0 not found, fell back to 1.0.0"`). *(FR-1.4.8)*
4. **Given** LangSmith is not configured or unreachable **When** the agent processes a query **Then** the response metadata fields in AC-1 above are still populated and correct. The trace tags are degraded silently, but the response metadata path is always available and testable. *(NFR-5.2.4 configurable tracing)*

*SRS mapping: FR-1.4.6, NFR-5.2.5–5.2.9, AC-8.1*

---

### Edge Cases

- **PS-01 extraction: version in path vs version in metadata**: The roadmap PS-01 initially specified `src/prompts/system/react_analyst/v1.md` (version in path), but this conflicts with the canonical ADR taxonomy per [ARCHITECTURE_DESIGN.md §4.5.1.1](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#4511-prompt-asset-layout-current-vs-target) and [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md §Proposed Prompt Asset Model](../../docs/domains/agent/PROMPT_SYSTEM_RESEARCH_PROPOSAL.md#proposed-prompt-asset-model), which place version in frontmatter metadata. M1 adopts the ADR taxonomy: `system/react_analyst.md` with `version: 1.0.0` in frontmatter. The roadmap's `v1.md` reference should be interpreted as the frontmatter `version: 1.0.0` value.
- **PS-01 extraction: missing frontmatter**: The prompt asset file exists but lacks frontmatter `---` delimiters. The loader must reject it as malformed and fall back to baseline (FR-1.4.8). The loader must not attempt to infer version or agent_role from heuristics or filename patterns.
- **PS-02/PS-03 fallback chain exhaustion**: All configured baseline lineages fail to load (e.g., the single `react_analyst.md` is also missing). The loader should report an unresolvable-prompt error that prevents agent startup rather than synthesizing a prompt from heuristics. Currently scoped as a documented startup-error condition for M1; full graceful handling is reserved for M3/M4 rollout gates.
- **PS-03 config reload vs restart**: NFR-6.2.3 states prompts should be configurable without code deployment, but "via configuration reload or service restart" admits two implementation strategies. M1 initializes from config at startup only; live config reload is deferred to PS-04 or a follow-up task.
- **PS-03 structural vs content validation**: The two-layer model described in User Story 3 must be preserved. An invalid `selection_mode` value is a structural validation failure (blocks startup). A non-existent `active_version` is a content-resolution failure (falls back with WARN, allows startup). Tests must verify both paths independently.
- **PS-05 metadata on stateless requests**: Queries without `conversation_id` still receive prompt identity and provider metadata in the response. The trace span must include prompt identifiers regardless of stateful/stateless mode.
- **PS-05 LangSmith-unavailable fallback**: When LangSmith is not configured or unreachable, the response metadata path must still emit `prompt_version`, `prompt_variant`, `prompt_selection_mode`, `model_provider`, and `model_name`. Trace tags degrade silently; response metadata is always populated.
- **PS-06 rollback safety before experiment modes**: Auto-rollback triggers for live candidate observation (FR-1.4.13) are gated until experiment modes (PS-11) are active in M4. M1 implements the baseline fallback (FR-1.4.8) but not the ongoing-observation rollback trigger (FR-1.4.13). This is an explicit scope boundary for M1.
- **Legacy `REACT_SYSTEM_PROMPT` removal**: The hardcoded constant must be removed or deprecated from the primary ReAct path after PS-04 verification. A deprecation comment and a 2-sprint fallback alias may remain during the M1 observation window.

## Requirements *(mandatory)*

### Functional Requirements

- **M1-FR-001 (PS-01)**: System MUST externalize the current ReAct prompt from source code into a versioned markdown file at `src/prompts/system/react_analyst.md` with frontmatter containing `name`, `version`, `agent_role`, `status`, and `variant`. Version and variant are expressed in frontmatter metadata, not in the directory path. *(FR-1.4.5, NFR-6.2.3)*
- **M1-FR-002 (PS-01)**: The externalized prompt MUST produce semantically equivalent agent behavior to the hardcoded `REACT_SYSTEM_PROMPT` for all 8 route categories, verified by a fixed 5-query seed set. *(NFR-6.2.3 behavioral parity)*
- **M1-FR-003 (PS-04)**: `StockAssistantAgent` MUST replace `REACT_SYSTEM_PROMPT` as the primary prompt source with the externalized asset resolved through `PromptAssetLoader`. *(FR-1.4.5)*
- **M1-FR-004 (PS-02)**: System MUST implement a `PromptAssetLoader` component that resolves a `PromptSelection` from the full 8-field selection tuple (`agent_role`, `route`, `locale`, `selection_mode`, `requested_version`, `prompt_experiment_id`, `workspace_mode`, `env`) and the prompt manifest. At M1, the 5 future-oriented fields (`route`, `locale`, `prompt_experiment_id`, `workspace_mode`, `env`) MUST accept documented default values and MUST be wired in the resolver signature for M2+-ready expansion. *(FR-1.4.5, FR-1.4.16)*
- **M1-FR-005 (PS-02)**: The `PromptSelection` output MUST include `selected_assets`, `prompt_version`, `prompt_variant`, `selection_mode`, `fallback_used`, `degraded_reason`, and `trace_metadata`. *(FR-1.4.16)*
- **M1-FR-006 (PS-02, PS-06)**: When the configured prompt asset is missing, malformed, or fails manifest validation, the loader MUST fall back to the most recent known-good baseline lineage and log a WARN-level event with the failed prompt version identifier. *(FR-1.4.8, AC-8.2)*
- **M1-FR-007 (PS-02, PS-06)**: The fallback MUST NOT silently widen prompt authority or inject unvalidated prompt content; fail-closed to baseline lineage is required. *(FR-1.4.8)*
- **M1-FR-008 (PS-03)**: System MUST support a dedicated `prompts.*` configuration namespace in `config.yaml` covering `directory`, `selection_mode`, `default_locale`, `system.active_role`, `system.active_version`, `system.variants[]`, and `experiments.enabled` / `experiments.active_id`. *(NFR-6.2.3, FR-1.4.5)*
- **M1-FR-009a (PS-03 structural)**: Structural configuration validation at startup MUST reject invalid schema keys, unsupported `selection_mode` values, and missing required fields with a clear startup error that prevents agent activation. *(Constitution fail-closed rule)*
- **M1-FR-009b (PS-03 content resolution)**: Content-resolution validation (via `PromptAssetLoader`) MUST fall back to the baseline lineage when the configured version does not exist in the manifest, logging WARN with the failed version. This is not a startup failure; the agent starts with baseline content. *(FR-1.4.8)*
- **M1-FR-010 (PS-05)**: Every agent invocation MUST emit `prompt_version`, `prompt_variant`, `prompt_selection_mode`, `fallback_used`, `model_provider`, and `model_name` in the response metadata. *(FR-1.4.6, NFR-5.2.9, AC-8.1)*
- **M1-FR-011 (PS-05)**: Every agent invocation MUST emit LangSmith trace metadata for `prompt_version`, `prompt_variant`, `prompt_selection_mode`, `agent_role`, `model_provider`, and `model_name`. Missing or unreachable LangSmith MUST NOT degrade the response metadata path. *(NFR-5.2.5, NFR-5.2.9)*
- **M1-FR-012 (PS-05)**: Evaluation and live-observation runs MUST include complete prompt-governance metadata: `prompt_version`, `prompt_variant`, `prompt_selection_mode`, `agent_role`, `model_provider`, `model_name`, and when applicable `prompt_experiment_id`, `routing_decision`, and `conversation_id`. *(NFR-5.2.9)*

### Non-Functional Requirements

- **M1-NFR-001 (PS-02)**: Prompt asset caching SHOULD cache parsed frontmatter by the full 8-field selection tuple (`agent_role`, `route`, `locale`, `selection_mode`, `requested_version`, `prompt_experiment_id`, `workspace_mode`, `env`). Cache invalidation MUST be tied to manifest-version, review-state, or lineage changes. *(FR-1.4.16 segment reuse)*
- **M1-NFR-002 (PS-04)**: Prompt asset loading MUST NOT add more than 50ms to agent startup time. Subsequent invocations reuse the cached resolution. *(Baseline performance)*
- **M1-NFR-003 (PS-05)**: Trace metadata emission MUST NOT add more than 10ms to request processing time. *(NFR-1.1.5 performance guard)*
- **M1-NFR-004 (PS-05)**: Response metadata for `prompt_version`, `prompt_variant`, `prompt_selection_mode`, `model_provider`, and `model_name` MUST always be populated regardless of LangSmith connectivity. LangSmith trace tags are an additional observability channel, not the primary metadata source. *(NFR-5.2.4, NFR-5.2.9)*

### Key Entities

- **PromptAsset**: A versioned, frontmatter-annotated markdown file under `src/prompts/` containing behavioral instructions and policy for the agent. Key metadata: `name`, `version`, `agent_role`, `status`, `locale`, `parity_group`.
- **PromptSelection**: The output contract from `PromptAssetLoader` that identifies which assets were selected, which baseline lineage was used, whether fallback occurred, and trace metadata for observability. Implemented as a frozen dataclass with fields: `selected_assets` (List[str]), `prompt_version` (str, semver), `prompt_variant` (str, e.g. `"baseline"`), `selection_mode` (str, one of `fixed`, `forced`, `shadow`, `weighted`), `fallback_used` (bool), `degraded_reason` (Optional[str]), `trace_metadata` (dict).
- **Prompts Config Namespace**: The `prompts.*` YAML configuration surface in `config.yaml` that governs prompt directory, selection mode, active role/version, variant weights, locale defaults, and experiment controls.
- **Prompt Version Identity**: The `prompt_version` and `prompt_variant` identifiers emitted in response metadata and trace spans for every agent invocation, enabling attributable prompt behavior.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-M1-01**: The hardcoded `REACT_SYSTEM_PROMPT` is no longer the primary prompt source for the ReAct path; the externalized asset is used instead.
- **SC-M1-02**: Agent behavior for all 8 route categories is semantically equivalent before and after externalization (verified by diff on a known query set).
- **SC-M1-03**: A configured missing or malformed prompt asset results in baseline lineage fallback with WARN-level logging (verified by fault-injection test — AC-8.2).
- **SC-M1-04**: Agent startup with an invalid `prompts.*` configuration is rejected with a clear error message (verified by configuration test).
- **SC-M1-05**: Every agent response includes `prompt_version`, `prompt_variant`, `prompt_selection_mode`, `model_provider`, and `model_name` in metadata (verified by integration test — AC-8.1, NFR-5.2.9). This path is always testable regardless of LangSmith availability.
- **SC-M1-06**: LangSmith traces include `prompt_version`, `prompt_variant`, `prompt_selection_mode`, `agent_role`, `model_provider`, and `model_name` metadata for every invocation (verified by trace audit when LangSmith is connected — NFR-5.2.5, NFR-5.2.9). Missing LangSmith does not degrade the response metadata path.
- **SC-M1-07**: Structural configuration errors (invalid `selection_mode`) block agent startup with a clear error message. Content-resolution errors (non-existent `active_version`) allow startup with baseline fallback and WARN-level logging. Both paths are verified by independent configuration tests.

## Assumptions

- The canonical baseline prompt file is `src/prompts/system/react_analyst.md` with frontmatter `version: 1.0.0` and `variant: baseline`. The `prompts.directory` config key may override the root, but the relative path within that root is `system/react_analyst.md`. The roadmap's `v1.md` path is superseded by the ADR taxonomy in ARCHITECTURE_DESIGN.md §4.5.1.1 and PROMPT_SYSTEM_RESEARCH_PROPOSAL.md §Proposed Prompt Asset Model.
- Prompt version identity consists of a two-level identifier: `prompt_version` (semver string from `version` frontmatter, e.g., `"1.0.0"`) and `prompt_variant` (stable cohort label from `variant` frontmatter, e.g., `"baseline"`). Both are emitted in response metadata and trace spans.
- LangSmith tracing integration already exists in the project (verified: `langsmith` SDK in requirements, existing trace spans). M1 adds new metadata keys and tags to existing traces; it does not introduce LangSmith as a hard runtime dependency. Response metadata is the always-available test path.
- The `prompts.*` config namespace replaces any previously scattered prompt-related config keys; backward compatibility aliases may be provided for a 2-sprint deprecation window.
- PS-03 validation follows a two-layer model: structural config errors (invalid keys, unsupported modes) block startup; content-resolution errors (non-existent version) trigger baseline fallback with WARN-level logging.
- PS-06 (auto-rollback for live candidate observation) is partially scoped to M1: baseline fallback for load-time failures is in scope; ongoing-observation rollback triggers (FR-1.4.13) require experiment modes (PS-11) in M4 and are explicitly deferred.
- M1 does not address locality-specific prompt variants (FR-1.4.15), tool-risk envelope enforcement (FR-1.4.14), or route-specific prompt context (FR-1.4.7). Those are M2/M3 scope.
