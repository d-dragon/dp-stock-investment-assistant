# Implementation Plan: Vietnam Market and Visualization Coverage - M2B.3

**Branch**: `feature/tool-system-m2b.3` | **Date**: 2026-07-07 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/tool-system-m2b.3/spec.md`

## Summary

M2B.3 follows the verified M2B.1 gateway baseline and verified M2B.2 symbol/provider/normalization backbone by adding concrete Vietnam market-data and visualization coverage. The implementation plan covers roadmap `TS-06`, `TS-07`, `TS-08`, and `TS-12`: Vietnam quote/history and fundamentals as P1 market-data tool families, breadth/flow/disclosure/corporate-action coverage as a P2 independently testable slice, TradingView `VisualizationProvenance`, source attribution, cache freshness, provider-backed traces, and Vietnamese/mixed-language route evaluation.

The target implementation is additive around the single ReAct runtime, existing route-filtered `ToolSurfaceBuilder`, thin `ToolGateway`, M2B.2 `ProviderSelectionPolicy`, normalized outputs, and request-scoped `ToolContextPack`. Provider adapters remain below model-visible tools; TradingView remains visualization provenance only; generic web fetch, report persistence, remote/MCP admission, production symbol-store writes, and production provider enablement remain out of scope.

## Technical Context

**Language/Version**: Python 3.10+ as declared in `requirements.txt`

**Primary Dependencies**: LangChain/LangGraph ReAct runtime, semantic-router route classification, Pydantic 2.x and dataclasses for internal contracts, existing `ToolRegistry`, `ToolSurfaceBuilder`, `ToolGateway`, provider-policy and normalization modules from M2B.2, PyMongo repositories, Redis or in-memory cache backends, `pytest`/`pytest-cov`, and existing Spec Kit sync tooling

**Storage**: Existing MongoDB-backed repositories for domain records and metadata; Redis/in-memory cache for tool/provider freshness and performance only; filesystem remains artifact-content storage. M2B.3 market-data facts and `ToolContextPack` content are request-scoped unless explicitly retained as approved derivatives or trace metadata.

**Testing**: `pytest`, `pytest-cov`, focused unit/regression suites following `tests/test_tool_gateway_m2b1.py`, `tests/test_provider_policy_m2b2.py`, `tests/test_tool_normalization_m2b2.py`, `tests/test_stock_query_router.py`, and `tests/test_agent_regression.py` conventions. M2B.3 suites must cover market-data evidence, provider fallback/degradation, TradingView provenance, route evaluation, cache freshness, and trace sanitization.

**Target Platform**: Backend/agent runtime in the existing Flask/LangGraph service

**Project Type**: Python web-service and agent backend

**Performance Goals**: Preserve M2B.1 route-filter reduction behavior and M2B.2 normalization determinism. Route evaluation must meet the SRS `FR-4.1.3` threshold of at least 85% meaning-based classification accuracy for Vietnamese/mixed-language M2B.3 fixtures. Market-data and visualization tests must remain deterministic and avoid live provider/network dependency by default.

**Constraints**: Keep one ReAct runtime; keep service lifecycle/session/archive controls outside the agent runtime; keep the checkpointer limited to conversation-scoped STM; keep providers hidden below tools; keep TradingView non-evidence by default; keep raw provider payloads and credentials out of prompts/traces; do not change public REST, SSE, Socket.IO, or OpenAPI contracts; do not enable production providers without license/ToS posture, source attribution, freshness behavior, and degraded-state review.

**Scale/Scope**: Current M2B.1/M2B.2 tool-system baseline plus M2B.3 Vietnam market-data families, TradingView visualization outputs, provider/cache/freshness traces, and Vietnamese/mixed-language route fixtures. Live provider integrations may be represented by reviewed descriptors, deterministic fixture adapters, or degraded states until production provider posture is approved.

## Governance and Traceability Context

**Source Requirements**:
- `FR-2.6.2` through `FR-2.6.6` for Vietnam quote/history, fundamentals, breadth/flow, disclosure/corporate-action, and Vietnamese/mixed-language route coverage.
- `FR-2.7.3` through `FR-2.7.5` for Vietnam-first provider priority, market-fact attribution, and freshness-aware cache metadata.
- `FR-2.8.1` through `FR-2.8.4` for TradingView visualization provenance, chart/widget payloads, symbol validation, and non-evidence classification.
- `FR-4.1.3` for at least 85% meaning-based route-classification accuracy.
- `NFR-2.3.5`, `NFR-5.2.13`, `NFR-5.3.8`, `CON-7`, `CON-9`, `AC-9.8`, `AC-9.9`, `AC-9.11`, and `AC-9.16`.
- Explicitly deferred: `IR-3.8` generic web evidence, `FR-2.10.*` reporting composition/persistence, remote/MCP admission, production symbol-store writes, and production provider enablement without governed provider posture.

**Authority References**:
- [PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#phase-2b-enhanced-tool-system-feature-implementations), especially [Milestone Gates](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#milestone-gates), [2B.5 Concrete Market Data and Visualization Tools](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#2b5-concrete-market-data-and-visualization-tools), and [2B.9 Verification and Quality Gates](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#2b9-verification-and-quality-gates).
- [ARCHITECTURE_DESIGN.md](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#485a-tool-gateway-and-evidence-admission-boundary), [section 4.3.4](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#434-tool-provider-selection-and-fallback-view), [section 5.3](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#53-terminology-and-concept-evolution), and [section 7](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#7-architecture-considerations-and-planned-evolution).
- [TECHNICAL_DESIGN.md](../../docs/domains/agent/TECHNICAL_DESIGN.md#322-target-phase-2b-runtime-flow), [section 3.2.3](../../docs/domains/agent/TECHNICAL_DESIGN.md#323-tool-and-adapter-responsibility-split), [section 3.2.4](../../docs/domains/agent/TECHNICAL_DESIGN.md#324-target-tool-contract-and-failure-realization), [section 3.2.5](../../docs/domains/agent/TECHNICAL_DESIGN.md#325-tool-data-model-and-persistent-storage-realization), and [section 4.2](../../docs/domains/agent/TECHNICAL_DESIGN.md#42-routing-output-and-prompt-evolution).
- [TOOLS_RESEARCH_AND_PROPOSAL.md](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#7-target-tool-system-architecture), [section 8](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#8-technical-design-proposal), [section 9](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#9-tool-data-architecture-and-integrity-design), and [section 12](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#12-implementation-roadmap).
- [.specify/memory/constitution.md](../../.specify/memory/constitution.md#vietnam-market-data-and-visualization-evidence-gates), [.specify/memory/architecture.md](../../.specify/memory/architecture.md#current-target-planned-and-gated-labels), and the five architecture view memory files for current/target labels, provider-hidden execution, request-scoped context, cache freshness, and visualization provenance boundaries.
- [.github/instructions/documentation-and-specification.instructions.md](../../.github/instructions/documentation-and-specification.instructions.md), [.github/instructions/backend-python.instructions.md](../../.github/instructions/backend-python.instructions.md), [.github/instructions/langchain-python.instructions.md](../../.github/instructions/langchain-python.instructions.md), and [.github/instructions/testing.instructions.md](../../.github/instructions/testing.instructions.md).
- Verified predecessor evidence in [specs/tool-system-implementation-m2b.1/spec.md](../tool-system-implementation-m2b.1/spec.md), [specs/tool-system-implementation-m2b.1/.verify-done](../tool-system-implementation-m2b.1/.verify-done), [specs/tool-system-m2b.2/spec.md](../tool-system-m2b.2/spec.md), and [specs/tool-system-m2b.2/.verify-done](../tool-system-m2b.2/.verify-done).

**Traceability Updates**: Update `specs/spec-traceability.yaml` so `tool-system-m2b.3` includes `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, and feature-local contracts as evidence. Keep `coverage_status: partial` because M2B.3 maps the Vietnam market-data, visualization, attribution, cache, and route-evaluation slice but intentionally defers generic web evidence, reporting persistence, remote/MCP admission, and later observability dashboards.

**Sync Report Updates**: Run `python scripts/sync_spec_status.py --gate` after plan evidence is added and after every later task, implementation, or verification lifecycle change. Generated reports expected to update are `specs/spec-sync-status.md` and `docs/domains/agent/SRS_SPEC_TRACEABILITY.md`.

**Public Contract Impact**: N/A. `docs/openapi.yaml` remains unchanged. M2B.3 contracts are feature-local internal contracts for market-data evidence, attribution/freshness/cache metadata, TradingView visualization provenance, and route-evaluation fixtures.

**Long-Lived Documentation Impact**: No long-lived architecture or technical-design document edit is required during planning. These documents are authority inputs. After implementation and verification, promote only stable implemented behavior if current/target labels change.

**Lifecycle Status Target**: Promote from `Clarified` to `Planned` when this plan, Phase 0/1 artifacts, updated traceability evidence, and sync gate are complete. Later `Implemented` and `Verified` states require tasks, code evidence, review, `.verify-done`, and passing sync gates.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / Governance Rule | Status | Plan Treatment |
|-----------------------------|--------|----------------|
| Spec-driven, traceable delivery | PASS | Plan maps every M2B.3 SRS item, adds synchronized plan evidence, and runs `python scripts/sync_spec_status.py --gate`. |
| Layered boundaries and explicit ownership | PASS | Service lifecycle/session/archive and STM checkpointer boundaries remain untouched; work stays inside agent tool/provider/normalization boundaries. |
| Evidence-grounded financial intelligence | PASS | Market facts require canonical symbol identity, provider/source, source reference, timestamps, exchange, currency, freshness, license posture, and warnings/degraded reasons. |
| Prompt and memory do not become truth stores | PASS | Raw provider payloads and visualization values do not enter prompts as authority; `ToolContextPack` remains request-scoped. |
| Deterministic tools and contracted interfaces | PASS | Market-data and visualization tools remain behind descriptors, route-filtered exposure, gateway admission, provider policy, normalized outputs, and degraded-state contracts. |
| Vietnam market-data and visualization gates | PASS | Provider production posture is gated; TradingView remains `VisualizationProvenance`; Vietnamese route fixtures and source-attribution coverage are planned. |
| Public contract synchronization | PASS | No OpenAPI/REST/SSE/Socket.IO change is planned; any later public metadata change must be explicit before implementation. |
| Current/target status semantics | PASS | M2B.3 does not promote production provider enablement or generic web/reporting behavior to current status. |

Post-design re-check: PASS. Phase 0/1 artifacts remain feature-local, preserve public contract boundaries, and do not introduce a second runtime, remote tool admission, direct provider exposure to the model, or production provider claims.

## Project Structure

### Documentation (this feature)

```text
specs/tool-system-m2b.3/
|-- spec.md
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   |-- market-data-evidence-contract.md
|   |-- attribution-cache-trace-contract.md
|   |-- tradingview-visualization-contract.md
|   `-- route-evaluation-contract.md
|-- checklists/
|   `-- requirements.md
`-- tasks.md             # Created by /speckit-tasks, not by /speckit-plan
```

### Source Code (repository root)

`src/data/` entries below are authority/context references for canonical symbol identity, retained derivatives, and future approved persistence. M2B.3 implementation tasks do not modify market-data persistence schemas unless a later governed retention task explicitly admits that work.

```text
src/core/
|-- stock_assistant_agent.py       # Existing ReAct entrypoint; integrate filtered market/visualization tools without a second runtime
|-- stock_query_router.py          # Static route taxonomy and Vietnamese/mixed-language fixture evaluation surface
|-- routes.py                      # Existing route enum remains stable
`-- tools/
    |-- descriptors.py             # Extend descriptors for market-data and visualization capabilities
    |-- surface.py                 # Preserve route-filtered model-visible surface behavior
    |-- gateway.py                 # Preserve thin admission/tracing boundary
    |-- provider_policy.py         # Extend provider posture and fallback policy for Vietnam market-data classes
    |-- normalization.py           # Extend output kinds/metadata for market facts, freshness, and VisualizationProvenance
    |-- context.py                 # Preserve request-scoped ToolContextPack assembly
    |-- stock_symbol.py            # Use canonical symbol identity; no production writes
    |-- market_data.py             # Planned Vietnam quote/history/fundamental/breadth/flow/disclosure/corporate-action tool family
    `-- tradingview.py             # Extend as VisualizationProvenance producer, not evidence source

src/data/
|-- repositories/
|   |-- market_snapshot_repository.py
|   `-- symbol_repository.py       # Existing symbol authority; M2B.3 reads canonical identity only
`-- schema/
    |-- market_data_schema.py
    `-- market_snapshots_schema.py

tests/
|-- fixtures/tool_system_m2b3/
|-- helpers/tool_system_m2b3_helpers.py
|-- test_market_data_m2b3.py
|-- test_tradingview_m2b3.py
|-- test_route_evaluation_m2b3.py
|-- test_attribution_cache_m2b3.py
|-- test_tool_gateway_m2b1.py
|-- test_provider_policy_m2b2.py
|-- test_tool_normalization_m2b2.py
|-- test_stock_query_router.py
`-- test_agent_regression.py
```

**Structure Decision**: Use the existing single Python backend/agent layout. Add M2B.3 market-data, visualization, fixtures, and tests around `src/core/tools/` and existing route/agent integration points. Do not add public API routes, a separate gateway service, a second agent runtime, or production provider credentials in this milestone.

## Complexity Tracking

No constitution violations are introduced by this plan.
