# Phase 1 Data Model: Agent Structured Outputs & Response Tool Schemas

**Feature**: `003-agent-structured-outputs`  
**Branch**: `feature/agent-structured-ouputs`  
**Status**: Complete  

---

## Authority & Cross-References

- [Constitution v2.6.0 §Structured Output Subsystem Governance](../../.specify/memory/constitution.md#structured-output-subsystem-and-response-tool-governance)
- [ADR-AGENT-005 §3 (Decision)](../../docs/domains/agent/DECISIONS/ADR-AGENT-005-STRUCTURED-OUTPUT-BOUNDARY-AND-RESPONSE-TOOL-PATTERN.md#3-decision)
- [ARCHITECTURE_DESIGN.md §4.2.1 (Logical Building Blocks & Response Types)](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#421-logical-building-blocks)
- [TECHNICAL_DESIGN.md §2.1 (Key Characteristics & Response Types)](../../docs/domains/agent/TECHNICAL_DESIGN.md#21-key-characteristics)
- [TECHNICAL_DESIGN.md §3.1 (StockAssistantAgent & Structured Execution Behavior)](../../docs/domains/agent/TECHNICAL_DESIGN.md#31-agent-runtime-and-orchestration)

---

## 1. Domain Pydantic v2 Schemas (`src/core/types.py`)

### Enums

```python
from enum import Enum

class ResponseStatus(str, Enum):
    SUCCESS = "SUCCESS"    # Contract validated via response tool or fallback formatter
    PARTIAL = "PARTIAL"    # Formatter failed or degraded; raw text preserved in content
    FAILED = "FAILED"      # System exception or unhandled pipeline error

class StockQueryRoute(str, Enum):
    FUNDAMENTALS = "FUNDAMENTALS"
    TECHNICAL_ANALYSIS = "TECHNICAL_ANALYSIS"
    PRICE_CHECK = "PRICE_CHECK"
    IDEAS = "IDEAS"
    PORTFOLIO = "PORTFOLIO"
    GENERAL_CHAT = "GENERAL_CHAT"
    MARKET_WATCH = "MARKET_WATCH"
    NEWS_ANALYSIS = "NEWS_ANALYSIS"
```

---

### Union Type Alias (no shared base class)

Each domain response model is a standalone `pydantic.BaseModel` with its own `route_kind` discriminator field typed as `StockQueryRoute` enum. The combined type is expressed as a `Union` type alias — not an inheritance hierarchy.

```python
from typing import Union

AgentStructuredOutput = Union[
    StockAnalysisResponse,
    RecommendationResponse,
    GeneralChatResponse,
    ErrorResponse,
]
```

---

### Route-Specific Response Schemas

#### 1. `StockAnalysisResponse` (Routes: `FUNDAMENTALS`, `TECHNICAL_ANALYSIS`, `PRICE_CHECK`)

```python
class StockAnalysisResponse(BaseModel):
    """Structured response for stock fundamental & technical analysis."""
    route_kind: StockQueryRoute = Field(default=StockQueryRoute.FUNDAMENTALS, description="Discriminator field identifying route kind")
    symbol: str = Field(..., description="Target stock ticker symbol (e.g., AAPL, FPT)")
    summary: str = Field(..., description="High-level analytical summary")
    sentiment: str = Field(default="NEUTRAL", description="Market sentiment (BULLISH, BEARISH, NEUTRAL)")
    key_metrics: Dict[str, Any] = Field(default_factory=dict, description="Key fundamental/technical metrics")
    citations: List[str] = Field(default_factory=list, description="Data provider citations and source references")
```

#### 2. `RecommendationResponse` (Routes: `IDEAS`, `PORTFOLIO`)

```python
class RecommendationResponse(BaseModel):
    """Structured response for stock investment ideas & recommendations."""
    route_kind: StockQueryRoute = Field(default=StockQueryRoute.IDEAS, description="Discriminator field identifying route kind")
    recommendation: str = Field(..., description="Actionable recommendation (BUY, SELL, HOLD, WATCH)")
    time_horizon: str = Field(default="MEDIUM_TERM", description="Target investment horizon (SHORT_TERM, MEDIUM_TERM, LONG_TERM)")
    thesis: str = Field(..., description="Core investment rationale and thesis")
    risk_factors: List[str] = Field(default_factory=list, description="Primary risk factors to monitor")
    disclaimer: str = Field(default="Not financial advice. For informational purposes only.", description="Mandatory financial disclosure")
```

#### 3. `GeneralChatResponse` (Routes: `GENERAL_CHAT`, `MARKET_WATCH`, `NEWS_ANALYSIS`)

```python
class GeneralChatResponse(BaseModel):
    """Structured response for general chat & market commentary."""
    route_kind: StockQueryRoute = Field(default=StockQueryRoute.GENERAL_CHAT, description="Discriminator field identifying route kind")
    message: str = Field(..., description="Natural language response text")
    topics_covered: List[str] = Field(default_factory=list, description="Key discussion topics identified")
    follow_up_suggestions: List[str] = Field(default_factory=list, description="Suggested follow-up queries for the user")
```

#### 4. `ErrorResponse` (Fallback & Degradation States)

```python
class ErrorResponse(BaseModel):
    """Structured response for error & fallback degradation states."""
    route_kind: str = Field(default="ERROR", description="Discriminator field identifying error route kind (not in StockQueryRoute enum)")
    error_code: str = Field(..., description="Categorized error identifier")
    description: str = Field(..., description="Human-readable error or degradation details")
    degraded_mode: bool = Field(default=True, description="Indicates if system operated in degraded partial mode")
```

---

### Envelope Schema

```python
@dataclass(frozen=True)
class AgentResponse:
    """Core envelope returned by StockAssistantAgent and ChatService."""
    content: str
    provider: str
    model: str
    status: ResponseStatus = ResponseStatus.SUCCESS
    tool_calls: tuple[ToolCall, ...] = ()
    token_usage: TokenUsage = TokenUsage()
    cached: bool = False
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    structured_content: Optional[AgentStructuredOutput] = None
```

---

## 2. Response Tool Descriptors (`src/core/tools/response_tools.py`)

| Tool Name | Class & Schema | Default Route Target | Risk Class | `return_direct` | Governing Anchor |
|-----------|----------------|----------------------|------------|-----------------|------------------|
| `submit_stock_analysis` | `StockAnalysisResponse` | `FUNDAMENTALS`, `TECHNICAL_ANALYSIS`, `PRICE_CHECK` | `RiskClass.BOUNDED_NON_MUTATING` | `True` | [ADR-AGENT-005 §3](../../docs/domains/agent/DECISIONS/ADR-AGENT-005-STRUCTURED-OUTPUT-BOUNDARY-AND-RESPONSE-TOOL-PATTERN.md#3-decision) |
| `submit_recommendation` | `RecommendationResponse` | `IDEAS`, `PORTFOLIO` | `RiskClass.BOUNDED_NON_MUTATING` | `True` | [ADR-AGENT-005 §3](../../docs/domains/agent/DECISIONS/ADR-AGENT-005-STRUCTURED-OUTPUT-BOUNDARY-AND-RESPONSE-TOOL-PATTERN.md#3-decision) |
| `submit_general_chat` | `GeneralChatResponse` | `GENERAL_CHAT`, `MARKET_WATCH`, `NEWS_ANALYSIS` | `RiskClass.BOUNDED_NON_MUTATING` | `True` | [ADR-AGENT-005 §3](../../docs/domains/agent/DECISIONS/ADR-AGENT-005-STRUCTURED-OUTPUT-BOUNDARY-AND-RESPONSE-TOOL-PATTERN.md#3-decision) |

---

## 3. MongoDB Persistence Schema Updates (`conversations` collection)

When a turn completes, `ChatService` appends a lightweight metadata frame to the `turns` array in the `conversations` collection:

```json
{
  "turn_id": "turn_12345",
  "user_query": "Danh gia HSG trung han",
  "route_kind": "TECHNICAL_ANALYSIS",
  "structured_status": "SUCCESS",
  "schema_version": "v1",
  "timestamp": "2026-07-23T11:40:00Z"
}
```

*Note: The heavy `AgentStructuredOutput` JSON payload is NOT stored in `agent_checkpoints` (STM checkpointer hygiene per [SRS v2.9 FR-1.2.8](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#128-stm-checkpointer-state-hygiene-and-payload-exclusion) and [Constitution v2.6.0 §II](../../.specify/memory/constitution.md#ii-layered-boundaries-and-explicit-ownership)).*
