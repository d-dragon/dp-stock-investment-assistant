# Feature Specification: Prompt Compiler Path — Milestone M2 (Route-Aware Skills)

**Feature Directory**: `specs/prompt-system-milestone2`

**Branch**: `prompt-system-milestone2`

**Created**: 2026-06-04

**Status**: Draft

**Input**: Milestone M2 from [PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md §2A.2 Prompt Compiler Path & Controlled Rollout](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#2a2-prompt-compiler-path--controlled-rollout), backlog items `PS-07` and `PS-08`.

**Prerequisite**: Milestone M1 (Prompt Runtime Parity) is complete — `PromptAssetLoader` implemented, prompt asset externalized to `src/prompts/system/react_analyst.md`, `prompts.*` config surface active, response metadata emitted on all invocations. See [specs/prompt-system-milestone1/review.md](../prompt-system-milestone1/review.md).

## Governance Context *(mandatory)*

- **Source Authorities**:
  - `PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md` §Milestone Gates — M2 (Route-Aware Skills: PS-07 to PS-08)
  - `PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md` §Execution Backlog Mirror — PS-07, PS-08
  - `ARCHITECTURE_DESIGN.md` §4.8.2 Planned Prompt Architecture (PromptAssetLoader → PromptAssembler → ResponseGuardrailMiddleware — M2 implements PromptAssembler)
  - `ARCHITECTURE_DESIGN.md` §4.3.2 Route Classification View (8 route categories: PRICE_CHECK, NEWS_ANALYSIS, PORTFOLIO, TECHNICAL_ANALYSIS, FUNDAMENTALS, IDEAS, MARKET_WATCH, GENERAL_CHAT)
  - `TECHNICAL_DESIGN.md` §3.5.2.3 PromptAssembler Realization Contract (deterministic assembly order, route-skill resolution, missing-skill degradation)
  - `TECHNICAL_DESIGN.md` §3.5.4 Static and Dynamic Segment Realization (segment classification, cache rules, authority treatment)
  - `PROMPT_SYSTEM_RESEARCH_PROPOSAL.md` §Skills Pattern — route-aware composition using existing semantic router
  - `SOFTWARE_REQUIREMENTS_SPECIFICATION.md` §FR-1.4.7 (Route-Specific Prompt Context)
  - `SOFTWARE_REQUIREMENTS_SPECIFICATION.md` §FR-1.4.11 (Prompt Authority Precedence)
  - `SOFTWARE_REQUIREMENTS_SPECIFICATION.md` §FR-1.4.16 (Prompt Segment Classification and Reuse)
  - `SOFTWARE_REQUIREMENTS_SPECIFICATION.md` §NFR-5.2.8 (Traces include prompt selection mode and machine-detectable guardrail outcomes)
  - `SOFTWARE_REQUIREMENTS_SPECIFICATION.md` §AC-8.5 (instruction authority separation — lower layers cannot weaken shared policy)
  - `SOFTWARE_REQUIREMENTS_SPECIFICATION.md` §AC-8.8 (trace metadata completeness — prompt selection mode in traces)
  - `SOFTWARE_REQUIREMENTS_SPECIFICATION.md` §AC-8.11 (prompt segment classification — static/dynamic/evidence separation)
  - Constitution v2.1.0 §Document Referencing in Spec-Kit Workflows
  - Constitution v2.1.0 §Spec Kit Lifecycle Obligations
  - `ADR-AGENT-002-SKILLS-PATTERN-PROMPT-COMPOSITION.md` — Skills-pattern composition authority (governs `PromptAssembler`)
  - `ADR-AGENT-003-EXTERNALIZE-VERSION-PROMPT-ASSETS.md` — Externalized asset governance (governs route-skill asset taxonomy)
- **M1 Dependencies**:
  - `PromptAssetLoader` — resolves prompt assets; M2 extends the manifest to include route skill assets
  - `PromptSelection` — output contract; M2 introduces `PromptAssembler` that consumes `PromptSelection` and produces `CompiledPrompt`
  - `prompts.*` config — extended with route context settings in M2
- **Affected Domains**: Agent (primary — new PromptAssembler component, route-skill assets), Backend (config surface extension)
- **Expected Sync Targets**:
  - `docs/domains/agent/TECHNICAL_DESIGN.md` §3.5.2 — mark PromptAssembler as implemented
  - `docs/domains/agent/ARCHITECTURE_DESIGN.md` §4.8.2 — update PromptAssembler status to Implemented - M2
  - `docs/domains/agent/SRS_SPEC_TRACEABILITY.md` — update FR-1.4.7, FR-1.4.11, AC-8.5, AC-8.8, AC-8.11 reverse-trace entries
  - `specs/spec-traceability.yaml` — add M2 feature entry
  - `specs/spec-sync-status.md` — add M2 delivery status
  - `config/config.yaml` — extend `prompts.*` with `route_contexts` section
  - `docs/openapi.yaml` — if REST API response metadata changes
- **Out-of-Scope / No-Sync Notes**: Experiment modes (PS-11 — M4), evaluation harness (PS-09/PS-10 — M3), multi-agent taxonomy (PS-12 — M5). ResponseGuardrailMiddleware remains planned for M3.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Route-Context Prompt Assets for All 8 Route Categories (Priority: P1)

A prompt maintainer creates 8 route-specific prompt skill files under `src/prompts/skills/routes/`, one for each `StockQueryRouter` category: `price_check.md`, `news_analysis.md`, `portfolio.md`, `technical_analysis.md`, `fundamentals.md`, `ideas.md`, `market_watch.md`, `general_chat.md`. Each file is a frontmatter-annotated markdown asset declaring its `agent_role: react_analyst`, `route_scope`, `status`, and `variant`. The `PromptAssetLoader._build_manifest()` (extended in M2) scans `skills/routes/` alongside `system/` and includes route-skill assets in the manifest, keyed by `agent_role` and `route_scope`. The route-skill assets narrow behavior for their route without weakening shared safety policy. (Maps to PS-07.)

**Why this priority**: Route-specific prompt context is the foundational prerequisite for PromptAssembler. Without authored skill assets per route, the assembler cannot compose route-aware behavior. PS-07 also has no dependency on PS-08 (assets can be authored and validated independently).

**Independent Test**: (1) Create a route-skill asset for `PRICE_CHECK` at `src/prompts/skills/routes/price_check.md` with valid frontmatter. Verify the manifest builder discovers it and includes it under the correct `agent_role` and `route_scope`. (2) Create a route-skill asset with invalid frontmatter — verify it is skipped with WARN-level logging (same pattern as M1). (3) Create route-skill assets for all 8 categories. Verify the manifest contains 8 entries across the correct route scopes.

**Acceptance Scenarios**:
1. **Given** the `PromptAssetLoader` manifest builder has been extended to scan `skills/routes/` **When** route-skill `.md` files exist with valid frontmatter declaring `route_scope` **Then** they are included in the manifest keyed by `(agent_role, route_scope)`.
2. **Given** a route-skill asset at `src/prompts/skills/routes/price_check.md` with frontmatter `route_scope: ["PRICE_CHECK"]` and `status: active` **When** the manifest is built **Then** the asset is resolvable for `agent_role="react_analyst"` and `route="PRICE_CHECK"`.
3. **Given** a route-skill asset has malformed frontmatter (missing `---` closing) **When** the manifest builder processes it **Then** it is skipped and a WARN-level event is logged with the file path.
4. **Given** only a subset of 8 route skills exist (e.g., 5 of 8) **When** the manifest is built **Then** missing routes are silently absent — no error raised. The manifest contains only the assets that exist.

*SRS mapping: FR-1.4.7*

---

### User Story 2 — PromptAssembler with Route-Aware Composition (Priority: P1)

A prompt maintainer implements `PromptAssembler` that composes one deterministic prompt contract from shared policy, the agent's role prompt, route-specific skill context, and bounded runtime context. The assembler accepts a `PromptSelection` (from `PromptAssetLoader`), a normalized route result, and optional dynamic controls. It returns a `CompiledPrompt` with segment manifest, compiled text, and trace metadata. The assembly order per TECHNICAL_DESIGN.md §3.5.2.3 is: shared policy → always-active skills → route-specific skill → bounded memory context → evidence and tool-derived facts → task framing → output contract. If a route skill is missing for the classified route, the assembler continues with approved inputs only (shared policy + role prompt), records the gap in metadata, and never synthesizes substitute instructions. (Maps to PS-08.)

**Why this priority**: Route-aware composition is the core M2 deliverable. Without the assembler, route-skill assets (PS-07) exist on disk but are not injected into the agent's runtime prompt. PS-08 depends on PS-07 (route-skill assets to compose) and M1's `PromptAssetLoader` (to resolve the base prompt and route skills).

**Independent Test**: (1) Configure the agent with a `PRICE_CHECK` route skill. Submit a `PRICE_CHECK` classified query. Verify the agent's system prompt contains the shared policy + role prompt + route-skill content (verified by metadata or trace tags). (2) Configure the agent with only 5 of 8 route skills. Submit a query classified to a missing route. Verify the agent composes without the route skill, records a gap in metadata (e.g., `"missing_route_skills": ["TECHNICAL_ANALYSIS"]`), and still produces a coherent response. (3) Submit the same query with and without route skills enabled. Verify that response metadata includes `route` classification and `route_skill_used` tag.

**Acceptance Scenarios**:
1. **Given** a `PRICE_CHECK` classified query and a route-skill asset exists for `PRICE_CHECK` **When** `PromptAssembler.compile()` is invoked **Then** the compiled prompt includes shared policy, the role prompt, and the `PRICE_CHECK` route-skill content. `CompiledPrompt.segment_manifest` lists all segments with their classifications. *(FR-1.4.7, FR-1.4.16)*
2. **Given** a query classified as `TECHNICAL_ANALYSIS` but no route-skill asset exists for that route **When** `PromptAssembler.compile()` is invoked **Then** the assembler continues with shared policy and role prompt only, adds `missing_route_skills: ["TECHNICAL_ANALYSIS"]` to trace metadata, and does not synthesize substitute instructions. *(FR-1.4.11 — lower layers cannot weaken; but missing layers are tolerated)*
3. **Given** a valid compilation **When** `CompiledPrompt` is returned **Then** it includes `compiled_text` (the assembled prompt string), `segment_manifest` (list of segment types and sources), and `trace_metadata` with `route`, `selected_skills`, `fallback_used` (if any route skill degraded), and `prompt_metadata`. *(FR-1.4.16, NFR-5.2.8)*
4. **Given** the prompt system is configured with `route_contexts.enabled: true` **When** the agent processes a query **Then** the response metadata includes `route` (the classified route name) and `prompt_selection_mode`. *(NFR-5.2.8, M2 delivers prompt selection mode only; guardrail outcome metadata is deferred to M3 when ResponseGuardrailMiddleware is implemented)*

*SRS mapping: FR-1.4.7, FR-1.4.11, FR-1.4.16, NFR-5.2.8, AC-8.5, AC-8.8, AC-8.11*

---

### Edge Cases

- **PS-07 missing route-skill directory**: The `skills/routes/` directory may not exist at M2 scope (only `system/` exists from M1). The manifest builder must silently skip missing directories (consistent with M1 behavior for `experiments/`).
- **PS-07 route_scope validation**: Route-skill frontmatter declares `route_scope` as a list. Invalid or unknown route values (e.g., `route_scope: ["INVALID_ROUTE"]`) should be skipped with WARN-level logging. The manifest builder should validate route_scope against the canonical 8-route set.
- **PS-08 route skill vs role prompt precedence**: Shared policy and role prompt are authoritative over route-skill content per FR-1.4.11. The assembler must never allow route-skill content to weaken safety, evidence, or disclosure rules from higher-authority layers.
- **PS-08 missing all route skills**: When `route_contexts.enabled: true` but none of the 8 route-skill assets exist, the assembler composes from shared policy + role prompt only. This is a degraded but valid state — no route-specific behavior, but the agent still functions (same as M1 baseline).
- **PS-08 dynamic controls rejection**: When dynamic control fields are present but not in the approved allowlist, the assembler drops them, records them in metadata, and does not elevate them into policy segments per TECHNICAL_DESIGN.md §3.5.2.3.
- **PS-08 route reclassification**: The assembler admits the route result from the semantic router. It must not reclassify or second-guess the route inside the assembler. Route reclassification is the router's responsibility.
- **LangSmith trace metadata for route skills**: When `route_contexts.enabled: true`, trace metadata must include `route`, `route_skill_used` (true/false), and `selected_skills` list. When a route skill is missing, `route_skill_used` is `false` and the gap is recorded.

## Requirements *(mandatory)*

### Functional Requirements

- **M2-FR-001 (PS-07)**: System MUST extend `PromptAssetLoader._build_manifest()` to scan `skills/routes/` subdirectory for `.md` files with frontmatter containing `agent_role`, `route_scope`, `status`, and `variant`. Route-skill assets MUST be keyed by `(agent_role, route_scope)` in the manifest. *(FR-1.4.7)*
- **M2-FR-002 (PS-07)**: Route-skill assets MUST be authored with frontmatter declaring `route_scope` as a list of canonical route names from `StockQueryRouter`. Frontmatter with unknown or invalid route values MUST be skipped with WARN-level logging. *(FR-1.4.7)*
- **M2-FR-003 (PS-07)**: The manifest builder MUST silently skip missing `skills/routes/` directories (consistent with M1 behavior). Only existing subdirectories are scanned. *(Operational resilience)*
- **M2-FR-004 (PS-08)**: System MUST implement a `PromptAssembler` component that composes a `CompiledPrompt` from a `PromptSelection`, a normalized route result, and optional dynamic controls. Assembly order per TECHNICAL_DESIGN.md §3.5.2.3: shared policy → always-active skills → route-specific skill → bounded memory context → evidence and tool-derived facts → task framing → output contract. *(FR-1.4.7, FR-1.4.16)*
- **M2-FR-005 (PS-08)**: The `CompiledPrompt` output MUST include `compiled_text` (str), `segment_manifest` (List of segment type and source), `prompt_version` (str), `prompt_variant` (str), and `trace_metadata` (dict) containing `route`, `selected_skills`, `fallback_used`, and `prompt_metadata`. *(FR-1.4.16, NFR-5.2.8)*
- **M2-FR-006 (PS-08)**: When the route-specific skill is missing for the classified route, the assembler MUST continue with shared policy and role prompt only, record the gap in `trace_metadata.missing_route_skills`, and NEVER synthesize substitute instructions. *(FR-1.4.11, FR-1.4.7)*
- **M2-FR-007 (PS-08)**: Route-skill content MUST NOT weaken shared policy safety, evidence, or disclosure rules per FR-1.4.11 precedence. Lower-authority layers (route skills) can narrow task framing but cannot override higher-authority layers (shared policy, role prompt). *(FR-1.4.11)*
- **M2-FR-008 (PS-08)**: Dynamic control fields from request context MUST be validated against an approved allowlist. Unrecognized fields MUST be dropped, recorded in trace metadata, and not elevated into policy segments. *(TECHNICAL_DESIGN.md §3.5.2.3)*
- **M2-FR-009 (PS-08)**: The agent invocation path MUST use `PromptAssembler` to compose the system prompt when `route_contexts.enabled: true` in config. The `PromptSelection` from `PromptAssetLoader.resolve()` is passed to `PromptAssembler.compile()` along with the route result. *(FR-1.4.7)*
- **M2-FR-010 (PS-08)**: The agent MUST emit `route`, `route_skill_used`, `selected_skills`, and `prompt_selection_mode` in response metadata and LangSmith trace metadata for every invocation when `route_contexts.enabled: true`. *(NFR-5.2.8 — M2 delivers prompt selection mode; guardrail outcome metadata is deferred to M3)*

### Non-Functional Requirements

- **M2-NFR-001 (PS-08)**: Prompt assembly MUST NOT add more than 50ms to request processing time. Segment classification and compilation are deterministic in-memory operations.
- **M2-NFR-002 (PS-08)**: Route-skill asset lookup from the manifest MUST complete in <5ms (in-memory dict lookup after manifest is built).
- **M2-NFR-003 (PS-07)**: Route-skill assets MUST be authored as standalone markdown files with frontmatter — no secondary manifest file required (consistent with M1 pattern).

### Key Entities

- **RouteSkillAsset**: A frontmatter-annotated markdown file under `src/prompts/skills/routes/` containing route-specific behavioral instructions. Key metadata: `name`, `version`, `agent_role`, `route_scope` (list), `status`, `variant`, `locale`.
- **CompiledPrompt**: The output contract from `PromptAssembler.compile()` containing the assembled prompt text, segment manifest, prompt identity, and trace metadata.
- **SegmentManifest**: A list within `CompiledPrompt` describing each segment's type (`shared_policy`, `role_prompt`, `route_skill`, `memory_context`, `evidence`, `task_framing`, `output_contract`), source asset path, and authority level.
- **Route Context Config**: Extended `prompts.*` configuration surface including `route_contexts.enabled`, `route_contexts.directory`, and `route_contexts.supported_routes` list.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-M2-01**: Route-skill assets exist for all 8 `StockQueryRouter` categories under `src/prompts/skills/routes/`. The manifest builder discovers all 8 assets and keys them by `(agent_role, route_scope)`.
- **SC-M2-02**: `PromptAssembler` composes a deterministic prompt from shared policy + role prompt + route skill when the route skill exists. Response metadata includes `route`, `route_skill_used: true`, and `selected_skills`.
- **SC-M2-03**: When a route skill is missing, the assembler continues without it, records the gap in metadata, and does not synthesize substitute instructions. The agent still produces a coherent response.
- **SC-M2-04**: Route-skill content does not weaken shared policy safety rules. Verified by test that route-skill content containing counter-policy instructions does not alter agent refusal posture.
- **SC-M2-05**: Assembly completes in <50ms (verified by unit benchmark).
- **SC-M2-06**: The agent functions correctly when `route_contexts.enabled: true` but no route-skill assets exist (degraded mode falls back to role prompt only, same as M1).

## Assumptions

- Route-skill assets are authored as standalone markdown files under `src/prompts/skills/routes/` following the same frontmatter conventions as M1's `system/react_analyst.md`. No additional manifest file is required.
- The 8 canonical route categories from `StockQueryRouter` are the authoritative route set: `PRICE_CHECK`, `NEWS_ANALYSIS`, `PORTFOLIO`, `TECHNICAL_ANALYSIS`, `FUNDAMENTALS`, `IDEAS`, `MARKET_WATCH`, `GENERAL_CHAT`.
- Route classification is owned by the existing `StockQueryRouter` (semantic-router library). `PromptAssembler` consumes the route result — it does not reclassify.
- Shared policy assets (`system/shared/investment_safety.md`, `system/shared/response_contract.md`, `system/shared/tool_use_policy.md`) are not yet authored — M2 scope uses the existing `react_analyst.md` role prompt as the shared policy base until shared policy assets are extracted (deferred to M3 if needed).
- Route-skill assets narrow task framing within their route domain but cannot weaken shared safety policy. Authority precedence: shared policy > role prompt > route skill > dynamic controls.
- M2 does not address experiment modes (PS-11), evaluation harness (PS-09/PS-10), or ResponseGuardrailMiddleware (PS-10). Those are M3-M5 scope.
- The `@dynamic_prompt` middleware from LangChain is the implementation strategy for `PromptAssembler`, but the assembler is also implementable as a standalone function without middleware dependency.
