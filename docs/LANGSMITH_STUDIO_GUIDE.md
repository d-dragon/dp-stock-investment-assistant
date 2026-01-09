# LangSmith Studio Integration Guide

This guide covers the LangSmith Studio integration for the Stock Investment Assistant, including setup, architecture, and development workflows.

## Table of Contents
1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Bootstrap Approach Explained](#bootstrap-approach-explained)
5. [Development Workflows](#development-workflows)
6. [Configuration Reference](#configuration-reference)
7. [Troubleshooting](#troubleshooting)

---

## Overview

### What is LangSmith Studio?

LangSmith Studio is a visual development environment for LangGraph agents that provides:

- **Visual Graph Editor**: See your agent's state machine as an interactive diagram
- **Real-time Debugging**: Step through agent execution node-by-node
- **Trace Inspection**: View detailed traces of tool calls, LLM interactions, and state transitions
- **Interactive Testing**: Send messages and watch the agent respond in real-time
- **State Visualization**: Inspect agent state at any point in execution

### Why Use It?

| Without Studio | With Studio |
|----------------|-------------|
| Print statements for debugging | Visual step-through debugging |
| Guessing at agent flow | See exact execution path |
| Manual trace inspection | Interactive trace explorer |
| Log file analysis | Real-time state visualization |
| Blind LLM prompt iteration | See prompts and responses inline |

---

## Quick Start

### Prerequisites

1. **Python virtual environment activated**
2. **Dependencies installed**: `pip install -r requirements.txt`
3. **MongoDB running**: `docker-compose up -d mongodb`
4. **Redis running**: `docker-compose up -d redis`
5. **LangSmith API key** (optional, for cloud tracing)

### Start Studio

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start LangGraph development server
langgraph dev
```

### Access Studio

Once started, you'll see:
```
🚀 API: http://127.0.0.1:2024
🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
📚 API Docs: http://127.0.0.1:2024/docs
```

**Click the Studio UI link** to open the visual development environment.

---

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    LangSmith Studio (Browser)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Graph View  │  │ Trace View  │  │ Interactive Chat Panel  │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────────┐
│              LangGraph API Server (localhost:2024)               │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                 langgraph_bootstrap.py                    │   │
│  │  • Adds 'src' to sys.path                                │   │
│  │  • Imports stock_assistant_agent                         │   │
│  │  • Exports compiled graph                                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              stock_assistant_agent.py                     │   │
│  │  • ReAct Agent with tools                                │   │
│  │  • stock_symbol tool                                     │   │
│  │  • reporting tool                                        │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │ MongoDB  │   │  Redis   │   │ OpenAI   │
        │ Database │   │  Cache   │   │   API    │
        └──────────┘   └──────────┘   └──────────┘
```

### File Structure

```
dp-stock-investment-assistant/
├── langgraph.json                    # LangGraph CLI configuration
├── src/
│   └── core/
│       ├── langgraph_bootstrap.py    # Bootstrap entry point for Studio
│       ├── stock_assistant_agent.py  # Main agent implementation
│       ├── langchain_adapter.py      # LangChain integration
│       └── tools/                    # Agent tools
│           ├── stock_symbol_tool.py
│           └── reporting_tool.py
└── config/
    └── config.yaml                   # Application configuration
```

---

## Bootstrap Approach Explained

### The Problem

When LangGraph CLI runs `langgraph dev`, it executes from the **project root directory** where `langgraph.json` is located. However, our project uses a `src/` directory structure with imports like:

```python
from core.data_manager import DataManager    # Expects 'src' in PYTHONPATH
from utils.config_loader import ConfigLoader
from data.repositories.factory import RepositoryFactory
```

This creates a mismatch:

| Context | Working Directory | PYTHONPATH | `from core.*` works? |
|---------|-------------------|------------|----------------------|
| Normal execution (`python src/main.py`) | Project root | Includes `src` | ✅ Yes |
| pytest (`python -m pytest`) | Project root | `conftest.py` adds `src` | ✅ Yes |
| Docker container | `/app` | `ENV PYTHONPATH=/app/src` | ✅ Yes |
| **LangGraph CLI** | Project root | Does NOT include `src` | ❌ No |

### Why Not Just Use `from src.core.*`?

We could change all imports to `from src.core.*`, but this would:

1. **Break project convention** - 57+ files use `from core.*` pattern
2. **Create maintenance burden** - Two import styles to maintain
3. **Cause confusion** - Some files using `from core.*`, others using `from src.core.*`
4. **Break existing tests** - All tests assume `src` is in PYTHONPATH

### The Solution: Bootstrap Wrapper

Instead of changing all source files, we created a **bootstrap module** that:

1. **Runs first** when LangGraph loads the graph
2. **Adds `src` to `sys.path`** before any project imports
3. **Uses project-standard imports** (`from core.*`)
4. **Re-exports the agent** for LangGraph to consume

```
langgraph dev
    │
    ▼ reads langgraph.json
    │
    ▼ imports "./src/core/langgraph_bootstrap.py:agent"
    │
    ├─► langgraph_bootstrap._setup_python_path()
    │       └─► sys.path.insert(0, 'G:/..../src')
    │
    ├─► from core.stock_assistant_agent import create_stock_assistant_agent
    │       └─► Works because 'src' is now in sys.path!
    │
    └─► agent = create_stock_assistant_agent()
            └─► Compiled graph ready for Studio
```

### Bootstrap Code Explained

```python
# src/core/langgraph_bootstrap.py

import sys
from pathlib import Path

def _setup_python_path() -> None:
    """Add src directory to sys.path for project imports."""
    bootstrap_dir = Path(__file__).resolve().parent  # src/core
    src_dir = bootstrap_dir.parent                    # src
    src_path = str(src_dir)
    
    if src_path not in sys.path:
        sys.path.insert(0, src_path)  # Add at front for priority

# Execute BEFORE any project imports
_setup_python_path()

# Now project-standard imports work!
from core.stock_assistant_agent import create_stock_assistant_agent

def get_agent():
    """Factory function for agent creation."""
    return create_stock_assistant_agent()

# Module-level export for LangGraph
agent = get_agent()
```

### Why This Approach Works

| Benefit | Explanation |
|---------|-------------|
| **Minimal changes** | Only 1 new file + 2 small edits |
| **Preserves conventions** | All 57+ source files unchanged |
| **Isolated concern** | LangGraph context separated from normal execution |
| **Testable** | Bootstrap has its own integration tests |
| **Future-proof** | Works with LangGraph updates |

---

## Development Workflows

### 1. Interactive Agent Testing

**Use Case**: Test agent responses to different queries

1. Start Studio: `langgraph dev`
2. Open Studio UI in browser
3. Select `stock_assistant` graph
4. Use the chat panel to send messages:
   ```
   What is the current price of AAPL?
   ```
5. Watch the agent:
   - Process your message
   - Decide which tools to use
   - Execute tool calls
   - Generate response

### 2. Debugging Tool Execution

**Use Case**: Understand why a tool is failing or returning unexpected results

1. Send a query that uses the tool:
   ```
   Get me detailed information about Microsoft stock
   ```
2. In the trace view, expand the tool call node
3. Inspect:
   - **Input**: What parameters were passed to the tool?
   - **Output**: What did the tool return?
   - **Duration**: How long did it take?
   - **Errors**: Any exceptions raised?

### 3. Prompt Engineering

**Use Case**: Iterate on agent system prompts

1. Modify the system prompt in `src/core/stock_assistant_agent.py`
2. Studio auto-reloads (watch mode is enabled by default)
3. Test the same query and compare responses
4. Use trace view to see exact prompts sent to LLM

### 4. State Inspection

**Use Case**: Debug complex multi-turn conversations

1. Have a multi-turn conversation:
   ```
   User: What stocks are in my watchlist?
   Agent: [lists stocks]
   User: Add NVDA to my watchlist
   Agent: [adds stock]
   User: What's the total value now?
   ```
2. Click any node in the execution graph
3. Inspect the state at that point:
   - Messages history
   - Tool call results
   - Agent reasoning

### 5. Performance Profiling

**Use Case**: Identify slow operations

1. Execute a complex query
2. In trace view, look at timing information
3. Identify bottlenecks:
   - Slow tool calls
   - Long LLM response times
   - Repeated operations

---

## Configuration Reference

### langgraph.json

```json
{
  "$schema": "https://langchain-ai.github.io/langgraph/schemas/langgraph.schema.json",
  "graphs": {
    "stock_assistant": "./src/core/langgraph_bootstrap.py:agent"
  },
  "env": ".env",
  "store": {
    "provider": "mongodb",
    "uri": "mongodb://localhost:27017/stock_assistant"
  }
}
```

| Field | Description |
|-------|-------------|
| `graphs.stock_assistant` | Path to bootstrap module and exported attribute |
| `env` | Environment file for API keys and secrets |
| `store.provider` | Persistence backend (mongodb) |
| `store.uri` | MongoDB connection string |

### Environment Variables

Required in `.env`:

```bash
# LangSmith (optional but recommended)
LANGSMITH_API_KEY=lsv2_pt_...
LANGSMITH_PROJECT=dp-stock-assistant
LANGSMITH_TRACING=true

# OpenAI
OPENAI_API_KEY=sk-...

# MongoDB
MONGODB_URI=mongodb://localhost:27017

# Redis  
REDIS_HOST=localhost
REDIS_PORT=6379
```

### LangGraph CLI Options

```powershell
# Start with specific port
langgraph dev --port 3000

# Start without auto-reload (for debugging)
langgraph dev --no-reload

# Start with verbose logging
langgraph dev --verbose

# Start with specific config file
langgraph dev --config langgraph.json
```

---

## Troubleshooting

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'core'`

**Cause**: Bootstrap not loading correctly

**Solution**: Verify `langgraph.json` points to bootstrap:
```json
"stock_assistant": "./src/core/langgraph_bootstrap.py:agent"
```

---

**Error**: `ModuleNotFoundError: No module named 'src'`

**Cause**: Code still using `from src.core.*` pattern

**Solution**: Revert to project-standard imports:
```python
# Wrong
from src.core.data_manager import DataManager

# Correct
from core.data_manager import DataManager
```

---

### Connection Errors

**Error**: `MongoDB connection failed`

**Cause**: MongoDB not running

**Solution**:
```powershell
docker-compose up -d mongodb
```

---

**Error**: `Redis connection refused`

**Cause**: Redis not running

**Solution**:
```powershell
docker-compose up -d redis
```

---

### Studio Not Loading

**Symptom**: Browser shows blank page or connection error

**Solutions**:
1. Check terminal for errors
2. Verify port 2024 is not in use
3. Try: `langgraph dev --port 3000`
4. Check firewall settings

---

### Agent Not Appearing in Studio

**Symptom**: Graph loads but no agent visible

**Solutions**:
1. Check `langgraph.json` syntax
2. Verify bootstrap exports `agent` at module level
3. Check for exceptions during agent creation in terminal logs

---

## Best Practices

### 1. Use Studio for Development, Not Production

Studio runs an in-memory development server. For production:
- Deploy via LangSmith Deployment
- Or use the Flask API (`src/web/api_server.py`)

### 2. Keep Bootstrap Minimal

The bootstrap module should only:
- Set up `sys.path`
- Import and re-export the agent

Don't add business logic to the bootstrap.

### 3. Test Changes Before Committing

Run integration tests after modifying agent code:
```powershell
python -m pytest tests/test_langsmith_integration.py -v
```

### 4. Use Tracing for Production Debugging

Enable LangSmith tracing to capture production traces:
```bash
LANGSMITH_TRACING=true
```

View traces at: https://smith.langchain.com/

---

## Related Documentation

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Project Architecture](../README.md)
- [Agent Implementation](../src/core/stock_assistant_agent.py)

---

## Changelog

| Date | Change |
|------|--------|
| 2026-01-09 | Initial LangSmith Studio integration |
| 2026-01-09 | Bootstrap approach implemented |
| 2026-01-09 | Integration tests added |
