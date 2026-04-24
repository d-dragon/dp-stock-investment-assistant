# Phase 2 Implementation Roadmap

**Created**: 2025-12-24  
**Branch**: `improve-openai-chat-response`  
**Status**: Planning

---

## Table of Contents

1. [Overview](#overview)
2. [Phase 1 Recap](#phase-1-recap)
3. [Current Architecture](#current-architecture)
4. [Phase 2 Architecture](#phase-2-architecture)
5. [Implementation Priority](#implementation-priority)
6. [Feature Specifications](#feature-specifications)
   - [StockSymbolTool Improvements](#1-stocksymboltool-improvements)
   - [TradingView Integration](#2-tradingview-integration)
   - [Reporting Enhancements](#3-reporting-enhancements)
7. [Tool Development Guide](#tool-development-guide)
8. [Testing Checklists](#testing-checklists)
9. [Configuration & Deployment](#configuration--deployment)

---

## Overview

### Phase 1 Goals (✅ Complete)
- Upgrade to LangChain 1.x ecosystem
- Create LangGraph ReAct agent (`StockAssistantAgent`)
- Build extensible tool framework with caching
- Implement semantic query routing
- Support structured `AgentResponse` with metadata

### Phase 2 Goals
- Enhance existing tools with richer data sources
- Complete TradingView integration for charting
- Build production-ready reporting system
- Add advanced technical analysis capabilities

---

## Phase 1 Recap

### Completed Components

| Component | Status | Description |
|-----------|--------|-------------|
| `StockAssistantAgent` | ✅ | LangGraph ReAct agent with fallback support |
| `ToolRegistry` | ✅ | Singleton registry with health checks |
| `CachingTool` | ✅ | Abstract base with Redis/memory caching |
| `StockSymbolTool` | ✅ | Symbol lookup via Yahoo Finance + MongoDB |
| `StockQueryRouter` | ✅ | Semantic routing with 8 categories |
| `AgentResponse` | ✅ | Structured response with tool_calls, token_usage |
| `ChatService` | ✅ | SSE streaming with structured methods |
| `GrokModelClient` | ✅ | xAI integration via OpenAI SDK |

### Key Files Reference

```
src/core/
├── stock_assistant_agent.py    # Main ReAct agent (588 lines)
├── types.py                    # AgentResponse, ResponseStatus, ToolCall
├── routes.py                   # Route enum + ROUTE_UTTERANCES
├── stock_query_router.py       # Semantic router implementation
├── model_factory.py            # Multi-provider factory with fallback
└── tools/
    ├── base.py                 # CachingTool abstract class
    ├── registry.py             # ToolRegistry singleton
    ├── stock_symbol.py         # StockSymbolTool (complete)
    ├── reporting.py            # ReportingTool (scaffold)
    └── tradingview.py          # TradingViewTool (placeholder)
```

---

## Current Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           PHASE 1 ARCHITECTURE (Complete)                        │
└─────────────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────────┐
                              │   User Query     │
                              │ "Price of AAPL"  │
                              └────────┬─────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                              CHAT SERVICE LAYER                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │ ChatService                                                                  │ │
│  │  • stream_chat_response()           → SSE streaming                         │ │
│  │  • stream_chat_response_structured() → SSE with tool_calls, token_usage     │ │
│  │  • process_chat_query_structured()   → Returns AgentResponse                │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────┬───────────────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                              AGENT LAYER                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │ StockAssistantAgent (LangGraph ReAct)                                       │ │
│  │  • process_query()           → String response                              │ │
│  │  • process_query_streaming() → Chunk iterator                               │ │
│  │  • process_query_structured()→ AgentResponse with metadata                  │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                       │                                           │
│              ┌────────────────────────┼────────────────────────┐                 │
│              ▼                        ▼                        ▼                 │
│  ┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐     │
│  │ StockQueryRouter│    │    ToolRegistry      │    │  ModelClientFactory │     │
│  │ (Semantic)      │    │    (Singleton)       │    │  (Fallback Support) │     │
│  │                 │    │                      │    │                     │     │
│  │ Routes:         │    │ Tools:               │    │ Providers:          │     │
│  │ • PRICE_CHECK   │    │ • StockSymbolTool ✅ │    │ • OpenAI (primary)  │     │
│  │ • NEWS_ANALYSIS │    │ • ReportingTool 🚧   │    │ • Grok (fallback)   │     │
│  │ • PORTFOLIO     │    │ • TradingViewTool ⏳ │    │                     │     │
│  │ • TECHNICAL     │    │                      │    │                     │     │
│  │ • FUNDAMENTALS  │    └──────────────────────┘    └─────────────────────┘     │
│  │ • IDEAS         │                                                             │
│  │ • MARKET_WATCH  │                                                             │
│  │ • GENERAL_CHAT  │                                                             │
│  └─────────────────┘                                                             │
└──────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                           │
│  ┌────────────────────────┐         ┌─────────────────────────────────────────┐  │
│  │     MongoDB            │         │              Redis Cache                │  │
│  │                        │         │                                         │  │
│  │ • SymbolRepository     │         │ Cache Keys:                             │  │
│  │ • UserRepository       │         │ • tool:stock_symbol:{symbol}   (60s)    │  │
│  │ • WorkspaceRepository  │         │ • tool:reporting:{hash}        (600s)   │  │
│  │ • PortfolioRepository  │         │ • tool:tradingview:{hash}      (300s)   │  │
│  └────────────────────────┘         └─────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL SERVICES                                       │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  │
│  │  Yahoo Finance │  │    OpenAI API  │  │    xAI (Grok)  │  │  TradingView*  │  │
│  │   (yfinance)   │  │    GPT-4/etc   │  │   grok-4-fast  │  │   (Phase 2)    │  │
│  └────────────────┘  └────────────────┘  └────────────────┘  └────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────────┘

Legend: ✅ Complete  🚧 Scaffold  ⏳ Placeholder
```

---

## Phase 2 Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           PHASE 2 ARCHITECTURE (Planned)                         │
└─────────────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────────┐
                              │   User Query     │
                              └────────┬─────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                              ENHANCED TOOL REGISTRY                               │
│                                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                         ToolRegistry (Expanded)                              │ │
│  │                                                                              │ │
│  │  PRIORITY 1: StockSymbolTool (Enhanced)                                     │ │
│  │  ┌────────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ • Multi-source data (Yahoo + Alpha Vantage + Polygon.io)               │ │ │
│  │  │ • Real-time quotes with WebSocket support                              │ │ │
│  │  │ • Extended company info (earnings, dividends, splits)                  │ │ │
│  │  │ • Sector/industry classification                                       │ │ │
│  │  │ • Peer comparison data                                                 │ │ │
│  │  └────────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                              │ │
│  │  PRIORITY 2: TradingViewTool (New Implementation)                           │ │
│  │  ┌────────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ Actions:                          │ Features:                          │ │ │
│  │  │ • get_chart_url(symbol, period)   │ • Interactive chart embedding     │ │ │
│  │  │ • get_widget(symbol, type)        │ • Technical indicator overlays    │ │ │
│  │  │ • get_technical_analysis(symbol)  │ • Drawing tools (support/resist)  │ │ │
│  │  │ • get_screener_results(filters)   │ • Multi-timeframe analysis        │ │ │
│  │  └────────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                              │ │
│  │  PRIORITY 3: ReportingTool (Enhanced)                                       │ │
│  │  ┌────────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ Report Types:                     │ Output Formats:                    │ │ │
│  │  │ • Symbol Analysis Report          │ • Markdown (chat display)          │ │ │
│  │  │ • Portfolio Performance Report    │ • PDF (downloadable)               │ │ │
│  │  │ • Market Overview Report          │ • HTML (email-ready)               │ │ │
│  │  │ • Watchlist Summary Report        │ • JSON (API consumption)           │ │ │
│  │  │ • Technical Analysis Report       │                                    │ │ │
│  │  └────────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                              │ │
│  │  FUTURE: Additional Tools                                                   │ │
│  │  ┌────────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ • NewsSentimentTool   - Analyze news sentiment for symbols             │ │ │
│  │  │ • EarningsCalendarTool - Track upcoming earnings dates                 │ │ │
│  │  │ • SECFilingsTool      - Access SEC filings and parse key data          │ │ │
│  │  │ • AlertTool           - Set and manage price/event alerts              │ │ │
│  │  └────────────────────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         ENHANCED DATA LAYER                                       │
│                                                                                   │
│  ┌─────────────────────────────┐       ┌─────────────────────────────────────┐  │
│  │    MongoDB (New Schemas)    │       │     Redis (Enhanced Caching)        │  │
│  │                             │       │                                     │  │
│  │ NEW:                        │       │ NEW Cache Patterns:                 │  │
│  │ • tradingview_charts        │       │ • tool:tradingview:chart:{hash}     │  │
│  │ • technical_indicators      │       │ • tool:technical:{symbol}:{ind}     │  │
│  │ • generated_reports         │       │ • report:generated:{report_id}      │  │
│  │ • price_alerts              │       │ • alert:user:{user_id}              │  │
│  │ • news_sentiment            │       │ • news:sentiment:{symbol}           │  │
│  └─────────────────────────────┘       └─────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES (Expanded)                                 │
│                                                                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │
│  │Yahoo Finance│ │Alpha Vantage│ │ Polygon.io  │ │ TradingView │ │ News APIs  │ │
│  │  (current)  │ │  (premium)  │ │ (real-time) │ │  (charts)   │ │(sentiment) │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └────────────┘ │
│                                                                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                                │
│  │  SEC EDGAR  │ │  OpenAI API │ │  xAI (Grok) │                                │
│  │  (filings)  │ │   (LLM)     │ │   (LLM)     │                                │
│  └─────────────┘ └─────────────┘ └─────────────┘                                │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Priority

| Priority | Feature | Effort | Dependencies | Value |
|----------|---------|--------|--------------|-------|
| **P1** | StockSymbolTool Improvements | Medium | None | High - Core functionality enhancement |
| **P2** | TradingView Integration | High | TradingView API access | High - Visual analysis capability |
| **P3** | Reporting Enhancements | Medium | P1 complete | Medium - User productivity |
| **P4** | News Sentiment Tool | Low | News API access | Low - Nice-to-have |
| **P5** | SEC Filings Tool | Medium | SEC EDGAR API | Low - Advanced users |

### Implementation Order

```
Week 1-2: StockSymbolTool Improvements
    └── Enhanced data sources
    └── Better caching strategy
    └── Extended company info

Week 3-4: TradingView Integration
    └── API client implementation
    └── Chart URL generation
    └── Widget embedding

Week 5-6: Reporting Enhancements
    └── Template system
    └── PDF generation
    └── Portfolio integration
```

---

## Feature Specifications

### 1. StockSymbolTool Improvements

**Current State**: Basic symbol lookup via Yahoo Finance + MongoDB fallback

**Enhancements**:

#### 1.1 Multi-Source Data Integration

```python
# Current: Single source
result = yf.Ticker(symbol).info

# Enhanced: Multi-source with fallback
class EnhancedStockSymbolTool(CachingTool):
    DATA_SOURCES = [
        YahooFinanceProvider(),      # Free, rate-limited
        AlphaVantageProvider(),      # Premium, high-quality
        PolygonProvider(),           # Real-time, WebSocket
    ]
    
    def _execute(self, symbol: str, action: str) -> str:
        for provider in self.DATA_SOURCES:
            try:
                return provider.fetch(symbol, action)
            except ProviderError:
                continue
        raise AllProvidersFailedError()
```

#### 1.2 Extended Actions

| Action | Description | Data Points |
|--------|-------------|-------------|
| `get_info` | Basic info (current) | price, name, sector |
| `get_extended_info` | **NEW** Full company profile | + employees, founded, description, executives |
| `get_financials` | **NEW** Financial statements | income, balance sheet, cash flow |
| `get_earnings` | **NEW** Earnings data | EPS history, estimates, surprises |
| `get_dividends` | **NEW** Dividend history | yield, payout ratio, ex-dates |
| `get_peers` | **NEW** Peer comparison | similar companies by sector/size |

#### 1.3 Caching Strategy

```yaml
# config.yaml
langchain:
  tools:
    cache_ttl:
      stock_symbol:
        get_info: 60           # 1 minute (price-sensitive)
        get_extended_info: 3600 # 1 hour (static data)
        get_financials: 86400   # 24 hours (quarterly)
        get_earnings: 3600      # 1 hour
        get_dividends: 86400    # 24 hours
        get_peers: 86400        # 24 hours
```

---

### 2. TradingView Integration

**Current State**: Placeholder with `NotImplementedError`

**Implementation Plan**:

#### 2.1 TradingView Widget Types

| Widget Type | Use Case | URL Pattern |
|-------------|----------|-------------|
| `chart` | Price chart with indicators | `tradingview.com/chart/?symbol=` |
| `mini_chart` | Compact price widget | `tradingview.com/embed-widget/mini-symbol-overview/` |
| `technical_analysis` | Analysis gauge | `tradingview.com/embed-widget/technical-analysis/` |
| `screener` | Stock screener | `tradingview.com/embed-widget/screener/` |
| `heatmap` | Sector heatmap | `tradingview.com/embed-widget/stock-heatmap/` |

#### 2.2 Implementation Structure

```python
# src/core/tools/tradingview.py

class TradingViewTool(CachingTool):
    """TradingView integration for charting and technical analysis."""
    
    name: str = "tradingview"
    description: str = "Get TradingView charts, widgets, and technical analysis"
    
    # Widget configuration
    WIDGET_BASE_URL = "https://s.tradingview.com/embed-widget"
    CHART_BASE_URL = "https://www.tradingview.com/chart"
    
    def _execute(
        self,
        symbol: str,
        action: str = "get_chart_url",
        **kwargs
    ) -> str:
        actions = {
            "get_chart_url": self._get_chart_url,
            "get_widget": self._get_widget,
            "get_technical_analysis": self._get_technical_analysis,
            "get_screener_url": self._get_screener_url,
        }
        
        handler = actions.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")
        
        return handler(symbol, **kwargs)
    
    def _get_chart_url(
        self,
        symbol: str,
        interval: str = "D",      # D, W, M, 1, 5, 15, 60
        theme: str = "dark",
        studies: List[str] = None  # ["RSI", "MACD", "BB"]
    ) -> str:
        """Generate TradingView chart URL with indicators."""
        params = {
            "symbol": self._normalize_symbol(symbol),
            "interval": interval,
            "theme": theme,
        }
        if studies:
            params["studies"] = ",".join(studies)
        
        return f"{self.CHART_BASE_URL}?{urlencode(params)}"
    
    def _get_widget(
        self,
        symbol: str,
        widget_type: str = "mini_chart",
        width: int = 400,
        height: int = 300,
    ) -> str:
        """Generate embeddable widget HTML/iframe."""
        config = {
            "symbol": self._normalize_symbol(symbol),
            "width": width,
            "height": height,
            "colorTheme": "dark",
            "isTransparent": False,
        }
        return json.dumps({
            "type": widget_type,
            "config": config,
            "embed_url": f"{self.WIDGET_BASE_URL}/{widget_type}/"
        })
    
    def _get_technical_analysis(
        self,
        symbol: str,
        interval: str = "1D",
    ) -> str:
        """Get technical analysis summary (buy/sell/neutral signals)."""
        # Integration with TradingView's technical analysis API
        # Returns oscillators, moving averages, summary recommendation
        ...
```

#### 2.3 Configuration Requirements

```yaml
# config.yaml
tradingview:
  enabled: true
  default_theme: "dark"
  default_interval: "D"
  default_studies:
    - "RSI"
    - "MACD"
    - "Volume"
  widget_defaults:
    width: 800
    height: 600
    
langchain:
  tools:
    cache_ttl:
      tradingview: 300  # 5 minutes
```

```bash
# .env (if using TradingView API for advanced features)
TRADINGVIEW_API_KEY=your_api_key_here  # Optional for basic widgets
```

---

### 3. Reporting Enhancements

**Current State**: Scaffold returning placeholder markdown

**Implementation Plan**:

#### 3.1 Report Types

| Report Type | Data Sources | Output |
|-------------|--------------|--------|
| `symbol` | StockSymbolTool, TradingViewTool | Company analysis with charts |
| `portfolio` | PortfolioRepository, StockSymbolTool | Holdings, performance, allocation |
| `market` | Market indices, sector data | Market overview, trends |
| `watchlist` | WatchlistRepository, StockSymbolTool | Tracked symbols summary |
| `technical` | TradingViewTool, indicators | Technical analysis report |

#### 3.2 Template System

```python
# src/core/tools/reporting.py

from jinja2 import Environment, PackageLoader

class ReportingTool(CachingTool):
    """Generate formatted reports for symbols, portfolios, and markets."""
    
    TEMPLATES = {
        "symbol": "reports/symbol_report.md.j2",
        "portfolio": "reports/portfolio_report.md.j2",
        "market": "reports/market_report.md.j2",
        "technical": "reports/technical_report.md.j2",
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.jinja_env = Environment(
            loader=PackageLoader("src.prompts", "templates")
        )
    
    def _execute(
        self,
        report_type: str = "symbol",
        output_format: str = "markdown",
        **kwargs
    ) -> str:
        # Gather data from tools/services
        data = self._gather_report_data(report_type, **kwargs)
        
        # Render template
        template = self.jinja_env.get_template(self.TEMPLATES[report_type])
        markdown = template.render(**data)
        
        # Convert to requested format
        if output_format == "markdown":
            return markdown
        elif output_format == "html":
            return self._markdown_to_html(markdown)
        elif output_format == "pdf":
            return self._generate_pdf(markdown)
        elif output_format == "json":
            return json.dumps(data)
```

#### 3.3 Sample Report Template

```jinja2
{# src/prompts/templates/reports/symbol_report.md.j2 #}

# {{ symbol }} Analysis Report

**Generated**: {{ timestamp }}
**Data as of**: {{ price_timestamp }}

---

## Company Overview

| Metric | Value |
|--------|-------|
| **Name** | {{ company_name }} |
| **Sector** | {{ sector }} |
| **Industry** | {{ industry }} |
| **Market Cap** | {{ market_cap | format_currency }} |
| **Employees** | {{ employees | format_number }} |

## Price Summary

| Metric | Value |
|--------|-------|
| **Current Price** | {{ current_price | format_currency }} |
| **Day Change** | {{ day_change | format_percent }} |
| **52-Week Range** | {{ week_52_low | format_currency }} - {{ week_52_high | format_currency }} |

{% if chart_url %}
## Technical Chart

![{{ symbol }} Chart]({{ chart_url }})
{% endif %}

{% if technical_analysis %}
## Technical Analysis

**Overall Signal**: {{ technical_analysis.summary }}

### Oscillators
{{ technical_analysis.oscillators | format_table }}

### Moving Averages
{{ technical_analysis.moving_averages | format_table }}
{% endif %}

---
*Report generated by Stock Investment Assistant*
```

---

## Tool Development Guide

### Creating a New Tool

#### Step 1: Extend CachingTool

```python
# src/core/tools/my_new_tool.py

from typing import Optional, Type
from pydantic import BaseModel, Field
from core.tools.base import CachingTool

class MyNewToolInput(BaseModel):
    """Input schema for MyNewTool."""
    symbol: str = Field(..., description="Stock symbol to analyze")
    action: str = Field(default="default_action", description="Action to perform")

class MyNewTool(CachingTool):
    """Description of what this tool does."""
    
    name: str = "my_new_tool"
    description: str = "Detailed description for LLM to understand when to use this tool"
    args_schema: Type[BaseModel] = MyNewToolInput
    
    # Cache configuration
    CACHE_TTL = 300  # 5 minutes
    CACHE_KEY_PREFIX = "tool:my_new_tool"
    
    def _execute(self, symbol: str, action: str = "default_action", **kwargs) -> str:
        """
        Implement the actual tool logic here.
        
        This method is called by the base class after cache check.
        """
        # Your implementation here
        return f"Result for {symbol}"
    
    def health_check(self) -> tuple:
        """Check tool dependencies are available."""
        try:
            # Check external service availability
            return True, {
                "component": self.name,
                "status": "ready",
            }
        except Exception as e:
            return False, {
                "component": self.name,
                "status": "error",
                "error": str(e),
            }
```

#### Step 2: Register in ToolRegistry

```python
# src/core/tools/__init__.py

from core.tools.my_new_tool import MyNewTool

# Tool is auto-registered when imported if using @register decorator
# Or manually register:
from core.tools.registry import ToolRegistry

registry = ToolRegistry()
registry.register(MyNewTool)
```

#### Step 3: Add Configuration

```yaml
# config.yaml
langchain:
  tools:
    enabled:
      - stock_symbol
      - reporting
      - tradingview
      - my_new_tool  # Add new tool here
    cache_ttl:
      my_new_tool: 300
```

#### Step 4: Write Tests

```python
# tests/test_my_new_tool.py

import pytest
from unittest.mock import MagicMock
from core.tools.my_new_tool import MyNewTool

class TestMyNewTool:
    @pytest.fixture
    def tool(self):
        return MyNewTool(cache=None)
    
    def test_execute_returns_expected_format(self, tool):
        result = tool._execute(symbol="AAPL", action="default_action")
        assert "AAPL" in result
    
    def test_health_check_returns_ready(self, tool):
        healthy, details = tool.health_check()
        assert healthy is True
        assert details["status"] == "ready"
```

---

## Testing Checklists

### StockSymbolTool Improvements

- [ ] **Unit Tests**
  - [ ] Test each new action (get_extended_info, get_financials, etc.)
  - [ ] Test multi-source fallback logic
  - [ ] Test cache key generation per action
  - [ ] Test error handling when all providers fail
  - [ ] Test data normalization across providers

- [ ] **Integration Tests**
  - [ ] Test Yahoo Finance provider
  - [ ] Test Alpha Vantage provider (if implemented)
  - [ ] Test MongoDB symbol lookup fallback
  - [ ] Test cache hit/miss scenarios

- [ ] **Performance Tests**
  - [ ] Benchmark multi-source lookup latency
  - [ ] Test cache effectiveness under load

---

### TradingView Integration

- [ ] **Unit Tests**
  - [ ] Test `get_chart_url` URL generation
  - [ ] Test `get_widget` configuration output
  - [ ] Test symbol normalization (AAPL → NASDAQ:AAPL)
  - [ ] Test interval validation
  - [ ] Test studies parameter handling
  - [ ] Test cache key generation

- [ ] **Integration Tests**
  - [ ] Test generated URLs are valid (HTTP 200)
  - [ ] Test widget HTML is renderable
  - [ ] Test technical analysis data retrieval (if API-based)

- [ ] **E2E Tests**
  - [ ] Test chart embedding in frontend
  - [ ] Test widget display in chat response

---

### Reporting Enhancements

- [ ] **Unit Tests**
  - [ ] Test template loading
  - [ ] Test data gathering for each report type
  - [ ] Test markdown rendering
  - [ ] Test HTML conversion
  - [ ] Test PDF generation
  - [ ] Test JSON output format

- [ ] **Integration Tests**
  - [ ] Test symbol report with real data
  - [ ] Test portfolio report with PortfolioRepository
  - [ ] Test market report data aggregation

- [ ] **Template Tests**
  - [ ] Test all Jinja2 filters work
  - [ ] Test missing data handling (optional sections)
  - [ ] Test number/currency formatting

---

## Configuration & Deployment

### New Configuration Keys

```yaml
# config.yaml additions for Phase 2

# StockSymbolTool enhancements
data_providers:
  yahoo_finance:
    enabled: true
    rate_limit: 2000  # requests per hour
  alpha_vantage:
    enabled: false    # Set to true with API key
    api_key: ${ALPHA_VANTAGE_API_KEY}
    rate_limit: 500
  polygon:
    enabled: false
    api_key: ${POLYGON_API_KEY}

# TradingView
tradingview:
  enabled: true
  api_key: ${TRADINGVIEW_API_KEY}  # Optional
  default_theme: "dark"
  default_interval: "D"
  default_studies:
    - "RSI"
    - "MACD"
    - "Volume"

# Reporting
reporting:
  templates_dir: "src/prompts/templates/reports"
  output_dir: "reports/generated"
  default_format: "markdown"
  pdf:
    enabled: true
    engine: "weasyprint"  # or "wkhtmltopdf"
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ALPHA_VANTAGE_API_KEY` | No | Premium stock data access |
| `POLYGON_API_KEY` | No | Real-time market data |
| `TRADINGVIEW_API_KEY` | No | Advanced TradingView features |
| `NEWS_API_KEY` | No | News sentiment analysis |

### Feature Flags

```yaml
# Feature flags for gradual rollout
features:
  enhanced_stock_symbol: true    # P1: Enable multi-source data
  tradingview_integration: false # P2: Enable when implemented
  advanced_reporting: false      # P3: Enable when implemented
  news_sentiment: false          # Future
  sec_filings: false             # Future
```

### Migration Notes

1. **No breaking changes** - Phase 2 features are additive
2. **Backward compatible** - Existing tool actions remain unchanged
3. **Feature-flagged** - New features disabled by default
4. **Database migrations** - None required for Phase 2

---

## Appendix: File Changes Summary

### Files to Create

| File | Purpose |
|------|---------|
| `src/prompts/templates/reports/symbol_report.md.j2` | Symbol report template |
| `src/prompts/templates/reports/portfolio_report.md.j2` | Portfolio report template |
| `src/prompts/templates/reports/market_report.md.j2` | Market report template |
| `tests/test_tradingview_tool.py` | TradingView tool tests |
| `tests/test_reporting_tool.py` | Reporting tool tests |

### Files to Modify

| File | Changes |
|------|---------|
| `src/core/tools/stock_symbol.py` | Add new actions, multi-source support |
| `src/core/tools/tradingview.py` | Replace placeholder with implementation |
| `src/core/tools/reporting.py` | Replace scaffold with template system |
| `config/config.yaml` | Add Phase 2 configuration sections |
| `requirements.txt` | Add jinja2, weasyprint (for PDF) |

---

*Document maintained as part of the LangChain ReAct Agent expansion project.*
