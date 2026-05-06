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
| Date | 2026-05-06 |
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

### 3.1 How Viewpoints and Views Are Used in This Document

This architecture description follows the ISO 42010 distinction between a **viewpoint** and a **view**:

- a **viewpoint** is the template that defines which stakeholders, concerns, and model kinds govern a view;
- a **view** is the actual architecture content produced using that viewpoint.

In this document, section 3 defines the viewpoints. Section 4 then provides one architecture view for each viewpoint so the framing rules and the resulting architecture description stay clearly separated.

### 3.2 Viewpoint Catalog

| Viewpoint | Stakeholders | Concerns Framed | Conventions / Model Kinds |
|-----------|--------------|-----------------|----------------------------|
| Context and Boundary Viewpoint | Architecture owners, backend maintainers, product reviewers | Domain scope, environment, external dependencies, system boundary, ownership boundaries | Narrative boundary statements, system context diagrams, context summaries, dependency tables |
| Logical Viewpoint | Engineers, product reviewers, architecture owners | Modularity, separation of concerns, responsibility allocation, extensibility seams, dependency direction | Component and responsibility tables, logical decomposition summaries, relationship narratives |
| Process Viewpoint | Agent maintainers, backend engineers, SREs | Runtime flow, route handling, tool orchestration, latency-sensitive paths, provider fallback, fault tolerance | Interaction flows, sequence-style diagrams, runtime decision summaries |
| Information and State Viewpoint | Architects, backend maintainers, compliance reviewers | STM scope, state ownership, lifecycle, metadata boundaries, hierarchy, memory constraints | State and lifecycle tables, hierarchy summaries, state ownership narratives |
| Development Viewpoint | Developers, maintainers, technical leads | Code organization, module ownership, maintainability, build-facing structure, extension points | Source-layout views, module-boundary summaries, ownership and dependency tables |
| Deployment Viewpoint | DevOps, security reviewers, SREs | Runtime topology, containers and services, health endpoints, scaling boundaries, environment overlays, secrets boundaries | Deployment context summaries, topology tables, environment and probe mappings |
| Operations and Maintenance Viewpoint | DevOps, security reviewers, developers, product owners | Production operation, availability, resilience, observability, drift detection, recovery surfaces, maintainability in service | Operational responsibility tables, resilience summaries, observability and health mappings |
| Prompt and Behavior Viewpoint | Agent maintainers, architecture owners, compliance reviewers | Prompt composition, guardrails, behavioral policy, prompt observability, prompt evolution | Layered prompt diagrams, taxonomy tables, metadata tables |

These viewpoints govern the corresponding views in section 4. Detailed code-oriented realization belongs in [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md), detailed STM realization belongs in [AGENT_MEMORY_TECHNICAL_DESIGN.md](./AGENT_MEMORY_TECHNICAL_DESIGN.md), and deployment procedure detail belongs in [IaC/README.md](../../../IaC/README.md).

---

## 4. Architecture Views

### 4.1 Context and Boundary View

The agent domain sits between the API and service layer and the external data and model-provider ecosystem. It does not own the frontend UI, REST or Socket.IO transport surface, or repository-wide operational policy. It does own reasoning workflow, tool orchestration, route-aware behavior, provider fallback, and conversation-scoped STM binding.

The primary context relationships are:

- API routes and Socket.IO handlers pass user requests into the agent runtime;
- service-layer components govern ownership, archival checks, and metadata synchronization around conversations;
- LangGraph checkpointer infrastructure stores conversation-scoped execution state;
- tool implementations gather external or repository-backed data;
- prompt assets and prompt composition logic govern model behavior, not factual storage.

This boundary is consistent with the repository methodology's rule that architecture descriptions should explain **what structures and interactions exist**, while implementation detail and contract detail remain in companion documents.

#### 4.1.1 System Context

The system context view clarifies the trust and integration boundary between client applications, internal services, external LLM providers, and external market data providers. This boundary is operationally important because security, compliance, and production-support responsibilities differ across these interfaces.

```text
┌────────────────────────────── External Clients ──────────────────────────────┐
│                                                                              │
│  Web Frontend / Browser Clients / Future API Consumers                       │
│                                                                              │
└─────────────────────────────────────┬────────────────────────────────────────┘
                                      │ HTTPS / WebSocket
                                      ▼
┌─────────────────────────── Internal Service Boundary ────────────────────────┐
│                                                                              │
│  API Routes / Socket.IO Handlers                                             │
│          │                                                                   │
│          ▼                                                                   │
│  ChatService / ConversationService                                           │
│          │                                                                   │
│          ▼                                                                   │
│  StockAssistantAgent                                                         │
│          │                                                                   │
│          ├──────────────► Tool Layer ───────────────► Redis Cache            │
│          │                                      └──► MongoDB Metadata / STM  │
│          │                                                                   │
│          └──────────────► Model Client Factory / Prompt Logic                │
│                                                                              │
└──────────────────────┬──────────────────────────────┬────────────────────────┘
                       │                              │
                       │ External model calls         │ External market-data calls
                       ▼                              ▼
             ┌────────────────────┐        ┌─────────────────────────┐
             │ LLM Providers      │        │ Market Data Providers   │
             │ OpenAI / Grok      │        │ Yahoo Finance / others  │
             └────────────────────┘        └─────────────────────────┘
```

```text
Boundary classification
-----------------------
Client apps            : Outside internal trust boundary
Internal services      : Inside application control boundary
LLM providers          : External AI processing boundary
Market data providers  : External evidence and pricing boundary
MongoDB / Redis        : Internal persistence and cache boundary
```

The architecture intentionally routes all external interactions through internal service and agent seams rather than allowing client applications to call providers directly. This preserves a single enforcement point for authentication, authorization, archive safety, observability, prompt policy, and provider fallback.

| Boundary | Primary Responsibility | Security / Compliance / Operations Significance |
|----------|------------------------|-------------------------------------------------|
| Client apps -> Internal services | Transport, authentication, request validation, streaming control | Protects internal capabilities from direct exposure and centralizes auditability |
| Internal services -> LLM providers | Prompted reasoning and generated responses | External AI providers must be treated as non-authoritative processors; prompts and outputs require policy and logging controls |
| Internal services -> Market data providers | Evidence and pricing retrieval through tools | Keeps factual market-data sourcing explicit and separable from model reasoning |
| Internal services -> MongoDB / Redis | Metadata, STM persistence, and cache management | Preserves operational recovery, drift detection, and lifecycle governance inside the system boundary |

From a compliance and operational perspective, this context establishes three hard boundaries:

1. Client applications are consumers of the system, not participants in internal orchestration.
2. LLM providers are external reasoning services and do not become the source of truth for market facts or conversation ownership.
3. Market data providers are external evidence sources and are accessed only through controlled internal tool paths.

This system context complements the deployment and operations views by showing who is inside the controlled system boundary and which dependencies remain external.

### 4.2 Logical View

#### 4.2.1 Logical Building Blocks

| Building Block | Responsibility |
|----------------|----------------|
| `stock_assistant_agent.py` | Main ReAct runtime and conversation-aware agent entry points |
| `langgraph_bootstrap.py` | Agent/bootstrap utilities including checkpointer creation |
| `stock_query_router.py` | Semantic route classification |
| `model_factory.py` and provider clients | Provider and model selection with cached client construction |
| `tools/` | Tool registration, caching, and domain data access |
| `conversation_repository.py` | Conversation metadata persistence |
| `chat_service.py` and `conversation_service.py` | Orchestration, archive guards, lifecycle and metadata helpers |
| `src/prompts/` | Planned prompt asset directory for system prompts, skills, and experiments |

These building blocks are separated so that reasoning orchestration, state management, metadata ownership, and provider integration can evolve independently. The agent runtime owns reasoning and tool orchestration, service-layer components own business lifecycle enforcement, repositories own metadata persistence, and prompt assets govern behavior rather than domain data.

#### 4.2.2 Responsibility and Dependency Boundaries

| Logical Concern | Primary Owner | Architectural Boundary |
|-----------------|---------------|------------------------|
| Reasoning and tool selection | `StockAssistantAgent` | Does not own conversation lifecycle or repository persistence |
| Semantic route classification | `stock_query_router.py` | Classifies requests but does not execute tools or persist state |
| Provider and model selection | `ModelClientFactory` and provider clients | Isolates provider-specific concerns from routes and services |
| Conversation lifecycle and archive rules | `ChatService`, `ConversationService` | Owns business guards and metadata synchronization outside the agent core |
| Conversation metadata persistence | `ConversationRepository` | Persists application metadata, separate from LangGraph checkpoint state |
| Prompt behavior and guardrails | Runtime prompt logic and planned `src/prompts/` assets | Controls behavioral policy, not business state or financial facts |

This logical separation is the primary extensibility mechanism for the domain. New providers, tools, prompt assets, or conversation-management behaviors should be added by extending the relevant building block rather than by collapsing responsibilities into the agent runtime.

#### 4.2.3 Layered Architecture Boundaries

The agent domain uses a layered architecture so personalization, conversation state, external evidence, behavioral policy, and deterministic computation remain separable concerns rather than blending into a single prompt or storage surface.

| Layer | Primary Purpose | Architectural Boundary |
|-------|-----------------|------------------------|
| Long-Term Memory (LTM) | Persist stable user preferences and symbol-tracking context across conversations | Personalization layer only; not a source of market facts, valuations, or recommendations |
| Short-Term Memory (STM) | Retain conversation-scoped state and thread-local reasoning context | Scoped to a conversation boundary; does not become a cross-session factual store |
| Intent Routing | Classify requests so the runtime selects the right tools, retrieval path, and response behavior | Classification layer only; does not own persistence, tool execution, or lifecycle rules |
| Retrieval-Augmented Generation (RAG) | Supply sourced evidence for domain-specific reasoning | Evidence layer only; stores retrieved source content, not user preferences or model-authored conclusions |
| Prompting and Guardrails | Control behavior, disclosure, and response framing | Policy layer only; governs how the model behaves, not where domain truth is stored |
| Tools and Deterministic Computation | Fetch data and compute auditable metrics | Computation layer only; performs data retrieval and calculations that the LLM then interprets |
| Fine-Tuning | Enforce reasoning structure and tone for selected workflows | Behavior-shaping layer only; does not function as a knowledge store |

This boundary model is the core rationale for ADR-001: it reduces hallucination pressure, keeps market facts external to memory and prompt state, and allows retrieval, prompting, and execution behavior to evolve independently.

#### 4.2.4 Structural Patterns and Stack Summary

| Category | Architectural Role |
|----------|--------------------|
| Factory | `ModelClientFactory`, `create_checkpointer()` |
| Registry / Singleton | `ToolRegistry` |
| Strategy | Provider-specific model clients |
| Template Method / Decorator | `CachingTool` |
| Repository | `ConversationRepository` |
| Planned Asset Loader / Composer / Middleware | Prompt system evolution path aligned to ADR-002 and ADR-003 |

The detailed class hierarchy, patterns catalog, configuration snippets, and file relationships are preserved in [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md).

### 4.3 Process View

The process view describes the runtime interactions that turn a user request into a routed, tool-aware, and provider-backed response. It focuses on the execution path and degraded-operation behavior rather than on class-level realization.

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

Service-layer orchestration remains on the outer edge of this process. Archive safety, ownership validation, and metadata synchronization are intentionally handled outside the core reasoning loop so the process path can stay focused on classification, tool use, and generation.

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

The provider and model path is mediated by `ModelClientFactory`, which caches provider-model client instances. Runtime fallback behavior preserves a graceful-degradation path if the primary provider fails or if the ReAct executor is unavailable.

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

These process flows express the domain's latency and fault-tolerance posture: semantic routing limits unnecessary tool exploration, provider fallback preserves degraded operation, and service-layer lifecycle checks keep archived or invalid conversation states out of the reasoning path.

### 4.4 Information and State View

The agent domain uses LangGraph's `MongoDBSaver` for conversation-scoped STM persistence, with `conversation_id -> thread_id` as the canonical binding. Sessions remain parent business context, while conversations own STM.

The layered LLM architecture (ADR-001) also defines a Long-Term Memory (LTM) layer for stable, slow-changing user preferences and symbol-tracking context. LTM is architecturally distinct from STM: it persists across conversations, enables personalization and routing, and explicitly excludes financial facts, which remain in RAG or tools. LTM is not yet implemented in the runtime; the design and scope boundaries are governed by the ADR-001 LTM boundary decision.

ADR-001 further defines **Retrieval-Augmented Generation (RAG)** and **Fine-Tuning** as distinct architectural layers. RAG provides intent-specific vector indices for sourced documents, while Fine-Tuning enforces reasoning structure and tone without storing knowledge. Neither layer is implemented in the current runtime; their scope and boundaries are governed by ADR-001.

#### 4.4.1 State and Evidence Allocation Boundaries

The state model is intentionally split so user context, conversation state, retrieved evidence, and computed financial results do not collapse into one storage boundary.

| Concern | Canonical Architectural Home | Explicit Exclusions |
|---------|------------------------------|---------------------|
| Stable personalization and reusable user context | LTM | Prices, ratios, valuations, forecasts, recommendations |
| Active conversation state and thread-local assumptions | STM via LangGraph checkpoints plus conversation metadata | Cross-conversation factual store, retrieved document corpus, durable financial truth |
| Sourced market and filing evidence | RAG indices and external data sources | User preferences, model-authored interpretations, long-lived conversation state |
| Deterministic metrics and fetched numbers | Tool execution and approved data providers | Prompt state, LTM/STM persistence, model-only inferred facts |
| Output behavior, disclosure, and tone | Prompt and guardrail policy | Persistent domain data and financial truth |

This allocation is what allows the domain to enforce the ADR-001 hard rules in architecture terms: memory personalizes and contextualizes, RAG informs, tools compute, and prompts govern behavior without becoming a shadow data layer.

| Aspect | Architectural Position |
|--------|------------------------|
| State owner | LangGraph checkpointer for agent execution state; application metadata in `conversations` |
| Binding | Direct 1:1 `conversation_id -> thread_id` |
| Hierarchy | `workspace -> session -> conversation` |
| Lifecycle | `active -> summarized -> archived` |
| Scope boundary | Conversation text and state only; no prices, ratios, or tool outputs in memory |

The runtime contract is now `conversation_id` across agent methods, REST chat, management APIs, repositories, reconciliation, and migration tooling. The REST `POST /api/chat` route still accepts a deprecated `session_id` alias and normalizes it into `conversation_id`; the Socket.IO handler accepts `conversation_id` only.

The information boundary is deliberate: LangGraph checkpoints retain agent execution state for a conversation, while the `conversations` collection and service layer retain application metadata and lifecycle control. This keeps behavioral state and business metadata aligned without making the checkpointer the source of truth for application ownership or archival rules.

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

### 4.5 Development View

The development view captures how the architecture is realized in the repository so maintainers can evolve the domain without eroding responsibility boundaries.

#### 4.5.1 Source Layout View

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

#### 4.5.2 Maintainability and Extension Boundaries

| Development Concern | Architectural Guidance |
|---------------------|------------------------|
| Module ownership | Keep agent reasoning in `src/core/`, business orchestration in `src/services/`, and persistence in `src/data/repositories/` |
| Extending providers | Add provider-specific clients behind `BaseModelClient` and register through `ModelClientFactory` |
| Extending tools | Add tool implementations under `src/core/tools/` and expose them through `ToolRegistry` rather than wiring ad hoc calls |
| Memory changes | Preserve `conversation_id -> thread_id` as the canonical STM binding and keep business metadata outside checkpoints |
| Prompt evolution | Add versioned assets under `src/prompts/` and keep prompt composition policy separate from tool or repository logic |

This view is intentionally about code organization and maintainability, not low-level realization. Detailed implementation behavior, configuration, and extension mechanics remain in [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md).

### 4.6 Deployment View

The agent domain runs inside a broader multi-service deployment topology. At architecture level, the important concern is how the agent-related runtime depends on API, cache, database, and model-provider boundaries across local and production-like environments.

#### 4.6.1 Runtime Topology Summary

| Runtime Element | Deployment Role | Boundary Notes |
|-----------------|-----------------|----------------|
| API container | Hosts Flask routes, Socket.IO handlers, and the agent invocation path | Primary entry point for frontend and service integration |
| Agent container | Background worker and health surface | Separates long-running or asynchronous work from request-serving flow |
| MongoDB | Stores conversation metadata and LangGraph checkpoint state | Metadata and checkpoint concerns remain logically separate even when stored on the same platform family |
| Redis | Cache and transient coordination layer | Supports performance and graceful degradation paths |
| Frontend container | User-facing interface | Consumes API and streaming surfaces but does not host agent logic |

#### 4.6.2 Environment and Reliability Boundaries

| Concern | Architecture Position |
|---------|-----------------------|
| Local development topology | Docker Compose provides an integration-faithful multi-service environment |
| Production-like topology | Helm-managed Kubernetes deployment scales API, agent, and frontend independently |
| Health contracts | API `GET /api/health`, agent `GET /health`, frontend `GET /healthz` |
| Configuration overlays | `APP_ENV` and environment-specific config overlays select environment behavior without changing architecture boundaries |
| Secrets boundary | Local secrets come from environment variables; production secrets are intended to come from Azure Key Vault or equivalent managed secret stores |

Detailed deployment procedures, port mappings, Docker and Helm specifics, and runbooks belong in [IaC/README.md](../../../IaC/README.md) and the infrastructure artifacts under `IaC/`.

### 4.7 Operations and Maintenance View

The operations and maintenance view addresses how the architecture supports production operation, resilience, and maintainability after deployment.

#### 4.7.1 Health, Observability, and Drift Surfaces

| Operational Concern | Current Architectural Surface |
|---------------------|-------------------------------|
| Health reporting | Agent and service health aggregate through explicit health endpoints and service health checks |
| Logging and traceability | Runtime logging exists now; the architecture anticipates structured logs and prompt-level trace metadata |
| Prompt observability | Prompt version, route, experiment, and guardrail outcomes are intended as traceable runtime metadata |
| Drift detection | Reconciliation and migration tooling provide visibility into conversation and checkpoint drift |
| Archive safety | `ChatService` protects the REST path from invalid archived-conversation execution |

#### 4.7.2 Resilience and Recovery Boundaries

| Failure Mode | Architectural Response |
|--------------|------------------------|
| Provider failure or timeout | Fallback order enables degraded continuation rather than immediate hard failure |
| Cache unavailability | In-memory fallback paths preserve partial operation where supported |
| Checkpointer unavailability | Agent runtime can run without checkpoint persistence, with reduced STM capability |
| Metadata and checkpoint drift | Reconciliation tooling and service ownership boundaries contain and repair mismatch risk |
| Archived conversation access | Service-layer guards prevent invalid runtime mutation of archived context |

#### 4.7.3 Quality Attribute Scenarios

The following quality scenarios summarize the failure, degradation, recovery, and performance expectations already established in this architecture description and its governing companion artifacts. They are expressed at architecture level so reviewers can assess whether the system's control boundaries and fallback paths are adequate without reading implementation detail.

##### 4.7.3.1 Reliability and Fault-Tolerance Scenarios

| Scenario | Stimulus and Environment | Expected Architectural Response |
|----------|--------------------------|---------------------------------|
| LLM provider outage or timeout | The primary model provider becomes unavailable during active query processing and fallback is enabled | Route generation to the next provider in `fallback_order`, preserve service continuity in degraded mode, and surface fallback metadata in the response path |
| Semantic-router primary encoder failure | The primary embeddings provider is unavailable during route classification | Use the configured secondary encoder and continue classification; if confidence remains insufficient, preserve a safe fallback route rather than fail the request outright |
| Cache backend unavailable | Redis or the primary cache path is unavailable during tool execution | Continue with in-memory fallback or uncached execution where supported so tool use remains available with reduced efficiency |
| Checkpointer unavailable | Checkpoint persistence cannot be reached during a conversation-scoped request | Continue without checkpoint persistence so the agent remains usable, but with reduced STM capability and no assumption of durable thread state |
| Legacy executor fallback required | The preferred ReAct execution path is unavailable or cannot be initialized | Use the retained legacy execution path so the system degrades functionally rather than becoming unavailable |

##### 4.7.3.2 Data Integrity and Lifecycle Scenarios

| Scenario | Stimulus and Environment | Expected Architectural Response |
|----------|--------------------------|---------------------------------|
| Archived conversation mutation attempt | A request targets a conversation whose lifecycle state is `archived` | Service-layer guards reject invalid mutation before the request enters the reasoning path |
| Metadata and checkpoint drift detected | Reconciliation tooling or runtime checks detect mismatch between application metadata and LangGraph checkpoint state | Contain the mismatch within service and repository boundaries, expose drift to operators, and use reconciliation tooling to repair alignment |
| Stateless request path | A request omits `conversation_id` and therefore does not bind to conversation-scoped STM | Preserve single-turn operation by using a stateless path rather than forcing checkpoint-dependent behavior |
| Migration interruption or partial progress | A migration or repair operation stops mid-run due to interruption or failure | Preserve non-destructive, resumable behavior with dry-run support so operators can recover without data loss |

##### 4.7.3.3 Interface and Streaming Scenarios

| Scenario | Stimulus and Environment | Expected Architectural Response |
|----------|--------------------------|---------------------------------|
| Streaming pipeline failure | An error occurs after a streaming response has started | End the stream with a machine-detectable terminal error condition rather than leaving the client with an indeterminate open channel |
| Client-initiated cancellation | A client cancels an in-progress streaming response | Stop further generation promptly and avoid continued background work for a cancelled response path |
| Transient upstream failure during active request | A retry-safe external failure occurs during generation or tool access | Preserve retry-safe or failover-safe behavior without corrupting conversation state or leaking partial invalid output as completed work |

##### 4.7.3.4 Prompt and Behavior Scenarios

| Scenario | Stimulus and Environment | Expected Architectural Response |
|----------|--------------------------|---------------------------------|
| Unmatched or ambiguous intent | A user query does not match a stronger domain route with sufficient confidence | Route to `GENERAL_CHAT` so the request remains serviceable rather than producing a routing failure |
| Guardrail violation candidate detected | Generated output appears to contain hype, manipulation, or missing uncertainty or attribution signals | Keep guardrail enforcement in the prompt and response-policy layer and emit violation metadata for traceability |
| Prompt asset parse or validation failure | A versioned prompt asset cannot be loaded or validated in the planned externalized prompt system | Load `_baseline.yaml` as the last-known-good prompt asset instead of blocking response generation entirely |

##### 4.7.3.5 Planned Retrieval and Asset-Dependency Scenarios

The following scenarios are architecture-relevant but remain future-state because the associated prompt-asset and retrieval layers are not yet fully implemented in the active runtime.

| Scenario | Stimulus and Environment | Expected Architectural Response |
|----------|--------------------------|---------------------------------|
| Vector-backed retrieval unavailable | A future LTM or RAG retrieval store is unavailable when retrieval-augmented behavior is expected | Degrade to a non-retrieval response path that continues to use available tools and prompt policy, while making reduced evidence coverage observable |
| Prompt experiment or version asset unavailable | A selected experimental or version-specific prompt asset cannot be resolved | Fall back to the baseline prompt path and preserve prompt-version traceability for operators |

##### 4.7.3.6 Performance and Availability Scenarios

| Scenario | Stimulus and Environment | Expected Architectural Response |
|----------|--------------------------|---------------------------------|
| Simple query under normal operating load | A price lookup or similar lightweight request is processed during steady-state operation | Preserve the architecture's low-latency path through routing, limited tool use, and bounded response generation |
| Multi-tool analytical query under normal operating load | A request requires multiple tool calls or a longer reasoning path | Preserve service availability while accepting a slower bounded path than lightweight requests |
| Sustained concurrent conversational load | Multiple active conversations and requests are processed concurrently | Preserve availability through independent service boundaries, cache support, and separation of API, agent, and persistence concerns |
| Partial observability degradation | Logging, metrics, or tracing coverage is reduced while the runtime remains healthy | Continue serving requests while keeping health and drift surfaces available so operators can detect reduced observability without mistaking it for full outage |

This view is architecture-level only. Runbook steps, CLI usage, monitoring dashboards, and operational procedures remain outside this document and belong in [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md) only where realization detail is needed, or in operational documentation such as [IaC/README.md](../../../IaC/README.md).

### 4.8 Prompt and Behavior View

#### 4.8.1 Current Behavior Contract

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

#### 4.8.2 Prompt Architecture View

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
| **ResponseGuardrailMiddleware** | Scan agent output for hype or manipulation language; verify source attribution and uncertainty disclosure; log violations | ADR-001 hard rules on behavior and evidence boundaries |

#### 4.8.3 Prompt Taxonomy and Skills Composition

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

#### 4.8.4 Prompt Observability View

| Trace Attribute | Source | Example Value |
|----------------|--------|---------------|
| `prompt.version` | PromptAssetLoader | `v1.2.0` |
| `prompt.route` | Semantic Router | `FUNDAMENTALS` |
| `prompt.experiment_id` | PromptAssembler | `exp-001` (or `null`) |
| `prompt.skills_active` | PromptAssembler | `['disclaimer', 'anti-hype', 'earnings-analysis']` |
| `guardrail.violations` | ResponseGuardrailMiddleware | `[]` or `['hype_language_detected']` |

---

## 5. Correspondences and Traceability

### 5.1 View-to-Document Correspondence

| Architecture View | Primary Companion Documents |
|-------------------|-----------------------------|
| Context and Boundary View | [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md), [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md) |
| Logical View | [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md), [ADR-AGENT-001-LAYERED-LLM-ARCHITECTURE.md](./decisions/ADR-AGENT-001-LAYERED-LLM-ARCHITECTURE.md) |
| Process View | [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md), [AGENT_MEMORY_TECHNICAL_DESIGN.md](./AGENT_MEMORY_TECHNICAL_DESIGN.md) |
| Information and State View | [AGENT_MEMORY_TECHNICAL_DESIGN.md](./AGENT_MEMORY_TECHNICAL_DESIGN.md), [ADR-AGENT-001-LAYERED-LLM-ARCHITECTURE.md](./decisions/ADR-AGENT-001-LAYERED-LLM-ARCHITECTURE.md) |
| Development View | [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md), [README.md](../../../README.md) |
| Deployment View | [IaC/README.md](../../../IaC/README.md), [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md) |
| Operations and Maintenance View | [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md), [IaC/README.md](../../../IaC/README.md) |
| Prompt and Behavior View | [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](./PROMPT_SYSTEM_RESEARCH_PROPOSAL.md), [ADR-AGENT-002-SKILLS-PATTERN-PROMPT-COMPOSITION.md](./decisions/ADR-AGENT-002-SKILLS-PATTERN-PROMPT-COMPOSITION.md), [ADR-AGENT-003-EXTERNALIZE-VERSION-PROMPT-ASSETS.md](./decisions/ADR-AGENT-003-EXTERNALIZE-VERSION-PROMPT-ASSETS.md) |

### 5.2 Concern-to-Decision Correspondence

| Concern | Governing Decision / Artifact |
|---------|-------------------------------|
| Layered LLM boundaries and memory scope | [ADR-AGENT-001-LAYERED-LLM-ARCHITECTURE.md](./decisions/ADR-AGENT-001-LAYERED-LLM-ARCHITECTURE.md) |
| Prompt skills composition | [ADR-AGENT-002-SKILLS-PATTERN-PROMPT-COMPOSITION.md](./decisions/ADR-AGENT-002-SKILLS-PATTERN-PROMPT-COMPOSITION.md) |
| Externalized prompt assets and prompt versioning | [ADR-AGENT-003-EXTERNALIZE-VERSION-PROMPT-ASSETS.md](./decisions/ADR-AGENT-003-EXTERNALIZE-VERSION-PROMPT-ASSETS.md) |
| Conversation hierarchy, checkpoints, and runtime reconciliation | [AGENT_MEMORY_TECHNICAL_DESIGN.md](./AGENT_MEMORY_TECHNICAL_DESIGN.md) |
| Prompt-system design research and rollout path | [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](./PROMPT_SYSTEM_RESEARCH_PROPOSAL.md) |

### 5.3 Terminology and Concept Evolution

| Original Concept (ADR-001 Prompt Compiler decision) | Evolved Realization (ADR-002, ADR-003) | Note |
|-------------------------------|----------------------------------------|------|
| Prompt Compiler | PromptAssetLoader → PromptAssembler → ResponseGuardrailMiddleware | The single-step compiler concept was elaborated into a three-layer architecture. See the ADR-001 Prompt Compiler decision and `TECHNICAL_DESIGN.md` for realization detail. |
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

#### 6.1.1 Architectural Hard Rules (from ADR-001 Hard Rules)

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
| 0.2 | 2026-05-05 | GitHub Copilot | Reframed the document around explicit ISO 42010 viewpoints versus views, added logical, process, development, deployment, and operations-and-maintenance coverage, and updated cross-document correspondences |
| 0.3 | 2026-05-05 | GitHub Copilot | Added a System Context subsection to the Context and Boundary View to make client, internal-service, LLM-provider, and market-data-provider boundaries explicit for security, compliance, and operations concerns |
| 0.4 | 2026-05-05 | GitHub Copilot | Added architecture-level quality attribute scenarios covering current failure, degradation, lifecycle, prompt, and planned retrieval cases under the Operations and Maintenance View |
| 0.5 | 2026-05-06 | GitHub Copilot | Migrated layered-boundary and state-versus-evidence allocation content out of ADR-001 into architecture views and replaced stale section-number references with concept-based citations |
