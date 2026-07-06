# Implementation Plan: Internal Symbol and Normalization Backbone - M2B.2

**Branch**: `feature/tool-system-m2b.2` | **Date**: 2026-07-06 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/tool-system-m2b.2/spec.md`

## Summary

M2B.2 follows the verified M2B.1 tool gateway baseline by adding the internal backbone required for governed tool output: internal symbol-store lookup semantics, provider adapter descriptors, provider selection policy, execution envelopes, normalized outputs, request-scoped `ToolContextPack`, retained derivative rules, degraded-state handling, and disabled-by-default mutation receipt contracts. The implementation plan stays scoped to roadmap `TS-03` through `TS-05` plus non-mutating `TS-11`; concrete Vietnam quote/history/fundamental providers, TradingView expansion, generic web fetch, report persistence, remote tool admission, and full market-data attribution remain downstream milestones.

The target implementation is additive around the current single ReAct runtime and the existing M2B.1 `ToolSurfaceBuilder` and `ToolGateway` boundary. It must keep provider adapters below model-visible tools, normalize outputs before prompt assembly, keep raw provider/web/tool payloads out of prompt context, and avoid public REST, SSE, Socket.IO, or OpenAPI contract changes.

## Technical Context

**Language/Version**: Python 3.10+ as declared in `requirements.txt`

**Primary Dependencies**: LangChain/LangGraph agent runtime, semantic-router route classification, Pydantic 2.x and dataclasses for internal contracts, PyMongo repositories, Redis or in-memory cache backends, existing Spec Kit sync tooling

**Storage**: Existing MongoDB-backed repositories for durable domain records and metadata; Redis/in-memory cache for freshness/performance only; filesystem remains the artifact-content boundary. `ToolContextPack`, execution envelopes, and normalized raw tool outputs are request-scoped by default and are not persisted wholesale.

**Testing**: `pytest`, `pytest-cov`, focused unit and regression suites following existing `tests/test_tool_gateway_m2b1.py`, `tests/test_tools.py`, `tests/test_stock_query_router.py`, and `tests/test_agent_regression.py` conventions. M2B.2 focused suites cover symbol normalization, provider policy, tool normalization, retention, and disabled mutation receipts.

**Target Platform**: Backend/agent runtime in the existing Flask/LangGraph service

**Project Type**: Python web-service and agent backend

**Performance Goals**: Preserve M2B.1 route-filtered tool-surface behavior and existing compatibility suites. M2B.2 introduces no new public latency SRS threshold; tests should prove normalization and provider-policy checks are deterministic, bounded, and do not expand model-visible tools.

**Constraints**: Keep the single ReAct runtime; keep service-owned lifecycle/session/archive controls out of the agent runtime; keep the checkpointer limited to conversation-scoped STM; keep providers hidden below tools; keep production symbol-store writes disabled; keep raw payloads out of prompts; do not change public API contracts; do not promote target architecture concepts to current status until implementation and long-lived docs agree.

**Scale/Scope**: Current registered tools plus feature-local provider-policy and normalization contracts for the Phase 2B tool backbone. Symbol coverage targets Vietnam symbol and index normalization semantics, not live quote/history/fundamental market-data tools.

## Governance and Traceability Context

**Source Requirements**:
- `FR-2.5.1` through `FR-2.5.5` for tool execution envelopes, normalized output kinds, request-scoped `ToolContextPack`, raw-payload exclusion, and degraded-state reporting.
- `FR-2.6.1` for Vietnam symbol and index normalization.
- `FR-2.7.1` and `FR-2.7.2` for provider classes and provider selection policy below model-visible tools.
- `FR-2.11.1` through `FR-2.11.6` for evolved `StockSymbolTool`, source-of-truth boundaries, symbol identity, retention rules, mutation classification, and mutation receipts.
- `NFR-2.2.6`, `NFR-2.3.4`, `NFR-5.2.15`, `NFR-6.2.5`, `CON-6`, `CON-10`, `AC-9.5`, `AC-9.6`, `AC-9.7`, `AC-9.10`, `AC-9.14`, `AC-9.15`, and `IR-3.3` through `IR-3.7` plus `IR-3.9`.
- Explicitly deferred: `FR-2.7.4`, `NFR-5.2.13`, `CON-9`, and `AC-9.8` remain `TS-06`/M2B.3 market-data attribution and cache-freshness work.

**Authority References**:
- [PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#phase-2b-enhanced-tool-system-feature-implementations), especially milestone gates, `2B.3 Evolved StockSymbolTool over Internal Symbol Store`, and `2B.4 Provider Policy and Normalized Output Backbone`.
- [ARCHITECTURE_DESIGN.md](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#485a-tool-gateway-and-evidence-admission-boundary), [section 4.3.4](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#434-tool-provider-selection-and-fallback-view), [section 5.3](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#53-tool-system-context-boundaries), and [section 7](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#7-architecture-considerations-and-planned-evolution) for target tool boundaries, provider policy, normalized context, source authority, and current-vs-target status rules.
- [TECHNICAL_DESIGN.md](../../docs/domains/agent/TECHNICAL_DESIGN.md#322-target-phase-2b-runtime-flow), [section 3.2.3](../../docs/domains/agent/TECHNICAL_DESIGN.md#323-tool-and-adapter-responsibility-split), [section 3.2.4](../../docs/domains/agent/TECHNICAL_DESIGN.md#324-target-tool-contract-and-failure-realization), and [section 3.2.5](../../docs/domains/agent/TECHNICAL_DESIGN.md#325-tool-system-persistence-and-data-model-realization) for runtime flow, tool/adaptor responsibility split, contract/failure handling, and request-scoped retention.
- [TOOLS_RESEARCH_AND_PROPOSAL.md](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#7-target-tool-system-architecture), [section 8](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#8-technical-design-proposal), [section 9](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#9-tool-data-architecture-and-integrity-design), and [section 12](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#12-implementation-roadmap) for target tool contracts and integrity decisions.
- [.specify/memory/constitution.md](../../.specify/memory/constitution.md#architecture-currenttarget-status-semantics), [.specify/memory/architecture.md](../../.specify/memory/architecture.md#current-target-planned-and-gated-labels), and the five architecture view memory files for project-governed status, boundary, and 4+1 view constraints.
- [spec-kit HOW-TO.md](../../docs/spec-driven%20development%20%28SDD%29/spec-kit%20HOW-TO.md) and [project-documentation-and-specification-methodology.md](../../docs/study-hub/project-documentation-and-specification-methodology.md) for local Spec Kit lifecycle, artifact boundaries, and traceability methodology.
- Verified M2B.1 feature evidence in [specs/tool-system-implementation-m2b.1/spec.md](../tool-system-implementation-m2b.1/spec.md), [review.md](../tool-system-implementation-m2b.1/review.md), and [.verify-done](../tool-system-implementation-m2b.1/.verify-done).

**Traceability Updates**: Update `specs/spec-traceability.yaml` so `tool-system-m2b.2` includes this plan, Phase 0 research, Phase 1 data model, quickstart, feature-local contracts, requirements-alignment checklist, and task breakdown as synchronized evidence. Keep `coverage_status: partial` because M2B.2 maps only the backbone requirements and intentionally defers `TS-06` market-data attribution and later provider capabilities.

**Sync Report Updates**: Run `python scripts/sync_spec_status.py --gate` after plan, task, implementation, or verification traceability updates. Generated reports expected to update are `specs/spec-sync-status.md` and `docs/domains/agent/SRS_SPEC_TRACEABILITY.md`.

**Public Contract Impact**: N/A. `docs/openapi.yaml` remains unchanged; no REST, SSE, Socket.IO, or OpenAPI contract change is planned for M2B.2.

**Long-Lived Documentation Impact**: No immediate long-lived documentation edit is required during planning. Architecture and technical design documents are the target-design authority. After implementation and verification, promote only stable implemented behavior back to long-lived docs if current/target status changes.

**Lifecycle Status Target**: Promote from `Clarified` to `Planned` when this plan and synchronized traceability evidence exist. Later `Implemented` and `Verified` states require completed tasks, implementation evidence, verification review, `.verify-done`, and passing sync gates.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / Governance Rule | Status | Plan Treatment |
|-----------------------------|--------|----------------|
| Spec-driven, traceable delivery | PASS | Plan maps every M2B.2 SRS item, updates traceability evidence, and runs the sync gate. |
| Layered boundaries and explicit ownership | PASS | Service lifecycle/session/archive and checkpointer STM boundaries remain untouched; this plan scopes only the agent tool backbone. |
| Evidence-grounded financial intelligence | PASS | Provider descriptors, source metadata, freshness, and degraded states are explicit; no unsourced market facts are promoted. |
| Prompt and memory do not become truth stores | PASS | `ToolContextPack` is request-scoped and raw payloads are excluded from prompt context. |
| Deterministic tools and contracted interfaces | PASS | Provider policy, normalization, envelopes, and mutation receipts are deterministic internal contracts, with providers hidden below model-visible tools. |
| Architecture current/target status semantics | PASS | Target concepts remain labeled as target/planned until implementation evidence and long-lived docs promote them. |
| Public contract synchronization | PASS | No public contract changes are planned; internal contracts remain feature-local. |

Post-design re-check: PASS. The Phase 0/1 artifacts keep implementation responsibilities in the current source layout and do not introduce a second runtime, public API change, broad provider exposure, or wholesale `ToolContextPack` persistence.

## Project Structure

### Documentation (this feature)

```text
specs/tool-system-m2b.2/
|-- spec.md
|-- plan.md
|-- tasks.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- review.md              # Created during implementation evidence capture
|-- contracts/
|   |-- symbol-normalization-contract.md
|   |-- provider-policy-contract.md
|   |-- tool-normalization-contract.md
|   `-- mutation-retention-contract.md
`-- checklists/
    |-- requirements.md
    `-- requirements-alignment.md
```

### Source Code (repository root)

```text
src/core/
`-- stock_assistant_agent.py # Existing prompt-boundary integration point for prompt-safe context projections

src/core/tools/
|-- descriptors.py          # M2B.1 descriptors extended only where needed
|-- surface.py              # M2B.1 route-filtered exposure preserved
|-- gateway.py              # M2B.1 admission boundary preserved
|-- stock_symbol.py         # Target internal symbol-store behavior
|-- provider_policy.py      # Planned M2B.2 provider descriptors and selection policy
|-- normalization.py        # Planned envelopes, normalized outputs, degraded states
|-- context.py              # Planned request-scoped ToolContextPack
`-- mutation_receipts.py    # Planned disabled mutation receipt contracts

src/data/repositories/
`-- symbol_repository.py    # Existing repository boundary for symbol records

src/data/schema/
`-- symbols_schema.py       # Existing symbol schema boundary; migrations only if tasks require them

src/services/
`-- symbols_service.py      # Existing service behavior remains outside model-visible tools

tests/
|-- fixtures/tool_system_m2b2/
|-- helpers/tool_system_m2b2_helpers.py
|-- test_tool_gateway_m2b1.py
|-- test_tools.py
|-- test_stock_query_router.py
|-- test_agent_regression.py
|-- test_stock_symbol_m2b2.py
|-- test_provider_policy_m2b2.py
|-- test_tool_normalization_m2b2.py
`-- test_tool_retention_m2b2.py
```

**Structure Decision**: Use the existing single Python backend/agent layout. Add internal tool-system modules under `src/core/tools/` because M2B.2 extends the M2B.1 gateway/tool boundary. Reuse existing data repositories for internal symbol records and avoid public API, transport, or migration work unless later tasks identify a concrete implementation need inside this feature scope.

## Complexity Tracking

No constitution violations are introduced by this plan.
