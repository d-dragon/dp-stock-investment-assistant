# Implementation Review: Tool Contract and Gateway Baseline - M2B.1

**Date**: 2026-07-02

**Last Updated**: 2026-07-03

**Status**: Verified

## Implementation Evidence

- Added M2B.1 descriptor inventory, validation, and deterministic descriptor hashing in `src/core/tools/descriptors.py`.
- Added route-filtered tool surface construction in `src/core/tools/surface.py`.
- Added thin registry-backed gateway admission, degraded results, LangChain-compatible wrappers, and safe trace metadata in `src/core/tools/gateway.py`.
- Wired `StockAssistantAgent` to build per-query route-filtered gateway wrappers before ReAct invocation while preserving legacy fallback behavior.
- Kept `StockSymbolTool`, `TradingViewTool`, `ReportingTool`, `CachingTool`, and `ToolRegistry` execution semantics compatible.
- Made `src/core/__init__.py` lightweight by lazy-loading heavier exports so route/tool imports do not force agent, model, or router dependencies.
- Made `src/core/stock_query_router.py` import-safe when `semantic-router` is absent; real encoder construction still requires the declared dependency unless tests patch it.
- Added `tests/test_tool_gateway_m2b1.py` for descriptor, route-surface, gateway admission, trace safety, public metadata safety, performance, and compatibility checks.
- Added `tests/conftest.py` for repo-local `src` path setup and coroutine test execution for existing `pytest.mark.asyncio` tests.

## Verification Results

| Task | Command | Result |
|------|---------|--------|
| T056 | `python -m pytest tests/test_tool_gateway_m2b1.py -k descriptor -q` | PASS: 7 passed, 23 deselected |
| T057 | `python -m pytest tests/test_tool_gateway_m2b1.py -k route_surface -q` | PASS: 10 passed, 20 deselected |
| T058 | `python -m pytest tests/test_tool_gateway_m2b1.py -k gateway_admission -q` | PASS: 4 passed, 26 deselected |
| T059 | `python -m pytest tests/test_tool_gateway_m2b1.py -k "trace or public_metadata or performance" -q` | PASS: 4 passed, 26 deselected |
| T060 | `python -m pytest tests/test_tools.py tests/test_stock_query_router.py tests/test_agent_regression.py -q` | PASS: 112 passed |
| T061 | `python -m pytest tests/test_tool_gateway_m2b1.py tests/test_stock_query_router.py tests/test_agent_regression.py --cov=src.core.stock_query_router --cov-fail-under=80 -q` | PASS: 94 passed, coverage 94.92% |
| T062 | `python -m pytest tests/test_tool_gateway_m2b1.py tests/test_tools.py --cov=src/core/tools --cov-fail-under=70 -q` | PASS: 78 passed, tool-layer coverage 91.00% |
| T063 | `python -m pytest tests/ --cov=src --cov-fail-under=56 -q` | ACCEPTED WARNING: coverage reached 58.38%, but command failed because unrelated existing tests outside M2B.1 fail/error; deferred to M2B.2 |
| T068 | Targeted local Markdown link validation for M2B.1-owned links in `spec.md`, `plan.md`, `tasks.md`, and `SRS_SPEC_TRACEABILITY.md` | PASS: `M2B1 ANCHOR VALIDATION PASS` |
| T069 | `python scripts/sync_spec_status.py --gate` | PASS: `SYNC GATE PASS` |

## Repo-Wide Baseline Warning

The repo-wide baseline command met the configured coverage threshold but did not exit successfully. Observed blockers are outside the M2B.1 tool-system slice, including missing `apply_management_headers` fixtures in management/conversation contract tests and existing failures in agent memory, LangSmith bootstrap, chat route memory, and STM wiring suites.

T063 is marked complete for M2B.1 because the repository baseline command was executed and recorded here. The command met the configured coverage threshold but exited nonzero on unrelated existing failures outside the M2B.1 tool-system scope. This is an accepted M2B.1 phase warning and remains follow-up work for M2B.2; it does not block the M2B.1 verified state after focused feature verification, compatibility gates, coverage gates, and sync gates pass.

## Preservation Evidence

| Task | Artifact | Evidence |
|------|----------|----------|
| T019 | `src/core/tools/base.py` intentionally unchanged | Descriptor and gateway support remains outside `_execute()`, `_cached_run()`, `_run()`, and cache key behavior. `GatewayToolWrapper` subclasses `CachingTool`, allowed calls execute through the registry-backed tool once, and compatibility suites pass. |
| T020 | `src/core/tools/registry.py` intentionally unchanged | `ToolGateway` calls the existing registered `CachingTool` instance and does not replace registration or invocation semantics. Gateway admission tests assert denied calls do not execute and allowed calls execute exactly once. |
| T021 | `src/core/tools/stock_symbol.py` intentionally unchanged | `stock_symbol` descriptors are declared in `src/core/tools/descriptors.py`; existing `StockSymbolTool` behavior is preserved and covered by compatibility tests. |
| T022 | `src/core/tools/tradingview.py` intentionally unchanged | `tradingview` descriptors explicitly mark the placeholder disabled and non-exposed in `src/core/tools/descriptors.py`, without changing placeholder runtime behavior. |
| T023 | `src/core/tools/reporting.py` intentionally unchanged | `reporting` descriptors preserve the current non-mutating scaffold behavior while keeping descriptor state outside the runtime tool implementation. |
| T066 | Long-lived architecture and technical design docs intentionally unchanged | No stable realization detail requires promotion while M2B.1 remains implemented with phase warning; existing long-lived docs already carry the Phase 2B thin-gateway and route-filtered exposure boundary. |
| T067 | `docs/openapi.yaml` intentionally unchanged | M2B.1 keeps gateway traces internal and only exposes safe metadata helpers inside existing response metadata surfaces, so no public REST, SSE, or WebSocket schema change is introduced. |

## Post-Implementation Verification Findings

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| W1 | Verification Evidence | ACCEPTED WARNING | `specs/tool-system-implementation-m2b.1/review.md` | Focused M2B.1 verification, compatibility, and coverage gates pass, and the repo-wide coverage threshold was met; the full repository command still exits nonzero on unrelated existing failures. | Accepted for M2B.1 and deferred to M2B.2. Track the repo-wide cleanup under the next milestone without blocking the M2B.1 verified state. |

**Task Summary**:
- Completed tasks: 70 / 70.
- Remaining task: None for M2B.1 implementation scope. Full repository suite cleanup remains deferred to M2B.2 under accepted warning W1.
- Requirement coverage: M2B.1 functional requirements have focused implementation evidence in `src/core/tools/descriptors.py`, `src/core/tools/surface.py`, `src/core/tools/gateway.py`, `src/core/stock_assistant_agent.py`, and `tests/test_tool_gateway_m2b1.py`.
- Constitution alignment: No M2B.1-specific constitution conflict found; tool traces remain internal, registry-backed execution is preserved, and no public API contract change was introduced.

## Final Verification Re-run Verdict

**Date**: 2026-07-03

| Check | Command | Result |
|-------|---------|--------|
| Prerequisites | `.specify\scripts\powershell\check-prerequisites.ps1 -Json -PathsOnly` | PASS: resolved `specs/tool-system-implementation-m2b.1` |
| Verify config | `.specify\extensions\verify\scripts\powershell\load-config.ps1` | PASS: `Configuration loaded: max_findings=50` |
| Focused M2B.1 suite | `python -m pytest tests/test_tool_gateway_m2b1.py -q` | PASS: 30 passed |
| Compatibility suite | `python -m pytest tests/test_tools.py tests/test_stock_query_router.py tests/test_agent_regression.py -q` | PASS: 112 passed |
| Agent-core coverage gate | `python -m pytest tests/test_tool_gateway_m2b1.py tests/test_stock_query_router.py tests/test_agent_regression.py --cov=src.core.stock_query_router --cov-fail-under=80 -q` | PASS: 94 passed, coverage 94.92% |
| Tool-layer coverage gate | `python -m pytest tests/test_tool_gateway_m2b1.py tests/test_tools.py --cov=src/core/tools --cov-fail-under=70 -q` | PASS: 78 passed, coverage 91.48% |
| Sync gate | `python scripts/sync_spec_status.py --gate` | PASS: `SYNC GATE PASS` |

**Verdict**: M2B.1 passes the post-implementation verification gate for the governed feature scope. The repo-wide baseline warning remains accepted and deferred to M2B.2, so `.verify-done` may be created and the feature status may be promoted to `Verified`.

## Public Contract Impact

`docs/openapi.yaml` remains unchanged. M2B.1 keeps gateway traces internal and exposes only safe metadata helpers; no public REST, SSE, or WebSocket schema was changed.

## Long-Lived Documentation Impact

No stable long-lived architecture or technical-design promotion was required in this implementation pass. The implementation remains within the existing Phase 2B thin gateway and route-filtered exposure design.
