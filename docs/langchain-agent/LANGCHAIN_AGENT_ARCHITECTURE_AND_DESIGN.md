# LangChain Agent Architecture Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architectural Decision and Design](#architectural-decision-and-design)
3. [Design Patterns and Software Stacks](#design-patterns-and-software-stacks)
4. [Component Deep Dive](#component-deep-dive)
5. [Data Flow and Interactions](#data-flow-and-interactions)
6. [Space for Improvements (Phase 2)](#space-for-improvements-phase-2)
7. [Appendix](#appendix)

---

## Overview

The **StockAssistantAgent** is a LangChain-based ReAct (Reasoning + Acting) agent designed for stock investment assistance. It orchestrates AI model providers and specialized tools to answer user queries about stock prices, technical analysis, and investment research.

### Key Characteristics

| Aspect | Description |
|--------|-------------|
| **Architecture** | ReAct pattern with tool orchestration |
| **AI Framework** | LangChain >=1.0.0 with `langchain_core` and `langchain_openai` |
| **Model Providers** | OpenAI (GPT-5-nano), Grok (grok-4-1-fast-reasoning) with automatic fallback |
| **Tool System** | Registry-based with caching support |
| **Memory** | LangGraph `MongoDBSaver` checkpointer for conversation-scoped STM, with sessions as reusable parent business context |
| **Semantic Router** | `semantic-router` library with OpenAI/HuggingFace encoders |
| **Response Types** | Structured (`AgentResponse`) with immutable dataclasses |

### File Structure

```
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
```

---

## Architectural Decision and Design

### 1. ReAct Pattern Selection

**Decision**: Use LangChain's ReAct (Reasoning + Acting) pattern over raw LLM calls.

**Implementation**: Uses `create_agent` from `langchain.agents` to build a `CompiledStateGraph`.

> **Migration Note (v1.0)**: Migrated from deprecated `langgraph.prebuilt.create_react_agent` to
> `langchain.agents.create_agent`. Key API change: `prompt=` parameter renamed to `system_prompt=`,
> and `name="stock_assistant"` added for subgraph compatibility.

**Rationale**:
- **Autonomous tool selection**: The agent decides which tools to invoke based on query semantics
- **Chain-of-thought reasoning**: Visible reasoning before actions improves transparency
- **Extensibility**: New tools can be added without modifying agent logic
- **Built-in error handling**: LangChain provides retry and fallback mechanisms

**Trade-offs**:
| Advantage | Disadvantage |
|-----------|--------------|
| Flexible tool orchestration | Higher latency (multiple LLM calls) |
| Transparent reasoning | More complex debugging |
| Easy extensibility | Dependency on LangChain framework |

### 2. Factory Pattern for Model Clients

**Decision**: Use `ModelClientFactory` with caching for model client instantiation.

**Implementation** (`src/core/model_factory.py`):
```python
class ModelClientFactory:
    _CACHE: Dict[str, BaseModelClient] = {}
    
    @staticmethod
    def get_client(config, *, provider=None, model_name=None) -> BaseModelClient:
        # Cache key: "provider:model_name"
        key = f"{provider_cfg}:{resolved_model_name or ''}"
        if key in ModelClientFactory._CACHE:
            return ModelClientFactory._CACHE[key]
        # Create and cache new client
```

**Rationale**:
- **Single responsibility**: Factory handles creation logic, clients handle generation
- **Lazy instantiation**: Clients created on-demand, not at startup
- **Cache efficiency**: Prevents redundant API client initialization
- **Provider agnostic**: Uniform interface regardless of OpenAI, Grok, or future providers

### 4. Singleton Tool Registry

**Decision**: Use singleton `ToolRegistry` for centralized tool management.

**Implementation** (`src/core/tools/registry.py`):
```python
_registry_instance: Optional["ToolRegistry"] = None

class ToolRegistry:
    @classmethod
    def get_instance(cls, logger=None) -> "ToolRegistry":
        global _registry_instance
        if _registry_instance is None:
            _registry_instance = cls(logger=logger)
        return _registry_instance
```

**Rationale**:
- **Global access**: All components access the same tool set
- **Dynamic registration**: Tools can be added/removed at runtime
- **Enable/disable support**: Tools can be toggled without unregistering
- **Health aggregation**: Single point for tool health checks

### 5. Semantic Router for Query Classification

**Decision**: Use `semantic-router` library with OpenAI embeddings (HuggingFace fallback) for intent classification.

**Implementation** (`src/core/stock_query_router.py`):
```python
class StockQueryRouter:
    """
    Semantic router for stock-related queries.
    Uses semantic similarity to classify queries into one of 8 route categories.
    """
    
    DEFAULT_THRESHOLD = 0.7
    DEFAULT_OPENAI_MODEL = "text-embedding-3-small"
    DEFAULT_HUGGINGFACE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    def route(self, query: str) -> RouteResult:
        """Classify a query into a stock query route."""
        result = self._router(query)
        return RouteResult(
            route=StockQueryRoute(result.name),
            confidence=result.similarity_score,
            query=query,
        )
```

**Route Categories** (`src/core/routes.py`):

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

**Encoder Fallback Strategy**:
```
1. Try OpenAI encoder (text-embedding-3-small)
   │
   ├─► Success: Use for all embeddings
   │
   └─► Failure: Log warning, fall back to HuggingFace
           │
           └─► Use HuggingFace (all-MiniLM-L6-v2)
```

**Configuration** (`config/config.yaml`):
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

**Rationale**:
- **Fast query classification**: Semantic similarity is faster than LLM-based routing
- **Extensible routes**: Add new route categories by updating `ROUTE_UTTERANCES`
- **Encoder resilience**: OpenAI primary with local HuggingFace fallback
- **Configurable threshold**: Tune confidence threshold per deployment

### 4. Immutable Response Types

**Decision**: Use frozen dataclasses for all response types.

**Implementation** (`src/core/types.py`):
```python
@dataclass(frozen=True)
class AgentResponse:
    content: str
    provider: str
    model: str
    status: ResponseStatus = ResponseStatus.SUCCESS
    tool_calls: tuple[ToolCall, ...] = field(default_factory=tuple)
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    ...
```

**Rationale**:
- **Thread safety**: Immutable objects can be shared across threads
- **Predictability**: Response data cannot be accidentally mutated
- **Clear contracts**: Dataclass defines explicit fields and types
- **Serialization**: `to_dict()` method provides JSON-safe output

### 5. Dual Execution Mode (ReAct + Legacy Fallback)

**Decision**: Maintain legacy processing path as fallback.

**Implementation**:
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

**Rationale**:
- **Graceful degradation**: If ReAct agent fails to build, legacy path works
- **Migration safety**: Allows gradual transition from old to new architecture
- **Testing isolation**: Legacy path can be tested independently

### 6. Short-Term Memory (STM) via LangGraph Checkpointer

**Decision**: Use LangGraph's `MongoDBSaver` checkpointer for conversation-scoped STM persistence, with `conversation_id -> thread_id` as the canonical memory mapping and sessions retained as parent workflow context.

**Status**: Implemented in the current runtime. Conversation-scoped checkpoints, management APIs, reconciliation tooling, and legacy-thread migration tooling are live on this branch.

**Key Design Choices**:

| Aspect | Decision |
|--------|----------|
| **Checkpointer** | LangGraph `MongoDBSaver` — native integration with agent execution |
| **Thread ID Mapping** | Direct 1:1: `conversation_id` → `thread_id` |
| **Hierarchy Model** | `workspace -> session -> conversation`, where the session owns reusable business context and the conversation owns STM |
| **Dual Collections** | `agent_checkpoints` (LangGraph-owned) + `conversations` (app-managed metadata) |
| **Backward Compatibility** | `conversation_id` is optional — omitting preserves stateless single-turn behavior |
| **Memory Scope** | Stores conversation text ONLY; never stores prices, ratios, or tool outputs (per ADR-001) |
| **Lifecycle** | `active` → `summarized` → `archived` (no hard delete per ADR-001) |
| **Configuration** | `MemoryConfig` frozen dataclass with 9 configurable parameters and fail-fast validation |

**Architecture Note**: The canonical runtime contract is now `conversation_id` across agent methods, REST chat, management APIs, repositories, reconciliation, and migration tooling. The REST `POST /api/chat` route still accepts a deprecated `session_id` alias and normalizes it into `conversation_id` before validation; the Socket.IO handler accepts `conversation_id` only. Session-context lookup helpers exist in the service layer, but that merged context is not yet injected into the agent prompt path.

**Wiring Flow**:
```
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

> **Detailed Design**: See [AGENT_MEMORY_TECHNICAL_DESIGN.md](./AGENT_MEMORY_TECHNICAL_DESIGN.md) for data models, sequence diagrams, API contracts, and configuration reference.

---

## Design Patterns and Software Stacks

### Design Patterns Used

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

### Software Stack

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

### Class Hierarchy

```
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

---

## Component Deep Dive

### StockAssistantAgent

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
|--------|------------|
| `process_query(query, *, conversation_id)` | Synchronous query processing with optional conversation-scoped memory |
| `process_query_streaming(query, *, conversation_id)` | Generator-based streaming with optional conversation-scoped memory |
| `process_query_structured(query, *, conversation_id)` | Returns `AgentResponse` with metadata |
| `set_default_model(provider, name)` | Update active model |
| `run_interactive()` | CLI REPL mode |

**Constructor** accepts an optional `checkpointer` parameter (injected by `APIServer`).
When a checkpointer is present and `conversation_id` is provided, the agent includes
`{"configurable": {"thread_id": conversation_id}}` in the invoke config, enabling
LangGraph to automatically load/save conversation state.

**Hierarchy Behavior**:
- Conversation state stores thread-specific checkpoints, message counters, and lifecycle metadata without leaking STM across sibling conversations.
- The REST chat path uses `ChatService` to reject archived conversations and record per-turn metadata non-blocking.
- Workspace/session/conversation ownership and lifecycle validation live in the management APIs and services, not inside `StockAssistantAgent` itself.
- Session-context resolution helpers exist in `ChatService` and `ConversationService`, but prompt-level injection of that merged context is still follow-up work.

**System Prompt**:
```
You are a professional stock investment assistant.
You help users with stock analysis, price lookups, technical analysis...

When answering questions:
1. Use the appropriate tools when you need real-time data
2. Provide accurate, factual information based on tool outputs
3. Include relevant disclaimers for investment-related advice
4. Be concise but comprehensive in your responses
```

### CachingTool Base Class

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
        # LangChain entry point
        result, was_cached = self._cached_run(**kwargs)
        return result
    
    def _cached_run(self, **kwargs) -> tuple[Any, bool]:
        cache_key = self._generate_cache_key(**kwargs)
        if cached := self._cache.get_json(cache_key):
            return cached, True
        result = self._execute(**kwargs)  # Subclass implements
        self._cache.set_json(cache_key, result, ttl_seconds=self.cache_ttl_seconds)
        return result, False
```

### StockSymbolTool

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

### ToolRegistry

**Location**: `src/core/tools/registry.py`

**API**:

| Method | Description |
|--------|-------------|
| `register(tool, enabled=True)` | Add tool to registry |
| `unregister(name)` | Remove tool |
| `get(name)` | Get tool by name |
| `get_enabled_tools()` | List enabled tools |
| `set_enabled(name, bool)` | Toggle tool state |
| `health_check()` | Aggregate tool health |

---

## Data Flow and Interactions

### Query Processing Flow

```
User Query
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│ StockAssistantAgent                                               │
│                                                                   │
│  ┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐  │
│  │ ReAct Agent ├───►│ Tool Selection   ├───►│ Tool Execution  │  │
│  │ (LangChain) │    │ (LLM Decision)   │    │ (CachingTool)   │  │
│  └─────────────┘    └──────────────────┘    └─────────────────┘  │
│         │                                          │              │
│         ▼                                          ▼              │
│  ┌─────────────┐                          ┌─────────────────┐    │
│  │ LLM Response │◄────────────────────────│  Tool Output    │    │
│  │ Generation   │                         │  (Cached/Fresh) │    │
│  └─────────────┘                          └─────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
AgentResponse (content, provider, model, tool_calls, token_usage)
```

### Model Client Selection

```
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

### Fallback Orchestration

```
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

---

## Space for Improvements (Phase 2)

### 1. StockSymbolTool Enhancements

| Area | Current State | Proposed Improvement |
|------|---------------|---------------------|
| **Data Sources** | Yahoo Finance only | Add Alpha Vantage, Polygon.io |
| **Actions** | `get_info`, `search` | Add `get_historical`, `get_fundamentals`, `compare` |
| **Caching** | Fixed 60s TTL | Per-action configurable TTL |
| **Error Handling** | Generic fallback | Retry with exponential backoff |

**Proposed New Actions**:
```python
# Phase 2 actions
actions = {
    "get_info": "Get current price and basic info",
    "search": "Search symbols by name",
    "get_historical": "Get OHLCV data for period",
    "get_fundamentals": "Get PE, EPS, dividends",
    "compare": "Compare multiple symbols",
    "get_news": "Get recent news for symbol",
}
```

### 2. TradingView Integration

**Current**: Placeholder with `NotImplementedError`

**Proposed Implementation**:

```python
class TradingViewTool(CachingTool):
    """Phase 2: Full TradingView integration"""
    
    WIDGET_TYPES = ["chart", "screener", "heatmap", "ticker_tape", "market_overview"]
    
    def _execute(self, **kwargs):
        action = kwargs.get("action")
        
        if action == "get_chart_url":
            return self._build_chart_url(kwargs)
        elif action == "get_widget":
            return self._generate_widget_config(kwargs)
        elif action == "get_analysis":
            return self._fetch_technical_analysis(kwargs)
```

**Widget Types to Support**:
- Advanced Chart (interactive)
- Mini Symbol Overview
- Ticker Tape (scrolling)
- Market Overview
- Screener Widget

### 3. Reporting Enhancements

| Area | Current State | Proposed Improvement |
|------|---------------|---------------------|
| **Templates** | Hardcoded markdown | Jinja2 template system |
| **Report Types** | Basic 3 types | Add earnings, comparison, sector |
| **Output Formats** | Markdown only | Add HTML, PDF export |
| **Data Integration** | Placeholder content | Real data from analysis services |

**Proposed Template System**:
```
src/templates/reports/
├── base.html.j2
├── symbol_analysis.html.j2
├── portfolio_overview.html.j2
├── market_summary.html.j2
├── earnings_calendar.html.j2
└── sector_comparison.html.j2
```

### 4. Agent Architecture Improvements

#### 4.1 Multi-Agent Orchestration

**Current**: Single ReAct agent handles all queries

**Proposed**: Specialized agents with routing

```
┌─────────────────────────────────────────────────────────────────┐
│ Orchestrator Agent (Router)                                     │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Price Agent     │  │ Analysis Agent  │  │ Research Agent  │ │
│  │ (fast queries)  │  │ (technical)     │  │ (deep analysis) │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

#### 4.2 Short-Term Memory (STM) — Implemented

**Status**: ✅ Conversation-scoped STM hierarchy implemented in the runtime; two follow-up gaps remain: automated summarization triggering and Socket.IO parity with the REST chat path.

**Implementation**: LangGraph `MongoDBSaver` checkpointer with conversation-scoped STM persistence, management APIs for workspace/session/conversation lifecycle, and operator tooling for reconciliation and legacy-checkpoint migration.

Each conversation owns its own checkpointer thread, while a session can contain multiple independent conversations under shared business context.
Stateful memory is controlled by `conversation_id` across `process_query()`, `process_query_streaming()`, `process_query_structured()`, REST API (`POST /api/chat`), and the management surface.
The REST chat route temporarily accepts `session_id` only as a deprecated alias normalized into `conversation_id`; the Socket.IO handler accepts `conversation_id` only and still takes the lighter direct-to-agent path.

**Key Components**:
- `langgraph_bootstrap.py::create_checkpointer()` — Factory for MongoDBSaver
- `utils/memory_config.py::MemoryConfig` — Immutable config with fail-fast validation
- `data/repositories/conversation_repository.py` — CRUD for `conversations` collection
- `services/conversation_service.py` — Lifecycle management, metadata helpers, management API ownership checks
- `services/chat_service.py` — REST chat orchestration, archive guard, non-blocking metadata recording
- `services/runtime_reconciliation_service.py` — Drift detection between conversation metadata and LangGraph checkpoint state

**Hierarchy Rules**:
- `conversation_id -> thread_id` is the canonical STM binding.
- A session can own multiple conversations; sibling conversations do not share checkpoints.
- Conversation metadata is stored separately from LangGraph checkpoints in the `conversations` collection.
- Session-context lookup and conversation override merging exist in service helpers, but the merged context is not yet injected into the agent prompt path.

**Remaining Future Work (Phase 2A.2+)**:
- Wire automated summarization triggers into the active chat execution path
- Route Socket.IO through `ChatService` or equivalent parity logic for archive guards and metadata sync
- Long-term vector store memory (semantic search over past conversations)
- Cross-session memory retrieval
- User preference learning (LTM personalization layer)

> **Detailed Design**: [AGENT_MEMORY_TECHNICAL_DESIGN.md](./AGENT_MEMORY_TECHNICAL_DESIGN.md)

#### 4.3 Structured Output Mode

**Current**: Unstructured text responses

**Proposed**: JSON schema enforcement

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

### 5. Semantic Router Enhancements

| Area | Current State | Proposed Improvement |
|------|---------------|---------------------|
| **Routes** | 8 static categories | Dynamic route discovery from tools |
| **Utterances** | Hardcoded examples | ML-generated training data |
| **Multi-language** | English only | Vietnamese + English utterances |
| **Confidence Calibration** | Fixed 0.7 threshold | Per-route adaptive thresholds |
| **Route Chaining** | Single route per query | Multi-intent detection |

**Proposed Enhancements**:

#### 5.1 Dynamic Route Discovery
```python
class DynamicStockQueryRouter(StockQueryRouter):
    """Auto-discover routes from registered tools."""
    
    def _build_routes_from_tools(self, registry: ToolRegistry) -> List[Route]:
        routes = []
        for tool in registry.get_enabled_tools():
            # Extract route utterances from tool docstring/metadata
            route = Route(
                name=tool.name,
                utterances=tool.example_queries,  # New tool attribute
            )
            routes.append(route)
        return routes
```

#### 5.2 Multi-Intent Detection
```python
def route_multi_intent(self, query: str) -> List[RouteResult]:
    """Detect multiple intents in a single query.
    
    Example: "Check AAPL price and show me the RSI"
    Returns: [PRICE_CHECK, TECHNICAL_ANALYSIS]
    """
    # Split complex queries into sub-queries
    sub_queries = self._split_query(query)
    return [self.route(sq) for sq in sub_queries]
```

#### 5.3 Adaptive Threshold
```python
# Per-route confidence thresholds
ROUTE_THRESHOLDS: Dict[StockQueryRoute, float] = {
    StockQueryRoute.PRICE_CHECK: 0.6,      # Lower - common queries
    StockQueryRoute.TECHNICAL_ANALYSIS: 0.75,  # Higher - specific intent
    StockQueryRoute.IDEAS: 0.8,            # Highest - avoid false positives
}
```

### 6. Performance Optimizations

| Area | Current | Proposed |
|------|---------|----------|
| **Caching** | Per-tool Redis cache | Tiered cache (memory + Redis) |
| **Async** | Sync-to-async wrapper | Native async tool execution |
| **Batching** | Single symbol queries | Batch symbol lookup |
| **Streaming** | Event-based chunks | Token-level streaming |

### 7. Observability Improvements

| Area | Current | Proposed |
|------|---------|----------|
| **Logging** | Basic Python logging | Structured JSON logs |
| **Metrics** | None | Prometheus metrics endpoint |
| **Tracing** | None | OpenTelemetry integration |
| **Dashboards** | None | Grafana monitoring |

**Proposed Metrics**:
```python
# Agent metrics
agent_query_duration_seconds = Histogram(...)
agent_tool_calls_total = Counter(...)
agent_fallback_total = Counter(...)
agent_cache_hits_total = Counter(...)
```

### 8. Testing Improvements

| Area | Current | Proposed |
|------|---------|----------|
| **Unit Tests** | Basic coverage | Mock all external APIs |
| **Integration** | Limited | Full agent → tool → data flow |
| **E2E** | None | Playwright/Selenium for UI |
| **Performance** | None | Locust load testing |

**Proposed Test Structure**:
```
tests/
├── unit/
│   ├── test_stock_symbol_tool.py
│   ├── test_tool_registry.py
│   └── test_model_factory.py
├── integration/
│   ├── test_agent_with_tools.py
│   └── test_streaming_flow.py
├── e2e/
│   └── test_chat_workflow.py
└── performance/
    └── test_agent_load.py
```

---

## Appendix

### A. Configuration Reference

```yaml
# config/config.yaml
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

database:
    mongodb:
        enabled: true
        connection_string: "mongodb://..."
        database_name: "stock_assistant"
```

### B. Type Definitions Quick Reference

```python
# ResponseStatus enum values
SUCCESS = "success"     # Primary model succeeded
FALLBACK = "fallback"   # Fallback model used
ERROR = "error"         # Complete failure
PARTIAL = "partial"     # Some tools failed

# AgentResponse factory methods
AgentResponse.success(content, provider, model, **kwargs)
AgentResponse.error(message, provider, model)
AgentResponse.fallback(content, provider, model, **kwargs)

# ToolCall attributes
name: str               # Tool name
input: Dict[str, Any]   # Input arguments
output: Any             # Execution result
cached: bool            # Was result cached?
execution_time_ms: float
```

### C. Key File Relationships

```
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
    
routes.py
    defines: StockQueryRoute (enum with 8 categories)
    defines: ROUTE_UTTERANCES (training data per route)
    defines: RouteResult (frozen dataclass)
    
tools/base.py
    extends: langchain_core.tools.BaseTool
    imports: types.py (ToolCall)
    imports: utils/cache.py (CacheBackend)
    
tools/stock_symbol.py
    extends: tools/base.py (CachingTool)
    imports: core/data_manager.py
    imports: data/repositories/symbol_repository.py
```

### D. Remaining Phase 2 Follow-Up Notes

1. **TradingView Tool**: Replace placeholder with full implementation
2. **Reporting Tool**: Integrate with Jinja2 template system
3. **StockSymbol Tool**: Add multi-source data providers
4. **Agent Memory Hierarchy**: Implemented for REST chat, management APIs, reconciliation, and migration tooling; remaining work is summarization triggering and Socket.IO parity
5. **Observability**: Integrate OpenTelemetry before production
6. **Long-Term Memory (LTM)**: Vector store for cross-session semantic recall (Phase 2A.2+)

---

**Document Version**: 2.2  
**Last Updated**: 2026-03-31  
**Author**: GitHub Copilot  
**Branch**: `stm-phase-cde`
