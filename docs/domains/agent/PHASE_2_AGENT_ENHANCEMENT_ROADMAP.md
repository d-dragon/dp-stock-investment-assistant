# Phase 2: LangChain Agent Enhancement Roadmap

> **Document Version**: 1.6
> **Created**: January 15, 2026  
> **Last Updated**: June 18, 2026
> **Status**: Planning (M2 Implemented)  
> **Branch**: `enhance-agent-prompt-system-followup`

## Executive Summary

This roadmap outlines the Phase 2 enhancements for the Stock Investment Assistant's LangChain agent. Building on the Phase 1 foundation (ReAct agent, cache-aware tool execution, ToolRegistry, semantic routing), Phase 2 focuses on **conversation-scoped STM and context-boundary hardening**, **prompt-system evolution**, **production-ready tools**, **structured outputs**, and **multi-agent orchestration**.

### Phase Overview

| Phase | Focus Area | Key Deliverables |
|-------|------------|------------------|
| **2A** | Foundation | STM foundation, future LTM design, prompt management, structured outputs |
| **2B** | Features | Enhanced tool system with Tool Gateway, provider adapters, normalized tool context, TradingView visualization, reporting |
| **2C** | Advanced | Multi-agent orchestration, technical refinements |

---

## Phase 2A: Foundation Enhancements

### 2A.1 Conversation Memory Foundation

**Objective**: Establish conversation-scoped short-term memory (STM) as the current runtime baseline, keep session context as reusable parent business context, and prepare a separate future long-term memory (LTM) track for stable personalization.

> **Status (2026-05-15):** The STM foundation is implemented on the REST path. The canonical runtime contract is `conversation_id -> thread_id` with the hierarchy `workspace -> session -> conversation`. Socket.IO lifecycle parity, automated summarization, and future LTM remain follow-up work.

#### Current Baseline

```
┌────────────────────────────────────────────────────────────────────┐
│              CURRENT BASELINE: Conversation-Scoped STM            │
├────────────────────────────────────────────────────────────────────┤
│  API Request (conversation_id optional)                           │
│      ↓                                                            │
│  REST: ChatService validates lifecycle, loads parent context      │
│      ↓                                                            │
│  agent.invoke(..., config={"configurable": {                     │
│      "thread_id": conversation_id}}) when stateful               │
│      ↓                                                            │
│  MongoDBSaver persists recoverable thread-local state             │
│      ↓                                                            │
│  Response + metadata sync on REST path                            │
└────────────────────────────────────────────────────────────────────┘
```

- `APIServer` creates and injects a LangGraph `MongoDBSaver` checkpointer.
- The canonical STM binding is `conversation_id -> thread_id`, not `session_id -> thread_id`.
- Sessions remain parent business context; sibling conversations do not share checkpoints.
- The REST chat path uses `ChatService` to reject archived conversations, ensure metadata records, and record per-turn metadata.
- Requests that omit `conversation_id` continue through the stateless single-turn path.
- Socket.IO preserves `conversation_id` but still bypasses `ChatService` lifecycle and metadata helpers.
- Summary fields and thresholds exist, but automated summarization is not yet triggered during chat execution.
- Future LTM personalization storage is not yet implemented.

#### Target Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│         TARGET: Layered Memory with Explicit Boundary Split       │
├────────────────────────────────────────────────────────────────────┤
│  Session context (parent business context)                        │
│      ↓                                                            │
│  Conversation-scoped STM via checkpoints                          │
│      ↓                                                            │
│  Agent runtime resumes thread-local state with conversation_id    │
│      ↓                                                            │
│  Future LTM store persists stable personalization only            │
│      ↓                                                            │
│  RAG and tools remain separate evidence and computation layers    │
└────────────────────────────────────────────────────────────────────┘
```

- STM remains conversation-scoped, with thread-local checkpoint state persisted through LangGraph using the canonical `conversation_id -> thread_id` binding.
- Session context is resolved outside the agent thread as service-owned parent business context and may be merged into active conversation context without collapsing sibling conversations into one checkpoint surface.
- Conversation lifecycle metadata and archive status remain service-owned authorities alongside, but outside, checkpoint persistence.
- Future LTM is a cross-conversation personalization layer for stable preferences and symbol-tracking context only.
- RAG remains the home for sourced evidence, tools remain the home for fetched numbers and deterministic computation, and the prompt system remains a behavioral boundary rather than a storage layer.

#### Remaining Work Items

1. **Close transport parity gaps**
    - Route Socket.IO through the same lifecycle and metadata helpers as REST, or provide an equivalent service-owned boundary.
    - Preserve archive enforcement and metadata synchronization across both transports.

2. **Wire STM summarization behavior**
    - Convert the current summary schema and thresholds into an actual runtime trigger.
    - Keep summarization framed as STM context management, not as LTM or RAG.

3. **Clarify session-context realization**
    - Keep service-side context resolution authoritative.
    - Document prompt or runtime injection only where the behavior is actually realized.

4. **Design future LTM phase**
    - Introduce a namespaced store for stable personalization and symbol-tracking context.
    - Keep LTM separate from financial facts, RAG evidence, and prompt assets.

5. **Extend observability and repair posture**
    - Keep reconciliation and migration tooling aligned with the canonical `conversation_id` contract.
    - Expand test and runbook coverage for degraded-state conditions such as checkpoint loss or metadata divergence.

#### Architecture Decision

> **Design Note**: Treat session context, lifecycle metadata, STM, future LTM, RAG, tools, and the prompt system as separate boundaries. The implemented STM baseline uses LangGraph `MongoDBSaver` for recoverable thread-local state, while service-owned metadata and lifecycle controls stay outside checkpoint persistence.

#### Implementation Pattern

```python
def process_query(self, query: str, *, conversation_id: str | None = None) -> AgentResponse:
     config = None
     if self.checkpointer is not None and conversation_id:
          config = {"configurable": {"thread_id": conversation_id}}

     result = self.agent_executor.invoke(
          {"messages": [HumanMessage(content=query)]},
          config=config,
     )
     return self._build_response(result)
```

#### Dependencies

- LangGraph checkpointer wiring through the API server bootstrap
- Service-owned conversation lifecycle and metadata boundary in `ChatService`
- Session and conversation management services that preserve `workspace -> session -> conversation`
- Future LTM design and storage strategy for Phase 2A.2+

#### Success Criteria

- The same `conversation_id` resumes the same conversation thread across requests and restarts.
- Requests without `conversation_id` preserve stateless single-turn behavior.
- Archived conversations are rejected on the service-governed path rather than silently resumed.
- Socket.IO parity and automated summarization are tracked as explicit remaining work, not implied as completed runtime behavior.
- Future LTM work remains separate from STM, RAG, and prompt-asset plans.

---

### 2A.2 Prompt Compiler Path & Controlled Rollout

**Objective**: Externalize prompt assets, establish the planned prompt compiler path (`PromptAssetLoader -> PromptAssembler -> ResponseGuardrailMiddleware`), and support controlled evaluation and rollout of prompt changes.

> **Status (2026-06-04):** Milestones M1 (Prompt Runtime Parity) and **M2 (Route-Aware Skills) are implemented and verified**. PS-01 through PS-08 are complete.  
> - **M1 delivery:** `PromptAssetLoader` implemented with full 8-field selection tuple; prompt asset externalized to `src/prompts/system/react_analyst.md` (per ADR taxonomy, version in frontmatter); `prompts.*` config surface with two-layer validation; response metadata emitted on all invocations; 42/42 tasks complete, 29/29 tests passing.  
> - **M2 delivery:** `SegmentType`/`SegmentEntry`/`CompiledPrompt` data types, extended manifest scanning for `skills/routes/`, 8 route-skill assets created, `PromptAssembler` with deterministic 7-segment assembly order, missing-skill graceful degradation, dynamic controls allowlist validation, agent wiring with route-context metadata emission; 45/45 tasks complete, 41/41 tests passing (~71µs average assembly performance).  
> - **Verification:** [M1 review](../../../specs/prompt-system-milestone1/review.md) | [M2 review](../../../specs/prompt-system-milestone2/review.md)  
> **Next step:** Plan Milestone M3 (Evaluation and Safety Gates — PS-09 to PS-10) for offline evaluation harness and finance-domain guardrail verification.
> **Design authority:** [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md v1.8](./PROMPT_SYSTEM_RESEARCH_PROPOSAL.md). Release-gate thresholds formalized in SRS v2.7.

#### Current Baseline (M1 Delivery — Prompt Runtime Parity)

- ReAct prompt externalized to `src/prompts/system/react_analyst.md` with frontmatter metadata (per ADR taxonomy — version in frontmatter, not directory path)
- `PromptAssetLoader` implemented in `src/core/prompt_asset_loader.py` with 8-field selection tuple, manifest caching, and baseline fallback
- `prompts.*` config surface with two-layer validation (structural errors block startup; content-resolution errors fall back with WARN)
- Prompt identity injected into response metadata (`prompt_version`, `prompt_variant`, `selection_mode`, `model_provider`, `model_name`) and LangSmith trace tags
- `REACT_SYSTEM_PROMPT` retained as deprecated alias during M1 observation window (will be removed after PS-04 verification)
- `langchain_adapter.py` has `PromptBuilder` pattern — marked as deprecated; `PromptAssetLoader` is the canonical prompt source

#### Target Compiler Path

- Prompt assets organized by ADR taxonomy under `src/prompts/system/`, `src/prompts/skills/`, and `src/prompts/experiments/`
- Prompt variants identified by version, variant label, and agent role
- Shared policy, route-aware skills, and bounded runtime context composed through the planned compiler path
- Offline evaluation and guarded rollout integrated with LangSmith metadata
- Prompt selection configurable through a dedicated `prompts.*` config surface

#### Execution Backlog Mirror (Synced to Proposal v1.8)

> Detailed dependency authority remains in [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](./PROMPT_SYSTEM_RESEARCH_PROPOSAL.md). This roadmap mirrors the execution backlog and milestone gates so planning and design stay synchronized in both directions.

| Order | Backlog ID | Priority | SRS Alignment | Depends On | Roadmap Outcome |
|---|---|---|---|---|---|
| 1 | `PS-01` | P0 | FR-1.4.5, FR-1.4.8, NFR-6.2.3 | None | Extract the current ReAct prompt into `src/prompts/system/react_analyst.md` (per ADR taxonomy, version in frontmatter, not directory path) and preserve it as the canonical baseline asset |
| 2 | `PS-02` | P0 | FR-1.4.5, FR-1.4.8, FR-1.4.16 | `PS-01` | Implement `PromptAssetLoader` / loader-facade behavior with metadata parsing, caching, validation, and baseline fallback conventions |
| 3 | `PS-03` | P0 | FR-1.4.5, FR-1.4.8, NFR-6.2.3 | `PS-01`, `PS-02` | Add `prompts.*` config surface and fail-closed validation rules so only valid prompt assets can activate |
| 4 | `PS-04` | P0 | FR-1.4.5, FR-1.4.6 | `PS-02`, `PS-03` | Replace `REACT_SYSTEM_PROMPT` as the primary source of truth for `StockAssistantAgent` |
| 5 | `PS-05` | P0 | FR-1.4.6, NFR-5.2.5–5.2.9 | `PS-04` | Inject prompt identity into response metadata and trace metadata for top-level runs |
| 6 | `PS-06` | P0 | FR-1.4.8, FR-1.4.13, AC-8.2, AC-8.7 | `PS-02`, `PS-04`, `PS-05` | Add rollback safety, WARN logging, and fault-injection coverage for invalid prompt activation |
| 7 | `PS-07` | P1 | FR-1.4.7 | `PS-04` | ✅ Create route-context prompt assets for all 8 `StockQueryRouter` categories — implemented M2 |
| 8 | `PS-08` | P1 | FR-1.4.7, FR-1.4.11, FR-1.4.16, NFR-5.2.8 | `PS-05`, `PS-07` | ✅ Compose route-aware prompt behavior with `PromptAssembler` and `@dynamic_prompt` middleware — implemented M2 |
| 9 | `PS-09` | P1 | FR-1.4.12, AC-8.6 | `PS-05`, `PS-08` | Build the offline evaluation harness and baseline prompt comparison datasets |
| 10 | `PS-10` | P1 | FR-1.4.12, FR-1.5.6, AC-8.5–8.8 | `PS-06`, `PS-09` | Enforce finance-domain guardrail verification before prompt promotion |
| 11 | `PS-11` | P2 | FR-1.4.9, FR-1.4.12, FR-1.4.13, AC-8.6–8.8 | `PS-09`, `PS-10` | Add controlled experiment and rollout modes (`fixed`, `forced`, `shadow`, optional `weighted`) |
| 12 | `PS-12` | P3 | Later evolution; no current release gate | `PS-08`, `PS-09`, `PS-11` | Introduce multi-agent prompt taxonomy only after Skills-pattern evidence justifies it |

#### Milestone Gates

| Milestone | Backlog IDs | Outcome | Gate |
|---|---|---|---|
| `M1` - Prompt Runtime Parity | `PS-01` to `PS-06` | Externalized, versioned, observable, rollback-safe ReAct prompt runtime | Do not begin route-context composition until the hardcoded prompt is fully removed from the primary ReAct path |
| `M2` - Route-Aware Skills | `PS-07` to `PS-08` | ✅ **Implemented and verified** — `PromptAssembler` with 7-segment deterministic assembly, 8 route-skill assets, missing-skill graceful degradation, dynamic controls allowlist, agent wiring with route-context metadata; 45/45 tasks, 41/41 tests passing | [M2 review](../../../specs/prompt-system-milestone2/review.md) — gate satisfied |
| `M3` - Evaluation and Safety Gates | `PS-09` to `PS-10` | Offline comparison and finance-safety regression coverage for prompt changes | Do not enter `shadow`, `weighted`, or `active` until finance-safety blockers pass at 100%, missing-data handling passes at >=98%, applicable route or tool datasets pass at >=95%, and mandatory metadata keys are present on 100% of relevant runs |
| `M4` - Controlled Rollout | `PS-11` | Safe candidate comparison in `forced` or `shadow` mode, with weighted exposure explicitly optional | Keep production on `fixed` unless the approved baseline fallback, rollback target, and FR-1.4.13 live rollback triggers remain active for any live candidate path |
| `M5` - Multi-Agent Prompt Foundation | `PS-12` | Specialist prompt families and handoff contracts ready for future orchestration | Do not start multi-agent runtime work until Skills-pattern evidence shows a real limitation |

These milestone gates mirror the target design in [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](./PROMPT_SYSTEM_RESEARCH_PROPOSAL.md) and the authoritative thresholds in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md); later implementation plans should inherit them unchanged.

#### Immediate Delivery Slice (M1 & M2 Complete)

##### M1 — Prompt Runtime Parity (PS-01 to PS-06)
- `PS-01`: ✅ Externalized to `src/prompts/system/react_analyst.md` with frontmatter metadata (ADR taxonomy).
- `PS-02`: ✅ `PromptAssetLoader` with 8-field tuple, manifest cache, frontmatter parsing, baseline fallback.
- `PS-03`: ✅ `prompts.*` config surface with two-layer validation (structural + content resolution).
- `PS-04`: ✅ `StockAssistantAgent` uses `PromptAssetLoader` as primary prompt source; `REACT_SYSTEM_PROMPT` deprecated.
- `PS-05`: ✅ Prompt identity in response metadata and LangSmith trace tags.
- `PS-06`: ✅ Baseline fallback safety with WARN logging and fault-injection coverage.
- **M1 verified**: [specs/prompt-system-milestone1/review.md](../../../specs/prompt-system-milestone1/review.md) — 42/42 tasks, 29/29 tests.

##### M2 — Route-Aware Skills (PS-07 to PS-08)
- `PS-07`: ✅ Created 8 route-skill assets under `src/prompts/skills/routes/` — one per `StockQueryRouter` category (`price_check`, `news_analysis`, `portfolio`, `technical_analysis`, `fundamentals`, `ideas`, `market_watch`, `general_chat`).
- `PS-08`: ✅ Implemented `PromptAssembler` (`src/core/prompt_assembler.py`) with:
  - `SegmentType` enum (7 segments: SHARED_POLICY, ROLE_PROMPT, ROUTE_SKILL, MEMORY_CONTEXT, EVIDENCE, TASK_FRAMING, OUTPUT_CONTRACT) with authority-level stratification
  - `compile(selection, route, runtime_context)` → `CompiledPrompt` with deterministic 7-segment assembly order
  - Missing-skill graceful degradation — logs WARN, records gap in `trace_metadata.missing_route_skills`
  - Dynamic controls allowlist validation — drops unrecognized fields, records in `trace_metadata.dropped_dynamic_fields`
  - Extended `_build_manifest()` in `PromptAssetLoader` to scan `skills/routes/` with `route_scope` validation
  - Wired into `StockAssistantAgent.__init__()` and `_inject_prompt_metadata()` when `route_contexts.enabled: true`
  - M1 backward compatibility preserved when `route_contexts.enabled: false`
- **M2 verified**: [specs/prompt-system-milestone2/review.md](../../../specs/prompt-system-milestone2/review.md) — 45/45 tasks, 41/41 tests.

#### Near-Term Implementation Pattern

```python
# src/prompts/system/react_analyst.md (ADR taxonomy — version in frontmatter, not path)
---
name: react_analyst_v1
version: 1.0.0
agent_role: react_analyst
status: active
variant: baseline
locale: en
---

You are a professional stock investment assistant...

# src/core/stock_assistant_agent.py
from core.prompt_asset_loader import PromptAssetLoader
from core.prompt_types import SelectionTuple

class StockAssistantAgent:
    def __init__(self, config, data_manager, *, prompt_asset_loader=None):
        if prompt_asset_loader:
            self._current_prompt = prompt_asset_loader.resolve(
                SelectionTuple(
                    agent_role="react_analyst",
                    selection_mode="fixed",
                    requested_version=config["prompts"]["system"]["active_version"],
                )
            )
            self._prompt_content = (...)  # read resolved asset from disk
```

#### Dependencies

- Existing `PromptBuilder` pattern in `langchain_adapter.py` as migration source material, not final authority
- LangSmith for trace metadata and evaluation (existing integration)
- Semantic router integration for route-based skill activation
- Research and dependency authority: [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md v1.8](./PROMPT_SYSTEM_RESEARCH_PROPOSAL.md)
- SRS: FR-1.4.5–1.4.16, FR-1.5.6, NFR-5.2.8–5.2.11, NFR-6.2.3, AC-8.5–8.11
- Governance validation reference: [PROMPT_SYSTEM_BENCHMARK_REVIEW.md](./PROMPT_SYSTEM_BENCHMARK_REVIEW.md)
- ADRs: [ADR-002](./DECISIONS/AGENT_ARCHITECTURE_DECISION_RECORDS.md), [ADR-003](./DECISIONS/AGENT_ARCHITECTURE_DECISION_RECORDS.md)

#### Success Criteria

- ✅ ReAct path loads the prompt from a versioned asset instead of the hardcoded `REACT_SYSTEM_PROMPT`
- ✅ Prompt version and variant are visible in relevant response metadata and trace metadata
- ✅ All 8 semantic routes can resolve explicit route-context assets before non-fixed rollout modes are considered
- ⬜ Offline evaluation blocks finance-safety regressions before any live prompt experimentation is enabled (M3)
- ✅ Proposal and roadmap remain aligned on backlog IDs, milestone gates, and the next delivery slice

---

### 2A.3 Structured Outputs

**Objective**: Guarantee JSON schema responses from the agent for consistent API contracts and frontend parsing.

#### Current State

- Agent returns unstructured text responses
- Frontend must parse freeform text
- No validation of response structure
- `AgentResponse` dataclass exists but content is unstructured string

#### Target State

- Agent uses `with_structured_output()` for typed responses
- Response schemas defined with Pydantic models
- Validation at agent output boundary
- Fallback to text for unexpected formats

#### Work Items

1. **Define Response Schemas**
   - Create Pydantic models for each response type (analysis, recommendation, error)
   - Add JSON schema generation for frontend contracts

2. **Integrate Structured Output**
   - Use `model.with_structured_output(ResponseSchema)` for final answers
   - Implement response router based on query type

3. **Add Validation Layer**
   - Validate agent output against schema
   - Graceful fallback for malformed responses
   - Log schema violations for debugging

4. **Update API Contracts**
   - Update OpenAPI spec with new response schemas
   - Document response types for frontend team

#### Implementation Pattern

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional, List

class StockAnalysisResponse(BaseModel):
    """Structured response for stock analysis queries."""
    symbol: str = Field(description="Stock ticker symbol")
    analysis_type: Literal["technical", "fundamental", "sentiment"]
    summary: str = Field(description="Brief analysis summary")
    metrics: dict = Field(default_factory=dict)
    recommendation: Optional[str] = None
    confidence: float = Field(ge=0, le=1)
    sources: List[str] = Field(default_factory=list)

# Usage in agent
structured_model = self.model.with_structured_output(StockAnalysisResponse)
```

#### Dependencies

- Pydantic v2 (existing)
- OpenAI function calling support (existing)
- OpenAPI spec updates

#### Success Criteria

- 100% of analysis responses conform to schema
- Frontend can rely on typed response structure
- Schema violations logged with context
- API documentation reflects new contracts

---

## Phase 2B: Enhanced Tool System Feature Implementations

Phase 2B replaces the earlier generic TradingView and multi-source-data plan with a enhanced tool-system roadmap. The roadmap keeps the current LangChain/LangGraph ReAct runtime, preserves `ToolRegistry` as the inventory boundary, and evolves the tool layer through runnable increments.

### 2B.0 Tool-System Goals, Boundaries, and Gates

**Objective**: Establish the tool-system direction before adding provider-specific integrations.

#### Target Direction

- Introduce a thin in-process `ToolGateway` as a policy, validation, and trace boundary around registry-backed tool execution.
- Make Vietnam-market data a first-class tool domain.
- Separate agent-visible tools from lower-level provider adapters.
- Treat TradingView output as visualization provenance, not canonical financial evidence.
- Delay generic web fetching until concrete market-data, symbol, visualization, and reporting tools are functional.
- Preserve the layered architecture rule: tools fetch and compute, the LLM reasons, and memory does not store market facts.

#### Promotion Gates

| Gate | Required Before | Pass Condition |
|------|-----------------|----------------|
| Contract gate | Provider expansion and report persistence | Minimum contracts for tool descriptors, execution envelopes, normalized outputs, `ToolContextPack`, provider policy, mutation receipts, and artifacts are defined |
| Tool exposure gate | Adding new model-visible tools | Route-to-tool exposure map exists and unrelated tools are hidden from representative route fixtures |
| Provider gate | Production provider use | License/ToS posture, provider class, freshness policy, attribution, and fail-closed behavior are documented |
| Generic web gate | Enabling `GenericWebFetchTool` | Allowlist, parser limits, prompt-injection quarantine, citation extraction, and malicious-content fixtures exist |
| Mutation gate | Enabling symbol-store writes | `workflow_mutation` policy, `internal_state_mutation` subtype, authorization, confirmation, audit metadata, and `MutationReceipt` behavior are defined |
| Report persistence gate | Persisting generated reports or artifacts | `ToolContextPack` inputs, source lineage, degraded-state visibility, artifact metadata, and URI retention are defined |
| TradingView authority gate | Using TradingView values as evidence | Explicit policy admits the data category; otherwise TradingView remains `VisualizationProvenance` only |
| Data integrity gate | Persisting market facts | Symbol + exchange + currency identity, provider/source metadata, timestamp, freshness, license mode, and cache policy are present |

#### Success Criteria

- Phase 2B planning distinguishes tools, adapters, normalized outputs, request-scoped context, and durable records.
- Implementation plans can start with existing tools and evolve without a second runtime or separate gateway service.
- Vietnam-provider production use remains blocked until licensing and source-attribution gates are satisfied.

#### Execution Backlog Mirror (Synced to Tool Proposal v1.6)

> Detailed research context remains in [TOOLS_RESEARCH_AND_PROPOSAL.md](./TOOLS_RESEARCH_AND_PROPOSAL.md). This roadmap mirrors the execution backlog and milestone gates so Phase 2B planning stays traceable to [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md) v2.8. The SRS remains the normative requirement source; this table carries sequencing and delivery intent only.

| Order | Backlog ID | Priority | SRS Alignment | Detailed Section | Depends On | Roadmap Outcome |
|---|---|---|---|---|---|---|
| 1 | `TS-01` | P1 | FR-2.4.1, FR-2.4.2, NFR-6.2.6, IR-3.1, IR-3.2, AC-9.1 | [2B.1 AgentTool Baseline and Descriptor Inventory](#2b1-agenttool-baseline-and-descriptor-inventory) | None | Introduce `AgentTool` target terminology and descriptors for `StockSymbolTool`, `TradingViewTool`, and `ReportingTool` while preserving current registry execution |
| 2 | `TS-02` | P1 | FR-2.4.3, FR-2.4.4, FR-2.4.5, FR-2.4.6, NFR-5.2.12, AC-9.2, AC-9.3, AC-9.4 | [2B.2 Route-Filtered Tool Surface and Thin Gateway](#2b2-route-filtered-tool-surface-and-thin-gateway) | `TS-01` | Add route-filtered `ToolSurfaceBuilder` and thin in-process `ToolGateway` admission around registry-backed tools |
| 3 | `TS-03` | P1 | FR-2.6.1, FR-2.11.1, FR-2.11.2, FR-2.11.3, AC-9.5, AC-9.6 | [2B.3 Evolved StockSymbolTool over Internal Symbol Store](#2b3-evolved-stocksymboltool-over-internal-symbol-store) | `TS-01`, `TS-02` | Evolve `StockSymbolTool` into the internal symbol-store lookup, normalization, coverage, aliases, identifiers, tags, and stored-snapshot boundary |
| 4 | `TS-04` | P1 | FR-2.7.1, FR-2.7.2, NFR-6.2.5, CON-6, IR-3.3, IR-3.4, AC-9.7 | [2B.4 Provider Policy and Normalized Output Backbone](#2b4-provider-policy-and-normalized-output-backbone) | `TS-02` | Define provider classes, adapter descriptors, provider selection policy, fallback posture, license posture, and provider-hidden model-visible tools |
| 5 | `TS-05` | P1 | FR-2.5.1-FR-2.5.5, NFR-2.2.6, IR-3.5-IR-3.7, AC-9.10 | [2B.4 Provider Policy and Normalized Output Backbone](#2b4-provider-policy-and-normalized-output-backbone) | `TS-02`, `TS-04` | Normalize tool outputs into execution envelopes, output kinds, degraded states, and request-scoped `ToolContextPack` inputs |
| 6 | `TS-06` | P1 | FR-2.6.2, FR-2.6.3, FR-2.7.3-FR-2.7.5, NFR-2.3.5, NFR-5.2.13, CON-9, AC-9.8, AC-9.9 | [2B.5 Concrete Market Data and Visualization Tools](#2b5-concrete-market-data-and-visualization-tools) | `TS-03`, `TS-04`, `TS-05` | Deliver approved Vietnam quote, history, fundamentals, provider attribution, freshness, stale-data, and cache-freshness behavior |
| 7 | `TS-07` | P2 | FR-2.6.4, FR-2.6.5, FR-2.6.6, AC-9.16 | [2B.5 Concrete Market Data and Visualization Tools](#2b5-concrete-market-data-and-visualization-tools) | `TS-06` | Extend Vietnam coverage to breadth, flow, disclosures, corporate actions, and Vietnamese/mixed-language route fixtures |
| 8 | `TS-08` | P2 | FR-2.8.1-FR-2.8.4, CON-7, AC-9.11 | [2B.5 Concrete Market Data and Visualization Tools](#2b5-concrete-market-data-and-visualization-tools) | `TS-02`, `TS-05` | Expand `TradingViewTool` for charts, widgets, deep links, symbol validation, ticker tape, heatmaps/screeners where supported, and visualization-only authority |
| 9 | `TS-09` | P2 | FR-2.10.1-FR-2.10.4, FR-1.5.1, FR-1.5.3, IR-3.10, AC-9.13, AC-9.17 | [2B.6 Reporting from ToolContextPack](#2b6-reporting-from-toolcontextpack) | `TS-05`, `TS-06`, `TS-08` | Make `ReportingTool` compose reports from `ToolContextPack`, visualization provenance, generated artifacts, source attribution, and finance-safety checks |
| 10 | `TS-10` | P2 | FR-2.9.1-FR-2.9.4, NFR-4.3.5, NFR-5.2.14, CON-8, IR-3.8, AC-9.12 | [2B.7 Generic Web Evidence Pipeline](#2b7-generic-web-evidence-pipeline) | `TS-05`, `TS-06`, `TS-09` | Add deny-by-default generic web evidence pipeline with allowlist, parser limits, ToS/licensing posture, citations, and prompt-injection quarantine |
| 11 | `TS-11` | P1 | FR-2.11.4-FR-2.11.6, NFR-2.3.4, NFR-5.2.15, CON-10, IR-3.9, AC-9.14, AC-9.15 | [2B.3 Evolved StockSymbolTool over Internal Symbol Store](#2b3-evolved-stocksymboltool-over-internal-symbol-store), [2B.4 Provider Policy and Normalized Output Backbone](#2b4-provider-policy-and-normalized-output-backbone) | `TS-03`, `TS-05` | Add tool data-integrity controls for request-scoped context, retained source lineage, gated internal symbol mutations, and `MutationReceipt` audit records |
| 12 | `TS-12` | P1 | FR-2.6.6, FR-4.1.3, NFR-5.3.8, AC-9.16 | [2B.9 Verification and Quality Gates](#2b9-verification-and-quality-gates) | `TS-02`, `TS-06` | Build Vietnamese and mixed-language eval sets for price, chart, fundamentals, disclosures, breadth, flow, and report routing |
| 13 | `TS-13` | P2 | NFR-5.2.12-NFR-5.2.15, NFR-5.3.7, NFR-5.3.8 | [2B.9 Verification and Quality Gates](#2b9-verification-and-quality-gates) | `TS-02`, `TS-05` | Add observability and quality dashboards for exposed tools, selected tools, provider classes, freshness, degraded states, attribution coverage, and mutation audit |
| 14 | `TS-14` | P3 | FR-2.4.5, NFR-6.2.6, IR-3.1-IR-3.5, AC-9.4 | [2B.8 Optional Remote MCP-Style Tool Admission](#2b8-optional-remote-mcp-style-tool-admission) | `TS-01`, `TS-02`, `TS-05`, `TS-13` | Keep remote or MCP-style tool admission optional until local descriptor integrity, policy admission, credentials, traceability, and operational need exist |

#### Milestone Gates

| Milestone | Backlog IDs | Outcome | Gate |
|---|---|---|---|
| `M2B.1` - Tool Contract and Gateway Baseline | `TS-01` to `TS-02` | Existing tools have descriptors, route-filtered exposure, and gateway admission without changing the current ReAct runtime | Do not add new provider-backed model-visible tools until descriptor integrity, route filtering, and degraded-state admission are testable |
| `M2B.2` - Internal Symbol and Normalization Backbone | `TS-03` to `TS-05`, `TS-11` | `StockSymbolTool` uses the internal symbol-store boundary and tool outputs normalize into envelopes, output kinds, source metadata, and request-scoped context | Do not enable symbol-store writes until `workflow_mutation`, `internal_state_mutation`, authorization/confirmation, and `MutationReceipt` behavior are defined |
| `M2B.3` - Vietnam Market and Visualization Coverage | `TS-06` to `TS-08`, `TS-12` | Vietnam quote/history/fundamental coverage, route fixtures, and TradingView visualization provenance are available through approved adapters | Do not treat TradingView values as evidence; do not promote Vietnam providers to production without license/ToS posture, source attribution, and freshness checks |
| `M2B.4` - Reports and Generic Web Evidence | `TS-09` to `TS-10` | Reports are generated from `ToolContextPack`; generic web fetch is allowlisted, parser-limited, cited, and prompt-injection quarantined | Do not enable generic web fetch before concrete market-data, symbol, visualization, and reporting flows are functional and tested |
| `M2B.5` - Observability and Optional Remote Tool Admission | `TS-13` to `TS-14` | Tool traces, degraded-state metrics, attribution coverage, and optional remote/MCP-style descriptor admission are ready for evaluated future use | Do not admit remote descriptors without local descriptor integrity, policy admission, credentials, timeout/rate-limit controls, and traceability |

#### Immediate Delivery Slice

The first delivery wave is intentionally split across milestone gates. `M2B.1` covers only `TS-01` to `TS-02`: existing tool descriptors, route-filtered exposure, and in-process gateway admission without changing the current ReAct runtime. Later milestones extend that foundation into `TS-03` to `TS-05` plus the non-mutating parts of `TS-11`, including internal symbol-store direction, provider policy, normalized outputs, and request-scoped `ToolContextPack` behavior. Vietnam provider expansion, reporting persistence, generic web fetch, and remote/MCP-style admission remain follow-up slices behind their gates.

---

### 2B.1 AgentTool Baseline and Descriptor Inventory

**Objective**: Rename and describe the current tool execution baseline without changing user-facing behavior.

#### Runnable Increment

`StockSymbolTool`, `TradingViewTool`, and `ReportingTool` continue through the current registry path, but each declares model-visible and internal descriptors.

#### Work Items

1. Introduce `AgentTool` as the target architectural name replacing the narrower `CachingTool` terminology while preserving cache-aware behavior.
2. Add `ToolCapabilityDescriptor` entries for existing `StockSymbolTool`, `TradingViewTool`, and `ReportingTool`.
3. Add `ToolPolicyDescriptor` entries with route family, risk class, cache policy, timeout budget, required metadata, and output kind.
4. Record descriptor version or hash in local trace metadata.
5. Add compatibility fixtures proving existing tool calls still work.

#### Success Criteria

- Current enabled tools can still be listed through `ToolRegistry`.
- Current tool calls remain backward-compatible except for added metadata, warnings, or degraded-state fields.
- Model-visible descriptors do not expose provider fallback rules, credentials, parser limits, or license policy.

---

### 2B.2 Route-Filtered Tool Surface and Thin Gateway

**Objective**: Add pre-model tool exposure and execution admission while keeping a fused in-process runtime.

#### Runnable Increment

The agent receives a compact route-filtered tool list, and selected tool calls execute through `ToolGateway.execute(route, tool_name, args)`.

#### Work Items

1. Add `ToolSurfaceBuilder` for route-filtered model-visible tool exposure.
2. Build a static route-to-tool exposure map from the current route taxonomy.
3. Add an in-process `ToolGateway` facade around `ToolRegistry` and `AgentTool`.
4. Enforce pre-execution argument validation, route-tool matching, risk-class admission, timeout handling, and degraded-state denial.
5. Emit trace metadata for pre-model exposure, pre-execution admission, execution, validation, and response assembly.
6. Document anti-goals in implementation notes: no separate gateway service, no provider parsing inside the gateway, and no dynamic route discovery in this phase.

#### Success Criteria

- Price, chart, report, disclosure, and market-breadth route fixtures expose only expected tool families.
- Disallowed tool calls return degraded-state metadata instead of executing.
- The LangChain/LangGraph ReAct execution path remains the primary runtime.

---

### 2B.3 Evolved `StockSymbolTool` over Internal Symbol Store

**Objective**: Reposition `StockSymbolTool` as the in-system persistent symbol lookup, normalization, and controlled manipulation tool.

#### Runnable Increment

Symbol lookup and search routes use `InternalSymbolStoreAdapter` over `SymbolRepository`. Live Yahoo-backed lookup is no longer the target path for this tool.

#### Work Items

1. Add `InternalSymbolStoreAdapter` over the MongoDB `symbols` collection.
2. Evolve `StockSymbolTool` actions for lookup, search, normalize, list by exchange, list by sector, list tracked symbols, and tag/coverage reads.
3. Optionally add `InternalStockSnapshotAdapter` for persisted price and fundamentals snapshots only.
4. Return `SystemRecord` output for symbol profiles, aliases, identifiers, listing, coverage, classification, tags, and stored snapshots.
5. Define gated `workflow_mutation` policy with an `internal_state_mutation` subtype for future symbol upsert, alias merge, tag update, coverage update, and retirement marker actions.
6. Keep mutation actions disabled by default until authorization, confirmation, and audit behavior exist.

#### Success Criteria

- `StockSymbolTool` no longer names Yahoo or DataManager as its target adapter path.
- Symbol identity fields come from the persistent symbol store.
- Live quote, history, and fundamental requests route to market-data tools, not `StockSymbolTool`.
- Write-like actions require policy admission and otherwise return a degraded or blocked state.

---

### 2B.4 Provider Policy and Normalized Output Backbone

**Objective**: Make provider-backed tools deterministic and source-attributed before adding more providers.

#### Runnable Increment

A provider-backed tool can select an adapter through policy, normalize output, and return a `ToolExecutionEnvelope`.

#### Work Items

1. Add `ProviderAdapterDescriptor` for in-system, official, licensed, public-web, wrapper/prototype, visualization, and international-fallback provider classes.
2. Add `ProviderSelectionPolicy` for provider order, fallback, licensing, freshness, market-session rules, timeout, and degraded-state mapping.
3. Add `NormalizedOutputKind` handling for `EvidenceFact`, `EvidenceSnippet`, `EvidenceDocument`, `SystemRecord`, `MutationReceipt`, `VisualizationProvenance`, `GeneratedArtifact`, and `DegradedState`.
4. Add normalization for source URL/reference, timestamp, currency, exchange, freshness, warnings, citations, and degraded-state reason.
5. Pass `ToolContextPack` into prompt assembly instead of raw provider payloads.

#### Success Criteria

- Provider choice is not visible to the model.
- Stale, missing, or license-blocked provider results produce explicit degraded states.
- Prompt assembly receives only normalized `ToolContextPack` instances.

---

### 2B.5 Concrete Market Data and Visualization Tools

**Objective**: Deliver functional stock, market, and visualization capabilities before enabling generic web fetch.

#### Runnable Increment

The agent can answer supported Vietnam stock, market, and chart queries through concrete tools using approved adapters and normalized outputs.

#### Work Items

1. Add external market-data tools separate from `StockSymbolTool`.
2. Use Vietnam-native and official sources first: `vnstock`, Vietstock, CafeF, FiinGroup/FiinTrade/FiinQuant, VSDC, HOSE, and HNX where terms and licensing allow.
3. Keep Yahoo and Alpha Vantage as international fallback or cross-market comparison sources, not primary Vietnam-market data.
4. Expand `TradingViewTool` to return `VisualizationProvenance` for advanced charts, widgets, deep links, symbol validation, ticker tape, and supported heatmap/screener views.
5. Add deterministic technical indicator calculation over approved price-history inputs.
6. Require source-attribution fields on market answers: provider, source URL/reference, timestamp, exchange, currency, freshness, and warnings.

#### Success Criteria

- `FPT`, `HOSE:FPT`, `HNX:SHS`, and `UPCOM:BSR` route to the correct symbol and market workflows.
- TradingView output is treated as visualization provenance, not canonical evidence.
- Quote, history, and fundamental outputs include source metadata and stale-data warnings where applicable.

---

### 2B.6 Reporting from `ToolContextPack`

**Objective**: Make reporting a composition layer over normalized evidence rather than a provider-scraping shortcut.

#### Runnable Increment

Symbol, market, and portfolio report routes generate reports from `ToolContextPack`, `VisualizationProvenance`, and `GeneratedArtifact` inputs.

#### Work Items

1. Define report input requirements for normalized facts, snippets, documents, system records, visualization provenance, generated artifacts, warnings, and degraded-state reasons.
2. Add report sections with source attribution and freshness labels.
3. Add degraded report behavior when one or more upstream evidence sources are unavailable.
4. Add finance-safety checks for unsourced recommendations, guaranteed-return language, and unsupported certainty.
5. Persist generated reports and artifacts only through approved report/artifact metadata paths with source lineage.

#### Success Criteria

- `ReportingTool` does not call provider adapters directly.
- Generated reports surface missing evidence and stale data instead of inventing claims.
- Report output remains useful when one provider path is degraded.

---

### 2B.7 Generic Web Evidence Pipeline

**Objective**: Add generic web fetch only after the concrete local tool system, provider policy, normalization, and reporting flow are functional.

#### Runnable Increment

Allowlisted public pages can be fetched as `read_only_evidence`, normalized, cited, and passed into `ToolContextPack` instances without raw page instructions.

#### Work Items

1. Add deny-by-default `GenericWebFetchPolicy`.
2. Configure domain allowlist, rate limits, render mode, extraction mode, parser limits, maximum content size, and freshness policy.
3. Capture ToS/licensing posture before production enablement.
4. Extract approved HTML text, tables, PDFs, news pages, disclosures, and public data pages into normalized snippets/documents.
5. Quarantine prompt-injection content in page instructions, hidden text, scripts, and malicious documents.
6. Return degraded states for blocked, stale, parser-limited, license-unclear, or source-incomplete pages.

#### Success Criteria

- An unapproved domain is blocked with a degraded-state reason.
- Approved web content becomes snippets/documents with citations, not raw HTML.
- Prompt-injection text in fetched content cannot alter tool behavior or prompt policy.

---

### 2B.8 Optional Remote MCP-Style Tool Admission

**Objective**: Admit remote or MCP-style tools only if local tools and provider adapters are insufficient.

#### Runnable Increment

A locally admitted remote descriptor can be exposed behind the same gateway policy, descriptor integrity, and execution-envelope controls.

#### Prerequisites

- Descriptor integrity and version/hash tracing.
- Local policy admission.
- Credential/scope ownership.
- Audit metadata.
- Timeout and rate-limit controls.
- Operational need that cannot be served by local adapters.

#### Success Criteria

- Remote descriptors are untrusted until locally admitted.
- Descriptor drift blocks or degrades execution.
- Remote tool results normalize into the same output kinds and `ToolContextPack` structure.

---

### 2B.9 Verification and Quality Gates

**Objective**: Make Phase 2B quality measurable before provider and tool expansion.

#### Verification Areas

- Existing-tool descriptor coverage for `StockSymbolTool`, `TradingViewTool`, and `ReportingTool`.
- Current-runtime compatibility with the LangChain/LangGraph ReAct path.
- Route-filtered tool visibility and static route preservation.
- Descriptor tampering and remote descriptor quarantine.
- `StockSymbolTool` migration from Yahoo/DataManager to `InternalSymbolStoreAdapter`.
- Tool-vs-adapter separation and provider fallback hiding.
- Provider failover, stale-data handling, source attribution, and cache freshness.
- Normalized output classification before prompt assembly.
- TradingView non-evidence handling.
- Generic web prompt-injection resistance.
- Reporting source discipline and degraded report behavior.
- Request-scoped `ToolContextPack` data retention.
- Mutation receipt integrity for future in-system symbol writes.
- Vietnamese and mixed-language route utterances for price, chart, fundamentals, disclosures, breadth, and flow.
- Finance-safety checks for unsourced recommendations, guaranteed-return language, and hype language.

#### Success Criteria

- Route-tool exposure precision and recall targets are defined before adding new model-visible tools.
- At least 95% of market-data answers include provider/source, timestamp, exchange, currency, freshness, and warnings where applicable.
- TradingView outputs are classified as `VisualizationProvenance` in 100% of tests unless a future policy explicitly admits them as evidence.
- Generic web adversarial fixtures produce zero critical prompt-injection escapes.

---

### 2B.10 Anti-Goals

- Do not create a second agent runtime for Phase 2B.
- Do not create a separate gateway service before operational need exists.
- Do not replace `ToolRegistry` in the first runnable phases.
- Do not put provider-specific parsing in `ToolGateway`.
- Do not expose provider adapters as a flat list of model-visible tools.
- Do not enable generic web fetch before concrete stock, symbol, provider, visualization, and report tools are functional.
- Do not enable symbol-store mutations without route admission, authorization, confirmation, and audit metadata.

---

## Phase 2C: Advanced Capabilities

### 2C.1 Multi-Agent Orchestration

**Objective**: Enable multiple specialized agents to collaborate on complex queries, with a supervisor agent coordinating work distribution.

#### Current State

- Single `StockAssistantAgent` handles all queries
- No agent-to-agent communication
- Complex queries processed sequentially

#### Target State

- Supervisor agent for query decomposition
- Specialized agents: Research, Technical Analysis, Portfolio
- Parallel execution for independent subtasks
- Result aggregation and synthesis

#### Work Items

1. **Design Agent Hierarchy**
   - Define supervisor agent responsibilities
   - Define specialized agent roles
   - Design inter-agent communication protocol

2. **Implement Supervisor Agent**
   - Query decomposition logic
   - Subtask routing to specialists
   - Result aggregation

3. **Implement Specialized Agents**
   - Research Agent (news, fundamentals, sentiment)
   - Technical Analysis Agent (charts, indicators, patterns)
   - Portfolio Agent (allocation, risk, performance)

4. **Implement Orchestration Layer**
   - Parallel execution where possible
   - Dependency resolution for sequential tasks
   - Timeout and error handling

5. **LangGraph Integration**
   - Model as LangGraph workflow
   - Visualize in LangSmith Studio

#### Architecture

```
                    ┌─────────────────────────┐
                    │    Supervisor Agent     │
                    │  (Query Decomposition)  │
                    └───────────┬─────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            ▼                   ▼                   ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│  Research Agent   │ │ Technical Agent   │ │ Portfolio Agent   │
│ • News            │ │ • Charts          │ │ • Allocation      │
│ • Fundamentals    │ │ • Indicators      │ │ • Performance     │
│ • Sentiment       │ │ • Patterns        │ │ • Risk            │
└───────────────────┘ └───────────────────┘ └───────────────────┘
            │                   │                   │
            └───────────────────┼───────────────────┘
                                ▼
                    ┌─────────────────────────┐
                    │   Result Aggregation    │
                    │   (Synthesis Agent)     │
                    └─────────────────────────┘
```

#### Dependencies

- LangGraph subgraph support
- Existing tool infrastructure
- Inter-agent message schemas

#### Success Criteria

- Complex queries decomposed into parallel subtasks
- 40% reduction in latency for multi-tool queries
- Agent collaboration visible in LangSmith traces
- Graceful degradation if specialist unavailable

---

### 2C.2 Technical Refinements

**Objective**: Improve reliability, performance, observability, and testing across the agent infrastructure.

#### 2C.2.a Streaming Retry Logic

**Current State**: No retry on streaming failures

**Work Items**:
- Implement exponential backoff for streaming
- Add circuit breaker for repeated failures
- Graceful reconnection with partial response recovery

#### 2C.2.b Singleton Pattern Standardization

**Current State**: `ToolRegistry` uses singleton, others inconsistent

**Work Items**:
- Audit all service classes for singleton needs
- Standardize singleton implementation pattern
- Document singleton usage guidelines

#### 2C.2.c Performance Optimization

**Current State**: No systematic performance monitoring

**Work Items**:
- Add latency tracking per component
- Implement connection pooling for external APIs
- Profile and optimize hot paths
- Add caching effectiveness metrics

#### 2C.2.d Observability Improvements

**Current State**: LangSmith tracing enabled

**Work Items**:
- Add custom metrics to traces (cache hits, token usage)
- Implement structured logging with correlation IDs
- Create monitoring dashboards
- Add alerting for error rate thresholds

#### 2C.2.e Testing Improvements

**Current State**: Unit tests exist, integration coverage partial

**Work Items**:
- Add integration tests for tool chains
- Implement LangSmith evaluation datasets
- Add performance benchmarks
- Create chaos testing for failover scenarios

#### Implementation Patterns

```python
# Streaming Retry
async def stream_with_retry(self, query: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            async for chunk in self._stream(query):
                yield chunk
            return
        except StreamingError as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff

# Observability
from langsmith import trace

@trace(name="process_query", tags=["agent"])
def process_query(self, query: str, conversation_id: str) -> AgentResponse:
    with trace.span("route_query"):
        route = self.router.route(query)
    with trace.span("invoke_agent"):
        result = self.agent_executor.invoke(...)
    return result
```

#### Success Criteria

- Streaming retry handles transient failures
- Singleton pattern documented and consistent
- P95 latency tracked and <3s for simple queries
- Full request traceability via correlation IDs
- 80% code coverage with integration tests

---

## Cross-Cutting Concerns

### Migration Path

All Phase 2 work should maintain backward compatibility:

1. **Deprecation Period**: Old patterns supported for 2 sprints after new patterns released
2. **Feature Flags**: New capabilities behind configuration flags
3. **Gradual Rollout**: Canary deployments for agent changes

### Configuration Updates

New configuration sections for Phase 2:

```yaml
# config.yaml additions

langchain:
  memory:
    enabled: true
    checkpointer: mongodb  # or "memory" for testing
    max_messages: 50
    summarization_threshold: 30

  tools:
    stock_symbol:
      target_adapter: internal_symbol_store
      mutations_enabled: false
    tool_gateway:
      enabled: false
      mode: in_process
      route_filtered_surface: true
      generic_web_fetch_enabled: false
    providers:
      vietnam_priority:
        - official_exchange_depository
        - licensed_commercial
        - vietnam_native_public_web
        - wrapper_prototype
      international_fallback:
        - yahoo_finance
        - alpha_vantage
    tradingview:
      cache_ttl: 300
      authority: visualization_provenance
    reporting:
      pdf_enabled: true
      template_dir: src/prompts/reports
      source_mode: tool_context_pack

  multi_agent:
    enabled: false
    supervisor_model: gpt-4
    specialist_model: gpt-3.5-turbo

prompts:
    registry:
        directory: "src/prompts"
        refresh_window_seconds: 300
    selection_mode: "fixed"  # fixed | weighted | forced | shadow
    default_locale: "en"
    system:
        active_role: "react_analyst"
        active_version: "1.0.0"
        variants:
            - name: "baseline"
              version: "1.0.0"
              file: "system/react_analyst.md"
              status: "active"
    route_contexts:
        enabled: true
        directory: "skills/routes"
        supported_routes:
            - PRICE_CHECK
            - NEWS_ANALYSIS
            - PORTFOLIO
            - TECHNICAL_ANALYSIS
            - FUNDAMENTALS
            - IDEAS
            - MARKET_WATCH
            - GENERAL_CHAT
    experiments:
        enabled: false
        active_id: ""
        allow_live_weighted_selection: false

langsmith:
    prompt_tracking:
        enabled: true
        metadata_keys:
            - prompt_version
            - prompt_variant
            - prompt_experiment_id
            - prompt_selection_mode
```

### Documentation Updates

- Update `LANGCHAIN_AGENT_HOWTO.md` with Phase 2 patterns
- Create operation runbooks for new features
- Update API documentation for structured outputs

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.6 | 2026-06-18 | System | Replaced generic Phase 2B plan with enhanced tool-system roadmap covering AgentTool descriptors, ToolGateway, ToolSurfaceBuilder, internal symbol-store evolution, provider policy, normalized outputs, TradingView visualization provenance, reporting from ToolContextPack, generic web evidence, and verification gates. |
| 1.5 | 2026-06-04 | System | Existing roadmap baseline before Phase 2B tool-system propagation. |

---

## Related Documents

- [LANGCHAIN_AGENT_HOWTO.md](./LANGCHAIN_AGENT_HOWTO.md) - Comprehensive development guide
- [TOOLS_RESEARCH_AND_PROPOSAL.md](./TOOLS_RESEARCH_AND_PROPOSAL.md) - Tool-system research and proposal for Phase 2B propagation
- [PHASE2_ROADMAP.md](./PHASE2_ROADMAP.md) - Original Phase 2 outline
- [SKILL.md](../../../.github/skills/langchain-agent-development/SKILL.md) - Development skill reference
- [Architecture Instructions](../../../.github/instructions/architecture.instructions.md) - System design conventions

---

## Appendix: Implementation Priority Matrix

| Item | Impact | Effort | Priority |
|------|--------|--------|----------|
| 2A.1 Conversation Memory Foundation | High | Medium | P0 |
| 2A.2 Prompt Refinement | Medium | Low | P1 |
| 2A.3 Structured Outputs | High | Low | P0 |
| 2B.1 AgentTool Baseline and Descriptor Inventory | High | Low | P1 |
| 2B.2 Route-Filtered Tool Surface and Thin Gateway | High | Medium | P1 |
| 2B.3 Evolved StockSymbolTool over Internal Symbol Store | High | Medium | P1 |
| 2B.4 Provider Policy and Normalized Output Backbone | High | Medium | P1 |
| 2B.5 Concrete Market Data and Visualization Tools | High | High | P1 |
| 2B.6 Reporting from ToolContextPack | Medium | Medium | P2 |
| 2B.7 Generic Web Evidence Pipeline | Medium | High | P2 |
| 2B.8 Optional Remote MCP-Style Tool Admission | Low | High | P3 |
| 2C.1 Multi-Agent | High | High | P2 |
| 2C.2 Technical Refinements | Medium | Medium | P1 |

---

*This roadmap is a living document and will be updated as implementation progresses.*
