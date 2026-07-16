# Implementation Plan: Tool System Integration and Verification

**Branch**: `feature/tool-integration-and-verification` | **Date**: 2026-07-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/002-tool-system-integration-verification/spec.md`

## Summary

This feature verifies integrated behavior across the three verified predecessor milestones (M2B.1, M2B.2, M2B.3), ensuring they work together as one coherent capability set. Unlike those milestones — which each delivered new tool-system components — this feature is a **verification-only slice**: it creates cross-boundary integrated test scenarios, runs evidence audits, validates architecture boundary preservation, and produces release-readiness evidence.

The implementation plan covers all **25 functional requirements** (TSIV-FR-001 through TSIV-FR-025) organized across **5 verification domains**:

1. **Integrated Readiness (US1)**: Cross-boundary scenarios exercising route, gateway, provider, normalization, and response composition together
2. **Financial Evidence Audit (US2)**: Source attribution, freshness, license posture, degraded states, finance safety
3. **Route Regression (US3)**: Route-filtered tool exposure stability across English, Vietnamese, and mixed-language prompts
4. **Visualization Boundary (US4)**: TradingView `VisualizationProvenance` and non-evidence enforcement
5. **Architecture Compliance (US6)**: Provider class authority, risk class enforcement, prompt-boundary safety, tool separation, gateway purity, registry integrity, STM evidence freedom
6. **Release Evidence (US5)**: Lifecycle artifacts, traceability sync, review evidence, verification

## Technical Context

**Language/Version**: Python 3.10+ as declared in `requirements.txt`

**Primary Dependencies**: Existing LangChain/LangGraph ReAct runtime, `pytest`/`pytest-cov`, all predecessor tool-system modules already in place:
- `src/core/tools/descriptors.py` — M2B.1 descriptors and hashing
- `src/core/tools/surface.py` — M2B.1 route-filtered surface builder
- `src/core/tools/gateway.py` — M2B.1 gateway admission and traces
- `src/core/tools/normalization.py` — M2B.2 output normalization
- `src/core/tools/provider_policy.py` — M2B.2 provider selection
- `src/core/tools/context.py` — M2B.2 ToolContextPack
- `src/core/tools/market_data.py` — M2B.3 Vietnam market-data tools
- `src/core/tools/tradingview.py` — M2B.3 TradingView provenance

**Storage**: Existing MongoDB and Redis services via Docker Compose. No new storage schemas or migrations.

**Testing**: `pytest`, `pytest-cov`, existing M2B test fixtures and modules. New integration test module `tests/test_tool_system_integration.py` for cross-boundary scenarios.

**Target Platform**: Backend/agent runtime in the existing Flask/LangGraph service

**Project Type**: Python web-service and agent backend — verification-only

**Performance Goals**: All integration tests must be deterministic with no live provider/network dependencies. Existing 107 M2B tool-system tests must remain passing throughout.

**Constraints**: 
- Single ReAct runtime preserved — no second runtime
- No public REST/SSE/Socket.IO/OpenAPI contract changes
- No generic web fetch, reporting persistence, remote/MCP admission, production symbol-store writes, or production provider enablement
- Provider adapters remain hidden below model-visible tools
- TradingView remains `VisualizationProvenance` only
- Raw provider payloads stay out of prompt context
- Market facts excluded from STM/memory stores
- `ToolGateway` free of provider-specific parsing
- `ToolRegistry` remains authoritative inventory boundary

**Scale/Scope**: Integration verification across verified predecessor baselines only. New files limited to test modules, fixture data, and lifecycle evidence artifacts.

## Governance and Traceability Context

**Source Requirements**: As defined in [spec.md](./spec.md#governance-context-mandatory):
- FR-2.4.1 through FR-2.8.4 — Tool gateway, provider policy, Vietnam market data, TradingView
- FR-4.1.3 — Meaning-based route classification accuracy
- NFR-2.3.5, NFR-5.2.12, NFR-5.2.13, NFR-5.3.8, NFR-6.1.3, NFR-6.1.4 — Freshness, traces, attribution, coverage
- CON-6, CON-7, CON-9, CON-10 — Tool-system constraints
- AC-9.1 through AC-9.17 — Tool-system acceptance criteria

**Authority References**:
- [PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#2b0-tool-system-goals-boundaries-and-gates), [2B.5 Concrete Market Data and Visualization Tools](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#2b5-concrete-market-data-and-visualization-tools), [2B.9 Verification and Quality Gates](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#2b9-verification-and-quality-gates)
- [ARCHITECTURE_DESIGN.md](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#485a-tool-gateway-and-evidence-admission-boundary), [section 4.3.4](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#434-tool-provider-selection-and-fallback-view), [section 7](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#7-architecture-considerations-and-planned-evolution)
- [TECHNICAL_DESIGN.md](../../docs/domains/agent/TECHNICAL_DESIGN.md#322-target-phase-2b-runtime-flow), [section 3.2.3](../../docs/domains/agent/TECHNICAL_DESIGN.md#323-tool-and-adapter-responsibility-split), [section 3.2.4](../../docs/domains/agent/TECHNICAL_DESIGN.md#324-target-tool-contract-and-failure-realization), [section 4.2](../../docs/domains/agent/TECHNICAL_DESIGN.md#42-routing-output-and-prompt-evolution)
- Verified predecessor evidence in `specs/tool-system-implementation-m2b.1/`, `specs/tool-system-m2b.2/`, `specs/tool-system-m2b.3/`

**Traceability Updates**: Update `specs/spec-traceability.yaml` to add `002-tool-system-integration-verification` with `coverage_status: partial` and evidence paths. Run `python scripts/sync_spec_status.py --gate` after each phase transition.

**Public Contract Impact**: None. `docs/openapi.yaml` remains unchanged. Verification contracts are feature-local integrated test scenarios, admission matrices, evidence audit records, and route evaluation results.

**Long-Lived Documentation Impact**: No long-lived architecture or technical-design document edit is planned during this feature. Only promote stable implemented behavior to current state if verification proves a documented baseline changed.

## Constitution Check

*GATE: Per constitution §Lifecycle Obligations — `speckit.plan` MUST list which docs/ documents are affected and whether section anchors or requirement IDs need updates.*

| Document | Affected? | Anchor/ID Changes Needed? | Notes |
|----------|-----------|---------------------------|-------|
| `SOFTWARE_REQUIREMENTS_SPECIFICATION.md` | No | No | Spec references existing FR-2.4–2.8, FR-4.1, NFR-2.3/5.2/5.3/6.1, CON-6/7/9/10, AC-9.1–9.17 anchors — all verified in cross-review as stable. No new SRS items proposed. |
| `ARCHITECTURE_DESIGN.md` | No | No | Spec references sections 4.1.1a, 4.3.4, 4.8.5a, 5.3, 7 — anchors verified as stable. No architecture claim changes in this verification-only feature. |
| `TECHNICAL_DESIGN.md` | No | No | Spec references sections 3.2.2–3.2.5, 4.2 — anchors verified as stable. Verification may prove stable current-state behavior for future promotion, but no immediate anchor change required. |
| `PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md` | No | No | Referenced roadmap milestone gates and verification areas are current. No roadmap change proposed. |
| `TOOLS_RESEARCH_AND_PROPOSAL.md` | No | No | Referenced design sections are stable research anchors. No change proposed. |
| `AGENT_ARCHITECTURE_DECISION_RECORDS.md` | No | No | ADR-004 (thin tool gateway) remains current. No ADR change proposed. |
| `.specify/memory/constitution.md` | No | No | Vietnam market-data gates remain current. No constitution amendment proposed. |
| `.specify/memory/architecture.md` | No | No | Current/target/planned/gated labels remain consistent with verification-only scope. |
| `docs/openapi.yaml` | No | No | No public contract changes. Verification confirms no OpenAPI impact. |

**Verdict**: PASS — no long-lived document anchors or requirement IDs require updates during this verification-only phase. Cross-reference verification will be re-run during Phase 7 (release evidence) to confirm no anchors drifted during implementation.

## Approach

### Phase 0: Foundation and Setup
1. Create integration test module `tests/test_tool_system_integration.py` with shared fixtures and cross-boundary scenario framework
2. Create integration fixture data covering all verification domains
3. Verify predecessor test baseline (107 M2B tests) passes before integration work
4. Verify all required runtime dependencies (MongoDB, Redis) and environment configuration (`config.yaml`, `.env`) are in place for application startup

### Phase 0a: Application Runtime Verification
1. Start MongoDB and Redis via Docker Compose: `docker-compose up -d mongodb redis`
2. Run database migration: `python src/data/migration/db_setup.py`
3. Start the API server in web mode: `python src/main.py --mode web` on a background terminal; verify `GET /api/health` returns `{"status": "healthy"}`
4. Start the CLI agent: `python src/main.py --mode cli` in a separate terminal; verify interactive prompt appears and a basic query (e.g., "What is AAPL?") produces a response through the integrated ReAct agent with tool system
5. Verify the agent processes at least one query through the full tool-system pipeline: route classification → ToolSurfaceBuilder → ToolGateway admission → provider-backed execution → normalization → response composition
6. Stop running processes and verify clean teardown

### Phase 1: Integrated Readiness (US1 — TSIV-FR-001 to TSIV-FR-002)
1. Create integrated scenario inventory covering descriptor-backed exposure, route filtering, gateway admission, provider policy, normalized output classification, request-scoped context, warnings, and degraded states
2. Implement cross-boundary scenarios that exercise multiple tool-system boundaries in one flow
3. Verify every scenario reaches the expected route, tool family, output classification, and user-facing outcome

### Phase 2: Financial Evidence Audit (US2 — TSIV-FR-007 to TSIV-FR-009, TSIV-FR-014 to TSIV-FR-015)
1. Create evidence audit scenarios for source attribution, freshness, license posture, warnings
2. Create degraded-state scenarios for stale, missing, blocked, provider-outage, and parser-limited outcomes
3. Create cache freshness scenarios
4. Create finance-safety scenarios for unsupported recommendations, hype language, unsupported certainty
5. Create public metadata safety scenarios

### Phase 3: Route and Tool Exposure Regression (US3 — TSIV-FR-003, TSIV-FR-012 to TSIV-FR-013)
1. Create route regression scenarios for price, chart, fundamentals, disclosures, breadth, flow, report-like, ambiguous, and unsupported prompts
2. Measure meaning-based classification accuracy (≥85%) across English, Vietnamese, and mixed-language fixtures
3. Measure route-tool exposure precision and recall separately from language classification

### Phase 4: Visualization Boundary (US4 — TSIV-FR-010 to TSIV-FR-011)
1. Create TradingView scenarios for chart, widget, deep-link, ticker-tape, heatmap, screener, and symbol-validation
2. Verify every visualization output is classified as `VisualizationProvenance`
3. Verify factual answer scenarios do NOT use visualization values as canonical evidence

### Phase 5: Architecture Compliance (US6 — TSIV-FR-019 to TSIV-FR-025)
1. **Provider class authority**: Verify all 7 provider classes produce correct admission or degraded behavior; verify no silent class promotion
2. **Risk class enforcement**: Verify each tool declares correct risk class; verify gateway enforces risk-class ceiling; verify prompt policy cannot downgrade risk class
3. **Prompt-boundary safety**: Verify raw provider payloads, chart widgets, tool descriptors, and document instructions excluded from prompt assembly
4. **Symbol-tool separation**: Verify `StockSymbolTool` handles identity/metadata only; market-data routing through market-data tool families
5. **Gateway purity**: Verify `ToolGateway` contains no provider-specific parsing
6. **Registry integrity**: Verify `ToolRegistry` remains authoritative inventory boundary
7. **STM evidence freedom**: Verify market facts not stored in checkpoint state or conversation metadata

### Phase 6: Predecessor Compatibility and Scope Boundaries (TSIV-FR-004 to TSIV-FR-006, TSIV-FR-016 to TSIV-FR-018)
1. Run full predecessor compatibility suite (107 M2B tests)
2. Verify gateway admission blocks invalid arguments, disallowed route/tool, blocked risk class, license-unclear, descriptor drift
3. Verify provider selection remains below model-visible tools
4. Verify single ReAct runtime preserved (no second runtime, no public API changes)
5. Verify scope boundaries (no generic web fetch, reporting, remote/MCP, symbol-store writes, production providers)

### Phase 7: Release Evidence and Sync (US5 — TSIV-FR-017 to TSIV-FR-018)
1. Create review.md with comprehensive evidence
2. Update `specs/spec-traceability.yaml` with feature entry and evidence paths
3. Run `python scripts/sync_spec_status.py --gate`
4. Create `.verify-done` marker
5. Verify long-lived doc updates limited to verified current-state behavior with explicit target/planned/gated labels

## Files to Touch

| File | Action | Purpose |
|------|--------|---------|
| `specs/002-tool-system-integration-verification/spec.md` | EXISTS | Feature specification |
| `specs/002-tool-system-integration-verification/plan.md` | CREATE | This plan |
| `specs/002-tool-system-integration-verification/tasks.md` | CREATE | Actionable task list |
| `specs/002-tool-system-integration-verification/review.md` | CREATE | Implementation review evidence |
| `specs/002-tool-system-integration-verification/checklists/requirements.md` | EXISTS | Quality checklist |
| `tests/test_tool_system_integration.py` | CREATE | Main integration test module |
| `tests/fixtures/integration/__init__.py` | CREATE | Integration fixture package |
| `tests/fixtures/integration/scenarios.py` | CREATE | Cross-boundary scenario fixtures |
| `tests/fixtures/integration/provider_classes.py` | CREATE | Provider class verification fixtures |
| `tests/fixtures/integration/risk_classes.py` | CREATE | Risk class verification fixtures |
| `tests/fixtures/integration/boundary_cases.py` | CREATE | Architecture boundary test cases |
| `specs/spec-traceability.yaml` | UPDATE | Add feature entry with evidence paths |
| `specs/002-tool-system-integration-verification/.verify-done` | CREATE | Final verification marker |
| `docker-compose.yml` | VERIFY | Confirm MongoDB/Redis services are configured for runtime test |
| `config/config.yaml` | VERIFY | Confirm configuration is present and correct |
| `.env` | VERIFY | Confirm environment variables are set |

## Success Criteria

All 17 success criteria (SC-001 through SC-017) from [spec.md](./spec.md#success-criteria-mandatory) must pass with 100% before `.verify-done` can be created. Key thresholds:
- 100% of predecessor capability areas represented by cross-boundary scenarios
- 100% of market-answer scenarios include complete source attribution or degraded-state classification
- 100% of TradingView scenarios classified as `VisualizationProvenance`; 0 factual answers use visualization values
- ≥85% route classification accuracy for Vietnamese/mixed-language fixtures
- 100% pass rate for all architecture boundary preservation scenarios
- 0 leaks of credentials, secrets, raw payloads in public responses
- 100% blocking/rewriting for finance-safety violations
- Sync gate passes before `.verify-done` creation
