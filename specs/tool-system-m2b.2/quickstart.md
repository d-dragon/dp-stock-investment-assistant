# Quickstart: Internal Symbol and Normalization Backbone - M2B.2

## Scope

Use this quickstart after implementation tasks are generated. M2B.2 is an internal agent/tool backbone feature; it should not require a dev server or public OpenAPI change.

## Preconditions

- Feature directory: `specs/tool-system-m2b.2`
- Feature status before implementation: `Planned`
- M2B.1 baseline remains verified.
- No public REST, SSE, Socket.IO, or OpenAPI contract change is expected.

## Focused Verification Commands

Run the existing M2B.1 compatibility gate:

```powershell
python -m pytest tests/test_tool_gateway_m2b1.py -q
```

Run M2B.2 focused tests after they are created:

```powershell
python -m pytest tests/test_stock_symbol_m2b2.py tests/test_provider_policy_m2b2.py tests/test_tool_normalization_m2b2.py tests/test_tool_retention_m2b2.py -q
```

Run the mutation-specific subset after the retention and mutation suite exists:

```powershell
python -m pytest tests/test_tool_retention_m2b2.py -q -k mutation
```

Run compatibility suites for current tools, routing, and agent wiring:

```powershell
python -m pytest tests/test_tools.py tests/test_stock_query_router.py tests/test_agent_regression.py -q
```

Run coverage checks for the touched tool and prompt-boundary surfaces:

```powershell
python -m pytest tests/test_stock_symbol_m2b2.py tests/test_provider_policy_m2b2.py tests/test_tool_normalization_m2b2.py tests/test_tool_retention_m2b2.py --cov=core.tools --cov-report=term-missing --cov-fail-under=56
python -m pytest tests/test_tool_normalization_m2b2.py tests/test_agent_regression.py --cov=core.tools.context --cov=core.tools.normalization --cov-report=term-missing --cov-fail-under=56
```

Run traceability sync after task, implementation, or verification evidence changes:

```powershell
python scripts/sync_spec_status.py --gate
```

## Expected Results

- Symbol normalization fixtures produce `SystemRecord` or `DegradedState`.
- Provider descriptors remain internal and fail closed on unreviewed licensing or production-ineligible status.
- Tool results are wrapped in `ToolExecutionEnvelope` and classified as exactly one normalized output kind.
- `ToolContextPack` contains normalized content only and excludes raw payloads.
- Production symbol-store writes remain disabled or degraded by default.
- Sync gate reports `tool-system-m2b.2` as current for the feature lifecycle stage.
