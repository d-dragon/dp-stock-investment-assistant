# Tools Architecture Benchmark Review

> **Status**: Active benchmark review; refreshed after tool data architecture update
> **Review Mode**: Design artifacts only; implementation excluded
> **Benchmark Basis**: Official vendor and framework documentation only
> **Companion Documents**: [TOOLS_RESEARCH_AND_PROPOSAL.md](./TOOLS_RESEARCH_AND_PROPOSAL.md), [ARCHITECTURE_DESIGN.md](./ARCHITECTURE_DESIGN.md), [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md), [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md)

## Document Control

| Field | Value |
|-------|-------|
| Project | DP Stock Investment Assistant |
| Domain | Agent |
| Focus | External benchmark review of the proposed tool architecture and technical design against current official guidance from OpenAI, Anthropic, Google Gemini, LangChain, LangGraph, and LangSmith |
| Date | 2026-06-15 |
| Status | Active design benchmark; refreshed after tool data architecture update; implementation not reviewed |
| Audience | Engineering, architecture, maintainers, reviewers, tool-system owners, and requirement custodians |
| Review Scope | Tool Gateway, AgentTool, ToolSurfaceBuilder, ProviderSelectionPolicy, provider adapters, ToolContextPack, tool data architecture, storage-tier integrity, generic web evidence, TradingView visualization provenance, observability, evaluation, and rollout sequencing |
| Explicit Exclusion | No runtime code, provider API, production credential, or licensing implementation review is performed in this document |

---

## Table of Contents

1. [Review Scope and Method](#1-review-scope-and-method)
2. [Executive Summary](#2-executive-summary)
3. [Key Findings](#3-key-findings)
4. [External Benchmark Synthesis](#4-external-benchmark-synthesis)
5. [Benchmark Matrix](#5-benchmark-matrix)
6. [Strengths of the Proposed Design](#6-strengths-of-the-proposed-design)
7. [Design Gaps and Risks](#7-design-gaps-and-risks)
8. [Recommended Documentation Follow-Ups](#8-recommended-documentation-follow-ups)
9. [Overall Evaluation](#9-overall-evaluation)
10. [Reference Index](#10-reference-index)

---

## 1. Review Scope and Method

### 1.1 Reviewed Project Artifacts

This review is based on the current tool-system proposal and stable agent design context in:

- [TOOLS_RESEARCH_AND_PROPOSAL.md](./TOOLS_RESEARCH_AND_PROPOSAL.md), especially the target tool architecture, technical design proposal, tool data architecture and integrity design, provider strategy, target contracts, implementation roadmap, and verification strategy.
- [ARCHITECTURE_DESIGN.md](./ARCHITECTURE_DESIGN.md), especially the layered architecture boundary and tool/data access principles.
- [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md), especially the current tool system, routing, reporting, and integration direction.
- [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md), as the eventual normative target for requirements and acceptance criteria.

### 1.2 Benchmark Sources

This review compares the proposed tool architecture against current official guidance from:

- OpenAI on function calling, tools, agent guardrails, human review, orchestration, and agent evaluation.
- Anthropic on tool use and building effective agents.
- Google Gemini on function calling and agent security posture.
- LangChain on tools, middleware, and guardrails.
- LangGraph on runtime, persistence, fault tolerance, and human-in-the-loop execution.
- LangSmith on tracing, metadata, threads, observability, and evaluation.

### 1.3 Review Question

The core review question is:

> Does the proposed tool architecture reflect modern agentic-AI practice for a finance-oriented stock assistant, and what refinements are still needed before the design is promoted into architecture, technical design, SRS, ADRs, or implementation plans?

### 1.4 Review Standard

The review uses the following benchmark expectations:

- start with the simplest effective in-process architecture;
- keep model-visible tool surfaces compact, typed, and route-filtered;
- separate tool capability, execution policy, provider selection, provider adapters, normalization, prompt assembly, persistence, cache, and artifact retention;
- validate tool arguments and outputs with strict schemas before model use;
- treat external content as untrusted data, not instructions;
- require human approval or equivalent policy gates for mutation and external side effects;
- keep provider credentials least-privilege and scoped;
- keep request-scoped tool context separate from durable memory and persistent market data;
- preserve source lineage for retained reports, artifacts, mutation receipts, and audit metadata;
- trace route, tool exposure, selected tool, provider, descriptor versions, freshness, warnings, and degraded states;
- convert design claims into repeatable eval datasets before rollout expansion.

---

## 2. Executive Summary

The proposed tool architecture is directionally strong and broadly aligned with current official guidance. Its strongest positions are the thin in-process Tool Gateway, route-filtered model-visible tool surface, separation between agent-facing tools and provider adapters, normalized output authority model, request-scoped tool data design, deny-by-default generic web fetching, and TradingView classification as visualization provenance rather than canonical financial evidence.

The design is also well aligned with the existing project architecture. It preserves the current LangChain/LangGraph runtime direction, keeps `ToolRegistry` as inventory, evolves the cache-aware base abstraction into `AgentTool`, and avoids adding a separate gateway service before there is operational need.

The main remaining work is not a redesign. It is precision work before implementation:

- make `ToolContextPack`, `NormalizedOutput`, source metadata, artifact metadata, and mutation receipt contracts exact schemas, not only logical target models;
- define `workflow_mutation` approval, authorization, and audit rules before enabling symbol-store writes;
- promote the proposal vocabulary into architecture, technical design, SRS, and ADRs consistently;
- convert quality gates into executable route, provider, prompt-injection, stale-data, source-lineage, cache-freshness, data-retention, and trace-completeness evals;
- keep generic web fetch deferred until concrete market-data, provider, visualization, and reporting tools are functional.

Overall assessment:

- **Strategic alignment**: High
- **Architecture compatibility**: High
- **Finance-grade evidence and data-integrity discipline**: High at proposal level; needs executable schemas and evals
- **Implementation readiness**: Medium; ready for scoped design promotion, not yet ready for broad implementation without contract detail
- **Risk posture**: Acceptable if mutation and generic web fetch remain gated

---

## 3. Key Findings

| Status / Severity | Finding | Why It Matters | Recommended Action |
|-------------------|---------|----------------|--------------------|
| Positive | Thin in-process Tool Gateway aligns with simplicity-first agent guidance. | It preserves current runtime compatibility and avoids unnecessary service boundaries. | Keep the gateway as a facade or middleware boundary around existing registry-backed tools. |
| Positive | `ToolSurfaceBuilder` correctly separates pre-model tool exposure from execution-time admission. | This reduces tool overload and makes route-tool visibility testable. | Promote route-filtered exposure into architecture and SRS acceptance criteria. |
| Positive | Tool-vs-adapter separation is a strong design correction. | It prevents the model-visible tool list from becoming a provider list and keeps licensing/fallback logic deterministic. | Keep provider selection below tools through `ProviderSelectionPolicy`. |
| Positive | `TradingViewTool` as `VisualizationProvenance` matches evidence-authority discipline. | It prevents chart/widget payloads from being treated as canonical market facts. | Keep TradingView numeric values out of factual answers unless a future policy explicitly admits them. |
| Positive | The new tool data architecture closes the prior persistence-boundary weakness at proposal level. | It distinguishes request-scoped tool context, cache, durable domain records, URI-backed artifacts, descriptors/config, and external providers. | Promote the storage-tier map and integrity rules into architecture, technical design, and SRS. |
| Positive | Source-lineage and artifact metadata are now explicit. | Retained reports, artifacts, and mutation receipts can preserve evidence provenance without persisting entire prompt-context packs. | Keep artifact storage URI-based until a delivery spec chooses the backend. |
| Medium | `ToolContextPack` and related data models are now well framed, but still need exact schemas. | Without executable contracts, prompt assembly and retention policy can drift back toward ad hoc provider payloads. | Define strict schemas for `ToolContextPack`, `NormalizedOutput`, source metadata, artifact metadata, and `MutationReceipt`. |
| Medium | `workflow_mutation` needs concrete approval and audit semantics. | Symbol-store writes are lower risk than brokerage actions, but they still alter persistent system state. | Treat `internal_state_mutation` as a subtype of `workflow_mutation`; require route admission, authorization, confirmation policy, mutation receipt, and audit metadata. |
| Medium | Generic web fetch is correctly deferred, but the allowlist and adversarial tests are still future work. | Public web content is a prompt-injection and licensing risk. | Define domain allowlists, parser limits, ToS posture, stale-data behavior, and malicious-content eval fixtures before enablement. |
| Medium | Observability and evaluation targets are good, but need executable datasets and trace field definitions. | Quality gates are not enforceable until they are measurable. | Convert benchmark tables into route fixtures, provider fixtures, prompt-injection fixtures, stale-data fixtures, source-lineage checks, retention checks, and trace-completeness checks. |
| Medium | Proposal vocabulary is ahead of some stable architecture and technical-design terminology. | Terms such as `AgentTool`, `ToolContextPack`, and `ProviderSelectionPolicy` need consistent authority across documents. | Promote these terms through controlled architecture, technical design, SRS, and ADR updates before implementation. |

No active High-severity design issue was found after the current refinements, provided higher-risk features remain gated.

---

## 4. External Benchmark Synthesis

### 4.1 OpenAI: Strict Schemas, Guardrails, Approvals, and Evals

OpenAI's function-calling and tools guidance reinforces that the model can select a tool call, but application code owns execution and validation. Its agent guardrail and human-review guidance also separates input, output, and tool guardrails from human approval for higher-risk tool calls. OpenAI's evaluation guidance starts from traces and then promotes repeated behavior into datasets and eval runs.

Fit to proposal:

- `ToolSurfaceBuilder` and `ToolGateway` align with application-owned exposure and execution.
- `ToolCapabilityDescriptor`, `ToolPolicyDescriptor`, and `ToolExecutionEnvelope` align with typed tool schemas and validation.
- `workflow_mutation` requires a concrete approval path before it should execute.
- Trace metadata and quality gates should become implementation requirements, not just design notes.

### 4.2 Anthropic: Simple, Composable Agent Patterns

Anthropic's agent engineering guidance emphasizes that successful agent systems often use simple, composable patterns and that frameworks can obscure prompts, responses, and tool behavior if used prematurely or too broadly. Anthropic's tool-use guidance also reinforces client-side execution, strict tool definitions, and awareness of token overhead from tool definitions and results.

Fit to proposal:

- The thin gateway and in-process implementation path match the simplicity-first recommendation.
- Route-filtered tool exposure reduces tool-definition token overhead and tool-selection confusion.
- Deferring remote/MCP-style tools until descriptor integrity and operational controls are mature is aligned.

### 4.3 Google Gemini: Function Calling, Trusted Tools, and Network Boundaries

Google Gemini's function-calling guidance frames tools as model-invoked interfaces to external systems, while its agent documentation highlights managed-agent security concerns: trusted tools, least-privilege credentials, network allowlists, and human review or verification for sensitive workflows.

Fit to proposal:

- Deny-by-default generic web fetch and explicit allowlists align with network-boundary guidance.
- Credential/scope owner metadata in provider descriptors aligns with least-privilege guidance.
- Symbol-store mutation should be treated as a sensitive data-modifying workflow even though it is internal.

### 4.4 LangChain: Tool Schemas, Middleware, Dynamic Tool Surfaces, and State Updates

LangChain treats tools as callable functions with well-defined inputs and outputs. Tool names, descriptions, schemas, and runtime context influence tool choice. LangChain middleware is the right shape for logging, tool selection, retries, fallbacks, rate limits, guardrails, PII checks, and error handling without creating a separate runtime. LangChain's state-update patterns also distinguish ordinary tool return values from explicit state updates.

Fit to proposal:

- `ToolSurfaceBuilder` maps to dynamic or route-aware tool selection before model invocation.
- In-process `ToolGateway` maps cleanly to middleware-like pre/post execution behavior.
- `ToolContextPack` should distinguish normal evidence returns from mutation receipts and state-related outputs.
- Direct provider-specific tools should not be exposed to the model unless they are true user-facing capabilities.

### 4.5 LangGraph: Durable Runtime, Persistence Separation, Fault Tolerance, and HITL

LangGraph provides a low-level runtime for stateful agents, durable execution, streaming, persistence, human-in-the-loop interruption, and fault tolerance. Its persistence model distinguishes thread checkpoints from long-term stores, and its fault-tolerance guidance supports retries, timeouts, error handling, and interrupts.

Fit to proposal:

- The proposal correctly preserves the current LangChain/LangGraph direction rather than introducing a second runtime.
- Timeouts, degraded states, retries, and provider failover should map to tool/gateway policies.
- Market facts should remain request-scoped or source-attributed artifacts, not unsourced durable memory.
- `workflow_mutation` is the likely boundary where interrupt/approval semantics should be considered.

### 4.6 Data Architecture: Request Context, Cache, Persistence, and Artifact Lineage

The updated proposal now maps tool data into separate tiers: request-scoped `ToolContextPack`, Redis/in-memory cache, MongoDB persistent domain records, URI-backed artifact metadata, reviewed code/config descriptors, and external provider data. This aligns with LangGraph's checkpointer-versus-store split: thread state and durable application data should not collapse into one authority boundary. It also aligns with OpenAI and LangSmith evaluation guidance because retained trace metadata should explain what tools ran, what provider data was used, what was cached, what was stale, and what was persisted.

Fit to proposal:

- Request-scoped `ToolContextPack` correctly avoids becoming long-term memory.
- Cache is framed as a performance layer, not a source of truth.
- Durable records are limited to existing domain records, reports, artifacts, mutation receipts, audit metadata, and selected source lineage.
- URI-backed artifact metadata avoids committing to a storage backend before implementation need.
- The remaining benchmark gap is executable schema precision for data contracts and retention rules.

### 4.7 LangSmith: Trace Metadata, Threads, Observability, and Evaluation

LangSmith guidance centers on traces, spans, metadata, tags, thread/session grouping, datasets, and repeatable evaluation. This is directly relevant for a finance assistant where data freshness, provider selection, and source attribution must be explainable after the fact.

Fit to proposal:

- Trace completeness benchmarks are appropriate and should be promoted into requirements.
- Tool runs should record route, exposed tools, selected tool, provider, descriptor versions, cache status, freshness, retention class, warnings, degraded-state reason, and latency.
- Evaluation datasets should cover route behavior, tool-result correctness, source lineage, cache freshness, retention discipline, and trace completeness.

---

## 5. Benchmark Matrix

| Benchmark Dimension | External Guidance Signal | Proposal Status | Assessment | Follow-Up |
|---------------------|--------------------------|-----------------|------------|-----------|
| Simplicity-first architecture | Anthropic and LangGraph favor simple composable patterns before complex orchestration | Thin in-process Tool Gateway around existing registry | Strong | Preserve anti-goal against separate gateway service until operational need exists |
| Model-visible tool surface | LangChain and Anthropic caution against overly broad tool surfaces | `ToolSurfaceBuilder` route-filters tools before ReAct invocation | Strong | Add executable route-to-tool exposure fixtures |
| Strict schemas and validation | OpenAI, Anthropic, Gemini, and LangChain emphasize structured tool inputs/outputs | Descriptor and envelope model proposed | Medium-strong | Define exact Pydantic/JSON-schema contracts and strict output validation |
| Tool execution ownership | All benchmark sources keep execution in application/client code | Gateway executes through registry-backed `AgentTool` path | Strong | Keep provider logic outside gateway |
| Tool-vs-adapter separation | Provider-specific behavior should stay below user-facing capabilities | Model-visible tools are coarse; adapters are internal | Strong | Prevent provider names from leaking into model-visible descriptors except as evidence metadata |
| Mutation approval | OpenAI, Gemini, LangChain, and LangGraph favor approvals/HITL for sensitive actions | `workflow_mutation` subtype model is proposed | Medium | Define confirmation, authorization, audit, and mutation receipt requirements before enabling writes |
| Generic web trust model | OWASP-style indirect injection controls are consistent with OpenAI/LangChain guardrails | Deny-by-default web fetch with allowlist and quarantine | Strong direction | Add allowlist registry, parser limits, ToS review workflow, and adversarial evals |
| Prompt authority and raw content | Tool and web outputs should be data, not higher-priority instructions | Normalized outputs and `ToolContextPack` proposed | Medium-strong | Define serialization limits and prompt-assembly acceptance rules |
| Visualization provenance | External visual widgets are not automatically factual evidence | TradingView is visualization-only by default | Strong | Keep 100% classification check in verification suite |
| Persistence boundary | LangGraph separates checkpoints and stores; project layered architecture keeps market facts out of memory | Request-scoped `ToolContextPack`, explicit cache tier, durable domain records, and URI-backed artifact metadata proposed | Strong | Promote retention rules into technical design and SRS |
| Cache and freshness integrity | Fault tolerance and finance accuracy require freshness-aware provider results, not TTL-only caching | Cache payloads must carry source timestamp, retrieved timestamp, provider, freshness category, and warnings | Strong direction | Define cache payload schema and stale-cache tests |
| Source lineage and artifacts | LangSmith/OpenAI trace guidance supports explainable retained outputs | Reports, artifacts, and mutation receipts retain lineage to normalized outputs and provider/source metadata | Strong direction | Define artifact metadata schema and lineage verification fixtures |
| Observability | OpenAI and LangSmith start with traces and promote to datasets/evals | Trace metadata, retention class, and quality gates proposed | Medium-strong | Bind trace fields to implementation and eval datasets |
| Finance-grade accuracy | Finance answers need citations, freshness, uncertainty, degraded states, and durable lineage for retained artifacts | Benchmarks added for attribution, stale data, route behavior, source lineage, retention discipline, and safety | Medium-strong | Convert benchmark targets into acceptance criteria and automated evals |

---

## 6. Strengths of the Proposed Design

1. **Architecture compatibility**: The design evolves the existing registry/tool runtime rather than replacing it.
2. **Policy boundary clarity**: The gateway owns exposure, admission, validation, degraded states, and trace metadata without owning provider parsing.
3. **Tool surface discipline**: Route-filtered tool exposure keeps model choice compact and reviewable.
4. **Provider neutrality**: Provider choice lives below agent-facing tools and is governed by policy.
5. **Vietnam-market fit**: Native, official, licensed, public-web, wrapper, visualization, and fallback provider classes are distinguished.
6. **Evidence authority**: `NormalizedOutputKind` and `ToolContextPack` prevent facts, snippets, records, mutations, visuals, and generated artifacts from being treated as equivalent.
7. **Data-tier discipline**: Request-scoped context, cache, durable domain records, artifact metadata, descriptors/config, and external providers now have separate authority boundaries.
8. **Lineage discipline**: Retained reports, artifacts, and mutation receipts preserve source lineage instead of requiring wholesale context-pack persistence.
9. **Web safety posture**: Generic web fetch is correctly scoped as deny-by-default `read_only_evidence`.
10. **Roadmap discipline**: Generic web fetch and remote/MCP-style tools are deferred until concrete local tools and policies are functional.

---

## 7. Design Gaps and Risks

### 7.1 Data Contracts Still Need Executable Schemas

The logical data architecture is now strong, but implementation promotion needs exact schemas. The schema set should define required fields, optional fields, allowed output kinds, citation model, source metadata, artifact metadata, freshness model, degraded-state model, warning model, retention class, trace references, and serialization limits for prompt assembly.

### 7.2 Mutation Policy Needs an Approval Model

Internal symbol-store writes are not external financial transactions, but they still mutate persistent system state. They should remain disabled until `workflow_mutation` includes authorization, route admission, confirmation policy, audit metadata, mutation receipts, rollback or correction behavior, and traceability.

### 7.3 Generic Web Fetch Needs Concrete Trust Controls

The design correctly defers generic web fetch, but the future implementation must be precise: domain allowlist, render mode, parser limits, max content size, ToS/licensing posture, citation extraction, prompt-injection quarantine, and malicious fixture tests.

### 7.4 Documentation Vocabulary Needs Promotion

The proposal now uses `AgentTool`, `ToolContextPack`, `ProviderSelectionPolicy`, and `workflow_mutation` subtype language. These terms should be promoted into architecture, technical design, SRS, and ADRs together to avoid mixed old/new terminology.

### 7.5 Evaluation Is Defined as Targets, Not Yet Datasets

The quality gates are meaningful, but not executable until there are curated datasets and trace checks. Without executable evals, source attribution and route-tool discipline can regress silently.

### 7.6 Retention and Artifact Storage Need Promotion Rules

The proposal correctly keeps `ToolContextPack` request-scoped and uses URI-backed artifact metadata, but formal documents still need promotion rules for what can be retained, who owns artifact storage, how retention class is selected, and how source lineage is verified.

---

## 8. Recommended Documentation Follow-Ups

| Priority | Follow-Up | Target Artifact |
|----------|-----------|-----------------|
| P1 | Promote the refined tool boundary into architecture: `Agent Runtime -> ToolSurfaceBuilder -> ToolGateway -> ToolRegistry/AgentTool -> ProviderSelectionPolicy -> ProviderAdapter -> EvidenceNormalizer -> ToolContextPack -> PromptAssembler`. | `ARCHITECTURE_DESIGN.md` |
| P1 | Promote the new tool data architecture: request-scoped `ToolContextPack`, cache tier, MongoDB domain records, URI-backed artifact metadata, reviewed descriptors/config, and external provider authority. | `ARCHITECTURE_DESIGN.md` |
| P1 | Define exact technical contracts for `AgentTool`, descriptors, `ToolExecutionEnvelope`, `NormalizedOutputKind`, `ToolContextPack`, provider/source metadata, artifact metadata, `MutationReceipt`, and `GenericWebFetchPolicy`. | `TECHNICAL_DESIGN.md` |
| P1 | Add SRS requirements and acceptance criteria for route-filtered tool exposure, descriptor integrity, source attribution, request-scoped tool context, data retention, cache freshness, artifact lineage, degraded states, TradingView provenance, and mutation gating. | `SOFTWARE_REQUIREMENTS_SPECIFICATION.md` |
| P1 | Create an ADR for the thin in-process Tool Gateway and another for the generic web evidence trust model when the design is promoted. | ADR set |
| P1 | Define `workflow_mutation` with `internal_state_mutation` as a subtype and require authorization, confirmation, mutation receipt, audit metadata, and trace capture before enabling writes. | SRS, technical design, ADR set |
| P2 | Convert quality benchmarks into executable route, provider, stale-data, prompt-injection, mutation, report, and trace-completeness datasets. | Evaluation assets and SRS acceptance criteria |
| P2 | Create a source-verification registry for official, licensed, public-web, wrapper, visualization, international fallback, and in-system sources. | Technical design and provider onboarding specs |
| P2 | Create data-integrity fixtures for no-wholesale `ToolContextPack` persistence, cache freshness metadata, artifact URI metadata, source lineage, and symbol + exchange + currency identity. | Evaluation assets and delivery specs |
| P2 | Add a migration note for removing Yahoo/DataManager ownership from `StockSymbolTool` and moving live data to dedicated market-data tools. | Technical design and roadmap |
| P2 | Define generic web allowlist governance and parser safety limits before enabling `GenericWebFetchTool`. | Technical design and delivery specs |

---

## 9. Overall Evaluation

The proposed tools architecture is suitable for promotion into formal architecture and requirements after the P1 documentation follow-ups are completed. It should not be implemented as a broad platform rewrite. The correct implementation posture is a narrow, runnable evolution:

1. Add descriptors and `AgentTool` naming around existing tools.
2. Add `ToolSurfaceBuilder` and a thin in-process `ToolGateway`.
3. Evolve `StockSymbolTool` onto the internal symbol store and remove Yahoo/DataManager ownership from that tool.
4. Add provider selection, normalized output contracts, and the data-integrity backbone.
5. Keep `ToolContextPack` request-scoped while retaining only approved reports, artifact metadata, mutation receipts, audit metadata, trace metadata, and domain records.
6. Deliver concrete market-data, visualization, and reporting tools.
7. Enable generic web fetch only after source, parser, retention, and adversarial controls exist.

The proposal is compatible with official guidance from OpenAI, Anthropic, Google Gemini, LangChain, LangGraph, and LangSmith because it keeps tool execution application-owned, narrows model-visible capabilities, separates providers from tools, validates and normalizes outputs before prompt assembly, treats web content as untrusted data, separates request context from durable memory, and makes observability/evaluation first-class.

The design should be accepted as a target design direction with two guardrails: mutation and generic web fetch must remain disabled until their approval, trust, retention, and evaluation controls are explicitly specified; and retained artifacts or reports must preserve source lineage without persisting wholesale prompt context.

---

## 10. Reference Index

### 10.1 OpenAI

- [OpenAI Function Calling](https://developers.openai.com/api/docs/guides/function-calling)
- [OpenAI Tools Guide](https://developers.openai.com/api/docs/guides/tools)
- [OpenAI Guardrails and Human Review](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals)
- [OpenAI Agent Orchestration](https://developers.openai.com/api/docs/guides/agents/orchestration)
- [OpenAI Agent Evals](https://developers.openai.com/api/docs/guides/agent-evals)
- [OpenAI Conversation State](https://developers.openai.com/api/docs/guides/conversation-state)
- [OpenAI Building Agents Track](https://developers.openai.com/tracks/building-agents)

### 10.2 Anthropic

- [Anthropic Tool Use Overview](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Anthropic Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Anthropic Prompt Engineering Overview](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)

### 10.3 Google Gemini

- [Google Gemini Agents](https://ai.google.dev/gemini-api/docs/agents)
- [Google Gemini Function Calling](https://ai.google.dev/gemini-api/docs/function-calling)
- [Google Gemini Grounding with Google Search](https://ai.google.dev/gemini-api/docs/google-search)
- [Google Gemini Code Execution](https://ai.google.dev/gemini-api/docs/code-execution)

### 10.4 LangChain, LangGraph, and LangSmith

- [LangChain Tools](https://docs.langchain.com/oss/python/langchain/tools)
- [LangChain Middleware](https://docs.langchain.com/oss/python/langchain/middleware)
- [LangChain Guardrails](https://docs.langchain.com/oss/python/langchain/guardrails)
- [LangChain Agents](https://docs.langchain.com/oss/python/langchain/agents)
- [LangGraph Overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangGraph Fault Tolerance](https://docs.langchain.com/oss/python/langgraph/fault-tolerance)
- [LangSmith Observability Concepts](https://docs.langchain.com/langsmith/observability-concepts)
- [LangSmith Metadata and Tags](https://docs.langchain.com/langsmith/add-metadata-tags)
- [LangSmith Threads](https://docs.langchain.com/langsmith/threads)
- [LangSmith Evaluation Concepts](https://docs.langchain.com/langsmith/evaluation-concepts)

### 10.5 Security and Trust

- [OWASP LLM01 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)

---

*End of Tools Architecture Benchmark Review*
