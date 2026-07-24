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

### Polymorphic Base Schema

```python
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

class AgentStructuredOutput(BaseModel):
    """Polymorphic base model for machine-readable agent structured responses."""
    schema_version: str = Field(default="v1", description="Schema version identifier")
    route_kind: StockQueryRoute = Field(..., description="Classified route kind")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Generation UTC timestamp")
```

---

### Route-Specific Response Schemas

#### 1. `StockAnalysisResponse` (Routes: `FUNDAMENTALS`, `TECHNICAL_ANALYSIS`, `PRICE_CHECK`)

```python
class DataPoint(BaseModel):
    metric: str = Field(..., description="Metric name, e.g. P/E, RSI, Revenue Growth")
    value: str = Field(..., description="Formatted string value")
    period: Optional[str] = Field(None, description="Time period, e.g. Q2 2026, 1Y")
    provenance_source: Optional[str] = Field(None, description="Source provider")

class StockAnalysisResponse(AgentStructuredOutput):
    """Structured response for stock technical, fundamental, and price queries."""
    route_kind: StockQueryRoute = StockQueryRoute.TECHNICAL_ANALYSIS
    symbol: str = Field(..., description="Stock symbol in uppercase, e.g. HSG, VNM, FPT")
    company_name: Optional[str] = Field(None, description="Company name")
    summary: str = Field(..., description="Concise analytical summary")
    sentiment: str = Field(..., description="BULLISH, BEARISH, or NEUTRAL")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    key_metrics: List[DataPoint] = Field(default_factory=list, description="Extracted metric data points")
    risks: List[str] = Field(default_factory=list, description="Identified risk factors")
    evidence_sources: List[str] = Field(default_factory=list, description="Sourced evidence citations")
```

#### 2. `RecommendationResponse` (Routes: `IDEAS`, `PORTFOLIO`)

```python
class RecommendationResponse(AgentStructuredOutput):
    """Structured response for stock ideas and portfolio recommendations."""
    route_kind: StockQueryRoute = StockQueryRoute.IDEAS
    symbols: List[str] = Field(..., description="Target stock symbols")
    action: str = Field(..., description="BUY, HOLD, SELL, WATCH, or ACCUMULATE")
    target_price_range: Optional[str] = Field(None, description="Target price range, e.g. 24,000 - 26,000 VND")
    time_horizon: str = Field(..., description="SHORT_TERM, MEDIUM_TERM, or LONG_TERM")
    rationale: str = Field(..., description="Strategic investment rationale")
    disclaimers: List[str] = Field(default_factory=list, description="Financial safety disclaimers")
```

#### 3. `GeneralChatResponse` (Routes: `GENERAL_CHAT`, `MARKET_WATCH`, `NEWS_ANALYSIS`)

```python
class GeneralChatResponse(AgentStructuredOutput):
    """Structured response for general market chat and macro news queries."""
    route_kind: StockQueryRoute = StockQueryRoute.GENERAL_CHAT
    topic: str = Field(..., description="Main topic or market sector discussed")
    summary: str = Field(..., description="Conversational summary")
    follow_up_suggestions: List[str] = Field(default_factory=list, description="Suggested follow-up questions")
```

---

### Discriminated Union & Envelope Schema

```python
AgentStructuredContent = Union[
    StockAnalysisResponse,
    RecommendationResponse,
    GeneralChatResponse,
]

class AgentResponse(BaseModel):
    """Core envelope returned by StockAssistantAgent and ChatService."""
    content: str = Field(..., description="Natural language markdown response text")
    structured_content: Optional[AgentStructuredContent] = Field(None, description="Typed machine-readable JSON payload")
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Contract validation status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Turn execution metadata (tokens, latency, route)")
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
