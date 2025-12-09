---
description: Backend API conventions for Python, Flask, MongoDB, Redis, and testing
applyTo: "**/*.py"
---

# Backend API - Python Conventions

## Language and Style
- **Python Version**: 3.8+ required
- **Style Guide**: PEP 8 compliance
- **Type Hints**: Use for function signatures and public APIs
- **Docstrings**: Required for modules, classes, and public functions (Google or NumPy style)
- **Immutable Contexts**: Prefer `dataclasses` with `frozen=True` for dependency injection

## Import Conventions
- **Absolute Imports**: Always use `from src.*` for application code
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

## Flask API Guidelines

### Blueprint Organization and Dependency Injection
- **Blueprint Pattern**: One blueprint per domain/feature (api_routes, models_routes, user_routes)
- **Factory Functions**: Blueprints created via factory functions that accept dependencies
- **Immutable Context**: Pass dependencies via frozen dataclass contexts (APIRouteContext, SocketIOContext)
  ```python
  @dataclass(frozen=True)
  class APIRouteContext:
      app: Flask
      agent: StockAgent
      config: Dict[str, Any]
      logger: logging.Logger
      # ... 7 more fields for services, helpers
  
  def create_api_routes(context: APIRouteContext) -> Blueprint:
      blueprint = Blueprint('api', __name__)
      # Routes access context for dependencies
      return blueprint
  ```
- **Lazy Service Initialization**: Instantiate optional services only when endpoint is called
  ```python
  @blueprint.route('/users/<user_id>')
  def get_user(user_id):
      if context.user_service is None:
          return jsonify({"error": "User service unavailable"}), 503
      # Use service...
  ```

### Request Validation and Schemas
- **Adopt Schema Library**: Use Marshmallow (ecosystem fit, Flask-Marshmallow integration) or Pydantic for request validation
- **Schema Definition Pattern**:
  ```python
  from marshmallow import Schema, fields, validate
  
  class ChatRequestSchema(Schema):
      message = fields.Str(required=True, validate=validate.Length(min=1, max=5000))
      provider = fields.Str(missing='openai', validate=validate.OneOf(['openai', 'grok']))
      temperature = fields.Float(missing=0.7, validate=validate.Range(min=0, max=2))
  ```
- **Validation in Routes**:
  ```python
  schema = ChatRequestSchema()
  try:
      data = schema.load(request.get_json())
  except ValidationError as err:
      return jsonify({"error": "Validation failed", "details": err.messages}), 422
  ```
- **Reusable Decorator** (optional enhancement):
  ```python
  def validate_json(schema_cls):
      def decorator(f):
          @wraps(f)
          def wrapper(*args, **kwargs):
              schema = schema_cls()
              try:
                  validated_data = schema.load(request.get_json())
                  return f(validated_data=validated_data, *args, **kwargs)
              except ValidationError as err:
                  return jsonify({"error": "Validation failed", "details": err.messages}), 422
          return wrapper
      return decorator
  
  @blueprint.route('/chat', methods=['POST'])
  @validate_json(ChatRequestSchema)
  def chat(validated_data):
      # Use validated_data directly
  ```

### Error Handling and Response Format
- **Global Error Handlers**: Use `@app.errorhandler()` for centralized error handling
  ```python
  @app.errorhandler(ValidationError)
  def handle_validation_error(e):
      return jsonify({"error": "Validation failed", "details": e.messages, "request_id": g.request_id}), 422
  
  @app.errorhandler(Exception)
  def handle_generic_error(e):
      logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
      return jsonify({"error": "Internal server error", "request_id": g.request_id}), 500
  ```
- **Standardized Error Format** (RFC 7807-inspired):
  ```python
  {
      "type": "validation_error",
      "title": "Validation Failed",
      "status": 422,
      "detail": "The 'message' field is required",
      "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "errors": {"message": ["This field is required"]}  # Optional field-level errors
  }
  ```
- **Request ID Tracking**: Inject unique ID per request for correlation
  ```python
  import uuid
  from flask import g
  
  @app.before_request
  def inject_request_id():
      g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
  
  @app.after_request
  def add_request_id_header(response):
      response.headers['X-Request-ID'] = g.request_id
      return response
  ```
- **Safe Error Messages**: Never expose stack traces, internal paths, or sensitive data in client responses
- **Structured Logging**: Log full exception details server-side with request context

### HTTP Status Code Standards
Use semantically correct status codes per REST conventions:

| Code | Use Case | Example |
|------|----------|---------|
| 200 OK | Successful GET, PUT, PATCH | Retrieve user, update resource |
| 201 Created | Successful POST creating resource | Create workspace, add symbol |
| 204 No Content | Successful DELETE or update with no body | Delete watchlist item |
| 400 Bad Request | Malformed request (invalid JSON, missing required header) | `{"error": "Invalid JSON"}` |
| 401 Unauthorized | Missing or invalid authentication | `{"error": "Missing API key"}` |
| 403 Forbidden | Authenticated but not authorized | `{"error": "Insufficient permissions"}` |
| 404 Not Found | Resource does not exist | `{"error": "User not found"}` |
| 409 Conflict | Resource conflict (duplicate, stale update) | `{"error": "Workspace name already exists"}` |
| 422 Unprocessable Entity | Validation error (well-formed but invalid data) | `{"error": "Validation failed", "details": {...}}` |
| 429 Too Many Requests | Rate limit exceeded | `{"error": "Rate limit exceeded", "retry_after": 60}` |
| 500 Internal Server Error | Unhandled exception | `{"error": "Internal server error", "request_id": "..."}` |
| 502 Bad Gateway | Upstream service failure | `{"error": "AI model service unavailable"}` |
| 503 Service Unavailable | Service temporarily unavailable | `{"error": "Database unavailable"}` |

**Key Clarifications:**
- **400 vs 422**: Use 400 for malformed requests (invalid JSON, missing Content-Type), 422 for semantic validation errors
- **401 vs 403**: Use 401 when authentication is missing/invalid, 403 when authenticated but lacks permissions
- **502 vs 503**: Use 502 for external service failures, 503 for internal service unavailability

**Current Usage Review:**
- ✅ Using 201 with Location header for resource creation
- ✅ Using 503 when services unavailable (user_routes.py)
- ⚠️ Using 400 for validation errors → Migrate to 422
- ⚠️ Missing 409 for conflicts (e.g., duplicate workspace names)
- ⚠️ Missing 429 for rate limiting (not yet implemented)

### Middleware Patterns
- **Request/Response Logging**:
  ```python
  import time
  
  @app.before_request
  def log_request():
      g.start_time = time.time()
      logger.info(f"Request: {request.method} {request.path}", extra={
          "method": request.method, "path": request.path, "request_id": g.request_id
      })
  
  @app.after_request
  def log_response(response):
      duration = time.time() - g.start_time
      logger.info(f"Response: {response.status_code} ({duration:.3f}s)", extra={
          "status": response.status_code, "duration": duration, "request_id": g.request_id
      })
      return response
  ```
- **Rate Limiting** (recommended: Flask-Limiter with Redis backend):
  ```python
  from flask_limiter import Limiter
  from flask_limiter.util import get_remote_address
  
  limiter = Limiter(
      app=app,
      key_func=get_remote_address,
      storage_uri="redis://localhost:6379",
      default_limits=["200 per day", "50 per hour"]
  )
  
  @blueprint.route('/chat', methods=['POST'])
  @limiter.limit("10 per minute")
  def chat():
      # Rate-limited endpoint
  ```
- **Security Headers**:
  ```python
  @app.after_request
  def add_security_headers(response):
      response.headers['X-Content-Type-Options'] = 'nosniff'
      response.headers['X-Frame-Options'] = 'DENY'
      response.headers['X-XSS-Protection'] = '1; mode=block'
      # HTTPS only: response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
      return response
  ```
- **CORS Best Practices**:
  - Explicit origins in production (avoid `*` with credentials)
  - Limit methods and headers to those actually used
  - Configure `supports_credentials=True` only if needed
  - Current: Using flask-cors with wildcard origin (acceptable for public API without auth)

### API Documentation and Versioning
- **OpenAPI Spec Maintenance**: Currently manual (`docs/openapi.yaml`); keep synchronized with code changes
- **Auto-Generation Option** (future enhancement):
  - **apispec**: Generate OpenAPI from code + Marshmallow schemas
  - **Flask-RESTX**: Automatic Swagger UI with decorator-based documentation
  - Choose based on team preference and tooling fit
- **Versioning Strategy** (not yet implemented):
  - Recommended: `/api/v1/` prefix for all routes
  - Add version to blueprint: `blueprint = Blueprint('api_v1', __name__, url_prefix='/api/v1')`
  - Deprecation policy: Support N and N-1 versions; announce deprecation with `Sunset` header
  - Current: All routes under `/api/` (implicit v1); add explicit versioning when breaking changes needed

### Streaming Responses
- **SSE Pattern**: Use Flask `Response` + `stream_with_context` for chat streaming
- **SSE Headers**: Set `Cache-Control: no-cache`, `Connection: keep-alive`, `Content-Type: text/event-stream`
- **CORS for SSE**: Set `Access-Control-Allow-Origin` (explicit origin or `*` for public streams)
- **Error Handling in Streams**: Catch exceptions inside generator; emit error event before closing
  ```python
  def generate_stream():
      try:
          for chunk in agent.process_query_streaming(message):
              yield f"data: {json.dumps({'chunk': chunk})}\n\n"
      except Exception as e:
          logger.error(f"Stream error: {e}", exc_info=True)
          yield f"data: {json.dumps({'error': 'Stream interrupted'})}\n\n"
  
  return Response(stream_with_context(generate_stream()), mimetype='text/event-stream')
  ```

### Migration Guidance for Existing Code
**Adopting Request Validation (Priority: High, Effort: Medium):**
1. Install Marshmallow: `pip install marshmallow flask-marshmallow`
2. Create schema definitions in `src/web/schemas/` (new directory)
3. Replace manual validation in `api_routes.py`, `user_routes.py` with schema.load()
4. Update status codes: 400 → 422 for validation errors
5. Test with existing API clients; ensure error format backward compatible

**Adopting Global Error Handlers (Priority: High, Effort: Low):**
1. Add error handlers to `api_server.py` app factory after blueprint registration
2. Remove per-route try-catch blocks; let exceptions bubble to global handlers
3. Ensure request_id middleware installed before error handlers
4. Test error responses include request_id for debugging

**Adding Rate Limiting (Priority: Medium, Effort: Low):**
1. Install Flask-Limiter: `pip install Flask-Limiter`
2. Configure in `api_server.py` with Redis storage_uri from config
3. Add `@limiter.limit()` decorators to high-traffic endpoints (/chat, /api/chat)
4. Test rate limit responses return 429 with Retry-After header

**Adding Request/Response Logging (Priority: Medium, Effort: Low):**
1. Add before_request/after_request hooks to `api_server.py`
2. Ensure request_id middleware runs first
3. Configure structured logging to capture method, path, status, duration, request_id
4. Test logs include all context for debugging

**OpenAPI Auto-Generation (Priority: Low, Effort: Medium):**
1. Evaluate apispec vs Flask-RESTX based on project needs
2. If choosing apispec: Add schema metadata to Marshmallow schemas, generate spec on build
3. If choosing Flask-RESTX: Refactor blueprints to use @api.route decorators with doc strings
4. Keep manual `docs/openapi.yaml` until migration complete; validate parity

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
Central wiring of repositories into services with singleton pattern:
```python
from services.factory import ServiceFactory
from data.repositories.factory import RepositoryFactory

repo_factory = RepositoryFactory(db, config)
service_factory = ServiceFactory(config, repository_factory=repo_factory, cache_backend=cache)

user_service = service_factory.get_user_service()      # Singleton, auto-wired
workspace_service = service_factory.get_workspace_service()
```
- **Singleton Pattern**: Services cached in `_services` dict; created once per factory
- **Repository Delegation**: Lazy-creates repositories via `RepositoryFactory`
- **Logger Hierarchy**: Child loggers (`parent.service_name`) for service-specific logging
- **Protocol Wiring**: Services receive other services as protocols for decoupling

### Protocols for Decoupling (`src/services/protocols.py`)
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class WorkspaceProvider(Protocol):
    def list_workspaces(self, user_id: str, *, limit: int, use_cache: bool = True) -> List[Dict]: ...

@runtime_checkable
class SymbolProvider(Protocol):
    def get_symbol(self, symbol: str, *, use_cache: bool = True) -> Optional[Dict]: ...
```
- **Structural Subtyping**: Duck typing via `@runtime_checkable` and `Protocol`
- **Avoids Circular Dependencies**: `UserService` depends on `WorkspaceProvider` protocol, not concrete `WorkspaceService`
- **Testability**: Any mock implementing required methods satisfies the protocol

### Service Implementation Pattern
```python
class MyService(BaseService):
    MY_CACHE_TTL = 300  # Class constant for cache TTL
    
    def __init__(
        self,
        *,
        my_repository: MyRepository,           # Required concrete repository
        other_provider: OtherProvider,         # Protocol dependency
        optional_repo: Optional[OtherRepo] = None,  # Optional dependency
        cache: Optional[CacheBackend] = None,
        time_provider: Optional[Callable[[], str]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        super().__init__(cache=cache, time_provider=time_provider, logger=logger)
        self._my_repository = my_repository
        self._other_provider = other_provider
        self._optional_repo = optional_repo
    
    def health_check(self) -> Tuple[bool, Dict[str, Any]]:
        return self._dependencies_health_report(
            required={"my_repo": self._my_repository},
            optional={"optional_repo": self._optional_repo}
        )
    
    def _cache_key(self, entity_id: str) -> str:
        return f"myservice:{entity_id}"
```

### Async and Streaming Patterns
- **Async Wrappers**: Use `run_in_executor` to wrap sync methods for async callers
  ```python
  async def list_items_async(self, user_id: str, *, limit: int = 20) -> List[Dict]:
      loop = asyncio.get_running_loop()
      return await loop.run_in_executor(None, lambda: self.list_items(user_id, limit=limit))
  ```
- **Streaming Methods**: Use `batched()` utility for chunked iteration (SSE/WebSocket)
  ```python
  def stream_items(self, user_id: str, *, chunk_size: int = 5) -> Iterator[List[Dict]]:
      records = self._fetch_items(user_id)
      serialized = [normalize_document(doc) for doc in records]
      yield from batched(serialized, chunk_size)
  ```

### Available Services
| Service | Domain | Key Methods |
|---------|--------|-------------|
| `UserService` | User orchestration | `get_user()`, `get_user_profile()`, `get_user_dashboard()` |
| `WorkspaceService` | Workspace CRUD | `list_workspaces()`, `create_workspace()`, `stream_workspaces()` |
| `SymbolsService` | Symbol discovery | `search_symbols()`, `get_symbol()`, `stream_symbols()` |

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
Services use protocols for cross-service dependencies, making tests cleaner:
```python
@pytest.fixture
def mock_workspace_provider():
    """Mock implementing WorkspaceProvider protocol."""
    provider = MagicMock()
    provider.list_workspaces.return_value = [{"id": "ws1", "name": "Test"}]
    return provider

@pytest.fixture
def mock_user_repo():
    """Mock repository with health_check stubbed."""
    repo = MagicMock()
    repo.health_check.return_value = (True, {"component": "user_repository", "status": "ready"})
    repo.find_one.return_value = {"_id": "user123", "email": "test@example.com"}
    return repo
```

### Service Test Helper Pattern
Use a `build_service()` helper for consistent construction:
```python
def build_user_service(
    user_repo,
    workspace_provider,
    symbol_provider,
    watchlist_repo=None,
    cache=None
) -> UserService:
    return UserService(
        user_repository=user_repo,
        workspace_provider=workspace_provider,
        symbol_provider=symbol_provider,
        watchlist_repository=watchlist_repo,
        cache=cache,
    )

def test_user_service_returns_user(mock_user_repo, mock_workspace_provider, mock_symbol_provider):
    service = build_user_service(mock_user_repo, mock_workspace_provider, mock_symbol_provider)
    user = service.get_user("user123")
    assert user["email"] == "test@example.com"
    mock_user_repo.find_one.assert_called_once()
```

### Health Check Testing
All services must implement `health_check()`. Test both healthy and degraded states:
```python
def test_service_health_check_returns_healthy(mock_user_repo, ...):
    service = build_user_service(mock_user_repo, ...)
    healthy, details = service.health_check()
    assert healthy is True
    assert details["status"] == "healthy"

def test_service_health_check_returns_degraded_on_optional_failure(mock_user_repo, ...):
    mock_optional_repo = MagicMock()
    mock_optional_repo.health_check.return_value = (False, {"error": "connection failed"})
    service = build_user_service(mock_user_repo, ..., optional_repo=mock_optional_repo)
    healthy, details = service.health_check()
    assert healthy is True  # Optional failure doesn't fail service
    assert "degraded" in details.get("optional_status", "")
```

## Model Factory and AI Clients
- **Factory**: `src/core/model_factory.py` creates provider-specific clients
- **Clients**: `OpenAIModelClient`, `GrokModelClient` inherit from `BaseModelClient`
- **Fallback Support**: Configure `allow_fallback` and `fallback_order` in config
- **Provider Selection**: `MODEL_PROVIDER` env var or config overrides default
- **Streaming**: All model clients support `generate_stream()` for SSE responses
- **Debug Mode**: Set `MODEL_DEBUG_PROMPT=true` in .env to log prompts (local only)

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
1. Define route and handler in a blueprint under `src/web/routes/`
2. Register blueprint in app factory if new
3. Update `docs/openapi.yaml` with endpoint schema
4. Add pytest tests in `tests/api/`

### Extend MongoDB Schema
1. Update repository/schema helpers in `src/data/repositories/` and `src/data/schema/`
2. Follow `db.command("listCollections")` pattern with fallback
3. Add/adjust migration in `src/data/migration/db_setup.py`
4. Document in README if user action required

### Add Model Provider
1. Create model client in `src/core/` inheriting from `BaseModelClient`
2. Update `src/core/model_factory.py` to instantiate new client
3. Adjust `.github/copilot-model-config.yaml` and review `.github/MODEL_ROUTING.md`
4. Add unit tests for selection and fallback behavior

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

## Pitfalls and Gotchas
- **Windows Reserved Ports**: 27017 may be blocked; use alternate host port (27034) via compose override
- **MongoDB Unauthorized**: User may lack `listCollections` permission; always catch and fall back
- **Relative Imports**: Break tests and packaging; use absolute `from src.*`
- **Real API Keys in Tests**: Mock external services; use env fixtures for keys only when unavoidable

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
