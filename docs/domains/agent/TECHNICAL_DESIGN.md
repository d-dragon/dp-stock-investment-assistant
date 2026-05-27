# Agent Domain — Technical Design

> **Status**: Scaffolded from current agent architecture material and ready for iterative refinement.
> **Standards Stance**: Aligned design practice
> **Technology Stack**: LangGraph 0.2.62+, LangChain, OpenAI SDK, semantic-router, MongoDB, Redis
> **Companion Documents**: [ARCHITECTURE_DESIGN.md](./ARCHITECTURE_DESIGN.md), [AGENT_MEMORY_TECHNICAL_DESIGN.md](./AGENT_MEMORY_TECHNICAL_DESIGN.md), [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md](./PROMPT_SYSTEM_RESEARCH_PROPOSAL.md), [ADR-AGENT-001-LAYERED-LLM-ARCHITECTURE.md](./decisions/ADR-AGENT-001-LAYERED-LLM-ARCHITECTURE.md), [ADR-AGENT-002-SKILLS-PATTERN-PROMPT-COMPOSITION.md](./decisions/ADR-AGENT-002-SKILLS-PATTERN-PROMPT-COMPOSITION.md), [ADR-AGENT-003-EXTERNALIZE-VERSION-PROMPT-ASSETS.md](./decisions/ADR-AGENT-003-EXTERNALIZE-VERSION-PROMPT-ASSETS.md)

## Document Control

| Field | Value |
|-------|-------|
| Project | DP Stock Investment Assistant |
| Domain | Agent |
| Focus | Technical realization of the LangChain ReAct agent domain, including orchestration, memory, prompt composition, and fallback behavior |
| Date | 2026-05-27 |
| Status | Active working scaffold |
| Audience | Engineering, architecture, agent maintainers, and reviewers |

## Purpose

Explains how the agent domain realizes allocated requirements and architecture decisions. This document preserves implementation-oriented material extracted from the current architecture description so that the architecture document can focus on viewpoint-governed views while this document holds realization detail.

The corresponding architecture views for context and boundary, logical structure, process flow, information and state, development, deployment, operations and maintenance, and prompt behavior are defined in [ARCHITECTURE_DESIGN.md](./ARCHITECTURE_DESIGN.md). This document complements those views by describing how the codebase realizes them, rather than restating the architecture-level framing.

## 1. Domain Scope and Boundaries

### 1.1 Scope

This document covers the technical realization of:

- ReAct agent orchestration
- Tool registration and execution
- Model selection and provider fallback
- Conversation-scoped STM and checkpointing
- Prompt composition and prompt asset evolution
- Runtime interaction flows, configuration, and extension points

### 1.2 Out of Scope

This document does not replace:

- The ADR set for architectural decisions and trade-offs
- SRS documents for requirement authority
- Operations/runbook documents for deployment procedures
- Testing strategy documents for cross-repository verification policy

## 2. Realization Overview

The StockAssistantAgent is a LangChain-based ReAct agent designed for stock investment assistance. It orchestrates AI model providers and specialized tools to answer user queries about stock prices, technical analysis, and investment research.

### 2.1 Key Characteristics

| Aspect | Description |
|--------|-------------|
| Architecture | ReAct pattern with tool orchestration |
| AI Framework | LangChain >=1.0.0 with `langchain_core` and `langchain_openai` |
| Model Providers | OpenAI (GPT-5-nano), Grok (grok-4-1-fast-reasoning) with automatic fallback |
| Tool System | Registry-based with caching support |
| Memory | Service-owned session context and lifecycle metadata, LangGraph `MongoDBSaver` for conversation-scoped STM, and a planned future LTM personalization boundary |
| Semantic Router | `semantic-router` library with OpenAI/HuggingFace encoders |
| Response Types | Structured (`AgentResponse`) with immutable dataclasses |

### 2.2 Source Layout

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
├── analysis_prompt.j2
├── generic_query.j2
├── system_stock_assistant-vn.txt
└── system_stock_assistant.txt
```

### 2.3 Prompt Asset Mapping (Current vs Planned)

| View | Prompt Asset Model | Status |
|------|--------------------|--------|
| Current runtime layout | Template/text assets under `src/prompts/` | Implemented |
| ADR taxonomy target (canonical) | Shallow metadata-driven layout under `src/prompts/system/`, `src/prompts/skills/`, and `src/prompts/experiments/` with files such as `system/react_analyst.md`, `system/react_analyst.vi.md`, `skills/routes/price_check.md`, and `experiments/react_analyst.evidence_strict.md` | Proposed |

The technical design treats ADR taxonomy as canonical for prompt assets. Planning-artifact path aliases are non-authoritative and must map back to ADR taxonomy paths.

The planned structure stays intentionally shallow. Asset class is conveyed by directory, while version, locale, variant, activation mode, and baseline fallback semantics are resolved through metadata and loader policy rather than deeper directory nesting.

## 3. Core Realization

### 3.1 Agent Runtime and Orchestration

#### StockAssistantAgent

**Location**: `src/core/stock_assistant_agent.py`

**Responsibilities**:

1. Initialize ReAct agent with enabled tools and optional checkpointer
2. Process queries via LangGraph or legacy path
3. Support streaming with `astream_events()`
4. Handle provider fallback orchestration
5. Expose model configuration APIs
6. Manage conversation-aware STM routing via `conversation_id`; parent session context is handled outside the agent in service and management layers

**Key Methods**:

| Method | Description |
|--------|-------------|
| `process_query(query, *, conversation_id)` | Synchronous query processing with optional conversation-scoped memory |
| `process_query_streaming(query, *, conversation_id)` | Generator-based streaming with optional conversation-scoped memory |
| `process_query_structured(query, *, conversation_id)` | Returns `AgentResponse` with metadata |
| `set_default_model(provider, name)` | Update active model |
| `run_interactive()` | CLI REPL mode |

**Constructor behavior**:

The constructor accepts an optional `checkpointer` parameter injected by `APIServer`. When a checkpointer is present and `conversation_id` is provided, the agent includes `{"configurable": {"thread_id": conversation_id}}` in the invoke config so LangGraph automatically loads and saves conversation state.

**Hierarchy behavior**:

- LangGraph checkpoints store thread-specific reasoning state without leaking STM across sibling conversations.
- Conversation lifecycle metadata, archive status, and per-turn counters remain outside the checkpoint store in service and repository surfaces.
- The REST chat path uses `ChatService` to reject archived conversations and record per-turn metadata non-blocking.
- The Socket.IO path validates `conversation_id` and preserves it through to the agent, but currently bypasses `ChatService` lifecycle and metadata helpers.
- Workspace/session/conversation ownership and lifecycle validation live in the management APIs and services, not inside `StockAssistantAgent` itself.
- Session-context resolution helpers exist in `ChatService` and `ConversationService`; merged context is resolved at query time in service helpers, but prompt-level injection of that merged context is still follow-up work.

#### 3.1.1 Mirror — Component Interface Diagram

This realization-oriented mirror corresponds to the architecture-level interface diagrams in [ARCHITECTURE_DESIGN.md](./ARCHITECTURE_DESIGN.md) section 4.1.1a and section 4.2.2a. It deliberately reuses the same canonical interface vocabulary, then ties each architectural interface to the concrete routes, protocols, factories, registries, and state adapters that realize it in the current codebase.

```mermaid
flowchart LR
	Client["Client Apps\n(Web, Browser, API Consumers)"] -->|"client transport interface"| Entry["API Routes / Socket.IO"]
	Entry -->|"request orchestration interface"| Orchestration["ChatService / ConversationService"]
	Orchestration -->|"agent execution interface"| Agent["StockAssistantAgent"]
	Orchestration -->|"conversation lifecycle interface"| StateSvc["ConversationProvider + SessionProvider"]
	Orchestration -->|"metadata persistence interface"| Repo["ConversationRepository"]
	Agent -->|"intent classification interface"| Router["stock_query_router"]
	Agent -->|"behavioral policy interface"| Prompt["Current system prompt / planned prompt compiler"]
	Agent -->|"provider selection interface"| Factory["ModelClientFactory"]
	Agent -->|"tool invocation interface"| Tools["ToolRegistry + Tools"]
	Agent -->|"conversational state interface"| Checkpoint["MongoDBSaver"]
	Tools -->|"cache interaction interface"| Cache["Redis / CacheBackend"]
	Tools -->|"market data integration interface"| MarketData["DataManager\n(Yahoo Finance)"]
	Factory -->|"model inference interface"| Providers["OpenAIModelClient / GrokModelClient"]
```

The current realization of those canonical interfaces is:

| Canonical Interface Name | Realization Path in Current Code | Primary Anchors |
|--------------------------|----------------------------------|-----------------|
| Client transport interface | User traffic enters through HTTP and Socket.IO entry points, with request-body validation and conversation identifier normalization at the transport edge | `src/web/routes/ai_chat_routes.py`, `src/web/sockets/chat_events.py` |
| Request orchestration interface | The REST transport edge dispatches into `ChatService` for non-streaming and SSE paths, preserving transport-mode handling outside the agent runtime; the Socket.IO path currently implements a thinner passthrough and does not yet have full orchestration parity | `create_chat_blueprint()`, `ChatService.process_chat_query()`, `ChatService.stream_chat_response()`, `register_chat_events()` |
| Agent execution interface | `ChatService` depends on the `AgentProvider` protocol and delegates query execution and model-info lookup through that contract | `src/services/protocols.py`, `ChatService`, `StockAssistantAgent.process_query*()` |
| Conversation lifecycle interface | Service-layer logic checks archive status, ensures conversation existence, resolves parent session context, and records message metadata outside the agent runtime; this boundary is fully realized on the REST path and remains a known parity gap on Socket.IO | `ConversationProvider`, `SessionProvider`, `_validate_conversation_active()`, `_ensure_conversation_exists()`, `_record_message_metadata()`, `_load_conversation_context()` |
| Metadata persistence interface | Conversation-management metadata is persisted through service and repository paths rather than through the LangGraph checkpoint store | `ConversationService`, `ConversationRepository`, service-factory wiring |
| Intent classification interface | The runtime consults `stock_query_router` as the query classification boundary, keeping intent selection separate from provider binding and tool execution | `src/core/stock_query_router.py`, runtime routing flow |
| Behavioral policy interface | The active runtime passes a built-in system prompt into agent construction; the explicit `PromptAssetLoader -> PromptAssembler -> ResponseGuardrailMiddleware` boundary remains planned | `StockAssistantAgent.REACT_SYSTEM_PROMPT`, `create_agent(... system_prompt=...)`, planned prompt components in section 3.5 |
| Provider selection interface | The runtime uses `ModelClientFactory` to resolve provider/model clients and fallback ordering without embedding provider construction logic into route or service code | `ModelClientFactory.get_client()`, `ModelClientFactory.get_fallback_sequence()`, `StockAssistantAgent._select_client()` |
| Tool invocation interface | The runtime materializes enabled tools from `ToolRegistry`, then passes that governed tool surface into the LangGraph ReAct agent | `get_tool_registry()`, `ToolRegistry.get_enabled_tools()`, `StockAssistantAgent._initialize_tools()`, `_build_agent_executor()` |
| Conversational state interface | `APIServer` injects the LangGraph checkpointer, and the runtime binds `conversation_id` into `configurable.thread_id` during invoke so checkpoints stay conversation-scoped | `create_checkpointer()`, `APIServer.__init__()`, `process_query_structured()`, `_process_with_react()` / streaming invoke path |
| Cache interaction interface | Cache-aware tools delegate lookup and write-through behavior to `CacheBackend` and Redis without making cache state part of the agent-facing reasoning contract | `CachingTool`, `CacheBackend`, `StockSymbolTool`, `ReportingTool` |
| Market data integration interface | Tool implementations invoke `DataManager` as the outbound data-access boundary to Yahoo Finance, keeping all market data retrieval behind the tooling surface | `src/core/data_manager.py`, `DataManager`, `StockSymbolTool` |
| Model inference interface | Provider-specific client classes encapsulate the outbound call contract to OpenAI or Grok once the factory has selected the provider/model binding | `OpenAIModelClient`, `GrokModelClient`, `BaseModelClient` |

Current transport note: the REST path fully realizes the request-orchestration and conversation-lifecycle interfaces through `ChatService`, while the Socket.IO path currently realizes client transport plus direct agent invocation with UUID validation only.

This split keeps the architecture package disciplined. The architecture description names the architectural boundaries and their ownership, while this technical view records the concrete adapters, protocol contracts, and call sites that currently realize those interfaces.

### 3.2 Tool Registry and Tool Execution

#### CachingTool Base Class

**Location**: `src/core/tools/base.py`

**Responsibilities**:

1. Extend LangChain's `BaseTool` with caching
2. Generate deterministic cache keys
3. Track execution metrics
4. Provide health check interface

**Key Features**:

```python
class CachingTool(BaseTool):
    cache_ttl_seconds: int = 60
    enable_cache: bool = True

    def _run(self, **kwargs) -> Any:
        result, was_cached = self._cached_run(**kwargs)
        return result

    def _cached_run(self, **kwargs) -> tuple[Any, bool]:
        cache_key = self._generate_cache_key(**kwargs)
        if cached := self._cache.get_json(cache_key):
            return cached, True
        result = self._execute(**kwargs)
        self._cache.set_json(cache_key, result, ttl_seconds=self.cache_ttl_seconds)
        return result, False
```

#### StockSymbolTool

**Location**: `src/core/tools/stock_symbol.py`

**Actions**:

- `get_info`: Retrieve stock price and metadata
- `search`: Search symbols by name pattern

**Data Sources**:

1. **DataManager** (Yahoo Finance) - Live price data
2. **SymbolRepository** (MongoDB) - Symbol metadata fallback

**Caching Strategy**:

- TTL: 60 seconds (default)
- Cache key: `tool:stock_symbol:<md5_hash>`

#### ToolRegistry

**Location**: `src/core/tools/registry.py`

| Method | Description |
|--------|-------------|
| `register(tool, enabled=True)` | Add tool to registry |
| `unregister(name)` | Remove tool |
| `get(name)` | Get tool by name |
| `get_enabled_tools()` | List enabled tools |
| `set_enabled(name, bool)` | Toggle tool state |
| `health_check()` | Aggregate tool health |

#### Tool Risk Realization

The runtime should expose tool risk as first-class control metadata so prompt policy, tool guardrails, and future approval hooks share one vocabulary instead of ad hoc per-tool assumptions.

| Risk Class | Current Technical Meaning | Registry / Runtime Requirement | Current Status |
|------------|---------------------------|-------------------------------|----------------|
| `read_only_evidence` | Fetches data without mutating durable state | Registry records class; runtime validates arguments and preserves provenance in traces | Supported target for current baseline |
| `bounded_transformation` | Computes or reformats governed inputs without mutating durable state | Registry records class; runtime validates input and output schema before results re-enter prompt assembly | Supported target for current baseline |
| `workflow_mutation` | Changes repo-owned or user-owned durable state | Requires service-owned authorization, approval-capable workflow hooks, and audit metadata before enablement | Future only |
| `external_side_effect` | Writes to third-party systems or triggers real-world actions | Requires explicit allowlisting, human approval, and fail-closed defaults before enablement | Not admitted in the current baseline |

Runtime rules:

1. `ToolRegistry.get_enabled_tools()` should filter by both enablement and the strongest risk class admitted by the selected prompt asset.
2. Prompt-facing tool policy may narrow exposure but must not reclassify a tool below the registry-declared risk class.
3. Any runtime path that exercises a class above `bounded_transformation` must emit approval-state and `tool_risk_class` metadata for tracing and audit.

### 3.3 Memory Architecture and Lifecycle

#### Short-Term Memory (STM) via LangGraph Checkpointer

**Decision in force**: Use LangGraph's `MongoDBSaver` checkpointer for conversation-scoped STM persistence, with `conversation_id -> thread_id` as the canonical memory mapping and service-owned session context retained as reusable parent business context.

**Status**: Implemented in the current runtime. Conversation-scoped checkpoints, management APIs, reconciliation tooling, and legacy-thread migration tooling are live on this branch.

**Reference model in force**:

- Session context remains a service-owned parent business context boundary rather than a memory tier.
- STM remains the implemented conversation-scoped, checkpoint-managed runtime state surface.
- Future LTM remains a planned cross-conversation personalization boundary only.
- RAG and tools remain evidence and computation surfaces rather than extensions of STM or LTM.

**Key Design Choices**:

| Aspect | Decision |
|--------|----------|
| Checkpointer | LangGraph `MongoDBSaver` — native integration with agent execution |
| Thread ID Mapping | Direct 1:1: `conversation_id` → `thread_id` |
| Hierarchy Model | `workspace -> session -> conversation`, where the session owns reusable business context and the conversation owns STM |
| Dual Collections | `agent_checkpoints` (LangGraph-owned runtime state) + `conversations` (app-managed lifecycle metadata) |
| Backward Compatibility | `conversation_id` is optional — omitting preserves stateless single-turn behavior |
| Memory Scope | Stores conversation text only; never stores prices, ratios, or tool outputs |
| Current lifecycle behavior | `active` and `archived` are current-state service controls; `summarized` remains schema-supported but not universally active runtime flow |
| Transport parity | REST uses `ChatService` lifecycle and metadata helpers; Socket.IO currently bypasses them |
| Session-context timing | Resolved at query time in service helpers via conversation-to-session lookup; not yet injected into the prompt path |
| Future LTM boundary | Planned cross-conversation personalization only; separate from session context, STM, and RAG |
| Configuration | `MemoryConfig` frozen dataclass with 9 configurable parameters and fail-fast validation |

**Architecture Note**:

The canonical runtime contract is now `conversation_id` across agent methods, REST chat, management APIs, repositories, reconciliation, and migration tooling. The REST `POST /api/chat` route still accepts a deprecated `session_id` alias and normalizes it into `conversation_id` before validation; the Socket.IO handler accepts `conversation_id` only.

#### 3.3.1 STM Store Boundaries and Authority

The current runtime keeps checkpoint state and business metadata in separate stores on purpose.

| Concern | Authoritative Surface | Supporting Surface | Current Behavior |
|---------|-----------------------|--------------------|------------------|
| Recoverable conversation execution state | `agent_checkpoints` via LangGraph `MongoDBSaver` | `conversation_id -> thread_id` mapping from app surfaces | The runtime binds `conversation_id` into `configurable.thread_id` and lets LangGraph load and save thread state |
| Archive status, ownership, and per-turn metadata | `conversations` plus service-layer helpers | Checkpoints may indirectly reflect message history only | Archive guards and metadata recording live outside the checkpoint store |
| Reusable parent business context | Session service plus conversation-linked `session_id` | Conversation `context_overrides` | `ChatService._load_conversation_context()` resolves merged context at query time |
| Stateless fallback | No STM store required | None | Requests without `conversation_id` preserve the single-turn path |

This split means the stores may diverge temporarily without collapsing into one source of truth. A metadata record may exist even when checkpoint persistence is unavailable, and a checkpoint may exist before metadata has been ensured. In those cases the service layer remains authoritative for ownership and lifecycle, while checkpoints remain authoritative only for recoverable thread-local reasoning state.

#### 3.3.2 Current Runtime Caveats

- The REST route is the only chat path that currently realizes archive guards, `ensure_conversation_exists()`, metadata sync, and session-context lookup through `ChatService`.
- The Socket.IO handler validates `conversation_id` and passes it to `agent.process_query(...)`, but it does not yet call the lifecycle and metadata helpers used by REST.
- `MemoryConfig` exposes `summarize_threshold`, `max_messages`, and related limits, but the chat execution path does not yet trigger automatic summarization when those thresholds are exceeded.
- The REST route still accepts deprecated `session_id` only as an alias normalized into `conversation_id` before validation.

**Wiring Flow**:

```mermaid
flowchart TD
	API["APIServer.__init__()"]
	CreateCheckpointer["create_checkpointer(config) -> MongoDBSaver | None"]
	AgentInit["StockAssistantAgent(config, data_manager, checkpointer=checkpointer)"]
	CreateAgent["create_agent(..., checkpointer=checkpointer)"]
	Invoke["invoke(messages, config={configurable: {thread_id: conversation_id}})"]

	API --> CreateCheckpointer
	API --> AgentInit --> CreateAgent --> Invoke
```

**Detailed Design**: [AGENT_MEMORY_TECHNICAL_DESIGN.md](./AGENT_MEMORY_TECHNICAL_DESIGN.md)

### 3.4 Model Selection, Routing, and Fallback

#### ModelClientFactory

**Decision**: Use `ModelClientFactory` with caching for model client instantiation.

```python
class ModelClientFactory:
		_CACHE: Dict[str, BaseModelClient] = {}
```

**Rationale**:

- Single responsibility: Factory handles creation logic, clients handle generation
- Lazy instantiation: Clients created on-demand, not at startup
- Cache efficiency: Prevents redundant API client initialization
- Provider agnostic: Uniform interface regardless of OpenAI, Grok, or future providers

#### Semantic Router for Query Classification

**Decision**: Use `semantic-router` with OpenAI embeddings and HuggingFace fallback for intent classification.

**Route Categories**:

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

**Configuration**:

```yaml
semantic_router:
	encoder:
		primary: openai
		fallback: huggingface
		openai_model: "text-embedding-3-small"
		huggingface_model: "sentence-transformers/all-MiniLM-L6-v2"
	threshold: 0.7
	cache_embeddings: true
```

#### Retrieval-Augmented Generation Realization

> **Status:** Planned architecture with partial evidence support today via tool paths; intent-specific retrieval indices are not yet fully implemented in the active runtime.

The layered architecture treats retrieval as a distinct evidence path rather than as an extension of memory. In realization terms, this means route classification determines which evidence sources are eligible for a request and keeps retrieved source material separate from LTM, STM, and prompt-policy assets.

| Intent Family | Retrieval Focus | Expected Freshness Profile |
|---------------|-----------------|----------------------------|
| `FUNDAMENTALS` | Filings, financial statements, and valuation-supporting evidence | Medium-lived; refreshed around reporting cycles |
| `NEWS_ANALYSIS` | Press releases, headlines, and event-driven evidence | Short-lived; refreshed frequently |
| `MARKET_WATCH` | Macro, sector, and index context | Medium-lived; refreshed on market cadence |
| `TECHNICAL_ANALYSIS` | Indicator-supporting data and chart-derived context | Near-real-time or recent-window bias |

This design preserves two technical invariants from ADR-001: retrieved evidence is sourced and attributable, and any interpretation produced from that evidence remains in the model output rather than being written back into memory as domain truth.

#### Immutable Response Types

**Decision**: Use frozen dataclasses for all response types.

```python
@dataclass(frozen=True)
class AgentResponse:
		content: str
		provider: str
		model: str
		status: ResponseStatus = ResponseStatus.SUCCESS
		tool_calls: tuple[ToolCall, ...] = field(default_factory=tuple)
		token_usage: TokenUsage = field(default_factory=TokenUsage)
```

#### Dual Execution Mode (ReAct + Legacy Fallback)

**Decision**: Maintain legacy processing path as fallback.

```python
def process_query(
		self,
		query: str,
		*,
		provider: Optional[str] = None,
		conversation_id: Optional[str] = None,
) -> str:
		try:
				if self._agent_executor:
						return self._process_with_react(
								query,
								provider=provider,
								conversation_id=conversation_id,
						)
				return self._process_legacy(query, provider=provider)
		except Exception as e:
				self.logger.error(f"Error generating response: {e}")
				return f"Sorry, I encountered an error: {e}"
```

### 3.5 Prompt Realization and Guardrails

> **Status:** Planned realization path.
> **Decision coupling:** This section reflects the prompt-system direction proposed in the companion research document and the prompt-related ADRs.

The prompt system should evolve from one governed runtime prompt into a structured realization path that externalizes prompt assets, composes route-aware behavior deterministically, and keeps response-policy enforcement visible. This section therefore emphasizes the technical-design views needed for implementation and review: realization stack, component interfaces, request flow, data flow, runtime contracts, degradation behavior, and control-plane configuration.

| Concern family | Primary authority | Use this section for |
|----------------|-------------------|----------------------|
| Boundary, precedence, and component ownership | [ARCHITECTURE_DESIGN.md §4.8 Prompt and Behavior View](./ARCHITECTURE_DESIGN.md#48-prompt-and-behavior-view), [ADR-AGENT-001-LAYERED-LLM-ARCHITECTURE.md](./decisions/ADR-AGENT-001-LAYERED-LLM-ARCHITECTURE.md), [ADR-AGENT-002-SKILLS-PATTERN-PROMPT-COMPOSITION.md](./decisions/ADR-AGENT-002-SKILLS-PATTERN-PROMPT-COMPOSITION.md), [ADR-AGENT-003-EXTERNALIZE-VERSION-PROMPT-ASSETS.md](./decisions/ADR-AGENT-003-EXTERNALIZE-VERSION-PROMPT-ASSETS.md) | Realization views that stay inside the architecture boundary rather than redefining it |
| Requirements, rollout gates, and release controls | [SOFTWARE_REQUIREMENTS_SPECIFICATION.md §FR-1.4 System Prompt](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-14-system-prompt), [SOFTWARE_REQUIREMENTS_SPECIFICATION.md §NFR-5: Observability](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md#nfr-5-observability), [SOFTWARE_REQUIREMENTS_SPECIFICATION.md §AC-8: Prompt System](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md#ac-8-prompt-system), [PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md §2A.2 Prompt Compiler Path & Controlled Rollout](./PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#22-prompt-compiler-path--controlled-rollout) | Mapping technical contracts, diagrams, and residual rules back to FR, NFR, AC, and rollout controls |
| Design rationale, benchmark alignment, and sync | [PROMPT_SYSTEM_RESEARCH_PROPOSAL.md §Target Prompt System Architecture](./PROMPT_SYSTEM_RESEARCH_PROPOSAL.md#target-prompt-system-architecture), [PROMPT_SYSTEM_BENCHMARK_REVIEW.md §4.3 Guardrails Belong at Boundaries](./PROMPT_SYSTEM_BENCHMARK_REVIEW.md#43-guardrails-belong-at-boundaries), [SRS_SPEC_TRACEABILITY.md §Reverse Trace](./SRS_SPEC_TRACEABILITY.md#reverse-trace) | Checking whether the realization stays aligned with the target design, benchmark guidance, and post-change traceability duties |

The following planned stack shows which runtime technologies realize the prompt control plane, orchestration loop, and observability boundary.

```mermaid
flowchart LR
	subgraph Control["Prompt control plane [Planned]"]
		Assets["Prompt assets\nsystem | skills | experiments"]
		Manifest["Manifest + review state"]
		Config["prompts.* config"]
	end
	subgraph Runtime["Request runtime"]
		Router["Route classification"]
		Loader["PromptAssetLoader"]
		Assembler["PromptAssembler"]
		Agent["LangGraph + LangChain agent loop"]
		Guard["ResponseGuardrailMiddleware"]
		Surface["REST / SSE / Socket.IO surface"]
	end
	subgraph StateObs["State and observability"]
		STM["LangGraph checkpoint / STM boundary"]
		Tools["Tool and retrieval layer"]
		Trace["LangSmith traces + prompt metadata"]
	end
	Model["Model providers\nOpenAI | Grok | future providers"]

	Assets --> Loader
	Manifest --> Loader
	Config --> Loader
	Router --> Loader
	Loader --> Assembler
	STM --> Assembler
	Tools --> Assembler
	Assembler --> Agent
	Model --> Agent
	Agent --> Guard
	Guard --> Surface
	Loader -.-> Trace
	Assembler -.-> Trace
	Guard -.-> Trace
	Surface -.-> Trace
```

The current baseline remains relevant only to explain the transition into the planned target design. It should not be read as evidence that the prompt compiler path, rollout controls, or prompt-governance verification model are already fully implemented.

#### 3.5.1 Current Baseline and Transition Direction

The current baseline is one centrally managed runtime prompt contract supported by prompt assets under `src/prompts/`. The planned prompt system does not replace that baseline with an unrelated design; it formalizes it into explicit technical boundaries for asset resolution, prompt assembly, and guardrail enforcement.

For technical design purposes, the key transition is:

- from one centrally managed prompt contract to versioned prompt assets;
- from implicit behavior shaping to explicit composition rules;
- from broad prompt changes to bounded route-aware prompt context via the Skills pattern; and
- from opaque prompt behavior to attributable prompt metadata and guardrail outcomes.

#### 3.5.2 Planned Prompt Compiler Path

The planned prompt compiler path remains `PromptAssetLoader -> PromptAssembler -> ResponseGuardrailMiddleware`. The following views explain the interfaces, call flow, and request-scoped data movement for that path.

##### 3.5.2.1 Component Boundaries and Interfaces

The following component diagram shows the planned service interfaces and the runtime contracts that move between them.

```mermaid
classDiagram
	class PromptAssetLoader {
		<<Service>>
		+select(requestEnvelope) PromptSelection
	}
	class PromptAssembler {
		<<Service>>
		+compile(selection, runtimeContext) CompiledPrompt
	}
	class ResponseGuardrailMiddleware {
		<<Service>>
		+finalize(compiledPrompt, modelDraft) GuardrailResult
	}
	class PromptSelection {
		<<Contract>>
		+selected_assets
		+prompt_version
		+prompt_variant
		+locale
		+parity_group
		+selection_mode
		+fallback_used
		+degraded_reason
		+tool_risk_ceiling
		+output_contract_id
		+trace_metadata
	}
	class CompiledPrompt {
		<<Contract>>
		+segment_manifest
		+dropped_dynamic_fields
		+tool_policy_snapshot
		+prompt_metadata
	}
	class GuardrailResult {
		<<Contract>>
		+status
		+triggered_rules
		+response_contract_status
		+rewrite_applied
		+user_visible_action
		+trace_metadata
	}

	PromptAssetLoader --> PromptSelection : emits
	PromptSelection --> PromptAssembler : input
	PromptAssembler --> CompiledPrompt : emits
	CompiledPrompt --> ResponseGuardrailMiddleware : input
	ResponseGuardrailMiddleware --> GuardrailResult : emits
```

| Component | Primary interface | Must not own |
|-----------|-------------------|--------------|
| `PromptAssetLoader` | `select(requestEnvelope) -> PromptSelection` | Route classification, prompt concatenation, tool execution, or model invocation |
| `PromptAssembler` | `compile(selection, runtimeContext) -> CompiledPrompt` | Asset approval, route reclassification, tool-authorization policy, or response disposition |
| `ResponseGuardrailMiddleware` | `finalize(compiledPrompt, modelDraft) -> GuardrailResult` | Prompt assembly, retrieval, tool execution, or request-level policy selection |

##### 3.5.2.2 PromptAssetLoader Realization Contract

- The selection tuple remains explicit: `agent_role`, `route`, `locale`, `selection_mode`, `requested_version`, `prompt_experiment_id`, `workspace_mode`, and `env`. Hidden global switching should not bypass this tuple.
- Asset admissibility should come only from asset frontmatter, the canonical manifest, review state, and baseline-lineage metadata.
- Failure remains fail-closed: missing manifest rows, malformed frontmatter, review-state rejection, or unresolved lineage should fall back to approved baseline lineage when available; otherwise the loader emits a controlled degraded selection outcome rather than passing unknown assets downstream.

##### 3.5.2.3 PromptAssembler Realization Contract

- `PromptAssembler` admits only `PromptSelection`, normalized route result, approved dynamic controls, bounded memory summary, evidence bundles, and output-contract requirements.
- Assembly remains deterministic in this order: shared policy -> always-active skills -> route-specific skill -> bounded memory context -> evidence and tool-derived facts -> task framing -> output contract.
- If route skills are missing or dynamic fields are rejected, the assembler continues with approved inputs only, records the gaps in metadata, and never synthesizes substitute instructions.

##### 3.5.2.4 ResponseGuardrailMiddleware Realization Contract

- The middleware executes after model generation and before any response is committed to a non-streaming or streaming surface.
- The ordered check sequence remains: output-contract completeness, evidence attribution, uncertainty and disclosure, anti-hype controls, instruction-data separation, and tool-risk or approval consistency.
- `GuardrailResult.status` remains one of `pass`, `warn`, `block`, or `degraded`; the middleware is the final boundary check and must not act as a second orchestrator.

##### 3.5.2.5 Request-Scoped Call Flow

The following sequence shows how one request moves through selection, assembly, generation, and final response commitment.

```mermaid
sequenceDiagram
	autonumber
	participant Router as Route classification
	participant Loader as PromptAssetLoader
	participant Assembler as PromptAssembler
	participant Agent as Agent invocation
	participant Guard as ResponseGuardrailMiddleware
	participant Surface as Response surface
	participant Trace as LangSmith / trace sink

	Router->>Loader: selection envelope
	alt Preferred lineage admissible
		Loader-->>Assembler: PromptSelection(fallback_used=false)
	else Approved baseline fallback
		Loader-->>Assembler: PromptSelection(fallback_used=true, degraded_reason)
	end
	opt Route skill missing or dynamic fields rejected
		Assembler->>Trace: prompt_metadata + dropped_dynamic_fields
	end
	Assembler-->>Agent: CompiledPrompt(segment_manifest, tool_policy_snapshot)
	Agent-->>Guard: model draft + evidence map + tool summary
	alt GuardrailResult.status is pass or warn
		Guard-->>Surface: response or bounded rewrite + trace metadata
	else GuardrailResult.status is block or degraded
		Guard-->>Surface: safe refusal or conservative terminal response
		Guard-->>Trace: triggered_rules + degraded state
	end
	Surface-->>Trace: prompt_version + locale + route + guardrail_outcome
```

##### 3.5.2.6 Data Flow and Request-Scoped Inputs

The following data-flow view separates control components from the request-scoped payloads they consume and emit.

```mermaid
flowchart LR
	Manifest[("Prompt manifest")]
	Assets[("Prompt assets")]
	Config[("prompts.* config")]
	Memory["Bounded memory summary"]
	Evidence["Evidence bundles"]
	Contract["Output contract"]
	Trace[("Prompt trace metadata")]

	Manifest --> Loader["PromptAssetLoader"]
	Assets --> Loader
	Config --> Loader
	Loader -->|PromptSelection| Assembler["PromptAssembler"]
	Memory --> Assembler
	Evidence --> Assembler
	Contract --> Assembler
	Assembler -->|CompiledPrompt + segment_manifest| Agent["Agent invocation"]
	Agent -->|model draft + tool summary| Guard["ResponseGuardrailMiddleware"]
	Guard -->|GuardrailResult| Surface["Response surface"]
	Loader -.-> Trace
	Assembler -.-> Trace
	Guard -.-> Trace
	Surface -.-> Trace
```

#### 3.5.3 Prompt Asset Model and Composition Rules

The planned asset taxonomy stays shallow: `system`, `skills`, and `experiments`, with baseline fallback governed by metadata rather than deep directory layout. The following composition view shows the deterministic layering rule that drives assembly.

```mermaid
flowchart TB
	Shared["1. Shared policy + investment-safety rules"]
	Always["2. Always-active behavioral skills"]
	Route["3. Route-specific skill"]
	Memory["4. Bounded memory context"]
	Evidence["5. Retrieved evidence + tool-derived facts"]
	Task["6. Task framing"]
	Output["7. Output contract"]
	Shared --> Always --> Route --> Memory --> Evidence --> Task --> Output
```

- Higher-authority policy wins from top to bottom in this stack.
- Baseline fallback remains a lineage rule carried by metadata and loader policy.
- The output contract may shape structure, but it must not override earlier policy or evidence constraints.

#### 3.5.4 Static and Dynamic Segment Realization

`PromptAssembler` should classify every fragment before provider invocation so caching, reuse, and authority treatment remain deterministic.

```mermaid
flowchart TD
	Start["Prompt fragment enters assembler"] --> Policy{"Approved instruction-bearing asset?"}
	Policy -->|Yes| Static["Static policy fragment\ncache by approved lineage only"]
	Policy -->|No| Dynamic{"Schema-approved request control?"}
	Dynamic -->|Yes| Control["Dynamic control fragment\nrequest-scoped by default"]
	Dynamic -->|No| Evidence["Runtime evidence payload\ndata-only context"]
	Control --> Reuse{"Safe and explicit reuse?"}
	Reuse -->|Yes| Limited["Equivalent-only reuse"]
	Reuse -->|No| Request["Rebuild per request"]
```

- Static policy fragments are keyed by approved prompt lineage only.
- Dynamic controls are admitted only from schema-approved request fields and are request-scoped unless explicit equivalence is safe.
- Runtime evidence remains data-only context and must never be promoted into instruction-bearing policy.
- If fragment classification is ambiguous, the safer implementation default is request-scoped data rather than static policy.

#### 3.5.5 Locale Parity and Variant Realization

The following logical model shows how approved lineages, locale variants, selections, compiled prompts, and guardrail outcomes relate in the planned runtime.

```mermaid
erDiagram
	PROMPT_LINEAGE ||--|{ PROMPT_ASSET : governs
	PARITY_GROUP ||--|{ PROMPT_ASSET : groups
	PROMPT_SELECTION }|--|{ PROMPT_ASSET : selects
	PROMPT_SELECTION ||--|| COMPILED_PROMPT : compiles_to
	COMPILED_PROMPT ||--|| GUARDRAIL_RESULT : finalizes_as

	PROMPT_LINEAGE {
		string lineage_id PK
		string baseline_lineage_id FK
		string review_state
	}
	PARITY_GROUP {
		string parity_group PK
		string default_locale
	}
	PROMPT_ASSET {
		string asset_id PK
		string version
		string variant
		string locale
	}
	PROMPT_SELECTION {
		string selection_mode
		boolean fallback_used
		string degraded_reason
	}
	COMPILED_PROMPT {
		string output_contract_id
		string prompt_metadata_ref
	}
	GUARDRAIL_RESULT {
		string status
		string triggered_rules
	}
```

- Locale resolution should use `asset_id`, `locale`, and `parity_group` together rather than treating locale files as isolated prompt families.
- Non-default locale variants remain `forced`-only until parity evaluation and locale-competent review are complete.
- Missing, malformed, or parity-blocked variants fall back to the configured default locale with explicit degradation metadata.

#### 3.5.6 Near-Term Skills Pattern and Future Expansion

The near-term specialization path remains the Skills pattern: one agent, one shared policy layer, and route-aware prompt context selected from the existing route taxonomy. Multi-agent routing and retrieval-specialist prompt families remain later evolutions only when contracts materially diverge.

| Route | Canonical route skill |
|-------|-----------------------|
| `PRICE_CHECK` | `skills/routes/price_check.md` |
| `NEWS_ANALYSIS` | `skills/routes/news_analysis.md` |
| `PORTFOLIO` | `skills/routes/portfolio.md` |
| `TECHNICAL_ANALYSIS` | `skills/routes/technical_analysis.md` |
| `FUNDAMENTALS` | `skills/routes/fundamentals.md` |
| `IDEAS` | `skills/routes/ideas.md` |
| `MARKET_WATCH` | `skills/routes/market_watch.md` |
| `GENERAL_CHAT` | `skills/routes/general_chat.md` |

Each route skill inherits shared policy and always-on skills so specialization narrows behavior without redefining common investment-safety or output-contract obligations.

#### 3.5.7 Prompt Observability and Fault Tolerance

Prompt behavior should remain observable runtime metadata rather than hidden implicit state. The minimum metadata families are:

- prompt identity: `prompt_version`, `prompt_variant`, `prompt_locale`, `parity_group`;
- request classification: selected route, role, skills, and effective tool-risk class; and
- outcome metadata: `fallback_used`, `degraded_reason`, and final `guardrail_outcome`.

The following planned flow shows how preferred selection, locale fallback, route-skill degradation, and final guardrail outcomes converge on traceable response states.

```mermaid
flowchart TD
	Preferred{"Preferred lineage admissible?"}
	Preferred -->|Yes| Locale{"Locale variant admissible?"}
	Preferred -->|No| Baseline{"Approved baseline lineage?"}
	Baseline -->|Yes| Locale
	Baseline -->|No| Conservative["Conservative degraded path\ntrace fallback failure"]
	Locale -->|Yes| Skill{"Route-specific skill available?"}
	Locale -->|No| DefaultLocale["Default locale fallback\ntrace locale degradation"]
	DefaultLocale --> Skill
	Skill -->|Yes| Guardrail{"Guardrail result"}
	Skill -->|No| SharedOnly["Shared-policy-only assembly\ntrace route-skill gap"]
	SharedOnly --> Guardrail
	Guardrail -->|pass / warn| Normal["Response + prompt metadata"]
	Guardrail -->|block / degraded| Conservative
```

When any planned prompt-governance surface changes, this section should be synchronized with [SRS_SPEC_TRACEABILITY.md §Reverse Trace](./SRS_SPEC_TRACEABILITY.md#reverse-trace) and the post-delivery synchronization duties in [spec-kit HOW-TO.md §3.3.5 Synchronization and Maintenance](../../spec-driven%20development%20%28SDD%29/spec-kit%20HOW-TO.md#335-synchronization-and-maintenance).

#### 3.5.7.1 Streaming Guardrail and Terminal Behavior

> **Status:** Planned streaming realization only. This subsection defines the target streaming boundary and does not claim full current-runtime parity across all response surfaces.

Streaming reuses the same guardrail rule set and `GuardrailResult` vocabulary as the non-streaming path. The streaming specialization is temporal rather than policy-specific: emission windows, blocker timing, cancellation semantics, and terminal framing.

- Partial output may be emitted only after local admission checks pass for the current emission window.
- Later blocker detection stops further emission immediately and forces a safe terminal action rather than an implied completed answer.
- Cancellation must be recorded as cancelled rather than completed.
- A success-complete marker must never be emitted before final guardrail commitment.

The following state flow shows how buffering, checkpoint evaluation, cancellation, and terminal behavior should work on streaming surfaces.

```mermaid
stateDiagram-v2
	[*] --> Generating
	Generating --> Buffered : draft tokens available
	Buffered --> Checkpoint : emission window closes
	Checkpoint --> Emitting : local admission passes
	Checkpoint --> SafeTerminal : block or degraded terminal path
	Emitting --> Buffered : more draft content
	Emitting --> FinalCheck : model completes
	Generating --> Cancelled : client cancellation
	Buffered --> Cancelled : client cancellation
	FinalCheck --> Completed : pass or warn with bounded rewrite
	FinalCheck --> SafeTerminal : block or degraded final check
	Cancelled --> [*]
	Completed --> [*]
	SafeTerminal --> [*]
```

#### 3.5.8 Prompt-System Config Surface

> **Status:** Planned control-plane surface only. The current runtime configuration is transitioning toward this shape; this subsection defines the target localized `prompts.*` design surface.

The following namespace map shows how the planned prompt control plane is grouped and which components each namespace governs.

```mermaid
flowchart LR
	subgraph Registry["prompts.registry"]
		Dir["directory"]
		Man["manifest"]
		Refresh["refresh_window_seconds"]
	end
	subgraph AgentCfg["prompts.agents.{role}"]
		Version["baseline_asset_id + active_version"]
		Mode["selection_mode + output_contract_id"]
		RouteMap["route_skill_map"]
	end
	subgraph Controls["prompts.dynamic_controls"]
		Allow["allowed_fields"]
		Reject["reject_unknown_fields"]
	end
	subgraph GuardCfg["prompts.guardrails + prompts.streaming"]
		GuardKeys["blocking + rewrite policy"]
		StreamKeys["checkpoint + terminal behavior"]
	end
	subgraph Policy["prompts.locale + prompts.selection + prompts.trace + prompts.cache"]
		Locale["default_locale + fallback_behavior"]
		Rollout["fixed | forced | shadow | weighted"]
		TraceFields["required_fields"]
		Cache["static segment cache"]
	end

	Registry --> Loader["PromptAssetLoader"]
	AgentCfg --> Loader
	AgentCfg --> Assembler["PromptAssembler"]
	Controls --> Assembler
	GuardCfg --> Guard["ResponseGuardrailMiddleware"]
	Policy --> Loader
	Policy --> Assembler
	Policy --> Guard
```

| Namespace family | Key responsibilities | Fail-closed note |
|------------------|----------------------|------------------|
| `prompts.registry` | Directory, manifest, refresh window, manifest validation behavior | Manifest or lineage errors must not widen selection authority |
| `prompts.agents.{role}` and `prompts.dynamic_controls` | Role defaults, active version, selection mode, output contract, route skills, allowed request controls | Unknown or out-of-policy dynamic fields are dropped and traced |
| `prompts.guardrails` and `prompts.streaming` | Blocking policy, bounded rewrite policy, checkpoint timing, cancellation handling, terminal behavior | Streaming completion requires final guardrail commitment |
| `prompts.locale`, `prompts.selection`, `prompts.trace`, and `prompts.cache` | Locale fallback, rollout mode, mandatory trace fields, static-segment reuse | Missing mandatory trace fields block promotion to wider rollout |

Supported selection modes remain `fixed`, `forced`, `shadow`, and `weighted`, aligned directly with the roadmap and SRS vocabulary.

#### 3.5.9 Component-Level Verification Matrix

This section defines the minimum component-level verification surface implied by the planned prompt compiler path. It states what must be proven for readiness and promotion; it does not prescribe the concrete test harness or repository-specific automation. Detailed verification execution remains governed by [SOFTWARE_REQUIREMENTS_SPECIFICATION.md §AC-8: Prompt System](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md#ac-8-prompt-system), [SOFTWARE_REQUIREMENTS_SPECIFICATION.md §NFR-5: Observability](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md#nfr-5-observability), and [VERIFICATION_AND_TRACEABILITY_STRATEGY.md](../../testing/VERIFICATION_AND_TRACEABILITY_STRATEGY.md).

| Component or slice | Planned scenario | Expected outcome | Required emitted metadata or evidence | Governing authority | Verification level |
|--------------------|------------------|------------------|---------------------------------------|---------------------|--------------------|
| `PromptAssetLoader` | Preferred asset version is unavailable, withdrawn, or fails manifest validation | Baseline lineage is selected instead of empty prompt resolution; fallback remains attributable | `prompt_version`, `prompt_variant=baseline`, `fallback_used=true`, `degraded_reason` | [SOFTWARE_REQUIREMENTS_SPECIFICATION.md §FR-1.4 System Prompt](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-14-system-prompt) with FR-1.4.8 and FR-1.4.13 | Component contract |
| `PromptAssetLoader` | Requested locale variant is missing or parity-blocked | Configured default locale is selected and locale degradation remains visible | `prompt_locale`, `parity_group`, `fallback_used`, `degraded_reason` | [SOFTWARE_REQUIREMENTS_SPECIFICATION.md §FR-1.4 System Prompt](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-14-system-prompt) with FR-1.4.15 and [SOFTWARE_REQUIREMENTS_SPECIFICATION.md §NFR-5: Observability](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md#nfr-5-observability) | Component contract |
| `PromptAssembler` | Request includes unknown or unapproved dynamic control fields | Unknown fields are dropped, recorded, and not elevated into policy segments | `dropped_dynamic_fields`, `segment_manifest`, request-to-segment classification evidence | [SOFTWARE_REQUIREMENTS_SPECIFICATION.md §FR-1.4 System Prompt](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-14-system-prompt) with FR-1.4.7 and FR-1.4.16, plus [SOFTWARE_REQUIREMENTS_SPECIFICATION.md §AC-8: Prompt System](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md#ac-8-prompt-system) | Component contract |
| `PromptAssembler` | Route-specific skill cannot be resolved for the classified route | Shared policy plus role contract still compile; route-specific degradation remains traceable | `route`, `selected_skills`, `fallback_used` or `degraded_reason`, `prompt_metadata` | [SOFTWARE_REQUIREMENTS_SPECIFICATION.md §FR-1.4 System Prompt](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-14-system-prompt) with FR-1.4.7 and FR-1.4.8 | Component contract |
| `PromptAssembler` | Bounded memory summary is included during assembly | Memory context remains a data-bearing runtime-evidence segment rather than policy text | `segment_manifest`, memory-summary classification evidence, prompt lineage preserved independently of memory content | [AGENT_MEMORY_TECHNICAL_DESIGN.md](./AGENT_MEMORY_TECHNICAL_DESIGN.md) and [SOFTWARE_REQUIREMENTS_SPECIFICATION.md §FR-1.4 System Prompt](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-14-system-prompt) with FR-1.4.16 | Component contract |
| `ResponseGuardrailMiddleware` | Output contract is incomplete or required disclosures are missing | Final response is blocked or conservatively rewritten before any completed-answer state is recorded | `status`, `triggered_rules`, `response_contract_status`, `user_visible_action` | [SOFTWARE_REQUIREMENTS_SPECIFICATION.md §FR-1.5 Finance-Domain Behavioral Guardrails](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-15-finance-domain-behavioral-guardrails) with FR-1.5.6, plus [SOFTWARE_REQUIREMENTS_SPECIFICATION.md §AC-8: Prompt System](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md#ac-8-prompt-system) | Component contract |
| `ResponseGuardrailMiddleware` | Anti-hype, unsupported certainty, instruction-data separation, or tool-risk inconsistencies are detected | The middleware emits `warn`, `block`, or `degraded` exactly as required by the rule class and preserves rule identifiers through any rewrite | `status`, `triggered_rules`, `rewrite_applied`, `trace_metadata` | [PROMPT_SYSTEM_BENCHMARK_REVIEW.md §4.3 Guardrails Belong at Boundaries](./PROMPT_SYSTEM_BENCHMARK_REVIEW.md#43-guardrails-belong-at-boundaries), [SOFTWARE_REQUIREMENTS_SPECIFICATION.md §FR-1.5 Finance-Domain Behavioral Guardrails](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-15-finance-domain-behavioral-guardrails), and [SOFTWARE_REQUIREMENTS_SPECIFICATION.md §AC-8: Prompt System](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md#ac-8-prompt-system) | Component contract |
| Cross-component streaming path | A blocker is detected after partial buffering has begun | No further chunks are admitted, a safe terminal frame or equivalent action is emitted, and the stream is not marked complete | `guardrail_outcome`, `triggered_rules`, `stream_terminal_reason`, `prompt_version`, `fallback_used` | [ARCHITECTURE_DESIGN.md §4.8.4 Guardrail Boundary Model](./ARCHITECTURE_DESIGN.md#484-guardrail-boundary-model), [ARCHITECTURE_DESIGN.md §4.8.7 Prompt Observability and Degraded Modes](./ARCHITECTURE_DESIGN.md#487-prompt-observability-and-degraded-modes), and [SOFTWARE_REQUIREMENTS_SPECIFICATION.md §FR-1.5 Finance-Domain Behavioral Guardrails](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-15-finance-domain-behavioral-guardrails) | Integration slice |
| Cross-component streaming path | Client cancellation occurs before final guardrail commitment | Generation stops, cancellation is attributed, and no terminal success marker is emitted | `cancelled=true`, `stream_terminal_reason=client_cancelled`, request-level prompt identity metadata | [ARCHITECTURE_DESIGN.md §4.8.7 Prompt Observability and Degraded Modes](./ARCHITECTURE_DESIGN.md#487-prompt-observability-and-degraded-modes) and [SOFTWARE_REQUIREMENTS_SPECIFICATION.md §NFR-5: Observability](./SOFTWARE_REQUIREMENTS_SPECIFICATION.md#nfr-5-observability) | Integration slice |

Interpret this matrix as the minimum design-level verification contract:

1. Each component row must be provable before the corresponding prompt compiler slice is considered ready for broader rollout.
2. Streaming-path rows are required before user-visible streaming prompt behavior is treated as promotion-ready.
3. Missing mandatory prompt identity, fallback, locale, or guardrail metadata is a verification failure even when the text output appears acceptable.
4. Release-gate evidence should be collected in the repository verification and traceability workflow rather than duplicated as a test procedure in this document.

### 3.6 Fine-Tuning Realization

> **Status:** Planned realization only; fine-tuning is not yet implemented in the current runtime.

ADR-001 constrains fine-tuning to reasoning structure and tone, not knowledge storage. The technical realization of that constraint should keep fine-tuning datasets narrow, human-verified, and explicitly separated from dynamic market facts.

| In Scope for Fine-Tuning | Out of Scope for Fine-Tuning |
|--------------------------|------------------------------|
| Earnings summary structure | Valuation logic as source of truth |
| Risk-framing patterns | Price targets and forecasts |
| Scenario-table formatting | Macro outlook as durable knowledge |
| Consistent disclosure tone | Invented numbers or unsupported claims |

Implementation-oriented safeguards:

- Training examples should contain human-verified outputs only.
- Numerical claims should remain runtime-injected from tools or retrieval, not baked into training data as durable facts.
- Evaluation should check formatting consistency, uncertainty disclosure, and unsupported-claim rates before any rollout.

### 3.7 Example Reasoning Flow

The following walkthrough preserves the layered contract in a concrete engineering form without making the ADR carry the worked example. It represents the target layered flow while keeping current-runtime caveats explicit: service-owned session context and STM are available today, while future LTM enrichment remains optional follow-up work rather than an active runtime dependency.

```mermaid
flowchart TD
	Q["User: \"Danh gia HSG trung han\""] --> SessionNode["Resolve service-owned session context\nrisk profile: moderate\ntime horizon: 6-18 months"]
	SessionNode --> STMNode["Load STM and conversation-scoped assumptions\ncurrent thread hypothesis: steel price bottoming"]
	STMNode --> RouteNode["Route classification\nroute: FUNDAMENTALS"]
	RouteNode --> Evidence["Retrieve evidence\ncompany financials + relevant steel-price context"]
	Evidence --> Assemble["Assemble prompt\nbase rules + skills + memory context + evidence + output contract"]
	Assemble --> Response["Generate response\nstructured reasoning with evidence-backed narrative"]
```

Future LTM, when introduced, should enrich the assembly step as optional cross-conversation personalization rather than replacing session context, STM, or evidence retrieval.

## 4. Engineering Constraints and Extension Paths

### 4.1 Tool and Reporting Enhancements

#### StockSymbolTool Enhancements

| Area | Current State | Proposed Improvement |
|------|---------------|---------------------|
| Data Sources | Yahoo Finance only | Add Alpha Vantage, Polygon.io |
| Actions | `get_info`, `search` | Add `get_historical`, `get_fundamentals`, `compare` |
| Caching | Fixed 60s TTL | Per-action configurable TTL |
| Error Handling | Generic fallback | Retry with exponential backoff |

#### TradingView Integration

**Current**: Placeholder with `NotImplementedError`

```python
class TradingViewTool(CachingTool):
		"""Phase 2: Full TradingView integration"""
```

#### Reporting Enhancements

| Area | Current State | Proposed Improvement |
|------|---------------|---------------------|
| Templates | Hardcoded markdown | Jinja2 template system |
| Report Types | Basic 3 types | Add earnings, comparison, sector |
| Output Formats | Markdown only | Add HTML, PDF export |
| Data Integration | Placeholder content | Real data from analysis services |

### 4.2 Routing, Output, and Prompt Evolution

#### Multi-Agent Orchestration

**Current**: Single ReAct agent handles all queries

**Proposed**: Specialized agents with routing

```mermaid
flowchart TD
	Orchestrator["Orchestrator Agent (Router)"]
	Price["Price Agent\n(fast queries)"]
	Analysis["Analysis Agent\n(technical)"]
	Research["Research Agent\n(deep analysis)"]

	Orchestrator --> Price
	Orchestrator --> Analysis
	Orchestrator --> Research
```

#### Structured Output Mode

```python
from langchain_core.output_parsers import JsonOutputParser

class StockPriceResponse(BaseModel):
		symbol: str
		current_price: float
		change_percent: float
		volume: int
		analysis: str

parser = JsonOutputParser(pydantic_object=StockPriceResponse)
```

#### Semantic Router Enhancements

| Area | Current State | Proposed Improvement |
|------|---------------|---------------------|
| Routes | 8 static categories | Dynamic route discovery from tools |
| Utterances | Hardcoded examples | ML-generated training data |
| Multi-language | English only | Vietnamese + English utterances |
| Confidence Calibration | Fixed 0.7 threshold | Per-route adaptive thresholds |
| Route Chaining | Single route per query | Multi-intent detection |

### 4.3 Performance, Observability, and Testing

#### Performance Optimizations

| Area | Current | Proposed |
|------|---------|----------|
| Caching | Per-tool Redis cache | Tiered cache (memory + Redis) |
| Async | Sync-to-async wrapper | Native async tool execution |
| Batching | Single symbol queries | Batch symbol lookup |
| Streaming | Event-based chunks | Token-level streaming |

#### Observability Improvements

| Area | Current | Proposed |
|------|---------|----------|
| Logging | Basic Python logging | Structured JSON logs |
| Metrics | None | Prometheus metrics endpoint |
| Tracing | None | OpenTelemetry integration |
| Dashboards | None | Grafana monitoring |

#### Testing Improvements

| Area | Current | Proposed |
|------|---------|----------|
| Unit Tests | Basic coverage | Mock all external APIs |
| Integration | Limited | Full agent → tool → data flow |
| E2E | None | Playwright/Selenium for UI |
| Performance | None | Locust load testing |

#### Mirror — Unified Degraded-Operation Diagram

This realization-oriented mirror corresponds to [ARCHITECTURE_DESIGN.md](./ARCHITECTURE_DESIGN.md) section 4.7.3.7.

```mermaid
flowchart TD
	Start["Inbound request"] --> Prompt{"Prompt asset load succeeds?"}
	Prompt -- "No" --> Baseline["Baseline prompt fallback"]
	Prompt -- "Yes" --> Checkpoint{"Checkpoint available?"}
	Checkpoint -- "No" --> Stateless["Stateless invocation path"]
	Checkpoint -- "Yes" --> Cache{"Cache available?"}
	Cache -- "No" --> Uncached["Uncached tool execution path"]
	Cache -- "Yes" --> Normal["Cached execution path"]
	Baseline --> Provider{"Primary provider succeeds?"}
	Stateless --> Provider
	Uncached --> Provider
	Normal --> Provider
	Provider -- "Yes" --> Success["Served response"]
	Provider -- "No" --> Fallback{"Fallback provider succeeds?"}
	Fallback -- "Yes" --> Degraded["Served degraded response"]
	Fallback -- "No" --> ControlledError["Controlled terminal error"]
```

### 4.4 Delivery Sequencing for Layered Runtime

The ADR decisions are realized in phases so memory, retrieval, prompt policy, and behavior shaping do not drift out of order.

| Phase | Realization Focus | Current State |
|------|--------------------|---------------|
| 1 | Conversation-scoped STM and checkpoint lifecycle | Implemented |
| 2 | Prompt externalization and composable skills | Planned |
| 3 | Intent-specific retrieval and evidence wiring | Planned / partial by tool path |
| 4 | Fine-tuning for structure and tone | Planned |
| 5 | Guardrail observability and experiment controls | Planned |

## 5. Supporting Patterns, Stacks, and Relationships

### 5.1 Design Patterns Used

| Pattern | Component | Purpose |
|---------|-----------|---------|
| **Factory** | `ModelClientFactory` | Create provider-specific clients |
| **Factory** | `create_checkpointer()` | Create MongoDBSaver or None based on config |
| **Singleton** | `ToolRegistry` | Centralized tool management |
| **Template Method** | `CachingTool._execute()` | Define tool execution skeleton |
| **Strategy** | `BaseModelClient` subclasses | Interchangeable model providers |
| **Adapter** | `langchain_adapter.py` | Bridge external prompts to LangChain |
| **Decorator** | `CachingTool._cached_run()` | Add caching to tool execution |
| **Registry** | `ToolRegistry` | Dynamic component registration |
| **Immutable Config** | `MemoryConfig` | Frozen dataclass with fail-fast validation |
| **Repository** | `ConversationRepository` | Data access for conversations collection |
| **Asset Loader** | `PromptAssetLoader` | Discover, validate, and cache versioned prompt files (planned) |
| **Composer** | `PromptAssembler` | Compose skills + base prompt by route classification (planned) |
| **Middleware** | `ResponseGuardrailMiddleware` | Post-process agent output for behavioral compliance (planned) |

### 5.2 Software Stack

#### Core Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| `langchain` | >=1.0.0 | Agent framework, tool definitions |
| `langchain_core` | >=0.3.28 | Base types (messages, prompts) |
| `langchain_openai` | >=0.3.5 | OpenAI ChatModel integration |
| `langgraph` | >=0.2.62 | LangGraph core for agent workflows |
| `langgraph-checkpoint` | >=2.0.9 | Checkpoint base interfaces |
| `langgraph-checkpoint-mongodb` | >=2.0.5 | MongoDB checkpointer for STM (FR-3.1) |
| `semantic-router` | >=0.1.0 | Query classification with embeddings |
| `pydantic` | 2.x | Data validation for tools |
| `openai` | 1.x | Direct API access for OpenAI |

#### Data Layer

| Library | Purpose |
|---------|---------|
| `yfinance` | Yahoo Finance data fetching |
| `pymongo` | MongoDB driver for symbol metadata |
| `redis` | Cache backend (via `CacheBackend`) |

#### Infrastructure

| Library | Purpose |
|---------|---------|
| `flask` | Web API framework |
| `flask_socketio` | Real-time streaming |
| `gunicorn` + `eventlet` | WSGI server with WebSocket |

### 5.3 Class Hierarchy

```text
BaseModelClient (ABC)
├── OpenAIModelClient
└── GrokModelClient

CachingTool (BaseTool)
├── StockSymbolTool
├── ReportingTool
└── TradingViewTool (placeholder)

AgentResponse (frozen dataclass)
├── .success() classmethod
├── .error() classmethod
└── .fallback() classmethod
```

### 5.4 Key File Relationships

```text
stock_assistant_agent.py
		imports: types.py (AgentResponse, ToolCall)
		imports: model_factory.py (ModelClientFactory)
		imports: langchain_adapter.py (build_prompt)
		imports: tools/registry.py (ToolRegistry)
		receives: checkpointer via constructor injection

langgraph_bootstrap.py
		imports: langgraph.checkpoint.mongodb (MongoDBSaver)
		imports: utils/memory_config.py (MemoryConfig)
		reads: config["database"]["mongodb"]["connection_string"]
		exports: create_checkpointer(), get_agent()

api_server.py
		imports: langgraph_bootstrap.py (create_checkpointer)
		wires: checkpointer → StockAssistantAgent constructor

conversation_repository.py
		extends: mongodb_repository.py (MongoGenericRepository)
		manages: conversations collection

chat_service.py
		uses: ConversationService + SessionService via protocols
		implements: archive guard, optional conversation auto-create, metadata recording

conversation_service.py
		uses: ConversationRepository
		implements: management ownership checks, archive/detail/list flows, metadata helpers

utils/memory_config.py
		defines: MemoryConfig (frozen dataclass, 9 parameters)
		defines: ContentValidator (FR-3.1.7/FR-3.1.8 compliance scanning)

stock_query_router.py
		imports: routes.py (ROUTE_UTTERANCES, RouteResult, StockQueryRoute)
		imports: semantic_router (Route, SemanticRouter)
		imports: semantic_router.encoders (OpenAIEncoder, HuggingFaceEncoder)
```

#### 5.4.1 Mirror — Dependency and Ownership Diagram

This realization-oriented mirror corresponds to [ARCHITECTURE_DESIGN.md](./ARCHITECTURE_DESIGN.md) section 4.2.3a.

```mermaid
flowchart TD
	Entry["Transport Entry\nAPI + Socket.IO"]
	Services["Service Ownership\nChatService + ConversationService"]
	Agent["Reasoning Runtime\nStockAssistantAgent"]
	Prompt["Prompt Policy Boundary\nLoader + Assembler + Guardrail"]
	Exec["Execution Boundary\nRouter + ModelFactory + Tools"]
	State["Persistence + Cache\nConversations + Checkpoints + Redis"]
	External["External Providers\nLLM + Market Data"]

	Entry --> Services --> Agent
	Agent --> Prompt
	Agent --> Exec
	Services --> State
	Agent --> State
	Exec --> External
```

## 6. Configuration and Reference Material

### 6.1 Configuration Reference

```yaml
model:
	provider: openai
	name: gpt-5-nano
	allow_fallback: true
	fallback_order:
		- openai
		- grok
	debug_prompt: false

openai:
	api_key: ${OPENAI_API_KEY}
	model: gpt-5-nano
	temperature: 0.7

grok:
	api_key: ${GROK_API_KEY}
	base_url: https://api.x.ai/v1
	model: grok-4-1-fast-reasoning

semantic_router:
	encoder:
		primary: openai
		fallback: huggingface
		openai_model: "text-embedding-3-small"
		huggingface_model: "sentence-transformers/all-MiniLM-L6-v2"
	threshold: 0.7
	cache_embeddings: true

langchain:
	tools:
		enabled: true
		cache_ttl:
			stock_symbol: 60
			reporting: 600
			tradingview: 300
			default: 120
	memory:
		enabled: true
		summarize_threshold: 4000
		max_messages: 50
		messages_to_keep: 10
		max_content_size: 32768
		summary_max_length: 500
		context_load_timeout_ms: 500
		state_save_timeout_ms: 50
		checkpoint_collection: "agent_checkpoints"
		conversations_collection: "conversations"
```

### 6.2 Type Definitions Quick Reference

```python
SUCCESS = "success"
FALLBACK = "fallback"
ERROR = "error"
PARTIAL = "partial"

AgentResponse.success(content, provider, model, **kwargs)
AgentResponse.error(message, provider, model)
AgentResponse.fallback(content, provider, model, **kwargs)
```

## 7. Revision History

| Version | Date | Author | Notes |
|---------|------|--------|-------|
| 0.0 | 2026-04-03 | GitHub Copilot | Skeleton created |
| 0.1 | 2026-04-16 | GitHub Copilot | Scaffolded from implementation-focused content formerly concentrated in `ARCHITECTURE_DESIGN.md` |
| 0.2 | 2026-04-16 | GitHub Copilot | Route taxonomy aligned to canonical `StockQueryRoute` enum from `src/core/routes.py` |
| 0.3 | 2026-05-06 | GitHub Copilot | Migrated realization-only material out of ADR-001: retrieval realization boundaries, prompt assembly order, fine-tuning realization, example reasoning flow, and layered runtime delivery sequencing |
| 0.4 | 2026-05-12 | GitHub Copilot | Aligned prompt taxonomy references to ADR-canonical paths (`src/prompts/system|skills|experiments`) and removed hybrid path language |
| 0.5 | 2026-05-19 | GitHub Copilot | Synchronized prompt-asset realization language with the simplified proposal layout by describing the ADR taxonomy as a shallow metadata-driven `system` / `skills` / `experiments` structure and replacing separate baseline-asset wording with metadata-governed fallback lineage |
| 0.6 | 2026-05-21 | GitHub Copilot | Added runtime tool-risk realization, static-versus-dynamic prompt segment handling, locale-parity selection rules, and observability metadata for locale and tool-risk governed prompt paths |
| 0.7 | 2026-05-27 | GitHub Copilot | Reframed section 3.5 as a realization-level traceability hub with explicit companion-document ownership, subsection-specific prompt-governance references, and synchronization guidance for reverse trace and Spec Kit workflow updates |
| 0.8 | 2026-05-27 | GitHub Copilot | Deepened section 3.5.2 with explicit planned component contracts, canonical route-to-skill mapping, and request-scoped prompt lifecycle and guardrail behavior |
| 0.9 | 2026-05-27 | GitHub Copilot | Added planned streaming guardrail behavior, localized `prompts.*` control-plane design, and a component-level verification matrix to section 3.5 |
| 0.10 | 2026-05-27 | GitHub Copilot | Simplified section 3.5 into diagram-first technical-design views for the prompt realization stack, component interfaces, call flow, data flow, logical model, degradation behavior, and config surface |
