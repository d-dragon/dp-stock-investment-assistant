# Quickstart: Tool Contract and Gateway Baseline - M2B.1

This guide describes focused validation for the M2B.1 plan. Commands assume the repository root is the working directory.

## Prerequisites

- Python environment with `requirements.txt` installed.
- Existing test configuration is available.
- No public API contract update is expected for this milestone.

## 1. Descriptor Inventory Validation

Run the focused descriptor tests after implementation:

```powershell
python -m pytest tests/test_tool_gateway_m2b1.py -k descriptor -q
```

Expected outcome:
- `StockSymbolTool`, `TradingViewTool`, and `ReportingTool` each have capability and policy descriptors.
- `TradingViewTool` is descriptor-complete but disabled/non-exposed while placeholder behavior remains.
- Model-visible capability descriptors exclude internal policy, credential, provider, and parser details.

## 2. Route Surface Validation

Run route filtering fixtures:

```powershell
python -m pytest tests/test_tool_gateway_m2b1.py -k route_surface -q
```

Expected outcome:
- Every tested route exposes only admitted tools.
- Routes without admitted M2B.1 tools expose an empty surface.
- Disabled, drifted, internal-only, unrelated, or risk-blocked tools remain hidden with internal filter reasons.

## 3. Gateway Admission Validation

Run admission fixtures:

```powershell
python -m pytest tests/test_tool_gateway_m2b1.py -k gateway_admission -q
```

Expected outcome:
- Allowed calls execute through the current registry-backed tool path.
- Invalid arguments, route mismatch, blocked risk, license-unclear posture, provider/cache/freshness failure where applicable, and descriptor drift fail closed.
- Blocked/degraded calls do not execute the underlying tool.

## 4. Compatibility Validation

Run current tool tests:

```powershell
python -m pytest tests/test_tools.py tests/test_stock_query_router.py tests/test_agent_regression.py -q
```

Expected outcome:
- Existing `CachingTool`, `ToolRegistry`, `StockSymbolTool`, `ReportingTool`, and `TradingViewTool` behavior remains compatible.
- User-facing behavior does not regress except for safe metadata, warnings, or degraded-state disclosures where admitted.

## 5. Agent Boundary Validation

Run focused agent/router tests:

```powershell
python -m pytest tests/test_tool_gateway_m2b1.py tests/test_stock_query_router.py tests/test_agent_regression.py --cov=src.core.stock_query_router --cov-fail-under=80 -q
python -m pytest tests/test_tool_gateway_m2b1.py tests/test_tools.py --cov=src/core/tools --cov-fail-under=70 -q
```

Expected outcome:
- The agent still uses a single ReAct runtime.
- Tool exposure is route-filtered before model invocation.
- Gateway admission wraps selected tool calls without creating a second runtime or remote gateway service.

## 6. Sync Gate

After updating traceability artifacts, regenerate sync reports:

```powershell
python scripts/sync_spec_status.py --gate
```

Expected outcome:
- `SYNC GATE PASS`
- `specs/spec-sync-status.md` shows `tool-system-implementation-m2b.1` as `planned` and `current`.
- `docs/domains/agent/SRS_SPEC_TRACEABILITY.md` reverse trace rows for mapped SRS items point to this feature with `planned` status.
