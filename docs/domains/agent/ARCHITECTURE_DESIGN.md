# Agent Domain — Architecture Description

> **Status**: Active working draft
> **Standards Stance**: Aligned to ISO/IEC/IEEE 42010
> **Technology Stack**: LangGraph 0.2.62+, LangChain, OpenAI SDK, semantic-router, MongoDB, Redis
> **Companion Documents**: [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md), [AGENT_MEMORY_TECHNICAL_DESIGN.md](./AGENT_MEMORY_TECHNICAL_DESIGN.md), [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](./PROMPT_SYSTEM_RESEARCH_PROPOSAL.md), [AGENT_ARCHITECTURE_DECISION_RECORDS.md](./decisions/AGENT_ARCHITECTURE_DECISION_RECORDS.md)

## Document Control

| Field | Value |
|-------|-------|
| Project | DP Stock Investment Assistant |
| Domain | Agent |
| Focus | Architecture description of the agent domain, including boundaries, views, concerns, rationale, and evolution |
| Date | 2026-04-16 |
| Status | Active |
| Audience | Engineering, architecture, maintainers, and reviewers |

## Table of Contents

1. [Architecture Description Overview](#1-architecture-description-overview)
2. [Stakeholders, Perspectives, and Concerns](#2-stakeholders-perspectives-and-concerns)
3. [Viewpoint Catalog](#3-viewpoint-catalog)
4. [Architecture Views](#4-architecture-views)
5. [Correspondences and Traceability](#5-correspondences-and-traceability)
6. [Architecture Rationale](#6-architecture-rationale)
7. [Architecture Considerations and Planned Evolution](#7-architecture-considerations-and-planned-evolution)
8. [Revision History](#8-revision-history)

---

## 1. Architecture Description Overview

### 1.1 Purpose

This document is the architecture description for the agent domain. It expresses the fundamental concepts, structures, runtime interactions, and governing rationale of the LangChain-based stock investment assistant agent.

The document follows the repository's documentation methodology, where architecture descriptions are **aligned** to ISO/IEC/IEEE 42010 rather than presented as formal certification artifacts. In this repo, that means the document should identify the entity of interest, environment, stakeholders, concerns, viewpoints, views, correspondences, and rationale while avoiding duplication of detailed implementation material that belongs in technical design, ADRs, contracts, or delivery-scoped specs.

> **Note on scope**: The project methodology defines architecture descriptions at the system level. This is a domain-level architecture description created because the agent domain carries sufficient complexity (multi-layer LLM reasoning, memory management, prompt composition, tooling, and provider fallback) to warrant its own viewpoint-governed description within the system-wide architecture.

### 1.2 Entity of Interest

The **entity of interest** is the **agent domain** of the DP Stock Investment Assistant: the LangChain and LangGraph-based reasoning and tool-orchestration subsystem that answers stock-investment queries, manages conversation-scoped short-term memory, applies prompt policies and guardrails, and coordinates model/provider fallback behavior.

### 1.3 Environment and External Dependencies

The agent domain operates within a wider application and infrastructure environment that includes:

- frontend clients that initiate chat and streaming requests;
- backend API routes and Socket.IO handlers that invoke the agent;
- MongoDB collections for metadata and LangGraph checkpoints;
- Redis-backed caching and in-memory fallback cache paths;
- external model providers such as OpenAI and Grok;
- external financial data sources such as Yahoo Finance;
- future prompt asset, evaluation, and observability flows governed by prompt-version and runtime metadata.

### 1.4 Scope and Boundaries

This architecture description covers:

- agent orchestration and tool use;
- route classification and provider/model selection;
- conversation-scoped STM wiring and lifecycle boundaries;
- prompt composition and behavioral guardrail architecture;
- primary runtime flows and domain-level evolution directions.

This architecture description does not replace:

- [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md) for implementation-oriented realization detail;
- [AGENT_MEMORY_TECHNICAL_DESIGN.md](./AGENT_MEMORY_TECHNICAL_DESIGN.md) for STM and checkpoint subsystem detail;
- [AGENT_ARCHITECTURE_DECISION_RECORDS.md](./decisions/AGENT_ARCHITECTURE_DECISION_RECORDS.md) and the individual ADRs for decision authority;
- SRS or spec artifacts for requirement authority and delivery traceability.

### 1.5 Key Characteristics

| Aspect | Description |
|--------|-------------|
| Architecture | ReAct pattern with tool orchestration |
| AI Framework | LangChain >=1.0.0 with `langchain_core` and `langchain_openai` |
| Model Providers | OpenAI (GPT-5-nano), Grok (grok-4-1-fast-reasoning) with automatic fallback |
| Tool System | Registry-based with caching support |
| Memory | LangGraph `MongoDBSaver` checkpointer for conversation-scoped STM, with sessions as reusable parent business context |
| Semantic Router | `semantic-router` library with OpenAI/HuggingFace encoders |
| Response Types | Structured (`AgentResponse`) with immutable dataclasses |

### 1.6 Document Authority Split

| Document | Primary Responsibility |
|----------|------------------------|
| [ARCHITECTURE_DESIGN.md](./ARCHITECTURE_DESIGN.md) | Viewpoint-governed architecture description for the agent domain |
| [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md) | Technical realization, component behavior, configuration, and extension details |
| [AGENT_MEMORY_TECHNICAL_DESIGN.md](./AGENT_MEMORY_TECHNICAL_DESIGN.md) | Detailed memory subsystem design, data model, sequence diagrams, and API impacts |
| [ADR-AGENT-001-LAYERED-LLM-ARCHITECTURE.md](./decisions/ADR-AGENT-001-LAYERED-LLM-ARCHITECTURE.md) | Governing layered architecture and memory boundaries |
| [ADR-AGENT-002-SKILLS-PATTERN-PROMPT-COMPOSITION.md](./decisions/ADR-AGENT-002-SKILLS-PATTERN-PROMPT-COMPOSITION.md) | Prompt skills composition decision |
| [ADR-AGENT-003-EXTERNALIZE-VERSION-PROMPT-ASSETS.md](./decisions/ADR-AGENT-003-EXTERNALIZE-VERSION-PROMPT-ASSETS.md) | Externalized prompt asset decision |

---

## 2. Stakeholders, Perspectives, and Concerns

### 2.1 Stakeholders

| Stakeholder | Perspective | Primary Concerns |
|-------------|-------------|------------------|
| Agent maintainers | Runtime and behavior perspective | Correct orchestration, extensibility, debugging cost, prompt evolution |
| Backend/API maintainers | Integration and service perspective | Stable invocation contracts, archive behavior, streaming compatibility |
| Architecture owners | System and governance perspective | ADR alignment, separation of concerns, bounded responsibilities |
| Product and domain reviewers | Product behavior perspective | Response usefulness, safety, clarity, future extensibility |
| Operations and support | Operability perspective | Observability, health, reconciliation, drift visibility |
| Security and compliance reviewers | Risk and controls perspective | Evidence-first behavior, anti-hype safeguards, memory boundaries |

### 2.2 Concerns

The architecture description is intended to address the following recurring concerns:

- how the agent domain is bounded within the larger system;
- how the static architecture is decomposed across runtime, tools, memory, prompts, and supporting services;
- how requests flow through routing, tool use, fallback, and response generation;
- how conversation-scoped STM is isolated and governed;
- how prompt behavior, guardrails, and future prompt externalization align to ADRs;
- how current design choices support extensibility without collapsing responsibilities across layers;
- how future evolution paths remain explicit without turning this architecture description into a roadmap backlog.

### 2.3 Concern Categories

This architecture description uses the following concern categories to frame concerns:

- **structural**: source layout, major components, boundaries, and dependencies;
- **behavioral**: runtime flows, routing, fallback, streaming, and prompt assembly;
- **informational/stateful**: conversation state, checkpoint relationships, and metadata ownership;
- **operational**: traceability, observability hooks, and evolution constraints.

---

## 3. Viewpoint Catalog

| Viewpoint | Stakeholders | Concerns Framed | Conventions / Model Kinds |
|-----------|--------------|-----------------|----------------------------|
| Context and Boundary Viewpoint | Architects, backend maintainers, product reviewers | Domain boundary, environment, dependencies, scope | Narrative scope statements, dependency summary tables |
| Static Structure Viewpoint | Architects, maintainers | Major components, responsibilities, patterns, source layout | Source tree, component tables, pattern/stack summaries |
| Runtime Interaction Viewpoint | Backend maintainers, agent maintainers, operators | Query flow, routing, tool execution, fallback, response generation | Interaction flows and sequence-style diagrams |
| Memory and State Viewpoint | Architects, backend maintainers, compliance reviewers | STM scope, hierarchy, lifecycle, metadata separation | State/lifecycle tables, hierarchy summaries, subsystem references |
| Prompt and Behavior Viewpoint | Agent maintainers, architecture owners, compliance reviewers | Prompt composition, guardrails, observability, prompt evolution | Layered prompt diagrams, taxonomy tables, metadata tables |
| Evolution Viewpoint | Architects, product reviewers, maintainers | Major extension paths, unresolved considerations, planned direction | Concern-oriented change tables and future-state summaries |
| Evolution Viewpoint | Architects, product reviewers, maintainers | Major extension paths and unresolved architectural considerations | Concern-oriented change tables and future-state summaries |

These viewpoints govern the views in \u00a74. Detailed code-oriented realization belongs in [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md).

---

## 4. Architecture Views

### 4.1 Context and Boundary View

The agent domain sits between the API/service layer and external data/model providers. It does not own the frontend UI, REST/Socket transport surface, or the repository-wide operational policy layer. It does own reasoning workflow, tool orchestration, route-aware behavior, provider fallback, and conversation-scoped STM binding.

The primary context relationships are:

- API routes and Socket.IO handlers pass user requests into the agent runtime;
- service-layer components govern ownership, archival checks, and metadata synchronization around conversations;
- LangGraph checkpointer infrastructure stores conversation-scoped execution state;
- tool implementations gather external or repository-backed data;
- prompt assets and prompt composition logic govern model behavior, not factual storage.

This boundary is consistent with the repository methodology's rule that architecture descriptions should explain **what structures and interactions exist**, while implementation detail and contract detail remain in companion documents.

### 4.2 Static Structure View

#### 4.2.1 Domain Building Blocks

| Building Block | Responsibility |
|----------------|----------------|
| `stock_assistant_agent.py` | Main ReAct runtime and conversation-aware agent entry points |
| `langgraph_bootstrap.py` | Agent/bootstrap utilities including checkpointer creation |
| `stock_query_router.py` | Semantic route classification |
| `model_factory.py` and provider clients | Provider/model selection and cached client construction |
| `tools/` | Tool registration, caching, and domain data access |
| `conversation_repository.py` | Conversation metadata persistence |
| `chat_service.py` and `conversation_service.py` | Orchestration, archive guards, lifecycle and metadata helpers |
| `src/prompts/` | Planned prompt asset directory for system prompts, skills, and experiments |

#### 4.2.2 Source Layout View

```text
src/core/
├── stock_assistant_agent.py    # Main ReAct agent with conversation-aware STM routing
├── langgraph_bootstrap.py      # LangGraph agent builder + MongoDBSaver checkpointer factory
├── stock_query_router.py       # Semantic router for query classification
├── routes.py                   # Route definitions and utterances
├── types.py                    # Core types: AgentResponse, ToolCall, TokenUsage
├── langchain_adapter.py        # Prompt building with external file support
├── model_factory.py            # Factory pattern for model clients
├── base_model_client.py        # Abstract base for providers
├── openai_model_client.py      # OpenAI implementation
├── grok_model_client.py        # Grok (xAI) implementation
├── data_manager.py             # Yahoo Finance data fetching
└── tools/
    ├── base.py                 # CachingTool base class
    ├── registry.py             # ToolRegistry singleton
    ├── stock_symbol.py         # Stock lookup tool
    ├── tradingview.py          # TradingView placeholder (Phase 2)
    └── reporting.py            # Report generation tool

src/utils/
└── memory_config.py            # MemoryConfig frozen dataclass with fail-fast validation

src/data/repositories/
└── conversation_repository.py  # ConversationRepository (conversations collection)

src/services/
├── chat_service.py             # Chat orchestration, archive guard, metadata sync (REST path)
└── conversation_service.py     # ConversationService (lifecycle, management APIs, metadata helpers)

src/prompts/
├── system/
├── skills/
└── experiments/
```

#### 4.2.3 Structural Patterns and Stack Summary

| Category | Architectural Role |
|----------|--------------------|
| Factory | `ModelClientFactory`, `create_checkpointer()` |
| Registry / Singleton | `ToolRegistry` |
| Strategy | Provider-specific model clients |
| Template Method / Decorator | `CachingTool` |
| Repository | `ConversationRepository` |
| Planned Asset Loader / Composer / Middleware | Prompt system evolution path aligned to ADR-002 and ADR-003 |

The detailed class hierarchy, patterns catalog, configuration snippets, and file relationships are preserved in [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md).

### 4.3 Runtime Interaction View

#### 4.3.1 Primary Query Processing Flow

```text
User Query
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│ StockAssistantAgent                                             │
│                                                                  │
│  ┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐ │
│  │ ReAct Agent ├───►│ Tool Selection   ├───►│ Tool Execution  │ │
│  │ (LangChain) │    │ (LLM Decision)   │    │ (CachingTool)   │ │
│  └─────────────┘    └──────────────────┘    └─────────────────┘ │
│         │                                          │             │
│         ▼                                          ▼             │
│  ┌─────────────┐                          ┌─────────────────┐   │
│  │ LLM Response│◄────────────────────────│ Tool Output     │   │
│  │ Generation  │                         │ (Cached/Fresh)  │   │
│  └─────────────┘                          └─────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
AgentResponse (content, provider, model, tool_calls, token_usage)
```

#### 4.3.2 Route Classification View

The runtime uses `semantic-router` with OpenAI embeddings and HuggingFace fallback to classify user requests into one of eight route categories.

| Route | Description | Example Queries |
|-------|-------------|-----------------|
| `PRICE_CHECK` | Current prices, quotes, market cap | "What is AAPL trading at?" |
| `NEWS_ANALYSIS` | Headlines, earnings, market events | "Latest news on Tesla" |
| `PORTFOLIO` | Holdings, P&L, allocation | "Show my portfolio value" |
| `TECHNICAL_ANALYSIS` | Charts, MACD, RSI, patterns | "Show RSI for NVDA" |
| `FUNDAMENTALS` | P/E, P/B, DCF, financial ratios | "What's Apple's P/E ratio?" |
| `IDEAS` | Stock picks, investment strategies | "Recommend growth stocks" |
| `MARKET_WATCH` | Index updates, sector performance | "How is VN-Index doing?" |
| `GENERAL_CHAT` | Fallback for unmatched queries | "Hello, how are you?" |

#### 4.3.3 Provider Selection and Fallback View

The provider/model path is mediated by `ModelClientFactory`, which caches provider/model client instances. Runtime fallback behavior preserves a graceful-degradation path if the primary provider fails or if the ReAct executor is unavailable.

```text
ModelClientFactory.get_client(config)
    │
    ├─► Check _CACHE for "provider:model_name" key
    │       │
    │       ├─► Found: Return cached client
    │       │
    │       └─► Not found: Create new client
    │               │
    │               ├─► provider="openai" → OpenAIModelClient
    │               ├─► provider="grok"   → GrokModelClient
    │               └─► other             → ValueError
    │
    └─► Return BaseModelClient instance
```

```text
_generate_with_fallback(client, prompt, query)
    │
    ├─► Build sequence: [primary_provider] + fallback_order
    │       Example: ["openai", "grok"]
    │
    ├─► For each provider in sequence:
    │       │
    │       ├─► Try generate/generate_with_search
    │       │       │
    │       │       ├─► Success: Return result (with fallback prefix if not primary)
    │       │       │
    │       │       └─► Exception: Log warning, continue to next
    │       │
    └─► All failed: Return "All providers failed. Last error: {e}"
```

### 4.4 Memory and State View

The agent domain uses LangGraph's `MongoDBSaver` for conversation-scoped STM persistence, with `conversation_id -> thread_id` as the canonical binding. Sessions remain parent business context, while conversations own STM.

The layered LLM architecture (ADR-001) also defines a Long-Term Memory (LTM) layer for stable, slow-changing user preferences and symbol-tracking context. LTM is architecturally distinct from STM: it persists across conversations, enables personalization and routing, and explicitly excludes financial facts (which remain in RAG/tools). LTM is not yet implemented in the runtime; the design and scope boundaries are governed by ADR-001 §6.1.

ADR-001 further defines **Retrieval-Augmented Generation (RAG)** (§9) and **Fine-Tuning** (§10) as distinct architectural layers. RAG provides intent-specific vector indices for sourced documents (filings, news, macro data), while Fine-Tuning enforces reasoning structure and tone without storing knowledge. Neither layer is implemented in the current runtime; their scope and boundaries are governed by ADR-001.

| Aspect | Architectural Position |
|--------|------------------------|
| State owner | LangGraph checkpointer for agent execution state; application metadata in `conversations` |
| Binding | Direct 1:1 `conversation_id -> thread_id` |
| Hierarchy | `workspace -> session -> conversation` |
| Lifecycle | `active -> summarized -> archived` |
| Scope boundary | Conversation text and state only; no prices, ratios, or tool outputs in memory |

The runtime contract is now `conversation_id` across agent methods, REST chat, management APIs, repositories, reconciliation, and migration tooling. The REST `POST /api/chat` route still accepts a deprecated `session_id` alias and normalizes it into `conversation_id`; the Socket.IO handler accepts `conversation_id` only.

```text
APIServer.__init__()
    │
    ├─► create_checkpointer(config)  → MongoDBSaver | None
    │
    └─► StockAssistantAgent(config, data_manager, checkpointer=checkpointer)
            │
            └─► create_agent(..., checkpointer=checkpointer)
                    │
                └─► invoke(messages, config={"configurable": {"thread_id": conversation_id}})
```

The full memory data model, API impact, reconciliation behavior, and sequence diagrams are preserved in [AGENT_MEMORY_TECHNICAL_DESIGN.md](./AGENT_MEMORY_TECHNICAL_DESIGN.md).

### 4.5 Prompt and Behavior View

#### 4.5.1 Current Behavior Contract

The current runtime still carries a hardcoded system prompt in the agent runtime. The prompt system architecture below describes the planned transition to externalized, versioned, and composable prompt assets.

```text
You are a professional stock investment assistant.
You help users with stock analysis, price lookups, technical analysis...

When answering questions:
1. Use the appropriate tools when you need real-time data
2. Provide accurate, factual information based on tool outputs
3. Include relevant disclaimers for investment-related advice
4. Be concise but comprehensive in your responses
```

#### 4.5.2 Prompt Architecture View

> **Status:** Proposed design — not yet implemented.
> **Research Authority:** [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](./PROMPT_SYSTEM_RESEARCH_PROPOSAL.md)
> **Governing ADRs:** [ADR-AGENT-002-SKILLS-PATTERN-PROMPT-COMPOSITION.md](./decisions/ADR-AGENT-002-SKILLS-PATTERN-PROMPT-COMPOSITION.md), [ADR-AGENT-003-EXTERNALIZE-VERSION-PROMPT-ASSETS.md](./decisions/ADR-AGENT-003-EXTERNALIZE-VERSION-PROMPT-ASSETS.md)

```text
Layer 1: PromptAssetLoader
  │  Discovers and loads versioned YAML prompt files from src/prompts/
  │  Validates schema, extracts version metadata, implements fallback
  │
  ▼
Layer 2: PromptAssembler
  │  Composes base system prompt + active skills + LTM/STM context
  │  Selects skills by route classification and activation criteria
  │  Injects prompt version tag into metadata
  │
  ▼
Layer 3: ResponseGuardrailMiddleware
  │  Post-processes agent output to enforce behavioral guardrails
  │  Checks: anti-hype blocklist, source attribution, uncertainty disclosure
  │  Emits guardrail violations as structured trace events
```

| Component | Responsibility | Governing ADR |
|-----------|----------------|---------------|
| **PromptAssetLoader** | Load versioned prompt assets from `src/prompts/`; validate YAML schema; extract version identity; fall back to `_baseline.yaml` on failure | ADR-003 |
| **PromptAssembler** | Compose final prompt from base + skills + context; apply route-specific skill selection; inject prompt version into metadata; support experiment variant assignment | ADR-002 |
| **ResponseGuardrailMiddleware** | Scan agent output for hype/manipulation language; verify source attribution and uncertainty disclosure; log violations | ADR-001 §4.7 |

#### 4.5.3 Prompt Taxonomy and Skills Composition

| Type | Directory | Lifecycle | Example |
|------|-----------|-----------|---------|
| **System prompts** | `src/prompts/system/` | Versioned, one active at a time | `v1.0.0.yaml` — core persona and instructions |
| **Skills** | `src/prompts/skills/` | Composable, multiple active per request | `disclaimer.yaml`, `anti-hype.yaml` |
| **Experiments** | `src/prompts/experiments/` | Temporary variants for A/B testing | `exp-001-concise.yaml` |
| **Baseline** | `src/prompts/system/_baseline.yaml` | Permanent fallback, never deleted | Last-known-good system prompt |

```text
Query arrives
   │
   ▼
Semantic Router classifies route (e.g., FUNDAMENTALS)
   │
   ▼
PromptAssetLoader loads:
   ├─ Base system prompt (version-tagged)
   ├─ Always-active skills (disclaimer, anti-hype)
   └─ Route-matched skills (earnings-analysis, if FUNDAMENTALS)
   │
   ▼
PromptAssembler composes final prompt:
   [Base] + [Always-Active Skills] + [Route Skills] + [LTM/STM] + [RAG] + [Output Schema]
   │
   ▼
Agent invocation with assembled prompt
   (prompt_version + experiment_id recorded in trace span)
   │
   ▼
ResponseGuardrailMiddleware post-processes output
   (blocklist scan, attribution check, uncertainty check)
```

#### 4.5.4 Prompt Observability View

| Trace Attribute | Source | Example Value |
|----------------|--------|---------------|
| `prompt.version` | PromptAssetLoader | `v1.2.0` |
| `prompt.route` | Semantic Router | `FUNDAMENTALS` |
| `prompt.experiment_id` | PromptAssembler | `exp-001` (or `null`) |
| `prompt.skills_active` | PromptAssembler | `['disclaimer', 'anti-hype', 'earnings-analysis']` |
| `guardrail.violations` | ResponseGuardrailMiddleware | `[]` or `['hype_language_detected']` |

### 4.6 Operational and Quality View

Operationally significant architecture concerns include:

- archive-safe chat handling through `ChatService` on the REST path;
- separation of metadata persistence from LangGraph checkpoint persistence;
- route-aware evolution of prompt composition and observability metadata;
- maintainability through explicit factory, registry, and repository seams;
- future observability extension toward structured logs, metrics, and tracing.

The detailed configuration reference, metrics examples, testing structures, and code-oriented extension paths are preserved in [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md).

---

## 5. Correspondences and Traceability

### 5.1 View-to-Document Correspondence

| Architecture View | Primary Companion Documents |
|-------------------|-----------------------------|
| Context and Boundary View | [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md), [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md) |
| Static Structure View | [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md) |
| Runtime Interaction View | [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md), [AGENT_MEMORY_TECHNICAL_DESIGN.md](./AGENT_MEMORY_TECHNICAL_DESIGN.md) |
| Memory and State View | [AGENT_MEMORY_TECHNICAL_DESIGN.md](./AGENT_MEMORY_TECHNICAL_DESIGN.md), [ADR-AGENT-001-LAYERED-LLM-ARCHITECTURE.md](./decisions/ADR-AGENT-001-LAYERED-LLM-ARCHITECTURE.md) |
| Prompt and Behavior View | [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](./PROMPT_SYSTEM_RESEARCH_PROPOSAL.md), [ADR-AGENT-002-SKILLS-PATTERN-PROMPT-COMPOSITION.md](./decisions/ADR-AGENT-002-SKILLS-PATTERN-PROMPT-COMPOSITION.md), [ADR-AGENT-003-EXTERNALIZE-VERSION-PROMPT-ASSETS.md](./decisions/ADR-AGENT-003-EXTERNALIZE-VERSION-PROMPT-ASSETS.md) |
| Evolution View | [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md), [PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md](./PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md) |

### 5.2 Concern-to-Decision Correspondence

| Concern | Governing Decision / Artifact |
|---------|-------------------------------|
| Layered LLM boundaries and memory scope | [ADR-AGENT-001-LAYERED-LLM-ARCHITECTURE.md](./decisions/ADR-AGENT-001-LAYERED-LLM-ARCHITECTURE.md) |
| Prompt skills composition | [ADR-AGENT-002-SKILLS-PATTERN-PROMPT-COMPOSITION.md](./decisions/ADR-AGENT-002-SKILLS-PATTERN-PROMPT-COMPOSITION.md) |
| Externalized prompt assets and prompt versioning | [ADR-AGENT-003-EXTERNALIZE-VERSION-PROMPT-ASSETS.md](./decisions/ADR-AGENT-003-EXTERNALIZE-VERSION-PROMPT-ASSETS.md) |
| Conversation hierarchy, checkpoints, and runtime reconciliation | [AGENT_MEMORY_TECHNICAL_DESIGN.md](./AGENT_MEMORY_TECHNICAL_DESIGN.md) |
| Prompt-system design research and rollout path | [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](./PROMPT_SYSTEM_RESEARCH_PROPOSAL.md) |

### 5.3 Terminology and Concept Evolution

| Original Concept (ADR-001 §8) | Evolved Realization (ADR-002, ADR-003) | Note |
|-------------------------------|----------------------------------------|------|
| Prompt Compiler | PromptAssetLoader → PromptAssembler → ResponseGuardrailMiddleware | The single-step compiler concept was elaborated into a three-layer architecture. See ADR-001 §8 Implementation Reference. |
| Intent-based routing | `StockQueryRoute` enum with 8 canonical routes | Originally described with 7 working-name intents; refined to 8 routes during implementation. |

### 5.4 Content Preservation Correspondence

The pre-rewrite architecture document mixed architecture description, technical realization, and roadmap material. That content has been preserved as follows:

- viewpoint-relevant architecture content remains in this document;
- implementation-heavy component, configuration, pattern, and extension detail is preserved in [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md);
- memory-specific subsystem detail is preserved in [AGENT_MEMORY_TECHNICAL_DESIGN.md](./AGENT_MEMORY_TECHNICAL_DESIGN.md);
- prompt-system research, detailed rollout logic, and evaluation design are preserved in [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](./PROMPT_SYSTEM_RESEARCH_PROPOSAL.md);
- decision authority remains with the ADR set in [decisions](./decisions).

---

## 6. Architecture Rationale

### 6.1 Governing Decisions Already Recorded in ADRs

| ADR | Status | Architectural Effect on This Description |
|-----|--------|------------------------------------------|
| [ADR-AGENT-001-LAYERED-LLM-ARCHITECTURE.md](./decisions/ADR-AGENT-001-LAYERED-LLM-ARCHITECTURE.md) | **Accepted** | Governs memory boundaries, evidence separation, and layered LLM responsibilities |
| [ADR-AGENT-002-SKILLS-PATTERN-PROMPT-COMPOSITION.md](./decisions/ADR-AGENT-002-SKILLS-PATTERN-PROMPT-COMPOSITION.md) | **Proposed** | Governs the composable skills model used in the prompt architecture view |
| [ADR-AGENT-003-EXTERNALIZE-VERSION-PROMPT-ASSETS.md](./decisions/ADR-AGENT-003-EXTERNALIZE-VERSION-PROMPT-ASSETS.md) | **Proposed** | Governs the move from hardcoded prompts to versioned external assets |

#### 6.1.1 Architectural Hard Rules (from ADR-001 §4)

The following governing principles are established as accepted architectural constraints:

1. **Memory never stores facts** — LTM/STM retain user preferences and session context only; financial facts originate from external sources or verified data stores.
2. **RAG never stores opinions** — RAG indices contain sourced documents only; interpretations remain in LLM output tied to cited evidence.
3. **Fine-tuning never stores knowledge** — Fine-tuning enforces structure and tone, not factual content.
4. **Prompting controls behavior, not data** — Prompts encode rules, safety constraints, and output schema; data is injected at runtime.
5. **Tools compute numbers, LLM reasons about them** — Deterministic tools fetch and calculate; the LLM explains implications.
6. **Investment data sources are external** — Stock data is fetched from pre-listed external sources and the in-system database.
7. **Market manipulation safeguards are enforced** — Outputs are informational and grounded in verifiable sources only.

### 6.2 Additional Rationale Reflected in the Current Architecture

The current architecture also reflects several design choices that shape the views in this document:

- **ReAct pattern selection**: chosen for autonomous tool selection, extensibility, and transparent multi-step reasoning;
- **Model client factory and caching**: used to keep provider-specific creation logic outside call sites and to avoid redundant client initialization;
- **Singleton tool registry**: used to centralize enabled/disabled tool state and simplify health aggregation;
- **semantic routing**: preferred over LLM-only intent routing for speed and explicit route taxonomies;
- **immutable response types**: used to preserve predictable response contracts and avoid accidental mutation;
- **dual execution mode**: retained to preserve graceful degradation while the newer LangChain/LangGraph path matures.

These rationale elements are preserved as architecture context here and as realization detail in [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md).

---

## 7. Architecture Considerations and Planned Evolution

This section retains the major evolution themes from the previous architecture document, but reframes them as architecture considerations rather than mixing them into the active views.

### 7.1 Tooling and Data Access Evolution

| Area | Current State | Planned Direction |
|------|---------------|------------------|
| Stock symbol data | Yahoo Finance plus repository fallback | Multi-source data providers and richer domain actions |
| TradingView integration | Placeholder only | Full chart, widget, and analysis integration |
| Reporting | Basic report generation | Template-driven HTML/PDF capable reporting |

### 7.2 Agent Runtime Evolution

| Area | Current State | Planned Direction |
|------|---------------|------------------|
| Agent topology | Single ReAct agent | Skills-based prompt specialization, then possibly router-orchestrated specialists |
| Output format | Primarily unstructured text | Structured-output contracts for selected response types |
| Routing | 8 static route categories | Dynamic route discovery, multi-intent handling, and adaptive thresholds |
| Memory | Conversation-scoped STM implemented | Summarization triggers, Socket.IO parity, future LTM retrieval |

### 7.3 Prompt-System Evolution

| Area | Current State | Planned Direction |
|------|---------------|------------------|
| Prompt storage | Hardcoded runtime prompt plus planned files | Versioned file assets in `src/prompts/` |
| Composition | Single monolithic runtime prompt | Skills-based composable fragments |
| Versioning | Implicit in code changes | Embedded prompt identity and trace metadata |
| Guardrails | Inline instructions | Middleware-enforced response guardrails |
| Experimentation | Not supported in runtime | Controlled prompt variants and experiment metadata |

### 7.4 Quality and Operations Evolution

| Area | Current State | Planned Direction |
|------|---------------|------------------|
| Logging | Basic Python logging | Structured logs and richer runtime metadata |
| Metrics and tracing | Limited | Prometheus/OpenTelemetry-style observability |
| Testing | Existing but uneven by slice | Broader unit, integration, E2E, and performance coverage |

The detailed extension catalog, example snippets, configuration candidates, and engineering follow-up notes are preserved in [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md).

---

## 8. Revision History

| Version | Date | Author | Notes |
|---------|------|--------|-------|
| 0.0 | 2026-04-16 | GitHub Copilot | Reorganized the former mixed architecture document into an ISO 42010-aligned architecture description and redirected realization detail to companion documents |
| 0.1 | 2026-04-16 | GitHub Copilot | Applied cross-document review fixes: route taxonomy reconciliation with code ground truth, ADR-001 principles surfaced, status column added, methodology justification, prompt compiler correspondence, LTM acknowledgment, concern category terminology, SRS coverage simplified |
