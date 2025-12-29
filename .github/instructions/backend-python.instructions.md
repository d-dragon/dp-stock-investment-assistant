---
description: Backend API conventions for Python, Flask, MongoDB, Redis, and testing
applyTo: "**/*.py"
---

# Backend API - Python Conventions

## Table of Contents
1. [Quick Reference](#quick-reference)
   - [File Path Map](#file-path-map)
   - [Decision Trees](#decision-tree-i-need-to)
   - [Common Commands](#common-commands-powershell)
   - [Quick Diagnostics](#quick-diagnostics)
   - [Impact Metrics](#impact-before-vs-after-quick-reference)
2. [Architecture Overview](#architecture-overview)
3. [Flask API Patterns](#flask-api-patterns)
   - [Blueprint Factory Pattern](#blueprint-factory-pattern-with-frozen-context)
   - [Standard Error Response Format](#standard-error-response-format)
   - [Server-Sent Events (SSE)](#server-sent-events-sse-for-streaming)
4. [WebSocket Layer (Socket.IO)](#websocket-layer-socketio)
   - [Event Handler Registration](#event-handler-registration-pattern)
   - [Available Events](#available-socketio-events)
   - [Error Handling](#error-handling-best-practices)
5. [Language and Style](#language-and-style)
6. [Import Conventions](#import-conventions)
7. [Configuration Management](#configuration-management-srcutilsconfig_loaderpy)
   - [ConfigLoader Pattern](#configuration-management-srcutilsconfig_loaderpy)
   - [Environment Override Modes](#configuration-management-srcutilsconfig_loaderpy)
   - [Azure Key Vault Integration](#configuration-management-srcutilsconfig_loaderpy)
8. [Database Layer - MongoDB](#database-layer---mongodb)
   - [MongoDB Repository Quick Reference](#mongodb-repository-quick-reference)
9. [Database Layer - Redis](#database-layer---redis)
10. [Cache Backend](#cache-backend-srcutilscachepy)
    - [Cache Invalidation Patterns](#cache-invalidation-patterns)
11. [Service Utilities](#service-utilities-srcutilsservice_utilspy)
12. [Service Layer](#service-layer-srcservices)
    - [Service Layer At-A-Glance](#service-layer-at-a-glance)
    - [BaseService Abstract Class](#baseservice-abstract-class-srcservicesbasepy)
    - [ServiceFactory](#servicefactory-srcservicesfactorypy)
    - [Protocols for Decoupling](#protocols-for-decoupling-srcservicesprotocolspy)
    - [Service Implementation Pattern](#service-implementation-pattern)
    - [Async and Streaming Patterns](#async-and-streaming-patterns)
    - [Available Services](#available-services)
13. [Logging](#logging)
14. [Testing with pytest](#testing-with-pytest)
   - [Protocol-Based Mocking](#protocol-based-mocking-for-services)
   - [Service Test Helper Pattern](#service-test-helper-pattern)
   - [Health Check Testing](#health-check-testing)
   - [WebSocket Testing Patterns](#websocket-testing-patterns)
15. [Model Factory and AI Clients](#model-factory-and-ai-clients-srccoremodel_factorypy)
   - [Client Creation and Caching](#client-creation-and-caching)
   - [Supported Providers](#supported-providers)
   - [Fallback Support](#fallback-support)
   - [Provider Selection Priority](#provider-selection-priority)
   - [Model Client Interface](#model-client-interface)
16. [Data Manager](#data-manager-srccoredatamanagerpy)
17. [Migration and Schema Setup](#migration-and-schema-setup)
18. [Common Backend Tasks](#common-backend-tasks)
   - [Add an API Endpoint](#add-an-api-endpoint)
   - [Extend MongoDB Schema](#extend-mongodb-schema)
   - [Add Model Provider](#add-model-provider)
   - [Add a New Service](#add-a-new-service)
   - [Add a New Repository](#add-a-new-repository)
   - [Add a WebSocket Event Handler](#add-a-websocket-event-handler)
   - [Debug Service Health Check Failures](#debug-service-health-check-failures)
   - [Configure Model Fallback Behavior](#configure-model-fallback-behavior)
19. [Pitfalls and Gotchas](#pitfalls-and-gotchas)
   - [Platform-Specific Issues](#platform-specific-issues)
   - [Common Production Errors](#common-production-errors)
20. [Quick Verification](#quick-verification)

## Quick Reference

### File Path Map
```
src/
├── main.py                          # CLI entry point (local development)
├── wsgi.py                          # WSGI entry (production: gunicorn)
├── web/
│   ├── api_server.py                # Flask app factory
│   ├── routes/
│   │   ├── service_health_routes.py # GET /api/health
│   │   ├── ai_chat_routes.py        # POST /api/chat, /api/chat/stream
│   │   ├── models_routes.py         # GET /api/models, POST /api/models/select
│   │   └── user_routes.py           # GET /api/users/:id, /api/users/:id/dashboard
│   └── sockets/
│       └── chat_events.py           # Socket.IO: chat_message, chat_response
├── services/
│   ├── factory.py                   # ServiceFactory.get_*_service()
│   ├── base.py                      # BaseService (health_check contract)
│   ├── user_service.py              # UserService orchestration
│   ├── workspace_service.py         # WorkspaceService with caching
│   └── symbols_service.py           # SymbolsService for market data
├── data/
│   ├── repositories/
│   │   ├── factory.py               # RepositoryFactory.get_*_repository()
│   │   ├── mongodb_repository.py    # MongoGenericRepository base class
│   │   ├── user_repository.py       # User CRUD operations
│   │   └── workspace_repository.py  # Workspace CRUD operations
│   ├── schema/
│   │   └── schema_manager.py        # JSON schema validation
│   └── migration/
│       └── db_setup.py              # Database initialization script
├── core/
│   ├── agent.py                     # StockAgent (AI orchestration)
│   ├── model_factory.py             # ModelClientFactory
│   └── data_manager.py              # Financial data fetching
└── utils/
    ├── config_loader.py             # ConfigLoader.load_config()
    ├── cache.py                     # CacheBackend.from_config()
    └── service_utils.py             # normalize_document(), batched()

tests/
├── conftest.py                      # Shared pytest fixtures
├── test_*_service.py                # Service layer tests
└── api/
    └── test_*_routes.py             # API endpoint tests
```

### Decision Tree: "I need to..."

<details>
<summary><strong>I need to add a new API endpoint</strong></summary>

1. Create/update blueprint in `src/web/routes/<domain>.py`
2. Add route handler with `APIRouteContext` parameter
3. Register blueprint in `src/web/api_server.py` (if new)
4. Add tests in `tests/api/test_<domain>_routes.py`
5. Update `docs/openapi.yaml`

**See also:**
- [Add an API Endpoint](#add-an-api-endpoint) - Step-by-step workflow
- [Flask API Patterns](#flask-api-patterns) - Blueprint and context patterns
- [Testing with pytest](#testing-with-pytest) - API route testing

</details>

<details>
<summary><strong>I need to add a new service</strong></summary>

1. Create `src/services/<name>_service.py` extending BaseService
2. Implement `health_check()` with `_dependencies_health_report()`
3. Add cache TTL constants as class attributes
4. Define protocol dependencies (from `protocols.py`)
5. Add `get_<name>_service()` to ServiceFactory
6. Export in `src/services/__init__.py`
7. Write tests in `tests/test_<name>_service.py`

**See also:**
- [Add a New Service](#add-a-new-service) - Detailed implementation guide
- [Service Layer](#service-layer-srcservices) - Architecture overview
- [Testing with pytest](#testing-with-pytest) - Service testing patterns

</details>

<details>
<summary><strong>I need to add a new repository</strong></summary>

1. Create schema in `src/data/schema/<entity>_schema.py`
2. Create `src/data/repositories/<name>_repository.py` extending MongoGenericRepository
3. Add `setup_<entity>_collection()` to SchemaManager
4. Add `get_<name>_repository()` to RepositoryFactory
5. Export in `src/data/repositories/__init__.py`
6. Run: `python src\data\migration\db_setup.py`

**See also:**
- [Add a New Repository](#add-a-new-repository) - Complete workflow
- [Database Layer - MongoDB](#database-layer---mongodb) - Repository patterns

</details>

<details>
<summary><strong>I need to add a new AI model provider</strong></summary>

1. Create `src/core/<provider>_client.py` extending BaseModelClient ABC
2. Update `ModelClientFactory.get_client()` in model_factory
3. Add provider config to `config/config.yaml`
4. Update `.github/copilot-model-config.yaml`
5. Add tests for selection and fallback

**See also:**
- [Add Model Provider](#add-model-provider) - Implementation steps
- [Model Factory](#model-factory-and-ai-clients-srccoremodel_factorypy) - Factory patterns

</details>

<details>
<summary><strong>I need to debug a production issue</strong></summary>

**Common issues and quick links:**

- **Service returning 503?**  
  → [Pitfalls #6](#6-service-returning-503-without-clear-reason) | [Debug Health Check](#debug-service-health-check-failures)

- **Model fallback not working?**  
  → [Pitfalls #5](#5-model-fallback-not-triggering) | [Configure Fallback](#configure-model-fallback-behavior)

- **Cache miss storm / performance spike?**  
  → [Pitfalls #1](#1-cache-miss-storms) | [Cache Invalidation Patterns](#cache-invalidation-patterns)

- **Circular import errors?**  
  → [Pitfalls #2](#2-circular-import-errors) | [Service Layer Protocols](#protocols-for-decoupling-srcservicesprotocolspy)

- **MongoDB "not authorized" error?**  
  → [Pitfalls #4](#4-mongodb-not-authorized-on-listcollections) | [Database Layer](#database-layer---mongodb)

- **Health check passes but operations fail?**  
  → [Pitfalls #3](#3-health-check-false-positives) | [BaseService Abstract Class](#baseservice-abstract-class-srcservicesbasepy)

</details>

### Common Commands (PowerShell)

```powershell
# Setup and Environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
cp config\config_example.yaml config\config.yaml
cp .env.example .env

# Development
python src\main.py                                    # Run CLI/web locally
gunicorn -k eventlet -w 1 -b 0.0.0.0:5000 src.wsgi:app  # Production mode

# Testing
python -m pytest -v                                   # All tests
python -m pytest tests/test_agent.py -v               # Specific file
python -m pytest -k "test_agent" -v                   # Pattern match
python -m pytest --cov=src --cov-report=html          # With coverage
python -m pytest -x                                   # Stop on first failure

# Database
docker-compose up -d mongodb redis                    # Start services
python src\data\migration\db_setup.py                 # Run migration
mongo mongodb://localhost:27017/stock_assistant       # Connect to DB

# Docker Compose
docker-compose up --build                             # Build and start all
docker-compose up api frontend                        # Start specific services
docker-compose logs -f api                            # View logs
docker-compose down                                   # Stop and remove
docker-compose down -v                                # Also remove volumes (⚠️ data loss)

# Debugging
python -c "from src.main import main; print('OK')"   # Test imports
python -c "from src.utils.config_loader import ConfigLoader; print(ConfigLoader.load_config())"  # Test config
```

### Quick Diagnostics

**Problem: `ModuleNotFoundError: No module named 'src'`**
```powershell
# Solution: Add src to PYTHONPATH
$env:PYTHONPATH = "$PWD\src"
# Or in VS Code, ensure workspace root is g:\00_Work\Projects\dp-stock-investment-assistant
```

**Problem: `pymongo.errors.OperationFailure: not authorized on stock_assistant to execute command { listCollections...`**
```python
# Solution: Use db.command() pattern with fallback
try:
    result = db.command("listCollections")
    collections = [c['name'] for c in result['cursor']['firstBatch']]
except Unauthorized:
    logger.warning("Using known collection names")
    collections = ['market_data', 'symbols', 'users']  # Known schema
```

**Problem: Service returns 503 "Service unavailable"**
```python
# Solution: Check service health_check() implementation
healthy, details = service.health_check()
if not healthy:
    logger.error(f"Service unhealthy: {details}")
    # Check required dependencies in details['dependencies']
```


## Architecture Overview

This backend follows a **layered architecture** with clear separation of concerns:

**Layer Flow**: Configuration → Data Layer → Service Layer → API Layer

- **Configuration Layer** (`src/utils/config_loader.py`): Hierarchical config loading with environment overlays and Azure Key Vault integration
- **Data Layer** (`src/data/`): MongoDB repositories (extending `MongoGenericRepository`), Redis cache backend, and schema validation
- **Service Layer** (`src/services/`): Business logic orchestration using protocol-based dependencies for decoupling. All services extend `BaseService` and implement `health_check()`. ServiceFactory provides singleton instances.
- **API Layer** (`src/web/`): Flask blueprints with immutable dependency injection via frozen dataclass contexts (`APIRouteContext`). Routes delegate to services, never accessing databases directly.

**Key Patterns**:
- **Factory Pattern**: `ModelClientFactory`, `RepositoryFactory`, `ServiceFactory` centralize object creation with caching
- **Repository Pattern**: All database access through repositories; no ad-hoc DB queries in routes or services
- **Protocol-Based Dependencies**: Services depend on protocols (structural typing) rather than concrete classes for testability and decoupling
- **Immutable Contexts**: Flask blueprints receive dependencies via frozen dataclasses, preventing accidental mutation

**Dependency Flow Example**:
```
ConfigLoader → RepositoryFactory → ServiceFactory → Blueprint Factory → Flask App
```

This architecture enables independent testing of each layer by mocking dependencies at the boundaries.

## Flask API Patterns

### Blueprint Factory Pattern with Frozen Context
All blueprints use immutable dependency injection via frozen dataclasses to prevent accidental mutation and improve testability.

**📄 Complete Pattern**: [`examples/flask_blueprints/frozen_context_pattern.py`](../../examples/flask_blueprints/frozen_context_pattern.py)

<details>
<summary><strong>Blueprint Factory Example (click to expand)</strong></summary>

```python
from dataclasses import dataclass
from typing import TYPE_CHECKING, Mapping, Any

if TYPE_CHECKING:
    from flask import Flask
    from core.agent import StockAgent
    from logging import Logger

@dataclass(frozen=True)
class APIRouteContext:
    """Immutable context for HTTP route blueprints."""
    app: "Flask"
    agent: "StockAgent"
    config: Mapping[str, Any]
    logger: "Logger"
    # ... additional dependencies (services, helpers)

def create_chat_blueprint(context: APIRouteContext) -> Blueprint:
    blueprint = Blueprint("chat", __name__)
    agent = context.agent  # Unpack at function level
    logger = context.logger.getChild("chat")
    
    @blueprint.route('/chat', methods=['POST'])
    def chat():
        data = request.get_json()
        message = data.get('message', '').strip()
        response = agent.process_query(message)
        return jsonify({"response": response}), 200
    
    return blueprint
```

**Registration in `src/web/api_server.py`**:
```python
from web.routes.shared_context import APIRouteContext
from web.routes.ai_chat_routes import create_chat_blueprint

context = APIRouteContext(
    app=self.app,
    agent=self.agent,
    config=self.config,
    logger=self.logger,
)

blueprint = create_chat_blueprint(context)
self.app.register_blueprint(blueprint, url_prefix="/api")
```
</details>

### Standard Error Response Format
All routes return JSON errors with consistent structure: 4xx for client errors, 5xx for server errors, 503 when dependencies fail health checks.

**📄 Complete Examples**: See error handling in [`examples/testing/test_api_routes.py`](../../examples/testing/test_api_routes.py) (validation errors, 503/500 responses)

**Security**: Never expose internal details (stack traces, database errors, API keys) in client-facing error responses.

### Server-Sent Events (SSE) for Streaming
For real-time chat streaming, use SSE with proper headers and `stream_with_context`.

**📄 Complete Pattern**: [`examples/flask_blueprints/sse_streaming.py`](../../examples/flask_blueprints/sse_streaming.py)

<details>
<summary><strong>SSE Streaming Example (click to expand)</strong></summary>

```python
from flask import Response, stream_with_context
import json

SSE_HEADERS = {
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Access-Control-Allow-Origin': '*'  # Or specific origin in production
}

@blueprint.route('/chat/stream', methods=['POST'])
def chat_stream():
    data = request.get_json()
    message = data.get('message', '').strip()
    
    def generate():
        try:
            for chunk in agent.process_query_streaming(message):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        except Exception as e:
            logger.error(f"Stream error: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': 'Stream interrupted'})}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers=SSE_HEADERS
    )
```

**Frontend Consumption**:
```javascript
const eventSource = new EventSource('/api/chat/stream');
eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data.chunk);
};
```
</details>

**See Also**:
- [WebSocket Layer (Socket.IO)](#websocket-layer-socketio) - Socket.IO event patterns for real-time bidirectional communication
- [Common Backend Tasks > Add an API Endpoint](#add-an-api-endpoint) - Step-by-step workflow for creating new routes
- [Testing with pytest](#testing-with-pytest) - API route testing patterns with Flask test client

## WebSocket Layer (Socket.IO)

### Event Handler Registration Pattern
Socket.IO events use the same frozen context pattern as HTTP blueprints.

**📄 Complete Patterns**: 
- Registration: [`examples/socketio/chat_events_registration.py`](../../examples/socketio/chat_events_registration.py)
- Error Handling: [`examples/socketio/error_handling.py`](../../examples/socketio/error_handling.py)

<details>
<summary><strong>WebSocket Event Handler Example (click to expand)</strong></summary>

```python
from dataclasses import dataclass
from flask_socketio import SocketIO, emit

@dataclass(frozen=True)
class SocketIOContext:
    """Immutable context for Socket.IO event handlers."""
    socketio: SocketIO
    agent: "StockAgent"
    config: Mapping[str, Any]
    logger: "Logger"

def register_chat_events(context: SocketIOContext) -> None:
    socketio = context.socketio
    agent = context.agent
    logger = context.logger
    
    @socketio.on('connect')
    def handle_connect():
        logger.info('Client connected')
        emit('status', {'message': 'Connected to stock assistant'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info('Client disconnected')
    
    @socketio.on('chat_message')
    def handle_chat_message(data):
        try:
            message = data.get('message', '').strip()
            if not message:
                emit('error', {'message': 'Message cannot be empty'})
                return
            
            response = agent.process_query(message)
            emit('chat_response', {'response': response})
        except Exception as exc:
            logger.error(f"Chat error: {exc}", exc_info=True)
            emit('error', {'message': 'Failed to process message'})
```

**Registration in `src/web/api_server.py`**:
```python
from web.sockets.chat_events import register_chat_events

context = SocketIOContext(
    socketio=self.socketio,
    agent=self.agent,
    config=self.config,
    logger=self.logger,
)
register_chat_events(context)
```
</details>

### Available Socket.IO Events
| Event | Direction | Payload | Description |
|-------|-----------|---------|-------------|
| `connect` | Client → Server | - | Client connection established |
| `disconnect` | Client → Server | - | Client disconnected |
| `chat_message` | Client → Server | `{"message": str}` | Send chat message to agent |
| `chat_response` | Server → Client | `{"response": str}` | AI response from agent |
| `status` | Server → Client | `{"message": str}` | Connection status update |
| `error` | Server → Client | `{"message": str}` | Error notification |

**Frontend Configuration**: Event names defined in `frontend/src/config.ts` under `API_CONFIG.WEBSOCKET.EVENTS`.

### Error Handling Best Practices
Always emit errors to client; avoid silent failures. Validate inputs before processing, catch specific exceptions, and log errors with context.

**📄 Complete Examples**: [`examples/socketio/error_handling.py`](../../examples/socketio/error_handling.py) (validation decorators, structured error emission)

**See Also**:
- [Flask API Patterns](#flask-api-patterns) - HTTP route blueprints with similar context pattern
- [Common Backend Tasks > Add a WebSocket Event Handler](#add-a-websocket-event-handler) - Step-by-step workflow
- [Testing with pytest](#testing-with-pytest) - WebSocket handler testing patterns

## Language and Style
- **Python Version**: 3.8+ required
- **Style Guide**: PEP 8 compliance
- **Type Hints**: Use for function signatures and public APIs
- **Docstrings**: Required for modules, classes, and public functions (Google or NumPy style)
- **Immutable Contexts**: Prefer `dataclasses` with `frozen=True` for dependency injection

## Import Conventions
- **Absolute Imports**: Always use `from .*` for application code
- **Avoid Relative Imports**: They break tests and packaging; exceptions only for deeply nested internal modules
- **Import Order**: stdlib → third-party → local, sorted alphabetically within groups

## Configuration Management (`src/utils/config_loader.py`)
- **ConfigLoader Pattern**:
  1. Load base `config/config.yaml`
  2. Apply environment overlay (e.g., `config.k8s-local.yaml` based on `APP_ENV`)
  3. Apply environment variable overrides
  4. Optionally fetch secrets from Azure Key Vault
- **Environment Override Modes**:
  - `CONFIG_ENV_OVERRIDE_MODE=all` (default for `APP_ENV=local`): all env vars applied
  - `CONFIG_ENV_OVERRIDE_MODE=secrets-only` (default for k8s-local/staging/production): only API keys/passwords
  - `CONFIG_ENV_OVERRIDE_MODE=none`: skip env overrides entirely
- **Env Normalization**: `APP_ENV` values like `dev`, `local`, `k8s`, `staging`, `prod` are normalized internally
- **Azure Key Vault** (optional):
  - Enable with `USE_AZURE_KEYVAULT=true` and `AZURE_KEYVAULT_URI` or `KEYVAULT_NAME`
  - Secrets: `OPENAI_API_KEY`, `GROK_API_KEY`, `ALPHA_VANTAGE_API_KEY`, `REDIS_PASSWORD`, `MONGODB_PASSWORD`

## Database Layer - MongoDB
- **Connection**: Use PyMongo 4.10.1+ with `MONGODB_URI` from env/config
- **Auth Pattern**: SCRAM-SHA-256; specify `authSource` in connection string
- **Collection Discovery**: Use `db.command("listCollections")` with error handling; DO NOT use `list_collection_names()` (may raise Unauthorized in restricted contexts)
- **Fallback Pattern**:
  ```python
  try:
      result = db.command("listCollections")
      collections = [c['name'] for c in result['cursor']['firstBatch']]
  except Unauthorized:
      logger.warning("Unauthorized to list collections; assuming known collections exist")
      collections = ['market_data', 'symbols', 'fundamental_analysis']  # known schema
  ```
- **Collections** (organized by domain):
  - **User & Auth**: `users`, `user_profiles`, `user_preferences`, `accounts`, `sessions`, `groups`
  - **Workspaces & Organization**: `workspaces`, `watchlists`, `portfolios`, `positions`
  - **Market Data**: `market_data` (time-series), `symbols`, `market_snapshots`, `technical_indicators`
  - **Analysis & Reports**: `fundamental_analysis`, `analyses`, `reports`, `investment_reports`
  - **Investment Management**: `investment_ideas`, `investment_styles`, `strategies`, `rules_policies`, `trades`
  - **Collaboration**: `chats`, `notes`, `tasks`, `notifications`, `news_events`
- **Repository Pattern**: Centralize all DB access in `src/data/repositories/`; avoid ad-hoc queries in routes
  - **MongoGenericRepository** (`mongodb_repository.py`): Base class with CRUD operations
    - Provides `find_one()`, `find_many()`, `insert_one()`, `update_one()`, `delete_one()`
    - Handles ObjectId conversion and document normalization
    - All domain repositories extend this base class
  - **RepositoryFactory** (`factory.py`): Central wiring of database → repositories
    ```python
    from data.repositories.factory import RepositoryFactory
    repo_factory = RepositoryFactory(db, config)
    user_repo = repo_factory.get_user_repository()  # Singleton, auto-wired
    ```
    - Singleton pattern prevents duplicate repository instances
    - Provides `health_check()` for database connectivity status
- **Schema Validation**: Apply JSON schema in `src/data/schema/schema_manager.py`
- **Indexes**: Define in migration script; use compound indexes for common queries

### MongoDB Repository Quick Reference

`MongoGenericRepository` base class provides:

| Method | Signature | Description |
|--------|-----------|-------------|
| `find_one` | `find_one(filter: Dict) -> Optional[Dict]` | Returns single document or None |
| `find_many` | `find_many(filter: Dict, limit: int, skip: int) -> List[Dict]` | Returns list of documents |
| `insert_one` | `insert_one(document: Dict) -> str` | Returns inserted document ID |
| `update_one` | `update_one(id: str, updates: Dict) -> Dict` | Returns updated document |
| `delete_one` | `delete_one(id: str) -> bool` | Returns success boolean |
| `count` | `count(filter: Dict) -> int` | Returns document count |
| `health_check` | `health_check() -> Tuple[bool, Dict]` | Tests database connectivity |

**Usage**: All domain repositories extend this base class (e.g., `UserRepository`, `WorkspaceRepository`).

## Database Layer - Redis
- **Connection**: Configure via `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_PASSWORD`, `REDIS_SSL`
- **TTL Strategy** (from config):
  - `price_data`: 60s
  - `historical_data`: 3600s (1h)
  - `fundamental_data`: 86400s (24h)
  - `technical_data`: 900s (15m)
  - `reports`: 43200s (12h)
- **Testing**: Mock Redis in tests; avoid real connections

## Cache Backend (`src/utils/cache.py`)
- **Factory Creation**: Use `CacheBackend.from_config(config)` to instantiate with Redis or in-memory fallback
- **Dual Backend Strategy**: Automatically falls back to in-memory cache if Redis is unavailable
- **JSON Helpers**:
  - `get_json(key)` / `set_json(key, value, ttl)` for serialized data
  - Auto-handles ObjectId and datetime serialization
- **Health Check**: `is_healthy()` returns `bool`; `health_check()` returns `Tuple[bool, Dict]` with component details
- **Memory Cache**: Uses expiry timestamps; cleans up on `get()` if expired
- **Usage Pattern**:
  ```python
  from utils.cache import CacheBackend
  cache = CacheBackend.from_config(config)
  cache.set_json("user:123", user_data, ttl=300)
  data = cache.get_json("user:123")  # Returns None if expired/missing
  ```

### Cache Invalidation Patterns
Proper cache invalidation prevents stale data, cache storms, and memory bloat.

**Cache Key Naming Conventions**:
- **Entity prefix pattern**: `{entity}:{id}:{attribute}` (e.g., `user:123:profile`, `workspace:456:settings`)
- **Use `:` separators**: Enables pattern matching for bulk invalidation (`workspace:123:*`)
- **Avoid spaces**: Use underscores for compound keys (`market_data:AAPL:daily`)
- **Include version**: For schema changes, append version (`user:123:profile:v2`)

**TTL Jitter Pattern** (Prevent Thundering Herd):
```python
import random
from services.workspace_service import WorkspaceService

class WorkspaceService:
    BASE_TTL = 300  # 5 minutes
    
    def cache_workspace(self, workspace_id, data):
        # Add 0-60s jitter to prevent synchronized expiry
        jitter = random.randint(0, 60)
        ttl = self.BASE_TTL + jitter
        self.cache.set_json(f"workspace:{workspace_id}", data, ttl_seconds=ttl)
```

**Lock-Based Request Coalescing**:
Prevent multiple concurrent requests from fetching the same uncached data. See [Pitfalls and Gotchas > Cache Miss Storms](#1-cache-miss-storms) for complete implementation.

```python
import threading

class UserService:
    _fetch_locks = {}  # Class-level lock dictionary
    
    def get_user(self, user_id, use_cache=True):
        lock = self._fetch_locks.setdefault(user_id, threading.Lock())
        
        with lock:
            # Double-check cache after acquiring lock
            cached = self.cache.get_json(f"user:{user_id}")
            if cached:
                return cached  # Another thread populated cache
            
            # Only one thread fetches from database
            user = self._user_repository.find_one({"_id": user_id})
            self.cache.set_json(f"user:{user_id}", user, ttl_seconds=300)
            return user
```

**Write-Through vs Write-Behind Invalidation**:
- **Write-through**: Update cache immediately on write (strong consistency, slower writes)
  ```python
  def update_user(self, user_id, updates):
      updated_user = self._user_repository.update_one(user_id, updates)
      self.cache.set_json(f"user:{user_id}", updated_user, ttl_seconds=300)  # Update cache
      return updated_user
  ```
- **Write-behind**: Invalidate cache on write, lazy-load on next read (eventual consistency, faster writes)
  ```python
  def update_user(self, user_id, updates):
      updated_user = self._user_repository.update_one(user_id, updates)
      self.cache.delete(f"user:{user_id}")  # Invalidate, will reload on next get_user()
      return updated_user
  ```

**Bulk Invalidation Strategies**:
```python
# User-level: Invalidate all user-related keys
def invalidate_user_cache(self, user_id):
    keys_to_delete = [
        f"user:{user_id}",
        f"user:{user_id}:profile",
        f"user:{user_id}:preferences",
        f"user:{user_id}:dashboard"
    ]
    for key in keys_to_delete:
        self.cache.delete(key)

# Workspace-level: Invalidate all workspace-related keys
def invalidate_workspace_cache(self, workspace_id):
    # If using Redis, can use pattern matching
    if hasattr(self.cache, 'delete_pattern'):
        self.cache.delete_pattern(f"workspace:{workspace_id}:*")
    else:
        # Fallback: manual list of known keys
        keys = [f"workspace:{workspace_id}", f"workspace:{workspace_id}:settings"]
        for key in keys:
            self.cache.delete(key)
```


## Service Utilities (`src/utils/service_utils.py`)
- **`normalize_document(doc, id_fields=("_id",))`**: Convert MongoDB documents to JSON-safe format
  - Converts `ObjectId` to string, `datetime` to ISO format
  - Handles nested structures recursively
- **`batched(iterable, chunk_size)`**: Yield fixed-size chunks for streaming responses
  ```python
  for batch in batched(records, chunk_size=10):
      yield batch  # Returns lists of up to 10 items
  ```
- **`LoggingMixin`** (`src/utils/logging.py`): Provides `self.logger` property with auto-generated name (`module.ClassName`)
  - Supports explicit logger injection via constructor
  - All services inherit this via `BaseService`

## Service Layer (`src/services/`)
The service layer orchestrates business logic, combining repositories, caching, and cross-service dependencies.

### Service Layer At-A-Glance

| Pattern | Description | Implementation |
|---------|-------------|----------------|
| **Base Class** | All services extend `BaseService` | `from services.base import BaseService` |
| **Health Check** | Required method returning `(bool, dict)` | `def health_check(self) -> Tuple[bool, Dict[str, Any]]` |
| **Dependencies** | Use protocols for cross-service calls | `workspace_provider: WorkspaceProvider` (not concrete class) |
| **Factory Creation** | Singleton via `ServiceFactory` | `service_factory.get_user_service()` |
| **Caching** | Built-in cache via `self.cache` property | `self.cache.get_json(key)`, `self.cache.set_json(key, val, ttl)` |
| **Logging** | Auto-generated logger via `LoggingMixin` | `self.logger.info("message")` |
| **Time Provider** | Injectable clock via `self._utc_now()` | Enables deterministic testing with frozen time |
| **TTL Constants** | Class-level cache expiry settings | `WORKSPACE_CACHE_TTL = 300` |
| **Async Wrappers** | Suffix `_async` for async versions | `list_workspaces()` → `list_workspaces_async()` |

**Key Conventions**:
- Required dependencies = concrete types (repositories)
- Optional dependencies = protocols (other services) or `Optional[Type]`
- Optional failures don't mark service unhealthy
- Use `_dependencies_health_report(required={...}, optional={...})` helper

### Design Principles
- **Single Responsibility**: Each service owns one domain (users, workspaces, symbols)
- **Protocol-Based Dependencies**: Cross-service calls use protocols, not concrete types (see `src/services/protocols.py`)
- **Health Check Contract**: All services implement `health_check() -> Tuple[bool, Dict[str, Any]]`
- **Cache-Aware**: Built-in cache integration with TTL constants and invalidation helpers

### BaseService Abstract Class (`src/services/base.py`)
All services extend `BaseService(LoggingMixin, ABC)`:
- **Provides**: `self.logger`, `self.cache`, `self._utc_now()` (injectable time provider)
- **Requires**: `health_check()` implementation returning `(healthy: bool, details: dict)`
- **Health Aggregation**: `_dependencies_health_report(required={...}, optional={...})` aggregates component health
- **Optional vs Required**: Failed optional dependencies don't mark service unhealthy

### ServiceFactory (`src/services/factory.py`)
Central wiring of repositories into services with singleton pattern.

**📄 Complete Example**: See usage in [`examples/repository_factory_usage.py`](../../examples/repository_factory_usage.py)

**Key Features**:
- **Singleton Pattern**: Services cached in `_services` dict; created once per factory
- **Repository Delegation**: Lazy-creates repositories via `RepositoryFactory`
- **Logger Hierarchy**: Child loggers (`parent.service_name`) for service-specific logging
- **Protocol Wiring**: Services receive other services as protocols for decoupling
- **Health Aggregation**: Built-in health check patterns (see [Health Check Testing](#health-check-testing))

<details>
<summary><strong>ServiceFactory Usage Example (click to expand)</strong></summary>

```python
from services.factory import ServiceFactory
from data.repositories.factory import RepositoryFactory

repo_factory = RepositoryFactory(db, config)
service_factory = ServiceFactory(config, repository_factory=repo_factory, cache_backend=cache)

user_service = service_factory.get_user_service()      # Singleton, auto-wired
workspace_service = service_factory.get_workspace_service()
```
</details>

### Protocols for Decoupling (`src/services/protocols.py`)
Use structural subtyping for cross-service dependencies to avoid circular imports and improve testability.

**Key Benefits**:
- **Structural Subtyping**: Duck typing via `@runtime_checkable` and `Protocol`
- **Avoids Circular Dependencies**: `UserService` depends on `WorkspaceProvider` protocol, not concrete `WorkspaceService`
- **Testability**: Any mock implementing required methods satisfies the protocol

**📄 Complete Pattern**: [`examples/services/protocol_based_di.py`](../../examples/services/protocol_based_di.py)

### Service Implementation Pattern
All services extend `BaseService` with health checks, caching, and protocol-based dependencies.

**📄 Complete Pattern**: [`examples/services/health_check_implementation.py`](../../examples/services/health_check_implementation.py)

### Async and Streaming Patterns

**Async Wrappers**: Use `run_in_executor` to wrap sync methods for async callers (WebSocket handlers, future async frameworks):
```python
import asyncio
from typing import List, Dict

async def list_items_async(self, user_id: str, *, limit: int = 20) -> List[Dict]:
    """Async wrapper for synchronous list_items method."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: self.list_items(user_id, limit=limit))
```

**Async Method Naming Convention**:
- Sync method: `list_workspaces(user_id, limit=20)`
- Async wrapper: `list_workspaces_async(user_id, limit=20)`
- Pattern: Append `_async` suffix to sync method name

**When to Use Async Wrappers**:
- ✅ WebSocket event handlers requiring concurrent operations
- ✅ Future migration to async frameworks (Quart, FastAPI)
- ✅ Background tasks needing async/await syntax
- ❌ Flask synchronous routes (overhead without benefit)
- ❌ Simple CRUD operations without I/O parallelism

**Streaming Methods**: Use `batched()` utility for chunked iteration (SSE/WebSocket):
```python
from utils.service_utils import batched, normalize_document
from typing import Iterator, List, Dict

def stream_items(self, user_id: str, *, chunk_size: int = 5) -> Iterator[List[Dict]]:
    """Stream items in batches for SSE or WebSocket transmission."""
    records = self._fetch_items(user_id)  # Fetch from repository
    serialized = [normalize_document(doc) for doc in records]  # Convert ObjectId/datetime
    yield from batched(serialized, chunk_size)  # Yield chunks of 5
```

### Available Services
| Service | Domain | Key Methods |
|---------|--------|-------------|
| `UserService` | User orchestration | `get_user()`, `get_user_profile()`, `get_user_dashboard()` |
| `WorkspaceService` | Workspace CRUD | `list_workspaces()`, `create_workspace()`, `stream_workspaces()` |
| `SymbolsService` | Symbol discovery | `search_symbols()`, `get_symbol()`, `stream_symbols()` |

**See Also**:
- [Cache Backend](#cache-backend-srcutilscachepy) - Cache integration and invalidation patterns
- [Common Backend Tasks > Add a New Service](#add-a-new-service) - Step-by-step workflow
- [Pitfalls and Gotchas > Circular Import Errors](#2-circular-import-errors) - Protocol pattern rationale
- [Testing with pytest](#testing-with-pytest) - Service layer testing with protocol mocking

## Logging
- **Prefer Logging Over Print**: Use `logging` module
- **Context in Logs**: Include symbol, user action, request IDs, model name
- **Log Levels**:
  - DEBUG: Verbose internal state (disable in production)
  - INFO: Normal operations, config loading, API calls
  - WARNING: Fallbacks, missing optional features, auth issues
  - ERROR: Exceptions, API failures, data validation errors
- **Sensitive Data**: NEVER log API keys, passwords, full connection strings

## Testing with pytest
- **Framework**: pytest with fixtures in `tests/conftest.py`
- **Mocking**: Mock external APIs (OpenAI, financial APIs, MongoDB, Redis) for deterministic tests
- **Coverage**: Happy path + 1–2 edge cases per function minimum
- **Speed**: Keep tests fast; no network or real DB/Redis by default
- **Test Structure**:
  - `tests/` - Unit tests for core modules
  - `tests/api/` - API endpoint tests (Flask test client)
- **Run Tests**: `python -m pytest -v`
- **PYTHONPATH**: Ensure `src` is on PYTHONPATH if running outside VS Code: `$env:PYTHONPATH = "$PWD\src"`

### Protocol-Based Mocking for Services
Services use protocols for cross-service dependencies, making tests cleaner with structural typing.

**📄 Complete Pattern**: [`examples/testing/test_service_with_protocols.py`](../../examples/testing/test_service_with_protocols.py) demonstrates:
- Mock implementing protocol interfaces (duck typing)
- Service builder helper for consistent construction
- Protocol-based dependency injection in tests
- Testing with protocol mocks vs concrete implementations

### Service Test Helper Pattern
Use a `build_service()` helper for consistent construction and dependency injection in tests.

**📄 Complete Pattern**: See `build_user_service()` helper in [`examples/testing/test_service_with_protocols.py`](../../examples/testing/test_service_with_protocols.py)

### Health Check Testing

**Primary Documentation**: See [BaseService Abstract Class](#baseservice-abstract-class-srcservicesbasepy) for comprehensive implementation patterns including:
- `health_check()` contract and return format
- `_dependencies_health_report()` helper method usage
- Required vs optional dependency handling
- Service health aggregation patterns
- Component-level health reporting

**Testing Patterns**:

**📄 Complete Examples**: [`examples/testing/test_health_checks.py`](../../examples/testing/test_health_checks.py) demonstrates:
- Test all healthy state (baseline)
- Test required dependency failures (service becomes unhealthy)
- Test optional dependency failures (service stays healthy, degraded mode)
- Test uninitialized dependencies (None values)
- Test component detail aggregation with MagicMock
- ✅ Use MagicMock with `health_check.return_value = (bool, dict)`

**Common Fixtures**:
```python
@pytest.fixture
def healthy_repository():
    """Repository that passes health check."""
    repo = MagicMock()
    repo.health_check.return_value = (True, {"status": "ready"})
    return repo

@pytest.fixture
def unhealthy_repository():
    """Repository that fails health check."""
    repo = MagicMock()
    repo.health_check.return_value = (
        False, 
        {"error": "Database connection failed"}
    )
    return repo
```

### WebSocket Testing Patterns

WebSocket testing requires different patterns than REST API testing due to bidirectional communication and event-driven architecture.

**📄 Complete Examples**: [`examples/testing/test_websocket_handlers.py`](../../examples/testing/test_websocket_handlers.py)

**Testing Approaches**:

- **Mock Socket.IO Client Setup**: Use `SocketIOTestClient` fixture for integration tests (tests full event flow) or `MagicMock` for unit tests (fast, isolated handler logic)

- **Testing Event Handlers (Unit Tests)**: Extract handler from `mock_socketio.on()` calls, invoke with test data, verify `emit()` called with expected event and payload

- **Testing Connection Events (Integration Tests)**: Use `socketio_test_client.connect()`, verify received events with `get_received()`, test cleanup on disconnect

- **Testing Streaming Events**: Mock agent to return iterator, emit streaming start event, filter received events for chunks, verify chunk order and completion event

**Key Testing Patterns**:
- ✅ Use `SocketIOTestClient` for integration tests (full event flow)
- ✅ Use `MagicMock` for unit tests (fast, isolated handler logic)
- ✅ Test connection lifecycle (connect, disconnect, reconnect)
- ✅ Test input validation and error emission
- ✅ Test streaming with multiple chunk assertions
- ✅ Verify cleanup (listeners removed, resources released)

**See Also**:
- [WebSocket Layer (Socket.IO)](#websocket-layer-socketio) - Event handler registration patterns and frozen context usage
- [Common Backend Tasks > Add a WebSocket Event Handler](#add-a-websocket-event-handler) - Step-by-step guide for implementing new handlers

## Model Factory and AI Clients (`src/core/model_factory.py`)

### Client Creation and Caching
`ModelClientFactory` creates provider-specific clients with automatic caching to avoid redundant initialization:

```python
from core.model_factory import ModelClientFactory

# Primary client (from config model.provider)
client = ModelClientFactory.get_client(config)

# Override provider for specific request
client = ModelClientFactory.get_client(config, provider="grok")

# Override both provider and model
client = ModelClientFactory.get_client(config, provider="openai", model_name="gpt-4-turbo")
```

**Cache Key Format**: `{provider}:{model_name}`
- Examples: `"openai:gpt-4"`, `"grok:grok-beta"`
- Cache stored in `ModelClientFactory._CACHE` class variable
- Clear cache: `ModelClientFactory.clear_cache()` or `ModelClientFactory.clear_cache(provider="openai")`

### Supported Providers
| Provider | Client Class | Config Section | Model Examples |
|----------|-------------|----------------|----------------|
| `openai` | `OpenAIModelClient` | `config['openai']` | `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo` |
| `grok` | `GrokModelClient` | `config['grok']` | `grok-beta`, `grok-vision-beta` |

**Extensibility**: Add new providers by:
1. Create `<Provider>ModelClient` class extending `BaseModelClient`
2. Implement `generate()` and `generate_stream()` methods
3. Register in `ModelClientFactory.get_client()` provider selection logic

### Fallback Support
Configure automatic fallback when primary model fails (rate limits, API errors):

**Configuration** (`config/config.yaml`):
```yaml
model:
  provider: openai        # Primary provider
  allow_fallback: true    # Enable fallback
  fallback_order:         # Fallback sequence
    - openai
    - grok
```

**Retrieval**:
```python
fallback_sequence = ModelClientFactory.get_fallback_sequence(config)
# Returns: ["openai", "grok"]
```

**Agent Integration**: `StockAgent` in `src/core/agent.py` automatically retries with fallback models when primary fails. See logs for "Attempting fallback to {provider}" messages.

### Provider Selection Priority
Model provider determined by (highest to lowest priority):
1. **Per-request override**: `ModelClientFactory.get_client(config, provider="grok")`
2. **Cached user selection**: User preference stored in `cache["openai_config:model_name"]`
3. **Config default**: `config['model']['provider']` or `MODEL_PROVIDER` env var
4. **Hardcoded fallback**: `"openai"` if all else fails

### Model Client Interface
All clients extend `BaseModelClient` abstract base class (ABC), not Protocol.

**ABC vs Protocol in this codebase**:
- **ABC (Abstract Base Class)**: Used for `BaseModelClient` with `@abstractmethod` decorators to enforce implementation contracts at instantiation time
- **Protocol**: Used for service dependencies (e.g., `WorkspaceProvider`, `UserProvider`) for structural subtyping without inheritance
- **Why ABC here**: Model clients have shared initialization and caching logic in the base class; strict contract enforcement prevents runtime errors

```python
from abc import ABC, abstractmethod
from typing import Iterator

class BaseModelClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Synchronous generation. Subclasses MUST implement."""
        ...
    
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Streaming generation for SSE. Subclasses SHOULD implement for real-time responses."""
        ...
```

### Debug Mode
Enable prompt logging for local debugging (⚠️ **Never in production**):
```bash
# In .env (local development only)
MODEL_DEBUG_PROMPT=true
```

Logs will show:
```
DEBUG - Prompt sent to openai:gpt-4: "What is the price of AAPL?"
DEBUG - Response received: "The current price of Apple Inc. (AAPL) is..."
```

**Security Warning**: Prompts may contain sensitive user data. Only enable for local debugging.

**See Also**:
- [Common Backend Tasks > Configure Model Fallback Behavior](#configure-model-fallback-behavior) - Fallback debugging workflow
- [Pitfalls and Gotchas > Model Fallback Not Triggering](#5-model-fallback-not-triggering) - Common configuration issues
- [Architecture Overview](#architecture-overview) - Model factory role in system design

## Data Manager (`src/core/data_manager.py`)
- Abstracts financial data fetching (Yahoo Finance, Alpha Vantage)
- Caches API responses in Redis when enabled
- Returns standardized data structures for agent consumption

## Migration and Schema Setup
- **Run Migration**: `python src\data\migration\db_setup.py`
- Creates collections, applies validation schemas, creates indexes
- Idempotent: safe to run multiple times
- **Windows Port Note**: If 27017 is blocked, use `docker-compose.override.yml` to map host 27034 → container 27017; update `MONGODB_URI` accordingly

## Common Backend Tasks
### Add an API Endpoint
Create new REST API endpoints following the blueprint factory pattern with dependency injection.

1. **Create/update blueprint** in `src/web/routes/<domain>.py`  
   Organize related endpoints by domain (e.g., `user_routes.py`, `chat_routes.py`, `models_routes.py`)

2. **Add route handler with APIRouteContext parameter**  
   Use frozen dataclass for dependency injection:
   ```python
   def create_chat_blueprint(context: APIRouteContext) -> Blueprint:
       blueprint = Blueprint("chat", __name__)
       agent = context.agent  # Unpack dependencies
       logger = context.logger.getChild("chat")
       
       @blueprint.route('/chat', methods=['POST'])
       def chat():
           data = request.get_json()
           # Validation, processing, response
   ```

3. **Implement error handling patterns**  
   Return proper HTTP status codes:
   - **2xx**: Success (200 OK, 201 Created)
   - **4xx**: Client errors (400 Bad Request, 404 Not Found)
   - **5xx**: Server errors (500 Internal Server Error, 503 Service Unavailable)
   ```python
   if not message:
       return jsonify({"error": "Message is required"}), 400
   ```

4. **Add request validation**  
   Validate required fields, types, and business logic constraints before processing

5. **Register blueprint in app factory**  
   Add to `src/web/api_server.py` if new blueprint:
   ```python
   from web.routes.chat_routes import create_chat_blueprint
   chat_bp = create_chat_blueprint(context)
   self.app.register_blueprint(chat_bp, url_prefix="/api")
   ```

6. **Update OpenAPI specification**  
   Document endpoint in `docs/openapi.yaml` with request/response schemas

7. **Add pytest tests**  
   Create tests in `tests/api/test_<domain>_routes.py` covering:
   - Success cases (200 responses)
   - Validation errors (400 responses)
   - Not found errors (404 responses)
   - Service unavailable (503 responses)

**📄 Complete Pattern**: [`examples/testing/test_api_routes.py`](../../examples/testing/test_api_routes.py)

**See Also**:
- [Flask API Patterns](#flask-api-patterns) - Blueprint factory pattern with frozen context for dependency injection
- [Testing with pytest](#testing-with-pytest) - API route testing patterns with Flask test client and mock services

### Extend MongoDB Schema
1. Update repository/schema helpers in `src/data/repositories/` and `src/data/schema/`
2. Follow `db.command("listCollections")` pattern with fallback
3. Add/adjust migration in `src/data/migration/db_setup.py`
4. Document in README if user action required

### Add Model Provider
Add support for new AI model providers (e.g., Anthropic Claude, Google Gemini) by extending the model factory.

**Step 1: Create Model Client extending BaseModelClient ABC**

Create `src/core/<provider>_client.py` implementing required abstract methods:

```python
from abc import ABC, abstractmethod
from typing import Iterator

class MyProviderClient(BaseModelClient):
    """Client for MyProvider AI model."""
    
    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        # Initialize provider SDK client
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Synchronous generation for non-streaming requests."""
        # Call provider API
        response = self._call_api(prompt, stream=False)
        return response.text
    
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Streaming generation for real-time responses."""
        # Stream chunks from provider API
        for chunk in self._call_api(prompt, stream=True):
            yield chunk.text
```

**Step 2: Register in ModelClientFactory**

Update `src/core/model_factory.py` to instantiate new client:

```python
class ModelClientFactory:
    @staticmethod
    def get_client(config, provider=None, model_name=None):
        provider = provider or config.get('model', {}).get('provider', 'openai')
        
        if provider == 'openai':
            return OpenAIModelClient(...)
        elif provider == 'grok':
            return GrokModelClient(...)
        elif provider == 'myprovider':  # New provider
            return MyProviderClient(
                api_key=config['myprovider']['api_key'],
                model=config['myprovider']['model']
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
```

**Step 3: Add Provider Configuration**

Add to `config/config.yaml`:

```yaml
model:
  provider: myprovider  # Set as default or leave as fallback option
  allow_fallback: true
  fallback_order:
    - openai
    - myprovider  # Add to fallback chain

myprovider:
  api_key: ${MYPROVIDER_API_KEY}  # From environment variable
  base_url: https://api.myprovider.com/v1
  model: my-model-name
  timeout: 30
```

**Step 4: Update Copilot Configuration**

Add to `.github/copilot-model-config.yaml` for AI tooling integration:

```yaml
providers:
  - name: myprovider
    models:
      - my-model-name
```

**Step 5: Add Tests**

Create tests in `tests/test_model_factory.py`:

```python
def test_factory_creates_myprovider_client(mock_config):
    mock_config['myprovider'] = {'api_key': 'test-key', 'model': 'my-model'}
    client = ModelClientFactory.get_client(mock_config, provider='myprovider')
    assert isinstance(client, MyProviderClient)

def test_fallback_to_myprovider_when_primary_fails(mock_config):
    mock_config['model']['fallback_order'] = ['openai', 'myprovider']
    # Test fallback logic (see tests/test_agent_fallback.py for patterns)
```

**See Also**:
- [Model Factory and AI Clients](#model-factory-and-ai-clients-srccoremodel_factorypy) - Factory patterns, client creation, and caching strategies
- [Pitfalls > Model Fallback Not Triggering](#5-model-fallback-not-triggering) - Common configuration issues and debugging steps

### Add a New Service
1. **Create service file** `src/services/my_service.py` extending `BaseService`
2. **Define dependencies**: Required repositories (concrete) and optional cross-service (protocols)
3. **Implement `health_check()`** using `_dependencies_health_report(required={...}, optional={...})`
4. **Add cache key helpers** and TTL constants as class attributes
5. **Add builder method** to `ServiceFactory.get_my_service()` with singleton caching
6. **Export in `__init__.py`**: Add to `src/services/__init__.py`
7. **Write tests**: Mock repositories and protocol dependencies; test health check, cache behavior

### Add a New Repository
1. **Create schema file** `src/data/schema/my_entity_schema.py` with validation and indexes
2. **Create repository file** `src/data/repositories/my_repository.py` extending `MongoGenericRepository`
3. **Register in SchemaManager**: Add `setup_my_entity_collection()` method and call in `setup_all_collections()`
4. **Add to RepositoryFactory**: Create `get_my_repository()` builder method
5. **Export in `__init__.py`**: Add to `src/data/repositories/__init__.py`
6. **Run migration**: `python src\data\migration\db_setup.py`

### Add a WebSocket Event Handler
1. **Open `src/web/sockets/chat_events.py`** (or create new module like `trading_events.py`)
2. **Add event handler** inside `register_chat_events()` or new registration function:
   ```python
   @socketio.on('trade_order')
   def handle_trade_order(data):
       try:
           symbol = data.get('symbol')
           quantity = data.get('quantity')
           
           # Validate input
           if not symbol or not quantity:
               emit('error', {'message': 'Symbol and quantity required'})
               return
           
           # Process order (call service)
           result = trading_service.place_order(symbol, quantity)
           emit('trade_confirmation', {'status': 'success', 'order_id': result['id']})
           
       except Exception as exc:
           logger.error(f"Trade order error: {exc}", exc_info=True)
           emit('error', {'message': 'Order processing failed'})
   ```
3. **Register in `src/web/api_server.py`**: If new module, add to event registration calls
4. **Update `frontend/src/config.ts`**: Add event name to `API_CONFIG.WEBSOCKET.EVENTS`
5. **Add frontend handler**: In `frontend/src/services/socketService.ts`, add listener for new event
6. **Add tests**: Create `tests/test_trading_events.py` with mocked socketio and service

### Add a WebSocket Event Handler
1. **Open `src/web/sockets/chat_events.py`** (or create new module like `trading_events.py`)
2. **Add event handler** inside `register_chat_events()` or new registration function:
   ```python
   @socketio.on('trade_order')
   def handle_trade_order(data):
       try:
           symbol = data.get('symbol')
           quantity = data.get('quantity')
           
           # Validate input
           if not symbol or not quantity:
               emit('error', {'message': 'Symbol and quantity required'})
               return
           
           # Process order (call service)
           result = trading_service.place_order(symbol, quantity)
           emit('trade_confirmation', {'status': 'success', 'order_id': result['id']})
           
       except Exception as exc:
           logger.error(f"Trade order error: {exc}", exc_info=True)
           emit('error', {'message': 'Order processing failed'})
   ```
3. **Register in `src/web/api_server.py`**: If new module, add to event registration calls
4. **Update `frontend/src/config.ts`**: Add event name to `API_CONFIG.WEBSOCKET.EVENTS`
5. **Add frontend handler**: In `frontend/src/services/socketService.ts`, add listener for new event
6. **Add tests**: Create `tests/test_trading_events.py` with mocked socketio and service

### Debug Service Health Check Failures
When a route returns `503 Service unavailable`, diagnose service dependencies.

**📄 Complete Guide**: [`examples/troubleshooting/health_check_debugging.py`](../../examples/troubleshooting/health_check_debugging.py)

**Quick Diagnostic**:
```python
from services.factory import ServiceFactory

service = service_factory.get_user_service()
healthy, details = service.health_check()
print(f"Healthy: {healthy}\nDetails: {details}")
# Check details['dependencies'] to see which component failed
```

**Common root causes**: MongoDB disconnected, Redis unavailable, repository missing `health_check()`, optional dependency marked as required.

**See**: [`health_check_debugging.py`](../../examples/troubleshooting/health_check_debugging.py) for 8-step debugging workflow with examples.

### Configure Model Fallback Behavior
When a route returns `503 Service unavailable`, diagnose service dependencies.

**📄 Complete Guide**: [`examples/troubleshooting/health_check_debugging.py`](../../examples/troubleshooting/health_check_debugging.py)

**Quick Diagnostic**:
```python
from services.factory import ServiceFactory

service = service_factory.get_user_service()
healthy, details = service.health_check()
print(f"Healthy: {healthy}\nDetails: {details}")
# Check details['dependencies'] to see which component failed
```

**Common root causes**: MongoDB disconnected, Redis unavailable, repository missing `health_check()`, optional dependency marked as required.

**See**: [`health_check_debugging.py`](../../examples/troubleshooting/health_check_debugging.py) for 8-step debugging workflow with examples.

### Configure Model Fallback Behavior
If fallback models aren't triggering when primary model fails.

**📄 Complete Guide**: [`examples/troubleshooting/fallback_debugging.py`](../../examples/troubleshooting/fallback_debugging.py)

**Quick Config Check**:
```yaml
model:
  provider: openai
  allow_fallback: true   # Must be true
  fallback_order:        # Must have 2+ providers
    - openai
    - grok
```

**Quick Test**:
```python
from core.model_factory import ModelClientFactory

sequence = ModelClientFactory.get_fallback_sequence(config)
print(f"Fallback sequence: {sequence}")  # Should show: ["openai", "grok"]
# Empty list? Check config['model']['allow_fallback'] is true
```

**Expected logs**: `WARNING - Primary model failed...` → `INFO - Attempting fallback to provider=grok`

**See**: [`fallback_debugging.py`](../../examples/troubleshooting/fallback_debugging.py) for config verification, common issues, and manual testing.

**📄 Complete Guide**: [`examples/troubleshooting/fallback_debugging.py`](../../examples/troubleshooting/fallback_debugging.py)

**Quick Config Check**:
```yaml
model:
  provider: openai
  allow_fallback: true   # Must be true
  fallback_order:        # Must have 2+ providers
    - openai
    - grok
```

**Quick Test**:
```python
from core.model_factory import ModelClientFactory

sequence = ModelClientFactory.get_fallback_sequence(config)
print(f"Fallback sequence: {sequence}")  # Should show: ["openai", "grok"]
# Empty list? Check config['model']['allow_fallback'] is true
```

**Expected logs**: `WARNING - Primary model failed...` → `INFO - Attempting fallback to provider=grok`

**See**: [`fallback_debugging.py`](../../examples/troubleshooting/fallback_debugging.py) for config verification, common issues, and manual testing.

**See Also**:
- [Flask API Patterns](#flask-api-patterns) - Blueprint factory pattern with dependency injection via frozen dataclasses
- [WebSocket Layer](#websocket-layer-socketio) - Event handler registration with frozen context and error handling
- [Service Layer](#service-layer-srcservices) - BaseService implementation with health checks and protocol-based dependencies
- [Model Factory and AI Clients](#model-factory-and-ai-clients-srccoremodel_factorypy) - Client creation, caching, and fallback configuration
- [Testing with pytest](#testing-with-pytest) - Comprehensive testing patterns for API routes, services, and WebSocket handlers

## Pitfalls and Gotchas

### Platform-Specific Issues
**Windows Reserved Ports**: 27017 may be blocked by Windows; use alternate host port (27034) via `docker-compose.override.yml`

**MongoDB Unauthorized**: User may lack `listCollections` permission; always catch `Unauthorized` exception and fall back to known collection names (see Database Layer section)

**Relative Imports**: Break pytest discovery and packaging; always use absolute `from .*` imports

**Real API Keys in Tests**: Mock all external services (OpenAI, financial APIs); never use production keys in tests

### Common Production Errors

#### 1. Cache Miss Storms
**Symptom**: Database query spike, slow response times, Redis CPU at 100%, multiple concurrent requests for same data

**Cause**: Many concurrent requests hit uncached data simultaneously (cold start, cache expiry, or cache cleared)

**📄 Complete Solution**: [`examples/troubleshooting/cache_storm_solution.py`](../../examples/troubleshooting/cache_storm_solution.py)

<details>
<summary><strong>Key Pattern - Lock-based request coalescing (click to expand)</strong></summary>

```python
import threading

class WorkspaceService:
    _fetch_locks = {}  # Class-level lock dictionary
    
    def get_workspace(self, workspace_id: str, *, use_cache: bool = True):
        lock = self._fetch_locks.setdefault(workspace_id, threading.Lock())
        
        with lock:
            # Double-check cache after acquiring lock
            cached = self.cache.get_json(cache_key)
            if cached:  # Another thread populated cache
                return cached
            
            # Only one thread fetches from database
            result = self._workspace_repository.find_one({"_id": workspace_id})
            ttl = self.WORKSPACE_CACHE_TTL + random.randint(0, 60)  # Add jitter
            self.cache.set_json(cache_key, result, ttl_seconds=ttl)
            return result
```

**Prevention**: Lock-based coalescing + TTL jitter (0-60s) + cache warming
</details>

**See**: [`cache_storm_solution.py`](../../examples/troubleshooting/cache_storm_solution.py) for problem demonstration, 6-step solution, and benchmarks.

#### 2. Circular Import Errors
**Symptom**: `ImportError: cannot import name 'UserService' from partially initialized module`

**Cause**: Concrete type dependencies between services (e.g., `UserService` imports `WorkspaceService` and vice versa)

**Solution**: Use protocol-based dependencies (see Service Layer - Protocols section). Protocols use structural subtyping (duck typing), so no import of concrete `WorkspaceService` class needed.

**📄 Complete Pattern**: [`examples/services/protocol_based_di.py`](../../examples/services/protocol_based_di.py)

#### 3. Health Check False Positives
**Symptom**: Service reports `"healthy"` but operations fail with database errors or None values

**Cause**: Health check only verifies object exists, not that it's functional

**Solution**: Use `_dependencies_health_report()` helper to actually test dependencies. Don't check `bool(self._user_repository)` (always True), instead call `repo.health_check()` to verify functionality.

**📄 Complete Pattern**: [`examples/services/health_check_implementation.py`](../../examples/services/health_check_implementation.py)

#### 4. MongoDB "Not Authorized" on listCollections
**Symptom**: `pymongo.errors.OperationFailure: not authorized on stock_assistant to execute command { listCollections: 1 }`

**Cause**: User lacks `listCollections` permission in restrictive authentication setups

**Solution**: Use `db.command("listCollections")` with fallback to known collection names on `Unauthorized` exception.

**Prevention**: Grant `listCollections` action in MongoDB role, or always use fallback pattern.

**📄 Complete Pattern**: [`examples/repositories/mongodb_patterns.py`](../../examples/repositories/mongodb_patterns.py)

#### 5. Model Fallback Not Triggering
**Symptom**: Primary model fails with `RateLimitError` or `APIError`, but no fallback attempt; request fails immediately

**Cause**: `allow_fallback: false` in config, or fallback sequence misconfigured

**Debug steps**:
1. **Check `config.yaml`**:
   ```yaml
   model:
     provider: openai
     allow_fallback: true  # ← Must be true
     fallback_order:       # ← Must have 2+ providers
       - openai
       - grok
   ```

2. **Verify fallback sequence**:
   ```python
   sequence = ModelClientFactory.get_fallback_sequence(config)
   if not sequence or len(sequence) < 2:
       print("ERROR: Fallback not configured properly")
   ```

3. **Check provider API keys configured**:
   ```bash
   # In .env
   OPENAI_API_KEY=sk-...
   GROK_API_KEY=xai-...  # Must be present for fallback to work
   ```

4. **Verify agent logs** show fallback attempts:
   ```
   WARNING - Primary model failed: openai:gpt-4 (RateLimitError)
   INFO - Attempting fallback to provider=grok model=grok-beta
   ```

5. **Clear model cache** and retry:
   ```python
   ModelClientFactory.clear_cache()
   ```

#### 6. Service Returning 503 Without Clear Reason
**Symptom**: API returns `{"error": "Service unavailable"}` with no helpful context in logs

**Root causes and solutions**:

**Cause 1: Required dependency unhealthy**
```python
# Check service health details
healthy, details = service.health_check()
if not healthy:
    logger.error(f"Service unhealthy: {details}")
    # Look at details['dependencies'] to see which component failed
```

**Cause 2: ServiceFactory not initialized properly**
```python
# In route handler - verify service exists
if service is None:
    logger.error("Service is None - factory not wired in api_server.py")
    return jsonify({"error": "Service unavailable"}), 503
```

**Cause 3: Service not registered in ServiceFactory**
```python
# Missing in src/services/factory.py
def get_symbols_service(self) -> SymbolsService:
    if "symbols" not in self._services:
        self._services["symbols"] = SymbolsService(
            symbols_repository=self.repository_factory.get_symbols_repository(),
            cache=self.cache_backend,
        )
    return self._services["symbols"]
```

**Cause 4: Logger not propagating errors**
```python
# ❌ BAD: Exception swallowed silently
try:
    result = service.process(data)
except Exception:
    return jsonify({"error": "Service unavailable"}), 503

# ✅ GOOD: Log exception with traceback
try:
    result = service.process(data)
except Exception as exc:
    logger.error(f"Service error: {exc}", exc_info=True)  # Includes traceback
    return jsonify({"error": "Service unavailable"}), 503
```

**Debugging pattern for 503 errors**:
```python
@blueprint.route('/users/<user_id>')
def get_user(user_id):
    # Step 1: Verify service exists
    if context.user_service is None:
        logger.error("user_service is None")
        return jsonify({"error": "Service unavailable"}), 503
    
    # Step 2: Check service health
    healthy, details = context.user_service.health_check()
    if not healthy:
        logger.error(f"user_service unhealthy: {details}")
        return jsonify({"error": "Service unavailable", "details": details}), 503
    
    # Step 3: Proceed with operation
    try:
        user = context.user_service.get_user(user_id)
        return jsonify(user), 200
    except Exception as exc:
        logger.error(f"get_user error: {exc}", exc_info=True)
        return jsonify({"error": "Failed to retrieve user"}), 500
```

**See Also**:
- [Service Layer > BaseService](#service-layer-srcservices) - Health check implementation patterns
- [Cache Backend > Cache Invalidation Patterns](#cache-invalidation-patterns) - Preventing cache storms
- [Model Factory > Fallback Support](#model-factory-and-ai-clients-srccoremodel_factorypy) - Configuring fallback behavior
- [Common Backend Tasks](#common-backend-tasks) - Step-by-step debugging workflows

## Quick Verification
- **Import Check**: `python -c "from src.main import main; from src.wsgi import app; print('OK')"`
- **Agent Streaming** (Python REPL):
  ```python
  from core.agent import StockAgent
  from core.data_manager import DataManager
  from utils.config_loader import ConfigLoader
  cfg = ConfigLoader.load_config(); dm = DataManager(cfg); agent = StockAgent(cfg, dm)
  for chunk in agent.process_query_streaming("Latest news on AAPL"): print(chunk, end="")
  ```
- **Health Check**: `GET /api/health` → `{ "status": "healthy" }`
