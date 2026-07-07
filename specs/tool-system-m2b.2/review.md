# M2B.2 Implementation Review

**Feature**: Internal Symbol and Normalization Backbone - M2B.2
**Status**: Verified
**Date**: 2026-07-06

## Implementation Summary

M2B.2 implements the internal tool-system backbone that follows the verified M2B.1 gateway baseline:

- Internal symbol-store lookup, list, coverage, normalization, degraded-state, and disabled live-market-data semantics in `StockSymbolTool`.
- Provider adapter descriptors and provider selection policy below model-visible tool descriptors.
- Tool execution envelopes, normalized output kinds, source metadata, freshness metadata, degraded states, and raw-payload quarantine.
- Request-scoped `ToolContextPack` assembly and retained-derivative guardrails.
- Disabled-by-default symbol mutation receipts and no-durable-write mutation guards.
- Prompt-safe context projection integration at the agent boundary without introducing public API contract changes.

## Verification Evidence

| Gate | Result |
|------|--------|
| `python -m pytest tests/test_stock_symbol_m2b2.py -q` | 18 passed |
| `python -m pytest tests/test_provider_policy_m2b2.py -q` | 6 passed |
| `python -m pytest tests/test_tool_normalization_m2b2.py -q` | 21 passed |
| `python -m pytest tests/test_tool_retention_m2b2.py -q` | 13 passed |
| `python -m pytest tests/test_tool_retention_m2b2.py -q -k mutation` | 8 passed, 5 deselected |
| `python -m pytest tests/test_stock_symbol_m2b2.py tests/test_provider_policy_m2b2.py tests/test_tool_normalization_m2b2.py tests/test_tool_retention_m2b2.py -q` | 58 passed |
| `python -m pytest tests/test_tool_gateway_m2b1.py -q` | 30 passed |
| `python -m pytest tests/test_tools.py tests/test_stock_query_router.py tests/test_agent_regression.py -q` | 112 passed |
| `python -m pytest tests/test_stock_symbol_m2b2.py tests/test_provider_policy_m2b2.py tests/test_tool_normalization_m2b2.py tests/test_tool_retention_m2b2.py --cov=core.tools --cov-report=term-missing --cov-fail-under=56` | 58 passed, 73.75% coverage |
| `python -m pytest tests/test_tool_normalization_m2b2.py tests/test_agent_regression.py --cov=core.tools.context --cov=core.tools.normalization --cov-report=term-missing --cov-fail-under=56` | 28 passed, 87.25% coverage |

## Scope Checks

| Check | Result |
|-------|--------|
| OpenAPI public contract impact | `docs/openapi.yaml` has no working-tree diff |
| Provider visibility | Provider adapter descriptors remain below model-visible descriptors and route surfaces |
| Requirements alignment checklist | No unchecked items remain |
| Task-to-requirement mapping | 105 tasks, 105 mapped, 0 missing, 0 unknown |
| M2B.1 compatibility | Existing gateway, tool, router, and agent regression suites pass |
| Traceability sync | `python scripts/sync_spec_status.py --gate` passed |
| Diff hygiene | `git diff --check` passed with line-ending warnings only |

## Coverage Notes

The original prompt-boundary coverage command targeted the full `stock_assistant_agent` module. That module includes broad interactive, model-provider, streaming, and lifecycle paths outside the M2B.2 prompt-safe projection change. The executable gate now covers the touched prompt-boundary surfaces, `core.tools.context` and `core.tools.normalization`, while `tests/test_tool_normalization_m2b2.py` imports `StockAssistantAgent` with provider stubs and exercises `_build_prompt_safe_tool_context_projection`.

## Preservation Evidence

| Task | Disposition | Evidence |
|------|-------------|----------|
| T017 | Accepted preservation evidence | `src/core/tools/surface.py` was intentionally unchanged. Route-filtered exposure still returns only `model_visible_dict()` payloads, and provider adapter details remain below the model-visible surface. Evidence: `test_provider_adapters_are_hidden_from_model_visible_surface` and `test_provider_adapter_names_and_filter_reasons_are_not_model_visible` pass. |
| T079 | Accepted preservation-by-absence evidence | `src/services/symbols_service.py` and `src/data/repositories/symbol_repository.py` were intentionally unchanged. Targeted inspection found no `ToolContextPack`, prompt projection, normalized output bundle, or raw tool context persistence in those durable service/repository paths. Full request-scoped context remains isolated to `src/core/tools/context.py` and prompt-safe projection code. |
| T089 | Accepted no-exposure preservation evidence | `src/services/symbols_service.py` and `src/data/repositories/symbol_repository.py` write paths remain outside model-visible tool execution. Production symbol mutations are blocked in `src/core/tools/mutation_receipts.py` and surfaced as degraded/receipt-shaped normalized outputs instead of durable writes by default. |

## Final Verification Verdict

M2B.2 verification is accepted as complete for the governed scope after remediation of the three verify-run findings:

- `A1`: `T105` is complete after verify-tasks and verify-run evidence was recorded.
- `E1`: `T079` and `T089` preservation findings are accepted explicitly in this review.
- `E2`: lifecycle promotion is backed by complete tasks, this review, `.verify-done`, and synchronized traceability reports.

The feature remains scoped to M2B.2 internal symbol-store direction, provider policy, normalized outputs, `ToolExecutionEnvelope`, request-scoped `ToolContextPack`, retained derivatives, degraded states, and disabled-by-default mutation controls. Deferred M2B.3+ capabilities remain out of scope.
