Comprehensive overview of the **DP Stock Investment Assistant** project:

---

## 🏗️ Project Overview

This is an **AI-powered stock investment assistant** that combines financial data analysis with Large Language Models (LLMs) — primarily OpenAI GPT and xAI Grok — to answer market questions, analyze stocks, and generate investment insights. It's built as a **microservices-style** application with three main components.

---

## 📁 Backend Architecture (src)

### Core AI Layer (core)

| Component | Role |
|---|---|
| `StockAssistantAgent` | The main **ReAct (Reasoning + Acting) agent** using LangGraph. It orchestrates tools via a reasoning loop to answer stock queries. |
| `ModelClientFactory` | **Factory pattern** — creates AI model clients (OpenAI, Grok) with fallback support and caching (`{provider}:{model_name}` keys). |
| `DataManager` | Fetches stock data via **Yahoo Finance** (`yfinance`) with optional database caching. |
| `ToolRegistry` | Singleton registry for LangChain tools (stock symbol lookup, TradingView analysis, report generation). |
| agent.py | Legacy backward-compat alias (`StockAgent = StockAssistantAgent`). |

### Web Layer (web)

- **Flask app factory** in api_server.py using blueprints (modular route groups)
- **8 route blueprints**: health, chat, models, users, workspaces, sessions, conversations, AI chat
- **Socket.IO** integrated for real-time chat streaming
- **Immutable dataclass `APIRouteContext`** for clean dependency injection into blueprints
- **SSE (Server-Sent Events)** for streaming chat responses

### Service Layer (services)

- All services extend **`BaseService`** with abstract `health_check()` contract
- **`ServiceFactory`** wires repositories into services (DI pattern)
- Domain services: `UserService`, `WorkspaceService`, `SessionService`, `ConversationService`, `ChatService`, `SymbolsService`
- **Runtime reconciliation service** for operator-only maintenance tasks

### Data Layer (data)

- **Repository pattern** — ~20 repositories extending `MongoGenericRepository` (users, sessions, watchlists, portfolios, trades, positions, notes, tasks, etc.)
- **`RepositoryFactory`** centralizes creation and config parsing
- MongoDB with **time-series collections** for market data
- Schema validation and migration scripts in migration
- **Redis** for caching via `CacheBackend` (auto-falls back to in-memory)

### Configuration (config)

- **Hierarchical loading**: base config.yaml → env overlay (`config.local.yaml`, `config.production.yaml`) → env vars → Azure Key Vault
- `ConfigLoader` handles the full chain with `APP_ENV`-driven overlays

---

## 🖥️ Frontend Architecture (frontend)

- **React 18 + TypeScript** (bootstrapped with `react-scripts`)
- **Socket.IO client** for real-time chat
- **REST API client** for health checks and config
- **SSE streaming** for chat responses
- Components: `ModelSelector`, `WebSocketTest`, `MessageFormatter`, `PerformanceProfiler`
- The App.tsx is the main chat interface with message display, streaming, and provider selection

---

## 🐳 Infrastructure & Deployment (IaC)

| Environment | Setup |
|---|---|
| **Local Dev** | Docker Compose — API (port 5000), Agent (port 7000), Frontend (port 3000), MongoDB (27017), Redis (6379) |
| **Production** | AKS (Azure Kubernetes Service) via Helm chart dp-stock |
| **Cloud Provisioning** | Terraform in terraform — creates RG, ACR, AKS with managed identity |
| **CI/CD** | Build → push to ACR → Helm deploy to AKS → health probe verification |

Key Docker images:
- Dockerfile.api — Flask API with gunicorn + eventlet
- Dockerfile.agent — Background worker
- Dockerfile — Nginx serving static React build

---

## 🧪 Testing (tests)

~40+ test files covering:
- **Unit tests**: agent, models, services, repositories, tools, config
- **Integration tests**: API routes, service layer, database, WebSocket
- **Security & performance tests**
- **Mocking strategy**: external APIs, MongoDB, Redis, WebSocket connections mocked out

---

## 🔄 Key Design Patterns

1. **Factory Pattern** — `ModelClientFactory`, `RepositoryFactory`, `ServiceFactory`
2. **Repository Pattern** — All DB access through repositories, never ad-hoc
3. **Dependency Injection** — `APIRouteContext` (immutable dataclass), `ServiceFactory`
4. **Singleton** — `ToolRegistry`, service/repository singletons via factories
5. **ReAct Agent** — LangGraph-based reasoning loop with tool orchestration
6. **Hierarchical Config** — Layered YAML + env vars + cloud secrets

---

## 📚 Spec-Driven Development

The project uses a **Spec Kit** methodology with artifacts in:
- docs — long-lived architecture, ADRs, runbooks
- specs — delivery-scoped feature specs, plans, evidence
- instructions — domain-specific coding conventions

---

## 🧩 Current Branch Info

You're on the **`enhance-agent-prompt-system-followup`** branch, which suggests active work on improving the agent's prompt system. The prompts directory contains Jinja2 templates and system prompt files for the agent.

---

Would you like me to dive deeper into any specific area?