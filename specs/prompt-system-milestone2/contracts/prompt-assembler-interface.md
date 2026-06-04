# PromptAssembler Interface Contract

**Date**: 2026-06-04
**Authority**: TECHNICAL_DESIGN.md §3.5.2.1, §3.5.2.3

## Component Interface

```python
class PromptAssembler:
    """Compose a deterministic prompt contract from governed assets.

    Admits only PromptSelection, normalized route result, approved dynamic
    controls, bounded memory summary, evidence bundles, and output-contract
    requirements. Assembly order per TECHNICAL_DESIGN.md §3.5.2.3.
    """

    def compile(
        self,
        selection: PromptSelection,
        route: StockQueryRoute,
        runtime_context: Optional[Dict[str, Any]] = None,
    ) -> CompiledPrompt:
        """Compose a compiled prompt from the given inputs.

        Args:
            selection: Resolved prompt assets from PromptAssetLoader.
            route: Normalized route classification result.
            runtime_context: Optional dict with approved dynamic controls,
                bounded memory summary, evidence bundles, output contract.

        Returns:
            CompiledPrompt with assembled text, segment manifest, and
            trace metadata.

        Raises:
            ValueError: If selection has no assets (should not happen
                since PromptAssetLoader enforces fallback).
        """
        ...
```

## Input Contracts

### PromptSelection (from M1)

```python
@dataclass(frozen=True)
class PromptSelection:
    selected_assets: List[str]       # Relative asset paths
    prompt_version: str              # e.g. "1.0.0"
    prompt_variant: str              # e.g. "baseline"
    selection_mode: str              # "fixed", "forced", "shadow", "weighted"
    fallback_used: bool
    degraded_reason: Optional[str]
    trace_metadata: Dict[str, Any]
```

### RouteResult (from StockQueryRouter)

```python
@dataclass(frozen=True)
class RouteResult:
    route: StockQueryRoute
    confidence: float
    utterances_matched: Optional[List[str]] = None
```

## Output Contract

### CompiledPrompt

```python
@dataclass(frozen=True)
class SegmentEntry:
    type: SegmentType
    source_path: str        # Relative asset path, or "inline"
    authority_level: int    # 1 (highest) to 7 (lowest)

@dataclass(frozen=True)
class CompiledPrompt:
    compiled_text: str                    # Fully assembled prompt string
    segment_manifest: List[SegmentEntry]  # Ordered segment classifications
    prompt_version: str
    prompt_variant: str
    trace_metadata: Dict[str, Any]        # Route, skills, fallback, etc.
```

## Assembly Order (Deterministic)

Per TECHNICAL_DESIGN.md §3.5.2.3:

1. **Shared policy** — investment-safety rules (from role prompt or future shared assets)
2. **Role prompt** — agent role definition (from `PromptSelection` selected assets)
3. **Route skill** — route-specific context (resolved from manifest via `PromptSelection` + route)
4. **Memory context** — bounded conversation summary (from `runtime_context`)
5. **Evidence** — retrieved evidence and tool-derived facts (from `runtime_context`)
6. **Task framing** — specific task instruction (from `runtime_context`)
7. **Output contract** — format and structure rules (from `runtime_context`)

Each segment is separated by a `\n---\n` delimiter. Higher-authority segments (1-2) appear first; lower-authority segments (6-7) appear last.

## Degradation Rules

| Condition | Behavior | Metadata |
|-----------|----------|----------|
| Route skill asset missing for classified route | Skip segment; continue with available segments | `missing_route_skills: ["ROUTE"]`, `route_skill_used: false` |
| All route skills missing (empty manifest) | Compose from shared policy + role prompt only | `route_skill_used: false`, `missing_route_skills: ["ALL"]` |
| Dynamic control field not in allowlist | Drop field; continue with remaining controls | `dropped_dynamic_fields: ["field_name"]` |
| Memory/evidence/contract unavailable | Skip segment; compose from what's available | Segment omission visible in `segment_manifest` |

## Segment Classification Rules

Per TECHNICAL_DESIGN.md §3.5.4:

1. Assets from `system/` or `skills/` directories are static policy fragments
2. Dynamic controls from request context (bypassing frontmatter) are dynamic control fragments
3. Memory summaries, evidence bundles, and tool outputs are runtime evidence
4. Runtime evidence must never be promoted into instruction-bearing policy segments
5. When classification is ambiguous, default to request-scoped data rather than static policy
