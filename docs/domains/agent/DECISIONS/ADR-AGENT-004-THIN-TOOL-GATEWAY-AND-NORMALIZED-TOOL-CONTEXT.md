# Architecture Decision Record

## Document Control

| Field | Value |
|-------|-------|
| **ADR ID** | ADR-004 |
| **Domain** | Agent |
| **Standards Stance** | Practice-Based ADR discipline |
| **Status** | Proposed |
| **Date** | 2026-06-22 |
| **Last Updated** | 2026-06-22 |
| **Context** | DP-StockAI-Assistant |
| **Decision Owners** | Engineering · Architecture · Agent maintainers |

## ADR-004 — Adopt a Thin Tool Gateway and Normalized Tool Context Boundary

## 1. Decision Summary

Adopt a thin in-process `ToolGateway` and normalized request-scoped `ToolContextPack` boundary for Phase 2B tool-system evolution.

The target tool architecture is composed of:

- current `ToolRegistry` inventory and cache-aware tool execution;
- target `AgentTool` naming for descriptor-backed agent-callable tools;
- `ToolSurfaceBuilder` for route-filtered model-visible tool exposure;
- thin `ToolGateway` for exposure policy, execution admission, result validation, degraded-state handling, and trace metadata;
- provider adapters and `ProviderSelectionPolicy` below model-visible tools;
- normalized output kinds before prompt assembly;
- request-scoped `ToolContextPack` as the only tool-derived context passed toward prompt assembly.

## 2. Stakeholders Affected

- Product
- End Users
- AI Engineers / Agent Maintainers
- Backend Engineers
- QA / Test Maintainers
- Security & Compliance
- Architecture Owners

## 3. Architecture Concerns Addressed

- Current runtime compatibility with the LangChain/LangGraph ReAct path
- Route-filtered tool exposure before model invocation
- Tool-vs-adapter separation
- Source attribution, freshness, and provider licensing posture
- Vietnam-first market-data integration
- TradingView authority boundaries
- Generic web prompt-injection and trust controls
- Descriptor integrity and remote/MCP-style tool admission
- Request-scoped tool context and durable data-retention boundaries

## 4. Problem Statement

The current tool system exposes enabled tools from `ToolRegistry` and executes cache-aware `CachingTool` implementations. That baseline is simple and useful, but it does not yet provide enough architectural control for Vietnam-first provider expansion, source attribution, route-filtered tool exposure, descriptor integrity, generic web evidence, or future state-changing tool actions.

Without a stronger boundary, the model-visible tool list can grow into a provider list, provider fallback rules can become implicit, stale or license-unclear data can be silently substituted, and raw provider or web content can drift into prompt context without consistent authority labeling.

The agent domain therefore needs a tool architecture that starts simple, preserves the current runtime, and gives future provider adapters, evidence normalization, generic web fetch, reporting, and mutation receipts a governed path.

## 5. Decision

Adopt a **thin in-process Tool Gateway** as the policy and validation boundary around existing registry-backed tool execution.

The gateway SHALL:

1. Keep `ToolRegistry` as the current inventory and enablement boundary.
2. Treat `CachingTool` as the current implementation name and `AgentTool` as the target architecture name for cache-aware, descriptor-backed tools.
3. Use `ToolSurfaceBuilder` to expose only route-eligible, enabled, policy-admitted tools before ReAct invocation.
4. Validate selected tool calls before execution, including route match, arguments, risk class, license posture, freshness expectation, provider state, timeout budget, and descriptor integrity.
5. Keep provider selection below tools through `ProviderSelectionPolicy` and provider adapters.
6. Normalize every tool result into an admitted output kind before prompt assembly.
7. Pass tool-derived context through request-scoped `ToolContextPack` instances instead of raw provider payloads.
8. Return `DegradedState` for blocked, stale, missing, license-unclear, parser-limited, provider-down, or validation-failed outcomes.
9. Treat TradingView output as `VisualizationProvenance` by default, not canonical market evidence.
10. Keep generic web fetch deny-by-default and admit allowlisted web content only as normalized evidence snippets or documents.
11. Treat future symbol-store writes as `workflow_mutation` with `internal_state_mutation` subtype, requiring authorization, confirmation, audit metadata, and `MutationReceipt` output.

The gateway SHALL NOT:

- become a second agent runtime;
- become a separate service before operational need exists;
- parse provider-specific data itself;
- own service-layer business lifecycle policy;
- own prompt policy text;
- expose provider adapters as model-visible tools;
- persist `ToolContextPack` wholesale as conversation memory or durable market truth.

## 6. Alternatives Considered

| Option | Outcome |
|--------|---------|
| Keep direct registry-only execution | Rejected for target Phase 2B because it lacks route-filtered exposure, provider-policy admission, descriptor integrity, and normalized output authority controls. |
| Create a separate gateway service immediately | Rejected for near-term delivery because it adds latency, serialization, deployment, credential, and observability complexity before the project has operational need. |
| Expose provider adapters directly as model-visible tools | Rejected because it bloats the tool surface, increases tool-selection error risk, and leaks provider policy into the model. |
| Enable generic web fetch before concrete tools | Rejected because generic web evidence has higher trust and prompt-injection risk and should follow working concrete market, symbol, visualization, and reporting tools. |
| Adopt remote or MCP-style tools first | Rejected for near-term delivery because remote descriptors must be treated as untrusted until local descriptor integrity, credential ownership, timeout, and admission policy exist. |

## 7. Consequences

Positive:

- Preserves the current LangChain/LangGraph ReAct runtime while adding a clearer policy boundary.
- Keeps the model-visible tool surface compact and route-aware.
- Separates tools from provider adapters and source-specific parsing.
- Improves source attribution, freshness, licensing, degraded-state handling, and auditability.
- Gives Vietnam-first providers, TradingView visualization, generic web evidence, reports, and mutation receipts one consistent authority model.
- Reduces the chance that raw web/provider instructions become prompt authority.

Trade-offs:

- Adds descriptor, policy, and normalization contracts that must be kept consistent.
- Adds latency if admission, cache, provider fallback, and normalization are implemented inefficiently.
- Requires careful scope control so the gateway does not become a god object.
- Requires test coverage for route filtering, descriptor tampering, stale data, generic web prompt injection, TradingView authority, reporting source discipline, and mutation receipts.

## 8. Related Documents

- [ARCHITECTURE_DESIGN.md](../ARCHITECTURE_DESIGN.md) is the canonical home for architecture views and boundary placement.
- [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../SOFTWARE_REQUIREMENTS_SPECIFICATION.md) is the requirement authority for `FR-2.4` through `FR-2.11`, `AC-9`, `IR-3`, and related constraints.
- [PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md](../PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md) is the sequencing authority for Phase 2B delivery.
- [TOOLS_RESEARCH_AND_PROPOSAL.md](../TOOLS_RESEARCH_AND_PROPOSAL.md) is non-authoritative research input.
- ADR-001 defines the layered architecture rule that tools fetch or compute while the LLM reasons and memory does not store market facts.

## 9. Affected Views / Impacted Architectural Elements

### 9.1 Views Impacted by This Decision

| View | Impact Scope | Updated / Governed Content |
|------|--------------|----------------------------|
| Context and Boundary View | Primary | Adds the target tool surface, gateway, provider adapter, and normalization boundaries around current registry-backed tools |
| Logical View | Primary | Separates tool inventory, tool exposure/admission, provider adapters, normalization, and prompt assembly responsibilities |
| Process View | Primary | Adds pre-model exposure, pre-execution admission, post-execution validation, and response-assembly checks |
| Information and State View | Primary | Defines `ToolContextPack`, normalized output kinds, visualization provenance, mutation receipts, generated artifacts, and degraded states as request-scoped or explicitly retained derivatives |
| Prompt and Behavior View | Secondary | Keeps tool-derived content as data-only runtime context and prevents web/provider instructions from becoming prompt policy |
| Operations and Maintenance View | Secondary | Requires trace metadata for route exposure, selected tools, provider class, cache/freshness status, warnings, degraded states, and descriptor versions |

### 9.2 Architectural Elements Newly Defined or Reframed

- **AgentTool:** Target architecture name for descriptor-backed, cache-aware agent-callable tools.
- **ToolSurfaceBuilder:** Route-filtered model-visible tool exposure boundary.
- **ToolGateway:** Thin in-process policy and validation boundary around registry-backed execution.
- **ProviderSelectionPolicy:** Internal provider ordering, fallback, licensing, freshness, and degraded-state mapping.
- **ProviderAdapter:** Source-specific fetch, health, credential/scope, and mapping boundary below tools.
- **NormalizedOutputKind:** Authority classification for tool results before prompt assembly.
- **ToolContextPack:** Request-scoped normalized tool context passed toward prompt assembly.
- **VisualizationProvenance:** Non-authoritative chart/widget/deep-link output unless future policy explicitly admits a data category.
- **MutationReceipt:** Auditable output for approved state-changing tool actions.
- **DegradedState:** Machine-detectable blocked, stale, incomplete, or unsafe tool outcome.

### 9.3 Applicability Note

This ADR is **Proposed**. Architecture and requirement documents may describe the gateway, adapters, and normalized context as target Phase 2B boundaries, but companion documents must not imply they are implemented until code, contracts, and tests prove the runtime realization.

### 9.4 Consistency Checkpoints

- [ ] `ToolRegistry` and `CachingTool` remain labeled as current implementation facts until renamed or wrapped in code.
- [ ] `AgentTool`, `ToolSurfaceBuilder`, `ToolGateway`, provider adapters, normalized output kinds, and `ToolContextPack` remain target-state unless implementation artifacts prove otherwise.
- [ ] Provider adapters are not exposed as a flat model-visible tool list.
- [ ] TradingView remains visualization provenance by default.
- [ ] Generic web fetch remains deny-by-default and data-only after normalization.
- [ ] `ToolContextPack` is not persisted wholesale as conversation memory or durable market truth.
- [ ] Symbol-store mutations require `workflow_mutation` with `internal_state_mutation` subtype, approval controls, and mutation receipts.

## 10. Traceability

Supports:

Functional requirements:

- `FR-2.4` Tool Gateway and Tool Exposure
- `FR-2.5` Tool Output Normalization and ToolContextPack
- `FR-2.6` Vietnam-Market Tool Coverage
- `FR-2.7` Provider Selection and Source Attribution
- `FR-2.8` TradingView Visualization
- `FR-2.9` Generic Web Evidence
- `FR-2.10` Reporting and Generated Artifacts
- `FR-2.11` Tool Data Integrity and Mutation Receipts

Acceptance criteria:

- `AC-9.1` through `AC-9.17`

Interface requirements and constraints:

- `IR-3` Tool System Contracts
- `CON-6` Provider licensing and terms review
- `CON-7` TradingView authority
- `CON-8` Generic web deny-by-default
- `CON-9` Source-attributed market facts
- `CON-10` No wholesale `ToolContextPack` persistence

Architecture sections:

- `4.1.1` System Context
- `4.1.1a` External and Internal Interface Diagram
- `4.2` Logical View
- `4.3` Process View
- `4.4` Information and State View
- `4.8.5` Tool Risk and Approval Envelope

> Tools fetch and compute through governed boundaries. The LLM reasons over normalized context. Memory does not store market facts.
