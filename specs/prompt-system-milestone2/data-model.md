# Data Model — M2 Route-Aware Skills

**Date**: 2026-06-04
**Feature**: `specs/prompt-system-milestone2/spec.md`
**Authority**: TECHNICAL_DESIGN.md §3.5.2.3 (PromptAssembler Realization Contract), §3.5.4 (Static and Dynamic Segment Realization)

## Entities

### RouteSkillAsset

An extension of the M1 `PromptAsset` pattern. A frontmatter-annotated markdown file under `src/prompts/skills/routes/` containing route-specific behavioral instructions for the ReAct agent.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Human-readable identifier (from frontmatter) |
| `version` | string | Yes | Semantic version (e.g. `"1.0.0"`) |
| `agent_role` | string | Yes | Target agent role (e.g. `"react_analyst"`) |
| `route_scope` | list[string] | Yes | Canonical route names this asset applies to (e.g. `["PRICE_CHECK"]`) |
| `status` | string | Yes | Lifecycle status (`active`, `draft`, `deprecated`) |
| `variant` | string | No | Variant label (default: `"baseline"`) |
| `locale` | string | No | Locale code (default: `"en"`) |
| `parity_group` | string | No | Locale parity group (default: `""`) |
| `content` | string | Yes | Prompt body text (after frontmatter) |
| `file_path` | Path | Yes | Absolute path to the markdown file |
| `frontmatter` | dict | No | Raw parsed frontmatter fields |

**Validation rules**:
- `route_scope` values MUST be members of `StockQueryRoute` enum
- `status` MUST be one of: `active`, `draft`, `deprecated`, `archived`
- `agent_role` MUST be a non-empty string
- Files with invalid frontmatter or unknown `route_scope` values are skipped with WARN-level logging

### CompiledPrompt

The output contract from `PromptAssembler.compile()`. Contains the fully assembled prompt string, segment manifest, and trace metadata.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `compiled_text` | string | Yes | The assembled prompt string ready for agent invocation |
| `segment_manifest` | list[SegmentEntry] | Yes | Ordered list of segments that comprise the compiled prompt |
| `prompt_version` | string | Yes | Version of the resolved prompt lineage |
| `prompt_variant` | string | Yes | Variant label (e.g. `"baseline"`) |
| `trace_metadata` | dict | Yes | Metadata for observability (see below) |

**trace_metadata fields**:
- `route` (str): The classified route name
- `route_skill_used` (bool): Whether a route-specific skill was resolved
- `selected_skills` (list[str]): Names of skills included in assembly
- `fallback_used` (bool): Whether fallback occurred
- `missing_route_skills` (list[str], optional): Route names that had no asset
- `dropped_dynamic_fields` (list[str], optional): Dynamic control fields that were rejected
- `prompt_selection_mode` (str): From the resolved `PromptSelection`
- `prompt_version` (str): Effective prompt version
- `prompt_variant` (str): Effective prompt variant

### SegmentEntry

A single segment within `CompiledPrompt.segment_manifest`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | SegmentType | Yes | Classification of this segment |
| `source_path` | string | Yes | Relative path of the asset that contributed this segment (or `"inline"` for built-in policy) |
| `authority_level` | int | Yes | Authority precedence (1 = highest, 7 = lowest) |

### SegmentType (Enum)

Maps to the deterministic assembly order from TECHNICAL_DESIGN.md §3.5.2.3.

| Member | Authority Level | Description |
|--------|----------------|-------------|
| `SHARED_POLICY` | 1 | Investment-safety rules and shared behavioral policy |
| `ROLE_PROMPT` | 2 | Agent role definition (e.g. `react_analyst.md`) |
| `ROUTE_SKILL` | 3 | Route-specific skill content |
| `MEMORY_CONTEXT` | 4 | Bounded memory summary |
| `EVIDENCE` | 5 | Retrieved evidence and tool-derived facts |
| `TASK_FRAMING` | 6 | Task-specific framing instructions |
| `OUTPUT_CONTRACT` | 7 | Output formatting and structure requirements |

## Relationships

```
SelectionTuple ──► PromptAssetLoader.resolve() ──► PromptSelection
                                                          │
                                                          ▼
RouteResult ──────────────────────────────────────► PromptAssembler.compile()
                                                          │
                                                          ▼
                                                     CompiledPrompt
                                                          │
                                                          ▼
                                                  StockAssistantAgent
                                                  (system prompt input)
```

- `PromptAssetLoader` produces a `PromptSelection` identifying which assets to use
- `PromptAssembler` consumes `PromptSelection` + `RouteResult` + optional runtime context
- `PromptAssembler` produces `CompiledPrompt` with segment classification
- `StockAssistantAgent` uses `CompiledPrompt.compiled_text` as the system prompt

## State Transitions

The `route_contexts.enabled` flag is the primary configuration toggle:

```
route_contexts.enabled: false → M1 behavior (single system prompt, no route assembly)
route_contexts.enabled: true  → M2 behavior (PromptAssembler creates route-aware prompt)
```

No persistent state is involved — all `CompiledPrompt` instances are request-scoped in-memory objects.

## Validation Rules Applied in M2

1. Route-skill assets must declare `route_scope` as a list. Scalar values are invalid (WARN + skip).
2. Route names in `route_scope` must match `StockQueryRoute.__members__`. Unknown routes are WARN + skip.
3. Missing `skills/routes/` directory is silently ignored (no error, no WARN — same as M1's `experiments/`).
4. When `route_contexts.enabled: true` but zero route-skill assets exist, assembly degrades to shared policy + role prompt only.
5. Dynamic control fields not in the approved allowlist are dropped and recorded in trace metadata.
