# Tasks: Tool System Integration and Verification

**Feature**: `specs/002-tool-system-integration-verification`
**Total Tasks**: 48
**Status**: Complete

**Note**: All tasks verified. Task markers below use sync-script-compatible format for traceability.

## Phase 0: Foundation and Setup (Tasks T001-T005)

- [x] T001 [P] Review predecessor spec, plan, tasks, and review evidence from `specs/tool-system-implementation-m2b.1/`, `specs/tool-system-m2b.2/`, and `specs/tool-system-m2b.3/`; confirm `.verify-done` markers exist for all three milestones.
- [x] T002 [P] Create integration fixture package `tests/fixtures/integration/__init__.py` and shared scenario base classes.
- [x] T003 [P] Create cross-boundary scenario fixtures in `tests/fixtures/integration/scenarios.py` covering route→tool-family→gateway→provider→normalization→response flows.
- [x] T004 [P] Create provider class verification fixtures in `tests/fixtures/integration/provider_classes.py` covering all 7 architectural provider classes.
- [x] T005 [P] Create architecture boundary test cases in `tests/fixtures/integration/boundary_cases.py` for risk class, prompt safety, symbol-tool separation, gateway purity, registry integrity, and STM evidence freedom.

## Phase 0a: Application Runtime Verification (Tasks T005a-T005h)

- [x] **T005a** Verify required runtime dependencies are available: Docker Compose (MongoDB, Redis), `config.yaml` with valid settings, `.env` with required API keys.
- [x] **T005b** Start MongoDB and Redis: `docker-compose up -d mongodb redis`; verify both containers report healthy status.
- [x] **T005c** Run database migration to ensure all collections and indexes exist: `python src/data/migration/db_setup.py`; verify output confirms successful schema creation.
- [x] **T005d** Start the API server in web mode on a background terminal: `python src/main.py --mode web --port 5000`; verify startup log shows "API Server" and server is listening.
- [x] **T005e** Verify API health endpoint: `curl http://localhost:5000/api/health` returns `{"status": "healthy"}` with the tool system components initialized.
- [x] **T005f** Start the CLI agent in a separate terminal: `python src/main.py --mode cli`; verify interactive prompt appears and process at least one query (e.g., "What is AAPL?") confirms the ReAct agent processes through route classification → ToolSurfaceBuilder → ToolGateway → response composition.
- [x] **T005g** Verify the tool system integration is active by inspecting agent startup logs for `ToolSurfaceBuilder`, `ToolGateway`, and `ToolRegistry` initialization messages.
- [x] **T005h** Stop running processes and verify clean teardown (no orphaned processes, no MongoDB/Redis connection leaks).

## Phase 1: Integrated Readiness (US1 — Tasks T006-T012)

- [x] T006 Create the main integration test module skeleton in `tests/test_tool_system_integration.py` with shared fixtures, helper assertions, and test class structure.
- [x] T007 [P] Add integration scenarios that exercise route filtering + gateway admission + provider selection + normalization + response composition in a single flow.
- [x] T008 [P] Add integration scenarios for degraded gateway paths (blocked route/tool, invalid args, blocked risk class, license-unclear, descriptor drift).
- [x] T009 [P] Add integration scenarios for mixed provider fallback (Vietnam-first → international fallback → degraded).
- [x] T010 [P] Add integration scenarios for cache-hit with freshness metadata preservation.
- [x] T011 [P] Add integration scenarios for Vietnamese and mixed-language prompts through the full route→gateway→provider→normalization pipeline.
- [x] T012 [P] Add integration scenarios for ambiguous/unsupported prompts with route degradation or disambiguation.

## Phase 2: Financial Evidence Audit (US2 — Tasks T013-T020)

- [x] T013 [P] Add evidence audit scenarios verifying source attribution completeness (provider/source, URL/reference, retrieved timestamp, effective timestamp, exchange, currency, freshness, license posture, warnings).
- [x] T014 [P] Add evidence audit scenarios for stale, expired, freshness-unknown, anonymous, blocked-license, missing-field, parser-limited, and provider-unavailable outcomes.
- [x] T015 [P] Add cache freshness scenarios verifying cache hits do not hide stale/unsupported evidence (TTL/expiry metadata, warning propagation, degraded-state on expired cache).
- [x] T016 [P] Add finance-safety scenarios verifying unsupported recommendations, guaranteed-return language, hype language, and unsupported certainty are blocked or conservatively rewritten.
- [x] T017 [P] Add public response safety scenarios verifying credentials, secrets, raw provider payloads, parser internals, hidden trace details, and unsafe implementation details are NOT leaked.
- [x] T018 [P] Add provider-backed trace metadata scenarios verifying selected route, tool family, adapter, provider class, license mode, fallback, timestamps, and degraded reasons are recorded.
- [x] T019 [P] Add attribution coverage counter scenarios for complete attribution, degraded no-source, stale-cache, provider/license blocked, and unsafe leak counts.
- [x] T020 [P] Add scenario proving provider-backed results with missing mandatory fields produce deterministic degraded states.

## Phase 3: Route and Tool Exposure Regression (US3 — Tasks T021-T027)

- [x] T021 [P] Add route regression scenarios for PRICE_CHECK, NEWS_ANALYSIS, TECHNICAL_ANALYSIS, FUNDAMENTALS, MARKET_WATCH routes with expected tool-family exposure.
- [x] T022 [P] Add route regression scenarios for ambiguous ticker-only, unsupported, and deferred-scope prompts verifying degradation or disambiguation.
- [x] T023 [P] Add Vietnamese and mixed-language route fixture scenarios for price, chart, fundamentals, disclosures, breadth, flow, and report-like prompts.
- [x] T024 [P] Add meaning-based classification accuracy measurement scenarios targeting ≥85% for Vietnamese/mixed-language fixtures.
- [x] T025 [P] Add route-tool exposure precision and recall measurement scenarios (reported separately from language-classification accuracy).
- [x] T026 [P] Add route regression scenarios proving only route-eligible, enabled, policy-admitted tool families are exposed for each route.
- [x] T027 [P] Add scenarios proving report-like prompts remain route/evaluation fixtures only (no report generation, no persistence).

## Phase 4: Visualization Boundary (US4 — Tasks T028-T032)

- [x] T028 [P] Add TradingView scenario for chart, widget, deep-link, ticker-tape, heatmap, screener, and symbol-validation verifying `VisualizationProvenance` classification.
- [x] T029 [P] Add scenarios proving TradingView numeric values (price, indicators, heatmap rows, screener values) are NOT used as canonical market evidence in factual answers.
- [x] T030 [P] Add TradingView degraded-state scenarios for unsupported views, ambiguous symbols, invalid intervals, unsupported widgets, and validation failures.
- [x] T031 [P] Add public metadata safety scenarios for TradingView outputs (no credentials, no raw payload leaks).
- [x] T032 [P] Add scenario proving factual market-data composition rejects TradingView values as evidence.

## Phase 5: Architecture Compliance (US6 — Tasks T033-T044)

- [x] T033 [P] Verify all 7 provider classes (in-system, official, licensed, Vietnam-native public web, wrapper/prototype, visualization provider, international fallback) produce correct architectural behavior — admitted sources pass through, lower-authority classes produce appropriate caveats or degraded states, and no adapter is silently promoted without governing policy review.
- [x] T034 [P] Verify each tool in `ToolRegistry` declares a correct architectural risk class (`read_only_evidence`, `bounded_transformation`, `workflow_mutation`, `external_side_effect`); verify no current tool exceeds `bounded_transformation`.
- [x] T035 [P] Verify `ToolGateway` admission enforces the risk-class ceiling — calls exceeding the admitted class for the current route/prompt are blocked with explicit degraded outcomes.
- [x] T036 [P] Verify prompt-facing tool policy cannot reclassify a tool below its registry-declared risk class.
- [x] T037 [P] Verify raw provider payloads, chart widget content, tool descriptor text, and document/page instructions are NOT present in the prompt assembly input — only normalized `ToolContextPack` content reaches the prompt boundary.
- [x] T038 [P] Verify `StockSymbolTool` handles symbol identity, aliases, exchange/currency identity, coverage, tags, and stored snapshots only — quote/history/fundamental/breadth/flow requests route through market-data tool families.
- [x] T039 [P] Verify `ToolGateway` does NOT contain provider-specific parsing logic — provider-specific fetch, health, licensing, and parsing remain in the provider adapter layer.
- [x] T040 [P] Verify `ToolRegistry` remains the authoritative inventory and enablement boundary for all tools — no replacement or bypass mechanism is present.
- [x] T041 [P] Verify STM checkpoint state (LangGraph `MongoDBSaver`) does not retain market facts (prices, ratios, valuations, OHLCV data) as persistent memory content.
- [x] T042 [P] Verify conversation metadata stores (`conversations` collection) do not retain market facts.
- [x] T043 [P] Verify higher-risk tool calls (e.g., `workflow_mutation` if enabled) are not silently executed as lower-risk calls when prompt policy blocks them.
- [x] T044 [P] Verify request-scoped `ToolContextPack` is NOT persisted wholesale in MongoDB — only explicitly retained derivatives with source lineage are stored.

## Phase 6: Predecessor Compatibility and Scope Boundaries (Tasks T045-T050)

- [x] T045 Run the full predecessor M2B compatibility suite: `python -m pytest tests/test_tool_gateway_m2b1.py tests/test_provider_policy_m2b2.py tests/test_tool_normalization_m2b2.py tests/test_tool_retention_m2b2.py tests/test_market_data_tools.py tests/test_tradingview_visualization.py tests/test_market_route_evaluation.py tests/test_market_attribution_cache.py -q` — confirm 107 tests pass.
- [x] T046 Run the full integration test module: `python -m pytest tests/test_tool_system_integration.py -v -q` — confirm all integrated scenarios pass.
- [x] T047 Verify scope boundaries: single ReAct runtime preserved, no second runtime or separate gateway service, no public REST/SSE/Socket.IO/OpenAPI contract changes, no generic web fetch, no reporting persistence, no remote/MCP-style admission, no production symbol-store writes, no production provider enablement.
- [x] T048 Run coverage gates: `python -m pytest tests/test_tool_system_integration.py tests/test_tool_gateway_m2b1.py tests/test_provider_policy_m2b2.py tests/test_tool_normalization_m2b2.py tests/test_market_data_tools.py tests/test_tradingview_visualization.py tests/test_market_route_evaluation.py tests/test_market_attribution_cache.py --cov=src/core/tools --cov-fail-under=70 -q`
- [x] T049 Validate `docs/openapi.yaml` has no public contract changes and record result in review evidence.
- [x] T050 Validate all integration test imports use `core.*` paths (not relative imports) and record result in review evidence.

## Phase 7: Release Evidence and Sync (Tasks T051-T058)

- [x] T051 Create `specs/002-tool-system-integration-verification/review.md` with comprehensive evidence: scenario counts, pass rates, architecture compliance findings, scope boundary verification, coverage reports, and any accepted deferrals.
- [x] T052 Update `specs/spec-traceability.yaml` to add `002-tool-system-integration-verification` feature entry with evidence paths, lifecycle status, mapped SRS items, and `coverage_status: partial`.
- [x] T053 Run `python scripts/sync_spec_status.py --gate` and confirm regenerated `specs/spec-sync-status.md` plus `docs/domains/agent/SRS_SPEC_TRACEABILITY.md` are current.
- [x] T054 Run `git diff --check` and record whitespace or line-ending findings.
- [x] T055 Run `/speckit-validate` for artifact completeness and task-to-requirement traceability.
- [x] T056 Run `/speckit-analyze` for cross-artifact consistency after implementation evidence exists.
- [x] T057 Run `/speckit-verify-tasks` after tasks are marked complete and record findings.
- [x] T058 Run `/speckit-verify-run` and create `specs/002-tool-system-integration-verification/.verify-done` only if verification passes.
