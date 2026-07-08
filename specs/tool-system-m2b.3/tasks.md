# Tasks: Vietnam Market and Visualization Coverage - M2B.3

**Input**: Design documents from `specs/tool-system-m2b.3/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, `checklists/requirements.md`

**Tests**: Required. The specification defines independent tests and measurable success criteria for each M2B.3 story. Test tasks must be written before implementation tasks and should fail before the corresponding implementation is added.

**Organization**: Tasks are grouped by user story so quote/history, fundamentals, TradingView visualization, route evaluation, attribution/cache/trace coverage, and the P2 breadth/flow/disclosure slice can be implemented and verified independently after the shared foundation exists.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches a different file or isolated fixture surface
- **[Story]**: User story label from `spec.md`
- Every task names exact file paths
- Test files must use the project convention of `core.*` imports, not `src.core.*`

## Phase 1: Setup (Shared Evidence and Fixtures)

**Purpose**: Prepare the M2B.3 task, review, fixture, and test surfaces without changing runtime behavior.

- [X] T001 Review `specs/tool-system-m2b.3/spec.md`, `specs/tool-system-m2b.3/plan.md`, `docs/domains/agent/ARCHITECTURE_DESIGN.md#485a-tool-gateway-and-evidence-admission-boundary`, and `docs/domains/agent/TECHNICAL_DESIGN.md#322-target-phase-2b-runtime-flow`; record the implementation baseline in `specs/tool-system-m2b.3/review.md`.
- [X] T002 Create shared M2B.3 fixture directory `tests/fixtures/market_tools/`.
- [X] T003 [P] Add shared M2B.3 assertion helpers using `core.*` imports in `tests/helpers/market_tool_helpers.py`.
- [X] T004 [P] Create the market-data test module skeleton in `tests/test_market_data_tools.py`.
- [X] T005 [P] Create the TradingView visualization test module skeleton in `tests/test_tradingview_visualization.py`.
- [X] T006 [P] Create the route-evaluation test module skeleton in `tests/test_market_route_evaluation.py`.
- [X] T007 [P] Create the attribution/cache/trace test module skeleton in `tests/test_market_attribution_cache.py`.
- [X] T008 [P] After T002, add Vietnam symbol and exchange fixture data in `tests/fixtures/market_tools/symbols.py`.
- [X] T009 [P] After T002, add provider posture fixture data for Vietnam-native, official, licensed, fallback, visualization, and blocked providers in `tests/fixtures/market_tools/providers.py`.
- [X] T010 [P] After T002, add Vietnamese, English, and mixed-language route fixture data in `tests/fixtures/market_tools/route_cases.py`.
- [X] T011 [P] After T002, add safe market-data, stale-cache, missing-field, and degraded fixture payloads in `tests/fixtures/market_tools/market_payloads.py`.
- [X] T012 [P] After T002, add TradingView chart, widget, deep-link, heatmap, screener, ticker-tape, and validation fixture payloads in `tests/fixtures/market_tools/tradingview_payloads.py`.
- [X] T013 Create review sections for story gates, compatibility gates, provider posture, public-contract guard, sync evidence, and accepted deferrals in `specs/tool-system-m2b.3/review.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared internal contracts and preserve the verified M2B.1/M2B.2 tool-system baseline before story-specific behavior is implemented.

**Critical**: No user story implementation should begin until this phase is complete.

- [X] T014 [P] Add the Vietnam market-data tool module structure in `src/core/tools/market_data.py`.
- [X] T015 [P] Extend provider data-category and provider-class support for M2B.3 market-data and visualization classes in `src/core/tools/provider_policy.py`.
- [X] T016 [P] Extend normalized output helpers for market facts, price history, fundamentals, breadth/flow, disclosures, corporate actions, cache freshness, and attribution counters in `src/core/tools/normalization.py`.
- [X] T017 [P] Extend request-scoped context helpers for M2B.3 market-data warnings, freshness metadata, and retained-derivative candidates in `src/core/tools/context.py`.
- [X] T018 [P] Extend descriptor inventory with market-data and TradingView M2B.3 capability/policy descriptors in `src/core/tools/descriptors.py`.
- [X] T019 Preserve route-filtered exposure and prevent provider adapters from becoming model-visible tools in `src/core/tools/surface.py`.
- [X] T020 Preserve thin gateway admission, trace sanitization, and registry-backed execution for M2B.3 tool wrappers in `src/core/tools/gateway.py`.
- [X] T021 Export only stable M2B.3 internal tool contracts from `src/core/tools/__init__.py` after T014-T018 exist.
- [X] T022 Add canonical symbol fixture adapters and identity helpers for M2B.3 tests in `tests/helpers/market_tool_helpers.py`.
- [X] T023 Add source-attribution, cache-freshness, VisualizationProvenance, and no-raw-payload assertion helpers in `tests/helpers/market_tool_helpers.py`.
- [X] T024 Add route-evaluation metric helpers for accuracy, precision, and recall in `tests/helpers/market_tool_helpers.py`.
- [X] T025 Add provider posture fixtures for `vnstock`, Vietstock, CafeF, FiinGroup/FiinTrade/FiinQuant, VSDC, HOSE, HNX, Yahoo, Alpha Vantage, and TradingView in `tests/fixtures/market_tools/providers.py`.
- [X] T026 Add a no-public-contract-change verification note for `docs/openapi.yaml` in `specs/tool-system-m2b.3/review.md`.
- [X] T027 Run `python -m pytest tests/test_tool_gateway_m2b1.py tests/test_provider_policy_m2b2.py tests/test_tool_normalization_m2b2.py -q` and record predecessor compatibility evidence in `specs/tool-system-m2b.3/review.md`.

**Checkpoint**: Foundation ready. M2B.1 gateway behavior and M2B.2 provider/normalization/context behavior remain intact.

---

## Phase 3: User Story 1 - Vietnam Quote and Price History Evidence (Priority: P1)

**Goal**: Handle Vietnam quote, price-history, OHLCV, and deterministic indicator requests through approved market-data tool families instead of `StockSymbolTool`, raw provider payloads, or TradingView values.

**Independent Test**: `python -m pytest tests/test_market_data_tools.py -q -k "quote or history or indicator"`

### Tests for User Story 1

- [X] T028 [US1] Add supported-symbol quote and history tests for `FPT`, `HOSE:FPT`, `HNX:SHS`, and `UPCOM:BSR` in `tests/test_market_data_tools.py`.
- [X] T029 [US1] Add canonical symbol identity and ambiguous ticker degraded-state tests for quote/history evidence in `tests/test_market_data_tools.py`.
- [X] T030 [US1] Add Vietnam-first provider selection and international fallback tests for quote/history evidence in `tests/test_market_data_tools.py`.
- [X] T031 [US1] Add stale, missing-source, parser-limited, rate-limited, timeout, and blocked-license degraded-state tests for quote/history evidence in `tests/test_market_data_tools.py`.
- [X] T032 [US1] Add deterministic indicator lineage tests that prove indicators use approved price-history input in `tests/test_market_data_tools.py`.
- [X] T033 [US1] Add tests proving `StockSymbolTool` does not own quote, history, OHLCV, or indicator retrieval in `tests/test_market_data_tools.py`.

### Implementation for User Story 1

- [X] T034 [US1] Implement quote/history request and result structures in `src/core/tools/market_data.py`.
- [X] T035 [US1] Implement Vietnam-first provider selection for quote/history categories in `src/core/tools/provider_policy.py`.
- [X] T036 [US1] Implement `MarketFact` and `PriceHistorySeries` normalized output builders in `src/core/tools/normalization.py`.
- [X] T037 [US1] Implement source timestamp, retrieved timestamp, exchange, currency, freshness, and warning propagation for quote/history outputs in `src/core/tools/market_data.py`.
- [X] T038 [US1] Implement stale, missing-source, parser-limited, rate-limited, timeout, blocked-license, and unsupported-provider degraded states in `src/core/tools/market_data.py`.
- [X] T039 [US1] Implement deterministic indicator computation over approved price-history inputs with lineage preservation in `src/core/tools/market_data.py`.
- [X] T040 [US1] Update market-data capability and policy descriptors for quote/history and indicator families in `src/core/tools/descriptors.py`.
- [X] T041 [US1] Register the market-data tool family without exposing provider adapters directly in `src/core/tools/registry.py`.
- [X] T042 [US1] Ensure `StockAssistantAgent` can invoke the route-filtered market-data family through the existing gateway path in `src/core/stock_assistant_agent.py`.
- [X] T043 [US1] Run `python -m pytest tests/test_market_data_tools.py -q -k "quote or history or indicator"` and record US1 evidence in `specs/tool-system-m2b.3/review.md`.
- [X] T044 [US1] Record `SC-001`, `SC-002`, and `SC-003` quote/history fixture coverage evidence in `specs/tool-system-m2b.3/review.md`.

**Checkpoint**: US1 is independently testable and does not use TradingView or `StockSymbolTool` as canonical market-data evidence.

---

## Phase 4: User Story 2 - Vietnam Fundamentals Evidence (Priority: P1)

**Goal**: Route fundamentals and statement requests to the Vietnam market-data tool family with period metadata, source attribution, license posture, missing-field warnings, and degraded-state handling.

**Independent Test**: `python -m pytest tests/test_market_data_tools.py -q -k fundamentals`

### Tests for User Story 2

- [X] T045 [US2] Add fundamentals and statement route/tool-family tests in `tests/test_market_data_tools.py`.
- [X] T046 [US2] Add period, provider/source, source reference, timestamp, freshness, and license posture tests for fundamentals in `tests/test_market_data_tools.py`.
- [X] T047 [US2] Add missing-field, stale, parser-limited, blocked-license, and no-source degraded-state tests for fundamentals in `tests/test_market_data_tools.py`.
- [X] T048 [US2] Add tests proving fundamentals do not fall back to generic web fetch or TradingView values in `tests/test_market_data_tools.py`.

### Implementation for User Story 2

- [X] T049 [US2] Implement fundamentals and statement request/result structures in `src/core/tools/market_data.py`.
- [X] T050 [US2] Extend provider data-category support for fundamentals and statements in `src/core/tools/provider_policy.py`.
- [X] T051 [US2] Implement `FundamentalEvidence` normalized output builders in `src/core/tools/normalization.py`.
- [X] T052 [US2] Implement missing-field warning and degraded-state behavior for fundamentals in `src/core/tools/market_data.py`.
- [X] T053 [US2] Update market-data capability and policy descriptors for fundamentals in `src/core/tools/descriptors.py`.
- [X] T054 [US2] Integrate fundamentals outputs into request-scoped `ToolContextPack` assembly in `src/core/tools/context.py`.
- [X] T055 [US2] Run `python -m pytest tests/test_market_data_tools.py -q -k fundamentals` and record US2 evidence in `specs/tool-system-m2b.3/review.md`.
- [X] T056 [US2] Record `SC-002` and `SC-003` fundamentals fixture coverage evidence in `specs/tool-system-m2b.3/review.md`.

**Checkpoint**: US2 is independently testable and separates fundamentals from symbol lookup, visualization, and generic web evidence.

---

## Phase 5: User Story 4 - TradingView Visualization Provenance (Priority: P1)

**Goal**: Return TradingView charts, widgets, deep links, symbol validation, ticker tape, heatmaps, and screeners as `VisualizationProvenance`, never canonical market evidence by default.

**Independent Test**: `python -m pytest tests/test_tradingview_visualization.py -q`

### Tests for User Story 4

- [X] T057 [US4] Add chart, widget, deep-link, ticker-tape, heatmap, screener, and symbol-validation tests in `tests/test_tradingview_visualization.py`.
- [X] T058 [US4] Add tests that every TradingView output is classified as `VisualizationProvenance` in `tests/test_tradingview_visualization.py`.
- [X] T059 [US4] Add tests proving TradingView numeric values, indicators, heatmap rows, and screener values are not canonical evidence in `tests/test_tradingview_visualization.py`.
- [X] T060 [US4] Add unsupported, ambiguous, invalid interval, unsupported widget, and validation-failed degraded visualization tests in `tests/test_tradingview_visualization.py`.
- [X] T061 [US4] Add public metadata safety tests for TradingView outputs in `tests/test_tradingview_visualization.py`.

### Implementation for User Story 4

- [X] T062 [US4] Implement TradingView chart URL, widget, deep-link, ticker-tape, heatmap, screener, and symbol-validation output builders in `src/core/tools/tradingview.py`.
- [X] T063 [US4] Implement TradingView symbol, exchange/market, interval/view, generated timestamp, validation status, warning, and provenance metadata handling in `src/core/tools/tradingview.py`.
- [X] T064 [US4] Implement `VisualizationProvenance` normalized output helpers for TradingView payloads in `src/core/tools/normalization.py`.
- [X] T065 [US4] Update TradingView capability and policy descriptors for visualization-only exposure in `src/core/tools/descriptors.py`.
- [X] T066 [US4] Ensure TradingView route-surface exposure remains limited to visualization/chart routes in `src/core/tools/surface.py`.
- [X] T067 [US4] Ensure factual market-data composition rejects TradingView values as canonical evidence in `src/core/tools/market_data.py`.
- [X] T068 [US4] Run `python -m pytest tests/test_tradingview_visualization.py -q` and record US4 evidence in `specs/tool-system-m2b.3/review.md`.
- [X] T069 [US4] Record `SC-005` TradingView fixture coverage and non-evidence proof in `specs/tool-system-m2b.3/review.md`.

**Checkpoint**: US4 is independently testable and TradingView remains visualization provenance only.

---

## Phase 6: User Story 5 - Vietnamese and Mixed-Language Route Evaluation (Priority: P1)

**Goal**: Verify Vietnamese, English, and mixed-language route/tool-family selection for price, chart, fundamentals, disclosures, breadth, flow, and report-like prompts with at least 85% meaning-based classification accuracy.

**Independent Test**: `python -m pytest tests/test_market_route_evaluation.py -q`

### Tests for User Story 5

- [X] T070 [US5] Add deterministic price, chart, fundamentals, disclosure, breadth, flow, and report-like route fixtures in `tests/fixtures/market_tools/route_cases.py`.
- [X] T071 [US5] Add route accuracy and tool-family mapping tests with at least 85% meaning-based classification threshold in `tests/test_market_route_evaluation.py`.
- [X] T072 [US5] Add route-tool exposure precision and recall target tests in `tests/test_market_route_evaluation.py`.
- [X] T073 [US5] Add ambiguous ticker-only, unsupported, and deferred-scope disambiguation/degraded tests in `tests/test_market_route_evaluation.py`.
- [X] T074 [US5] Add tests proving report-like prompts remain route/evaluation fixtures only in `tests/test_market_route_evaluation.py`.

### Implementation for User Story 5

- [X] T075 [US5] Add Vietnamese and mixed-language route utterances while preserving the static `StockQueryRoute` taxonomy in `src/core/routes.py`.
- [X] T076 [US5] Add route evaluation helpers and deterministic fixture evaluation in `src/core/stock_query_router.py`.
- [X] T077 [US5] Map M2B.3 route outcomes to market-data, visualization, and deferred report tool families in `src/core/tools/surface.py`.
- [X] T078 [US5] Implement ambiguous and low-confidence route degradation or disambiguation behavior in `src/core/stock_query_router.py`.
- [X] T079 [US5] Ensure route evaluation does not enable report generation, generic web fetch, remote admission, or symbol-store writes in `src/core/tools/surface.py`.
- [X] T080 [US5] Run `python -m pytest tests/test_market_route_evaluation.py -q` and record US5 evidence in `specs/tool-system-m2b.3/review.md`.
- [X] T081 [US5] Record `SC-006` route accuracy, precision, recall, and ambiguity evidence in `specs/tool-system-m2b.3/review.md`.

**Checkpoint**: US5 is independently testable and route evaluation gates new market-data/visualization exposure.

---

## Phase 7: User Story 6 - Attribution, Freshness, Cache, and Trace Coverage (Priority: P1)

**Goal**: Preserve source attribution, freshness, provider posture, warnings, safe trace metadata, and coverage counters for market-data answers, cache hits, tool traces, and retained derivatives.

**Independent Test**: `python -m pytest tests/test_market_attribution_cache.py -q`

### Tests for User Story 6

- [X] T082 [US6] Add market-fact attribution completeness tests in `tests/test_market_attribution_cache.py`.
- [X] T083 [US6] Add cache-hit freshness metadata tests for provider/source, timestamps, TTL/expiry, warnings, and degraded reasons in `tests/test_market_attribution_cache.py`.
- [X] T084 [US6] Add provider-backed trace metadata tests for selected route, tool family, adapter, provider class, license mode, timestamps, fallback, and degraded reasons in `tests/test_market_attribution_cache.py`.
- [X] T085 [US6] Add unsafe public metadata leak tests for credentials, secrets, raw payloads, parser internals, and raw traces in `tests/test_market_attribution_cache.py`.
- [X] T086 [US6] Add attribution coverage counter tests for complete attribution, degraded no-source, stale-cache, provider/license blocked, and unsafe leak counts in `tests/test_market_attribution_cache.py`.

### Implementation for User Story 6

- [X] T087 [US6] Implement market-fact attribution validation helpers in `src/core/tools/normalization.py`.
- [X] T088 [US6] Implement cache freshness record helpers and stale-cache degraded behavior in `src/core/tools/market_data.py`.
- [X] T089 [US6] Implement provider-backed trace metadata assembly and sanitization for M2B.3 tool calls in `src/core/tools/gateway.py`.
- [X] T090 [US6] Extend provider selection decisions with M2B.3 source reference, license mode, fallback, and degraded metadata in `src/core/tools/provider_policy.py`.
- [X] T091 [US6] Implement attribution coverage counters in `src/core/tools/market_data.py`.
- [X] T092 [US6] Ensure request-scoped `ToolContextPack` preserves source metadata, freshness metadata, warnings, and degraded states without raw payloads in `src/core/tools/context.py`.
- [X] T093 [US6] Run `python -m pytest tests/test_market_attribution_cache.py -q` and record US6 evidence in `specs/tool-system-m2b.3/review.md`.
- [X] T094 [US6] Record `SC-002`, `SC-003`, `SC-004`, and `SC-007` attribution/cache/trace coverage evidence in `specs/tool-system-m2b.3/review.md`.

**Checkpoint**: US6 is independently testable and attribution/freshness/trace coverage is machine-detectable.

---

## Phase 8: User Story 3 - Vietnam Breadth, Flow, Disclosures, and Corporate Actions (Priority: P2)

**Goal**: Add independently testable P2 coverage for market breadth, flow, disclosures, official notices, dividends, rights, splits, listing changes, and other corporate actions when provider posture allows.

**Independent Test**: `python -m pytest tests/test_market_data_tools.py -q -k "breadth or flow or disclosure or corporate"`

### Tests for User Story 3

- [X] T095 [US3] Add breadth and flow route/tool-family tests in `tests/test_market_data_tools.py`.
- [X] T096 [US3] Add disclosure, official notice, dividend, rights, split, listing-change, and corporate-action tests in `tests/test_market_data_tools.py`.
- [X] T097 [US3] Add breadth/flow metadata tests for time window, exchange/market, provider/source, freshness, and warnings in `tests/test_market_data_tools.py`.
- [X] T098 [US3] Add disclosure/corporate-action metadata tests for event type, source reference, published timestamp, effective timestamp, provider class, parser warnings, freshness, and license posture in `tests/test_market_data_tools.py`.
- [X] T099 [US3] Add no-approved-source degraded-state tests that reject generic web fallback for P2 market evidence in `tests/test_market_data_tools.py`.

### Implementation for User Story 3

- [X] T100 [US3] Implement breadth and flow request/result structures in `src/core/tools/market_data.py`.
- [X] T101 [US3] Implement disclosure and corporate-action request/result structures in `src/core/tools/market_data.py`.
- [X] T102 [US3] Extend provider data-category support for breadth, flow, disclosure, and corporate-action evidence in `src/core/tools/provider_policy.py`.
- [X] T103 [US3] Implement `BreadthAndFlowEvidence` and `DisclosureCorporateActionEvidence` normalized output builders in `src/core/tools/normalization.py`.
- [X] T104 [US3] Update market-data capability and policy descriptors for P2 breadth/flow/disclosure/corporate-action families in `src/core/tools/descriptors.py`.
- [X] T105 [US3] Integrate P2 route-tool family exposure and degraded no-source behavior in `src/core/tools/surface.py`.
- [X] T106 [US3] Run `python -m pytest tests/test_market_data_tools.py -q -k "breadth or flow or disclosure or corporate"` and record US3 evidence in `specs/tool-system-m2b.3/review.md`.
- [X] T107 [US3] Record P2 `TS-07` scope evidence and non-blocking relation to P1 gates in `specs/tool-system-m2b.3/review.md`.

**Checkpoint**: US3 is independently testable and does not enable generic web evidence or report persistence.

---

## Phase 9: Final Verification, Governance, and Sync

**Purpose**: Prove all story work remains within M2B.3 scope, preserves M2B.1/M2B.2 compatibility, and updates Spec Kit traceability.

- [X] T108 Run `python -m pytest tests/test_market_data_tools.py -q` and record focused market-data evidence in `specs/tool-system-m2b.3/review.md`.
- [X] T109 Run `python -m pytest tests/test_tradingview_visualization.py -q` and record focused TradingView evidence in `specs/tool-system-m2b.3/review.md`.
- [X] T110 Run `python -m pytest tests/test_market_route_evaluation.py -q` and record route-evaluation evidence in `specs/tool-system-m2b.3/review.md`.
- [X] T111 Run `python -m pytest tests/test_market_attribution_cache.py -q` and record attribution/cache/trace evidence in `specs/tool-system-m2b.3/review.md`.
- [X] T112 Run `python -m pytest tests/test_tool_gateway_m2b1.py tests/test_provider_policy_m2b2.py tests/test_tool_normalization_m2b2.py tests/test_tool_retention_m2b2.py -q` and record predecessor compatibility evidence in `specs/tool-system-m2b.3/review.md`.
- [X] T113 Run `python -m pytest tests/test_stock_query_router.py tests/test_market_route_evaluation.py --cov=src.core.stock_query_router --cov-report=term-missing --cov-fail-under=80 -q` and record route/agent touched-surface coverage evidence for `NFR-6.1.3` in `specs/tool-system-m2b.3/review.md`; document any broader agent-core exception explicitly before promotion.
- [X] T114 Run `python -m pytest tests/test_market_data_tools.py tests/test_tradingview_visualization.py tests/test_market_route_evaluation.py tests/test_market_attribution_cache.py --cov=core.tools.market_data --cov=core.tools.tradingview --cov=core.tools.normalization --cov=core.tools.provider_policy --cov=core.tools.gateway --cov=core.tools.surface --cov-report=term-missing --cov-fail-under=70 -q` and record touched tool-layer coverage evidence for `NFR-6.1.4` in `specs/tool-system-m2b.3/review.md`.
- [X] T115 Validate `docs/openapi.yaml` has no public REST, SSE, Socket.IO, or OpenAPI contract changes for M2B.3 and record the result in `specs/tool-system-m2b.3/review.md`.
- [X] T116 Validate tests under `tests/test_market_data_tools.py`, `tests/test_tradingview_visualization.py`, `tests/test_market_route_evaluation.py`, and `tests/test_market_attribution_cache.py` use `core.*` imports and record the result in `specs/tool-system-m2b.3/review.md`.
- [X] T117 Validate no provider credentials, raw provider payloads, parser internals, or live-network assumptions were added to `tests/fixtures/market_tools/` and record the result in `specs/tool-system-m2b.3/review.md`.
- [X] T118 Validate `docs/domains/agent/ARCHITECTURE_DESIGN.md` and `docs/domains/agent/TECHNICAL_DESIGN.md` do not require current-state promotion before M2B.3 verification and record any deferred long-lived-doc sync in `specs/tool-system-m2b.3/review.md`.
- [X] T119 Validate feature-local links and long-lived document anchors referenced by `specs/tool-system-m2b.3/spec.md`, `specs/tool-system-m2b.3/plan.md`, `specs/tool-system-m2b.3/tasks.md`, and `specs/tool-system-m2b.3/contracts/` and record the result in `specs/tool-system-m2b.3/review.md`.
- [X] T120 Update `specs/tool-system-m2b.3/spec.md` to `Implemented` only after all implementation and verification-evidence tasks except final verify marker are complete.
- [X] T121 Update `specs/spec-traceability.yaml` with M2B.3 implementation evidence paths, lifecycle status, synchronized documents, task completion state, and accepted deferrals.
- [X] T122 Run `python scripts/sync_spec_status.py --gate` and confirm regenerated `specs/spec-sync-status.md` plus `docs/domains/agent/SRS_SPEC_TRACEABILITY.md` are current.
- [X] T123 Run `git diff --check` and record whitespace or line-ending findings in `specs/tool-system-m2b.3/review.md`.
- [X] T124 Run `/speckit-validate` for M2B.3 artifact completeness and task-to-requirement readiness; record any findings in `specs/tool-system-m2b.3/review.md`.
- [X] T125 Run `/speckit-analyze` for cross-artifact consistency after implementation evidence exists; record any findings in `specs/tool-system-m2b.3/review.md`.
- [X] T126 Run `/speckit-fleet-review` before final promotion if tasks or plan changed materially during implementation; record any findings in `specs/tool-system-m2b.3/review.md`.
- [X] T127 Run `/speckit-verify-tasks` after tasks are marked complete and record phantom-completion findings in `specs/tool-system-m2b.3/verify-tasks-report.md`.
- [X] T128 Run `/speckit-verify-run`, create `specs/tool-system-m2b.3/.verify-done` only if verification passes, and record the final verdict in `specs/tool-system-m2b.3/review.md`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup. Blocks all user story implementation.
- **US1 Quote/History (Phase 3)**: Depends on Foundation and is the MVP.
- **US2 Fundamentals (Phase 4)**: Depends on Foundation; can run in parallel with US1 after shared contracts exist.
- **US4 TradingView (Phase 5)**: Depends on Foundation; can run in parallel with US1/US2 because it uses separate output classification and tool code.
- **US5 Route Evaluation (Phase 6)**: Depends on Foundation; route fixture work can start early, but final route-tool mapping should be checked after US1/US2/US4 descriptors exist.
- **US6 Attribution/Cache/Trace (Phase 7)**: Depends on Foundation and integrates with US1/US2/US4 outputs.
- **US3 Breadth/Flow/Disclosure (Phase 8)**: Depends on Foundation and may reuse US1/US2 attribution/provider primitives; it is P2 and can be delivered after P1 gates.
- **Final Verification (Phase 9)**: Depends on all in-scope M2B.3 story phases. Completing only the P1 stories is interim evidence and MUST NOT promote the feature to `Verified` while the in-scope P2 `TS-07` story remains incomplete.

### User Story Dependencies

- **US1**: No dependency on other stories after Foundation.
- **US2**: No dependency on other stories after Foundation.
- **US4**: No dependency on US1/US2 for visualization-only behavior after Foundation.
- **US5**: Depends on descriptor and surface foundations; final mapping benefits from US1/US2/US4 descriptors.
- **US6**: Depends on normalized output and provider/cache metadata from Foundation plus story outputs.
- **US3**: P2; depends on shared market-data provider and normalization primitives.

### Within Each User Story

- Write tests first and confirm they fail before implementation.
- Define fixtures and helper assertions before integration.
- Preserve M2B.1 gateway and M2B.2 provider/normalization/context compatibility before changing integration behavior.
- Record independent story evidence in `specs/tool-system-m2b.3/review.md` before moving to final verification.

## Parallel Opportunities

- Setup tasks T003 through T007 can run in parallel after T001 clarifies the review baseline. Fixture-file tasks T008 through T012 can run in parallel only after T002 creates `tests/fixtures/market_tools/`.
- Foundation module-extension tasks T014 through T018 can run in parallel; T021 follows after those module updates exist.
- Fixture and helper tasks T022 through T025 can run in parallel.
- US1, US2, and US4 test tasks can be prepared in parallel after Foundation because they use different test files or distinct sections of `tests/test_market_data_tools.py`.
- US5 route fixture work can run in parallel with US1/US2/US4 implementation, but final route-tool mapping should wait for descriptors.
- US3 P2 work can run after Foundation if capacity exists, but should not block P1 verification unless the implementation changes shared market-data contracts.

## Parallel Example: P1 Story Work

```powershell
# Prepare independent P1 test files after Foundation:
Task: "T028 quote/history tests in tests/test_market_data_tools.py"
Task: "T057 TradingView tests in tests/test_tradingview_visualization.py"
Task: "T070 route fixtures in tests/fixtures/market_tools/route_cases.py"
Task: "T082 attribution tests in tests/test_market_attribution_cache.py"
```

## Implementation Strategy

### MVP First

1. Complete Setup and Foundation.
2. Complete US1 quote/history and indicators.
3. Run `python -m pytest tests/test_market_data_tools.py -q -k "quote or history or indicator"`.
4. Stop and review M2B.1/M2B.2 compatibility before adding fundamentals, visualization, and route expansion.

### Incremental Delivery

1. US1 establishes quote/history evidence and indicator lineage.
2. US2 adds fundamentals evidence.
3. US4 adds TradingView visualization provenance.
4. US5 proves Vietnamese and mixed-language route/tool-family mapping.
5. US6 adds attribution, cache, trace, and coverage counters across successful and degraded paths.
6. US3 completes P2 breadth/flow/disclosure/corporate-action coverage.
7. Final verification and sync promote only when evidence supports the lifecycle state.

### Team Parallel Strategy

1. One engineer owns shared `market_data.py`, descriptors, and provider-policy foundations.
2. One engineer owns market-data tests and fixtures.
3. One engineer owns TradingView visualization and route-evaluation tests.
4. One engineer owns attribution/cache/trace evidence and review/sync closeout.

## Requirement Coverage Matrix

| Requirement / Criterion | Task IDs |
|-------------------------|----------|
| M2B3-FR-001, M2B3-FR-020, SC-008 | T001, T013, T014, T015, T016, T017, T018, T019, T020, T021, T026, T027, T041, T042, T065, T066, T077, T079, T112, T113, T115, T118 |
| M2B3-FR-002, M2B3-FR-003, M2B3-FR-006, M2B3-FR-023, SC-001, SC-002 | T003, T008, T011, T022, T023, T028, T029, T032, T033, T034, T036, T037, T039, T040, T043, T044, T108 |
| M2B3-FR-004, M2B3-FR-005, M2B3-FR-024, SC-003 | T009, T015, T025, T030, T031, T035, T038, T043, T044, T090, T108 |
| M2B3-FR-007, SC-002, SC-003 | T004, T011, T022, T023, T045, T046, T047, T048, T049, T050, T051, T052, T053, T054, T055, T056, T108 |
| M2B3-FR-008, M2B3-FR-009, SC-003 | T095, T096, T097, T098, T099, T100, T101, T102, T103, T104, T105, T106, T107, T108 |
| M2B3-FR-010, M2B3-FR-011, M2B3-FR-012, M2B3-FR-013, SC-002, SC-003, SC-004, SC-007 | T007, T011, T016, T017, T023, T082, T083, T084, T085, T086, T087, T088, T089, T090, T091, T092, T093, T094, T111, T114 |
| M2B3-FR-014, M2B3-FR-015, M2B3-FR-016, M2B3-FR-017, SC-005 | T005, T012, T018, T023, T057, T058, T059, T060, T061, T062, T063, T064, T065, T066, T067, T068, T069, T109 |
| M2B3-FR-018, M2B3-FR-019, SC-006 | T006, T010, T024, T070, T071, T072, T073, T074, T075, T076, T077, T078, T079, T080, T081, T110 |
| M2B3-FR-021, M2B3-FR-022, SC-008 | T001, T013, T026, T048, T067, T074, T079, T099, T115, T116, T117, T118, T119, T120, T121, T122, T123, T124, T125, T126, T127, T128 |
| M2B3-FR-025, SC-009 | T113, T114, T120, T121, T122, T123, T124, T125, T126, T127, T128 |
| Governance, task readiness, and sync evidence | T002, T003, T004, T005, T006, T007, T008, T009, T010, T011, T012, T013, T027, T043, T044, T055, T056, T068, T069, T080, T081, T093, T094, T106, T107, T108, T109, T110, T111, T112, T113, T114, T115, T116, T117, T118, T119, T120, T121, T122, T123, T124, T125, T126, T127, T128 |

## Independent Test Criteria

- **US1**: `python -m pytest tests/test_market_data_tools.py -q -k "quote or history or indicator"`
- **US2**: `python -m pytest tests/test_market_data_tools.py -q -k fundamentals`
- **US3**: `python -m pytest tests/test_market_data_tools.py -q -k "breadth or flow or disclosure or corporate"`
- **US4**: `python -m pytest tests/test_tradingview_visualization.py -q`
- **US5**: `python -m pytest tests/test_market_route_evaluation.py -q`
- **US6**: `python -m pytest tests/test_market_attribution_cache.py -q`
- **Regression**: `python -m pytest tests/test_tool_gateway_m2b1.py tests/test_provider_policy_m2b2.py tests/test_tool_normalization_m2b2.py tests/test_tool_retention_m2b2.py tests/test_stock_query_router.py tests/test_agent_regression.py -q`
- **Agent-core touched surface coverage**: `python -m pytest tests/test_stock_query_router.py tests/test_market_route_evaluation.py --cov=src.core.stock_query_router --cov-report=term-missing --cov-fail-under=80 -q`
- **Tool-layer touched surface coverage**: `python -m pytest tests/test_market_data_tools.py tests/test_tradingview_visualization.py tests/test_market_route_evaluation.py tests/test_market_attribution_cache.py --cov=core.tools.market_data --cov=core.tools.tradingview --cov=core.tools.normalization --cov=core.tools.provider_policy --cov=core.tools.gateway --cov=core.tools.surface --cov-report=term-missing --cov-fail-under=70 -q`
- **Sync**: `python scripts/sync_spec_status.py --gate`

## Notes

- Keep provider adapters below model-visible tools.
- Keep TradingView as `VisualizationProvenance`, not canonical evidence.
- Keep `ToolContextPack` request-scoped and do not persist it wholesale.
- Keep generic web fetch, report persistence, remote/MCP admission, symbol-store writes, and production provider enablement deferred.
- Keep `docs/openapi.yaml` unchanged unless a later governed plan explicitly introduces a public contract change.
