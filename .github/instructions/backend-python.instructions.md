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
- **Blueprint Organization**: One blueprint per domain/feature (api_routes, models_routes)
- **Dependency Injection**: Pass dependencies via immutable dataclass contexts (APIRouteContext, SocketIOContext)
- **Response Format**: Always return JSON; use Flask `jsonify()` for consistency
- **Error Handling**:
  - 4xx for client errors (validation, missing parameters)
  - 5xx for server errors with safe messages; log full exceptions with context
- **Streaming Responses**: Use Flask `Response` + `stream_with_context` for SSE chat streaming
- **SSE Headers**: Set `Cache-Control: no-cache`, `Connection: keep-alive`, `Access-Control-Allow-Origin: *` (or specific origin)

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
- **Collections**:
  - `market_data` (time-series) - stock prices, volume
  - `symbols` - ticker metadata
  - `fundamental_analysis` - earnings, ratios
  - `investment_reports` - generated analysis reports
  - `news_events` - market news
  - `user_preferences` - settings
- **Repository Pattern**: Centralize all DB access in `src/data/repositories/`; avoid ad-hoc queries in routes
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
