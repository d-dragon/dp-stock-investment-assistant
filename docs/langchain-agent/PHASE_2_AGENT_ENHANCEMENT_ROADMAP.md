# Phase 2: LangChain Agent Enhancement Roadmap

> **Document Version**: 1.0  
> **Created**: January 15, 2026  
> **Status**: Planning  
> **Branch**: `integrate-langsmith-studio`

## Executive Summary

This roadmap outlines the Phase 2 enhancements for the Stock Investment Assistant's LangChain agent. Building on the Phase 1 foundation (ReAct agent, CachingTool pattern, ToolRegistry, semantic routing), Phase 2 focuses on **memory persistence**, **production-ready tools**, **structured outputs**, and **multi-agent orchestration**.

### Phase Overview

| Phase | Focus Area | Key Deliverables |
|-------|------------|------------------|
| **2A** | Foundation | Long-term memory, prompt management, structured outputs |
| **2B** | Features | TradingView integration, enhanced semantic routing, multi-source data, reporting |
| **2C** | Advanced | Multi-agent orchestration, technical refinements |

---

## Phase 2A: Foundation Enhancements

### 2A.1 Long-Term Conversation Memory

**Objective**: Enable the agent to maintain conversation context across sessions using LangGraph's memory primitives and MongoDB persistence.

#### Current State

```
┌─────────────────────────────────────────────────────────────┐
│                    CURRENT: Stateless                       │
├─────────────────────────────────────────────────────────────┤
│  API Request                                                │
│      ↓                                                      │
│  agent.invoke({"messages": [HumanMessage(query)]})         │
│      ↓                                                      │
│  Response (no history retained)                             │
└─────────────────────────────────────────────────────────────┘
```

- Agent processes each query in isolation with single `HumanMessage`
- No `thread_id` passed to agent `invoke()` configuration
- No checkpointer configured in LangGraph
- MongoDB `chats` and `sessions` schemas exist but not connected to agent
- `ChatRepository.get_by_session()` methods available but unused

#### Target State

```
┌─────────────────────────────────────────────────────────────┐
│                    TARGET: Persistent Memory                │
├─────────────────────────────────────────────────────────────┤
│  API Request (with session_id)                              │
│      ↓                                                      │
│  ChatService (validates session, gets workspace context)    │
│      ↓                                                      │
│  agent.invoke(                                              │
│      {"messages": [HumanMessage(query)]},                   │
│      config={"configurable": {"thread_id": session_id}}    │
│  )                                                          │
│      ↓                                                      │
│  MongoDBSaver Checkpointer (auto-persists conversation)     │
│      ↓                                                      │
│  Response (with full history context)                       │
└─────────────────────────────────────────────────────────────┘
```

#### Work Items

1. **Add LangGraph Checkpointer Integration**
   - Install `langgraph-checkpoint-mongodb` package
   - Configure `MongoDBSaver` with existing MongoDB connection
   - Wire checkpointer into `StockAssistantAgent._build_agent_executor()`

2. **Implement Thread ID Flow**
   - Modify `ChatService` to pass `session_id` as `thread_id`
   - Update API routes to accept and propagate `session_id`
   - Update Socket.IO handlers for streaming with session context

3. **Add Memory Configuration**
   - Add memory settings to `config.yaml` (max messages, summarization threshold)
   - Implement conversation summarization for long threads
   - Add memory-aware system prompt section

4. **Cross-Thread Memory Store (Optional)**
   - Implement `InMemoryStore` or MongoDB-backed store for user facts
   - Enable agent to remember user preferences across sessions

#### Architecture Decision

> **Design Note**: Use LangGraph's `MongoDBSaver` for checkpointer integration (simpler, built-in support). Continue using existing `ChatRepository` for UI queries (chat history display, search). This dual approach leverages both LangGraph's memory primitives and existing repository patterns.

#### Implementation Pattern

```python
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain_core.messages import HumanMessage

# In StockAssistantAgent.__init__()
self.checkpointer = MongoDBSaver(
    connection_string=config["mongodb"]["uri"],
    db_name=config["mongodb"]["database"],
    collection_name="agent_checkpoints"
)

# In _build_agent_executor()
self.agent_executor = create_react_agent(
    model=self.model,
    tools=self.tools,
    checkpointer=self.checkpointer  # Add checkpointer
)

# In process_query()
def process_query(self, query: str, session_id: str) -> AgentResponse:
    config = {"configurable": {"thread_id": session_id}}
    result = self.agent_executor.invoke(
        {"messages": [HumanMessage(content=query)]},
        config=config
    )
    return self._build_response(result)
```

#### Dependencies

- `langgraph-checkpoint-mongodb` package
- MongoDB connection (existing)
- Session management service (existing `ChatService`)

#### Success Criteria

- Agent recalls previous conversation turns within same session
- Conversation state persists across API restarts
- Memory does not degrade response latency by >100ms
- LangSmith traces show message history in context

---

### 2A.2 System Prompt Refinement & A/B Testing

**Objective**: Externalize system prompts to files, enable version control, and support A/B testing of prompt variants.

#### Current State

- `REACT_SYSTEM_PROMPT` hardcoded in `stock_assistant_agent.py` (lines 56-70)
- No mechanism to test prompt variants
- `langchain_adapter.py` has `PromptBuilder` pattern but used only for legacy fallback

#### Target State

- System prompts stored in `src/prompts/` directory
- Prompt variants identified by version/name
- A/B testing framework with LangSmith evaluation integration
- Prompt selection configurable via `config.yaml`

#### Work Items

1. **Extract Prompts to External Files**
   - Create `src/prompts/react_system/v1.md` (current prompt)
   - Update `StockAssistantAgent` to load from files using `PromptBuilder`
   - Support Jinja2 templating for dynamic sections

2. **Implement Prompt Versioning**
   - Add `prompts.active_version` to `config.yaml`
   - Create prompt registry for version management
   - Log prompt version in LangSmith traces

3. **A/B Testing Framework**
   - Implement prompt selector with weighted distribution
   - Add evaluation harness using LangSmith datasets
   - Create comparison metrics (response quality, tool usage, latency)

4. **Documentation**
   - Document prompt authoring guidelines
   - Create prompt changelog template

#### Implementation Pattern

```python
# src/prompts/react_system/v1.md
---
name: react_system_v1
description: Base ReAct system prompt for stock assistant
version: 1.0.0
---

You are a helpful AI assistant specialized in stock market analysis...

# src/core/stock_assistant_agent.py
from core.langchain_adapter import PromptBuilder

class StockAssistantAgent:
    def _load_system_prompt(self) -> str:
        version = self.config.get("prompts", {}).get("active_version", "v1")
        builder = PromptBuilder(template_dir="src/prompts/react_system")
        return builder.load(f"{version}.md")
```

#### Dependencies

- Existing `PromptBuilder` pattern in `langchain_adapter.py`
- LangSmith for evaluation (existing integration)
- Jinja2 (existing dependency)

#### Success Criteria

- System prompt loaded from external file
- Prompt version logged in every LangSmith trace
- A/B test framework can compare 2+ prompt variants
- Prompt changes require no code deployment

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

## Phase 2B: Feature Implementations

### 2B.1 TradingView Tool Integration

**Objective**: Implement fully functional TradingView integration for chart generation, technical analysis widgets, and market indicators.

#### Current State

- `TradingViewTool` exists at `src/core/tools/tradingview.py` (151 lines)
- All methods raise `NotImplementedError` with "Phase 2 feature" message
- Actions defined: `get_chart_url`, `get_widget`, `get_technical_analysis`

#### Target State

- Full TradingView widget URL generation
- Technical analysis data fetching
- Chart embedding support for web frontend
- Caching with configurable TTL

#### Work Items

1. **Implement Chart URL Generation**
   - Generate TradingView Advanced Chart URLs
   - Support customizable timeframes, indicators, chart types
   - Validate symbol against supported exchanges

2. **Implement Widget Generation**
   - Mini chart widgets for embedding
   - Technical analysis widget
   - Market overview widget

3. **Implement Technical Analysis Fetching**
   - Oscillators summary (RSI, MACD, Stochastic)
   - Moving averages summary
   - Buy/Sell/Neutral recommendation parsing

4. **Add Caching Layer**
   - Use `CachingTool` base class pattern
   - Configure TTL in `config.yaml` (existing: 300s)

5. **Frontend Integration**
   - Create chart component consuming TradingView URLs
   - Add widget embedding support

#### Implementation Pattern

```python
class TradingViewTool(CachingTool):
    """TradingView integration for charts and analysis."""
    
    TRADINGVIEW_BASE_URL = "https://www.tradingview.com"
    
    def _execute(self, action: str, parameters: Dict[str, Any]) -> str:
        if action == "get_chart_url":
            return self._get_chart_url(parameters)
        elif action == "get_technical_analysis":
            return self._get_technical_analysis(parameters)
        # ...
    
    def _get_chart_url(self, params: Dict[str, Any]) -> str:
        symbol = params["symbol"]
        interval = params.get("interval", "D")
        return f"{self.TRADINGVIEW_BASE_URL}/chart/?symbol={symbol}&interval={interval}"
    
    def _get_technical_analysis(self, params: Dict[str, Any]) -> str:
        # Use tradingview-ta library or web scraping
        from tradingview_ta import TA_Handler
        handler = TA_Handler(symbol=params["symbol"], exchange=params["exchange"])
        analysis = handler.get_analysis()
        return json.dumps(analysis.summary)
```

#### Dependencies

- `tradingview-ta` package (for technical analysis data)
- TradingView public widget URLs (no API key required)
- Frontend chart component

#### Success Criteria

- Agent can generate valid TradingView chart URLs
- Technical analysis data returned for major exchanges
- Response latency <2s for cached requests
- Frontend displays embedded charts correctly

---

### 2B.2 Semantic Router Enhancements

**Objective**: Improve query routing accuracy, add new route categories, and implement confidence-based fallback strategies.

#### Current State

- 8 route categories defined in `src/core/routes.py`
- Threshold-based routing (0.7) in `config.yaml`
- HuggingFace encoder fallback when OpenAI unavailable
- `cache_embeddings: true` for performance

#### Target State

- Additional route categories for new tools
- Dynamic threshold adjustment based on confidence distribution
- Route disambiguation for ambiguous queries
- Route analytics and monitoring

#### Work Items

1. **Add New Route Categories**
   - `tradingview` route for chart/widget requests
   - `multi_step` route for complex analysis requiring multiple tools
   - `clarification` route for ambiguous queries

2. **Implement Confidence-Based Routing**
   - Track confidence distribution per route
   - Implement soft routing for borderline confidence scores
   - Add "unknown" route with clarification response

3. **Route Disambiguation**
   - When multiple routes have similar confidence, prompt for clarification
   - Implement route suggestion in responses

4. **Analytics Integration**
   - Log route decisions to LangSmith
   - Track route accuracy over time
   - Alert on routing degradation

#### Implementation Pattern

```python
# src/core/routes.py - New routes
tradingview_route = Route(
    name="tradingview",
    utterances=[
        "show me a chart for AAPL",
        "technical analysis chart",
        "TradingView widget for Tesla",
        "display the candlestick chart",
    ]
)

clarification_route = Route(
    name="clarification",
    utterances=[
        "what do you mean",
        "can you explain that",
        "I don't understand",
    ]
)

# Confidence-based routing
def route_query(self, query: str) -> Tuple[str, float]:
    result = self.router(query)
    if result.confidence < 0.5:
        return "clarification", result.confidence
    return result.name, result.confidence
```

#### Dependencies

- Existing semantic router infrastructure
- LangSmith tracing (existing)
- Route utterance expansion (manual curation)

#### Success Criteria

- New routes achieve >85% accuracy on test set
- Ambiguous queries trigger clarification response
- Route confidence logged in every trace
- No regression in existing route accuracy

---

### 2B.3 StockSymbolTool Multi-Source Enhancement

**Objective**: Extend StockSymbolTool with multiple data sources for improved reliability, coverage, and data quality.

#### Current State

- Single data source: Yahoo Finance (`yfinance` package)
- Actions: `get_price`, `get_history`, `get_info`, `search`
- Caching via `CachingTool` base class (60s TTL)

#### Target State

- Multiple data sources: Yahoo Finance, Alpha Vantage, Polygon.io
- Source failover for reliability
- Data source selection based on query type
- Unified response format across sources

#### Work Items

1. **Add Alpha Vantage Integration**
   - Implement Alpha Vantage API client
   - Map to existing action interface
   - Add API key configuration (existing placeholder in config)

2. **Add Polygon.io Integration (Optional)**
   - Real-time data source option
   - WebSocket support for live quotes

3. **Implement Source Router**
   - Select optimal source based on data type
   - Implement failover chain
   - Configure source priority in `config.yaml`

4. **Unify Response Format**
   - Normalize data across sources
   - Handle source-specific fields
   - Add source attribution in responses

#### Implementation Pattern

```python
class StockSymbolTool(CachingTool):
    """Multi-source stock data tool."""
    
    SOURCE_PRIORITY = ["yahoo", "alpha_vantage", "polygon"]
    
    def _execute(self, action: str, parameters: Dict[str, Any]) -> str:
        source = parameters.get("source", "auto")
        
        if source == "auto":
            return self._execute_with_failover(action, parameters)
        return self._execute_from_source(source, action, parameters)
    
    def _execute_with_failover(self, action: str, params: Dict) -> str:
        for source in self.SOURCE_PRIORITY:
            try:
                return self._execute_from_source(source, action, params)
            except DataSourceError:
                continue
        raise AllSourcesFailedError("All data sources unavailable")
```

#### Dependencies

- `alpha_vantage` package
- Alpha Vantage API key (free tier available)
- Optional: Polygon.io subscription

#### Success Criteria

- Failover works seamlessly when Yahoo Finance unavailable
- Alpha Vantage provides fundamental data not in Yahoo
- No increase in average response latency
- Data source logged in responses

---

### 2B.4 Reporting Tool Implementation

**Objective**: Implement production-ready reporting tool with templated outputs, PDF generation, and portfolio analytics.

#### Current State

- `ReportingTool` exists at `src/core/tools/reporting.py` (273 lines)
- Scaffold implementation with placeholder markdown output
- Report types defined: `symbol`, `portfolio`, `market`

#### Target State

- Full report generation with Jinja2 templates
- PDF export capability
- Portfolio analytics calculations
- Chart embedding in reports

#### Work Items

1. **Implement Symbol Reports**
   - Company overview section
   - Financial metrics table
   - Technical analysis summary
   - Price chart embedding

2. **Implement Portfolio Reports**
   - Holdings summary with allocation
   - Performance metrics (returns, Sharpe ratio)
   - Risk analysis (beta, volatility)
   - Comparison to benchmarks

3. **Implement Market Reports**
   - Market overview (indices, sectors)
   - Top movers
   - Sentiment summary
   - Economic indicators

4. **Add Export Capabilities**
   - Markdown output (existing)
   - HTML with styling
   - PDF generation (using WeasyPrint or similar)

5. **Template System**
   - Create Jinja2 templates in `src/prompts/reports/`
   - Support custom branding/styling

#### Implementation Pattern

```python
from jinja2 import Environment, FileSystemLoader

class ReportingTool(CachingTool):
    """Report generation with Jinja2 templates."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.template_env = Environment(
            loader=FileSystemLoader("src/prompts/reports")
        )
    
    def _generate_symbol_report(self, symbol: str) -> str:
        template = self.template_env.get_template("symbol_report.md.j2")
        
        # Gather data from other tools
        price_data = self._get_price_data(symbol)
        fundamentals = self._get_fundamentals(symbol)
        technicals = self._get_technicals(symbol)
        
        return template.render(
            symbol=symbol,
            price=price_data,
            fundamentals=fundamentals,
            technicals=technicals,
            generated_at=datetime.now()
        )
```

#### Dependencies

- Jinja2 (existing)
- WeasyPrint for PDF (new dependency)
- Chart generation library (matplotlib or plotly)

#### Success Criteria

- Reports include all specified sections
- PDF exports render correctly
- Report generation <5s for single symbol
- Templates customizable without code changes

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
def process_query(self, query: str, session_id: str) -> AgentResponse:
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
  
  prompts:
    active_version: v1
    ab_testing:
      enabled: false
      variants: [v1, v2]
      weights: [0.5, 0.5]
  
  tools:
    stock_symbol:
      sources: [yahoo, alpha_vantage]
      failover_enabled: true
    tradingview:
      cache_ttl: 300
    reporting:
      pdf_enabled: true
      template_dir: src/prompts/reports

  multi_agent:
    enabled: false
    supervisor_model: gpt-4
    specialist_model: gpt-3.5-turbo
```

### Documentation Updates

- Update `LANGCHAIN_AGENT_HOWTO.md` with Phase 2 patterns
- Create operation runbooks for new features
- Update API documentation for structured outputs

---

## Related Documents

- [LANGCHAIN_AGENT_HOWTO.md](./LANGCHAIN_AGENT_HOWTO.md) - Comprehensive development guide
- [PHASE2_ROADMAP.md](./PHASE2_ROADMAP.md) - Original Phase 2 outline
- [SKILL.md](../../.github/skills/langchain-agent-development/SKILL.md) - Development skill reference
- [Architecture Instructions](../../.github/instructions/architecture.instructions.md) - System design conventions

---

## Appendix: Implementation Priority Matrix

| Item | Impact | Effort | Priority |
|------|--------|--------|----------|
| 2A.1 Long-term Memory | High | Medium | P0 |
| 2A.2 Prompt Refinement | Medium | Low | P1 |
| 2A.3 Structured Outputs | High | Low | P0 |
| 2B.1 TradingView Tool | Medium | Medium | P1 |
| 2B.2 Semantic Router | Low | Low | P2 |
| 2B.3 Multi-Source Data | Medium | Medium | P1 |
| 2B.4 Reporting Tool | Medium | High | P2 |
| 2C.1 Multi-Agent | High | High | P2 |
| 2C.2 Technical Refinements | Medium | Medium | P1 |

---

*This roadmap is a living document and will be updated as implementation progresses.*
