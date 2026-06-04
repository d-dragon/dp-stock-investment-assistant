# Research Findings — M2 Route-Aware Skills

**Date**: 2026-06-04
**Feature**: `specs/prompt-system-milestone2/spec.md`
**Branch**: `prompt-system-milestone2`

## Purpose

Resolve all unknowns from Technical Context and validate design decisions against existing codebase patterns before Phase 1 design.

## Unknowns Resolved

### 1. M1 `_build_manifest()` extension point
- **Question**: How does M1's manifest builder scan subdirectories, and what is the cleanest extension for `skills/routes/`?
- **Finding**: M1's `_build_manifest()` iterates over `("system", "skills", "experiments")` top-level subdirs using `dir_path.glob("*.md")`. It does NOT recurse into subdirectories. Since `skills/` may eventually contain both `routes/` and `always_on/` subdirs, the M2 extension should add `"skills/routes"` as a fourth scan path alongside the existing three. This preserves the flat-scan pattern and avoids deep recursion.
- **Decision**: Add `"skills/routes"` to the scan tuple in `_build_manifest()`. This is additive and does not change existing M1 scanning behavior.

### 2. `route_scope` frontmatter field
- **Question**: What format should `route_scope` take in frontmatter, and how is it validated?
- **Finding**: The canonical route enum `StockQueryRoute` in `src/core/routes.py` defines 8 members: `PRICE_CHECK`, `NEWS_ANALYSIS`, `PORTFOLIO`, `TECHNICAL_ANALYSIS`, `FUNDAMENTALS`, `IDEAS`, `MARKET_WATCH`, `GENERAL_CHAT`. Route-skill assets declare `route_scope` as a YAML list (e.g., `route_scope: ["PRICE_CHECK"]`). Validation checks each value against `StockQueryRoute.__members__`.
- **Decision**: `route_scope` is a list type in frontmatter. The manifest builder validates each value against `StockQueryRoute.__members__` keys. Invalid values are WARN-logged and the file is skipped.

### 3. `CompiledPrompt` contract shape
- **Question**: What fields should `CompiledPrompt` contain, and how does it differ from `PromptSelection`?
- **Finding**: `PromptSelection` (M1) identifies *which* assets were selected. `CompiledPrompt` (M2) contains the *assembled result*: the compiled text, the segment manifest showing which segments compose it, and trace metadata. TECHNICAL_DESIGN.md §3.5.1 defines `segment_manifest`, `dropped_dynamic_fields`, `tool_policy_snapshot`, `prompt_metadata`. The spec §Key Entities adds `compiled_text`.
- **Decision**: `CompiledPrompt` is a frozen dataclass with: `compiled_text` (str), `segment_manifest` (List[SegmentEntry]), `prompt_version` (str), `prompt_variant` (str), `trace_metadata` (Dict). Each `SegmentEntry` has `type`, `source_path`, `authority_level`.

### 4. Config surface for `route_contexts`
- **Question**: What does the `prompts.route_contexts.*` config block look like?
- **Finding**: M1's config already has `prompts.registry.*`, `prompts.system.*`, `prompts.selection_mode`, `prompts.default_locale`, `prompts.experiments.*`. The M2 addition follows the same YAML pattern. TECHNICAL_DESIGN.md §3.5.8 shows the target config namespace as `prompts.agents.{role}.route_skill_map`.
- **Decision**: Add `prompts.route_contexts.enabled` (bool, default false), `prompts.route_contexts.directory` (str, default "skills/routes"), `prompts.route_contexts.supported_routes` (list, auto-derived from `StockQueryRoute` or explicit override).

### 5. Agent integration point
- **Question**: Where in `StockAssistantAgent` does `PromptAssembler` wire in?
- **Finding**: M1 already modified `StockAssistantAgent.__init__()` to accept an optional `prompt_asset_loader`. M2 extends this by also accepting an optional `prompt_assembler`. When `route_contexts.enabled: true`, the agent's `_load_system_prompt()` uses `prompt_assembler.compile()` instead of the raw `PromptSelection` content. The route result is obtained from the existing `stock_query_router`.
- **Decision**: Add `prompt_assembler` parameter to `StockAssistantAgent.__init__()`. In `_load_system_prompt()`, when both assembler and `route_contexts.enabled` are set, call `assembler.compile(selection, route_result)` to produce `CompiledPrompt`, then use `compiled_prompt.compiled_text` as the system prompt.

### 6. PromptAssembler implementation strategy
- **Question**: Implement as LangChain `@dynamic_prompt` middleware or standalone function?
- **Finding**: The roadmap and ADR-002 reference `@dynamic_prompt` middleware, but the spec assumes standalone is acceptable. LangChain's `@dynamic_prompt` decorator is designed for simple template-string substitution, not for multi-segment deterministic assembly with authority ordering and segment classification. A standalone `PromptAssembler` class with a `compile()` method is cleaner, more testable, and directly aligns with TECHNICAL_DESIGN.md §3.5.2.1's component diagram.
- **Decision**: Implement `PromptAssembler` as a standalone class with a `compile(selection: PromptSelection, route_result: RouteResult, runtime_context: Optional[Dict] = None) -> CompiledPrompt` method. No `@dynamic_prompt` middleware dependency.

## Technology Choices

### 7. PromptAssetLoader extension
- **Decision**: Modify `_build_manifest()` scan paths to include `"skills/routes"`.
- **Rationale**: Minimal change to existing, well-tested M1 code. Follows same pattern as existing three subdirs.
- **Alternatives considered**: Recursive scanning of `skills/` — rejected because `skills/routes/` is the only M2 target; recursive scan is over-engineered.

### 8. Segment classification
- **Decision**: Use a `SegmentType` enum with values: `SHARED_POLICY`, `ROLE_PROMPT`, `ROUTE_SKILL`, `MEMORY_CONTEXT`, `EVIDENCE`, `TASK_FRAMING`, `OUTPUT_CONTRACT`.
- **Rationale**: Matches TECHNICAL_DESIGN.md §3.5.2.3's assembly order exactly. Enables `segment_manifest` output with machine-detectable classifications.
- **Alternatives considered**: String-based segment labels — rejected due to lack of type safety and discoverability.

## Best Practices

### 9. Missing-skill degradation
- **Following M1 pattern**: When a route skill is missing, the assembler continues with available segments (shared policy + role prompt), records `missing_route_skills` in `trace_metadata`, and does NOT raise or block. Same degraded-but-functional pattern as M1's `_resolve_fallback()`.

### 10. Dynamic controls allowlist
- **Following TECHNICAL_DESIGN.md §3.5.4**: Dynamic controls are admitted only from schema-approved request fields. The assembler validates against a configurable allowlist (`prompts.dynamic_controls.allowed_fields`). Unknown fields are dropped and recorded in `trace_metadata.dropped_dynamic_fields`.
