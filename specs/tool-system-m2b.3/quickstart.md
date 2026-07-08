# Quickstart: Vietnam Market and Visualization Coverage - M2B.3

## Purpose

Use this guide to validate the M2B.3 implementation after tasks are generated and implemented. Commands are local, deterministic, and should not require live provider credentials unless a later task explicitly adds an approved provider integration.

## Prerequisites

- Work from `feature/tool-system-m2b.3`.
- Use the repository Python environment.
- Keep `PYTHONPATH` compatible with existing tests; `tests/conftest.py` currently supports `core.*` imports.
- Do not add real provider credentials to tests or fixtures.

## Planned Focused Verification

```powershell
python -m pytest tests/test_market_data_tools.py -q
python -m pytest tests/test_tradingview_visualization.py -q
python -m pytest tests/test_market_route_evaluation.py -q
python -m pytest tests/test_market_attribution_cache.py -q
```

Expected outcomes:

- Vietnam quote/history and fundamentals produce normalized evidence or degraded states.
- P2 breadth/flow/disclosure/corporate-action paths are independently testable.
- TradingView outputs are always `VisualizationProvenance`.
- Route evaluation records at least 85% meaning-based accuracy.
- Provider/cache/trace metadata omits credentials, raw payloads, and unsafe internals.

## Regression Verification

```powershell
python -m pytest tests/test_tool_gateway_m2b1.py tests/test_provider_policy_m2b2.py tests/test_tool_normalization_m2b2.py -q
python -m pytest tests/test_stock_query_router.py tests/test_agent_regression.py -q
```

Expected outcomes:

- M2B.1 descriptor, route-surface, and gateway behavior remains intact.
- M2B.2 provider policy, normalization, and request-scoped context behavior remains intact.
- Existing route taxonomy remains static unless a governed route change is explicitly introduced.
- No public API contract behavior changes are required.

## Coverage Verification

```powershell
python -m pytest tests/test_stock_query_router.py tests/test_market_route_evaluation.py --cov=src.core.stock_query_router --cov-report=term-missing --cov-fail-under=80 -q
python -m pytest tests/test_market_data_tools.py tests/test_tradingview_visualization.py tests/test_market_route_evaluation.py tests/test_market_attribution_cache.py --cov=core.tools.market_data --cov=core.tools.tradingview --cov=core.tools.normalization --cov=core.tools.provider_policy --cov=core.tools.gateway --cov=core.tools.surface --cov-report=term-missing --cov-fail-under=70 -q
```

Expected outcomes:

- Route-evaluation touched surface stays above the agent-core threshold.
- M2B.3 tool-layer touched modules stay above the tool threshold without measuring unrelated legacy tools.

## Traceability Sync

```powershell
python scripts/sync_spec_status.py --gate
```

Expected outcome:

- `specs/spec-sync-status.md` reports `tool-system-m2b.3` as synchronized for the current lifecycle phase.
- `docs/domains/agent/SRS_SPEC_TRACEABILITY.md` maps the M2B.3 SRS items to the feature.

## Manual Review Checklist

- Confirm all M2B.3 market facts bind to canonical symbol identity or degrade.
- Confirm provider candidates are posture-gated and do not claim production readiness without license/ToS review.
- Confirm TradingView values are never used as canonical evidence in factual answers.
- Confirm generic web fetch, reporting persistence, remote admission, and symbol-store writes remain deferred.
- Confirm any long-lived architecture or technical-design promotion happens only after verified implementation evidence.
