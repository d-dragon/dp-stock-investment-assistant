# Quick Start — M2 Route-Aware Skills Implementation

**Date**: 2026-06-04
**Feature**: `specs/prompt-system-milestone2/spec.md`

## Prerequisites

- M1 implementation complete: `PromptAssetLoader`, `react_analyst.md`, `prompts.*` config, response metadata
- Python venv activated: `venv\Scripts\Activate.ps1`
- Working directory: repository root

## Implementation Order

### Phase 1: Route-Skill Assets (PS-07)

1. **Create route-skill assets**
   ```powershell
   mkdir src/prompts/skills/routes
   ```
   Create 8 frontmatter-annotated markdown files under `src/prompts/skills/routes/`:
   - `price_check.md`, `news_analysis.md`, `portfolio.md`
   - `technical_analysis.md`, `fundamentals.md`, `ideas.md`
   - `market_watch.md`, `general_chat.md`
   Each with frontmatter: `name`, `version`, `agent_role: react_analyst`, `route_scope`, `status: active`, `variant: baseline`.

2. **Extend PromptAssetLoader manifest**
   - In `_build_manifest()`, add `"skills/routes"` to the scan subdirectory tuple
   - Add `route_scope` validation: check values against `StockQueryRoute.__members__`
   - Invalid values → WARN-level log, skip file

3. **Verify manifest discovery**
   ```powershell
   python -c "
   from pathlib import Path
   from core.prompt_asset_loader import PromptAssetLoader
   loader = PromptAssetLoader(Path('src/prompts'), {'prompts': {'registry': {'refresh_window_seconds': 300}}})
   manifest = loader._build_manifest()
   for role, assets in manifest.items():
       for a in assets:
           print(f'{a.agent_role}:{a.frontmatter.get(\"route_scope\", \"N/A\")} -> {a.file_path}')
   "
   ```

### Phase 2: PromptAssembler (PS-08)

4. **Add data types** (`prompt_types.py`)
   - Add `SegmentType` enum with 7 members
   - Add `SegmentEntry` frozen dataclass
   - Add `CompiledPrompt` frozen dataclass

5. **Implement PromptAssembler** (`src/core/prompt_assembler.py`)
   - Constructor: accepts `prompt_root: Path`, `config: dict`, optional `logger`
   - `compile(selection, route, runtime_context) -> CompiledPrompt`
   - Assembly order: shared policy → role prompt → route skill → memory → evidence → task framing → output contract
   - Route skill resolution from manifest using `selection.selected_assets` + `route`
   - Missing skill degradation with metadata recording
   - Dynamic controls allowlist validation

6. **Wire into agent** (`stock_assistant_agent.py`)
   - Add `prompt_assembler` parameter to `__init__`
   - In `_load_system_prompt()`, check `config.get("prompts", {}).get("route_contexts", {}).get("enabled", False)`
   - If enabled: call `prompt_assembler.compile(selection, route_result)` → use `compiled_prompt.compiled_text`
   - If disabled: unchanged M1 behavior

7. **Update config** (`config/config.yaml`)
   ```yaml
   prompts:
     # ... existing M1 config ...
     route_contexts:
       enabled: false
       directory: "skills/routes"
       supported_routes:
         - PRICE_CHECK
         - NEWS_ANALYSIS
         - PORTFOLIO
         - TECHNICAL_ANALYSIS
         - FUNDAMENTALS
         - IDEAS
         - MARKET_WATCH
         - GENERAL_CHAT
     dynamic_controls:
       allowed_fields: []
       reject_unknown_fields: true
   ```

### Phase 3: Tests

8. **PromptAssembler unit tests** (`tests/test_prompt_assembler.py`)
   - Test assembly order (all segments present in correct order)
   - Test missing route skill degradation
   - Test all route skills missing (empty manifest)
   - Test dynamic controls allowlist rejection
   - Test segment classification correctness
   - Test performance (<50ms).

9. **Extended manifest tests** (`tests/test_prompt_asset_loader.py`)
   - Test `skills/routes/` scanning with valid route-skill assets
   - Test invalid `route_scope` values (WARN + skip)
   - Test missing `skills/routes/` directory (silent skip).

10. **Agent regression tests** (`tests/test_agent_regression.py`)
    - Test route-aware agent with `route_contexts.enabled: true`
    - Test route-aware agent with `route_contexts.enabled: false` (M1 parity)
    - Test metadata emission (`route`, `route_skill_used`, `selected_skills`)

### Phase 4: Verification & Sync

11. Run all tests: `pytest -v` — expect 29 M1 tests + ~20 new M2 tests all green.
12. Update long-lived docs after verification.

## Verification

```powershell
# Run all tests
pytest -v --tb=short

# Run specific M2 test files
pytest tests/test_prompt_assembler.py -v
pytest -k "route" -v

# Verify config loads correctly
python -c "from utils.config_loader import ConfigLoader; c=ConfigLoader.load_config(); print(c.get('prompts', {}).get('route_contexts', {}))"
```
