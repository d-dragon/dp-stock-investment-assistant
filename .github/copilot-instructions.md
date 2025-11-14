| 'g:\00_Work\Projects\dp-stock-investment-assistant\.github\instructions\infrastructure-deployment.instructions.md' | IaC/** | Infrastructure, deployment, and IaC conventions for Docker, Kubernetes, Terraform, and CI/CD |
| 'g:\00_Work\Projects\dp-stock-investment-assistant\.github\instructions\testing.instructions.md' | tests/** | Comprehensive testing strategy across all levels - unit, integration, E2E, performance, security |
# Copilot Instructions for dp-stock-investment-assistant

**Purpose**: Make AI coding agents productive and safe in this repository by encoding our conventions, workflows, and gotchas. Favor precise, minimal edits with tests green before done.

> **Domain-Specific Instructions**: For detailed guidance, see:
> - [Architecture & System Design](instructions/architecture.instructions.md)
> - [Backend Python API](instructions/backend-python.instructions.md)
> - [Frontend React](instructions/frontend-react.instructions.md)
> - [Infrastructure & Deployment](instructions/infrastructure-deployment.instructions.md)
> - [Testing](instructions/testing.instructions.md)
## Universal Principles

### Security & Secrets Management
- **Never expose sensitive data**: API keys, passwords, connection strings, tokens, or credentials must never appear in code, logs, or error messages
- **Use environment-based configuration**: Secrets come from `.env` (local), environment variables (CI/CD), or Azure Key Vault (production)
- **Separation of concerns**: Keep configuration separate from code; use overlays for environment-specific settings (`config.local.yaml`, `config.production.yaml`)
- **Fail securely**: When handling auth errors, log safely without exposing credentials or internal system details

### Code Quality Standards
- **Readability over cleverness**: Write code that's easy to understand, maintain, and debug
- **Type safety**: Use static typing (Python type hints, TypeScript interfaces) for public APIs and data contracts
- **Self-documenting code**: Prefer clear naming and structure; add comments only for "why", not "what"
- **Consistent style**: Follow language-specific style guides (PEP 8 for Python, Airbnb/Standard for TypeScript)
- **DRY principle**: Eliminate duplication through abstraction, but avoid premature abstraction
- **Dependency management**: Minimize external dependencies; prefer standard library or well-maintained, focused libraries

### Testing Philosophy
- **Test behavior, not implementation**: Focus on user-facing functionality and contracts
- **Mock external dependencies**: Tests should not depend on network, external APIs, or live databases
- **Fast feedback loops**: Keep unit tests fast (<1s per test suite); integration tests can be slower but still reasonable
- **Test pyramid**: Many unit tests, fewer integration tests, minimal E2E tests
- **Coverage targets**: Aim for meaningful coverage (happy path + edge cases + error handling), not just percentage metrics
- **Test-first mindset**: Consider testability during design; if it's hard to test, it's probably hard to use

### Error Handling & Observability
- **Structured logging**: Use logging frameworks with levels (DEBUG, INFO, WARNING, ERROR); include context (user ID, request ID, resource name)
- **Graceful degradation**: Handle errors gracefully; provide fallbacks where possible (e.g., model fallback, cached data)
- **User-friendly messages**: External-facing errors should be actionable; internal errors should be detailed for debugging
- **No silent failures**: Every error path should be logged and/or surfaced appropriately
- **Observability**: Emit metrics and traces for production systems; make debugging easier with correlation IDs

### Change Management
- **Small, focused commits**: One logical change per commit with clear, descriptive messages
- **Pull request discipline**: Explain "why" and "impact"; include verification steps, screenshots, or test evidence
- **Backward compatibility**: When changing APIs or schemas, consider migration paths; use deprecation warnings
- **Documentation as code**: Update docs (README, inline comments, OpenAPI specs) in the same PR as code changes
- **Rollback-ready**: Design changes to be easily reversible; use feature flags for risky deployments

### Performance & Scalability Considerations
- **Profile before optimizing**: Use data to identify bottlenecks; avoid premature optimization
- **Efficient data access**: Minimize database queries (avoid N+1), use indexing, leverage caching strategically
- **Resource awareness**: Be mindful of memory usage, connection pooling, and external rate limits
- **Async where appropriate**: Use asynchronous patterns for I/O-bound operations; avoid blocking threads
- **Horizontal scalability**: Design stateless services; use shared state (Redis, databases) for multi-instance deployments

## Project-Specific Guidelines

### Import & Module Organization
- **Absolute imports**: Always use `from src.*` for application code; relative imports break tooling and tests
- **Import order**: stdlib → third-party → local project modules, alphabetically sorted within groups
- **Avoid circular dependencies**: Refactor to use dependency injection or interface abstraction

### Configuration Management
- **Hierarchical config loading** (via `src/utils/config_loader.py`):
  1. Base YAML (`config/config.yaml`)
  2. Environment overlay (`config.{APP_ENV}.yaml`)
  3. Environment variable overrides
  4. Cloud secrets (Azure Key Vault in production)
- **Environment normalization**: `APP_ENV` values (`dev`, `local`, `k8s-local`, `staging`, `production`) are normalized automatically
- **Override modes**: Control env var overrides via `CONFIG_ENV_OVERRIDE_MODE` (all/secrets-only/none)

### Database & Persistence Patterns
- **MongoDB**: Use `db.command("listCollections")` with error handling; avoid `list_collection_names()` (auth issues in restricted contexts)
- **Repository pattern**: Centralize data access in `src/data/repositories/`; no ad-hoc DB queries in routes or presentation layers
- **Schema validation**: Apply JSON schema validation for data integrity; define in `src/data/schema/`
- **Migration discipline**: Run `src/data/migration/db_setup.py` for schema changes; document user-facing actions in README
- **Redis caching**: Use TTL strategies per data type; mock in tests; configure via `REDIS_*` env vars

### API Design Principles
- **Blueprint/module organization**: Group related endpoints; one blueprint per domain (e.g., `api_routes`, `models_routes`)
- **Consistent response format**: Always return JSON; use standard status codes (2xx success, 4xx client error, 5xx server error)
- **Streaming support**: Use SSE (Server-Sent Events) with proper headers for real-time data (Flask `Response` + `stream_with_context`)
- **Validation & sanitization**: Validate all inputs; sanitize outputs (especially user-generated content)
- **Versioning strategy**: Plan for API versioning (e.g., `/api/v1/`, `/api/v2/`) when breaking changes are needed

### Infrastructure & Deployment Conventions
- **Local override pattern**: Keep `docker-compose.yml` upstream-friendly; use `docker-compose.override.yml` for local tweaks (ports, volumes)
- **Health probes alignment**: Ensure containerPort, health endpoints, and Helm probe paths match across all layers
- **Environment parity**: Keep dev, staging, and production as similar as possible; use same base images and config patterns
- **Secrets in CI/CD**: Use pipeline secret stores or managed identities; never hardcode or check in credentials

## Golden Rules (All Domain Instructions Must Follow)

1. **Security First**: No secrets in code, logs, or version control
2. **Test Before Merge**: All changes must have passing tests
3. **Logging Over Print**: Use structured logging with appropriate levels and context
4. **Document Intent**: Explain "why" in code comments, commit messages, and PRs
5. **Backward Compatibility**: Consider migration paths; don't break existing integrations without notice
6. **Fail Fast**: Validate early; provide clear error messages; log failures with context
7. **Keep It Simple**: Prefer simple, maintainable solutions over complex abstractions
8. **Follow Domain Standards**: Adhere to language/framework-specific guidelines in domain instruction files

## Quick project map (what matters most)
- Backend
  - `src/main.py` – local entry; CLI runner.
  - `src/wsgi.py` – WSGI entry for production servers (gunicorn/eventlet or gevent).
  - `src/web/` – Flask blueprints and Socket.IO.
    - `routes/api_routes.py` – health, chat, config endpoints.
    - `routes/models_routes.py` – model management endpoints.
    - `sockets/` – Socket.IO server events.
  - `src/core/` – agent, model factory/clients, data manager.
  - `src/utils/config_loader.py` – config loader with .env, APP_ENV overlays, and optional Azure Key Vault.
  - `src/data/` – repositories, schema, services, and migrations.
    - `migration/db_setup.py` – creates collections, indexes, validation.
- Frontend
  - `frontend/` – React app served by Nginx in production.
- Infra/IaC
  - `docker-compose.yml` (+ `.override.yml` for local tweaks), `IaC/` (Dockerfiles, Helm chart, Terraform).
- Docs
  - `README.md` – setup, testing, DB migration.
  - `.github/MODEL_ROUTING.md` – multi-model routing docs.
  - `.github/chatmodes/*` – custom Copilot chat modes (docs; model routing not enforced by Copilot yet).

## Setup and run (Windows PowerShell examples)
- Python env
  - `python -m venv venv` → `venv\Scripts\Activate.ps1`
  - `python -m pip install -r requirements.txt`
- Environment
  - Copy `config/config_example.yaml` → `config/config.yaml`
  - Copy `.env.example` → `.env`, set keys as needed. APP_ENV controls overlay files like `config.k8s-local.yaml`.
- Run locally
  - API dev: `python src\main.py`
  - WSGI (container): `gunicorn -k eventlet -w 1 -b 0.0.0.0:5000 "src.wsgi:app"`
- Tests
  - `python -m pytest -v`
  - Ensure `src` is on PYTHONPATH if running outside VS Code: `$env:PYTHONPATH = "$PWD\src"`

## Database and cache
- Services
  - Use Docker Compose: `docker-compose up -d mongodb redis`
  - If Windows blocks 27017 (reserved range), map a safe port via `docker-compose.override.yml` (e.g., host 27034 → container 27017) and update `MONGODB_URI` accordingly.
- Migration
  - Run: `python src\data\migration\db_setup.py`
  - Collections created: `market_data` (time-series), `symbols`, `fundamental_analysis`, `investment_reports`, `news_events`, `user_preferences`.
- MongoDB pattern
  - Use `db.command("listCollections")` for existence checks. Catch Unauthorized and fall back gracefully.
  - Don’t depend on `list_collection_names()` in authenticated contexts.
- Redis
  - Configure via env (`REDIS_*`). Avoid real connections in tests; use stubs/mocks.

## API guidelines
- Blueprints
  - Add new endpoints in a dedicated module under `src/web/routes/` and register via the app factory.
  - Keep responses JSON, typed, and validated where practical.
- Streaming
  - For chat streaming, use Flask `Response` + `stream_with_context` and SSE headers (see `api_routes.py`).
- Error handling
  - Return 4xx for client errors, 5xx with safe messages for server errors. Log exceptions with context.

## Config and secrets
- `src/utils/config_loader.py` loads:
  - Base YAML (`config/config.yaml`) → APP_ENV overlay (e.g., `config.local.yaml`, `config.k8s-local.yaml`) → env vars → optional Azure Key Vault.
- Env overrides
  - SAFE defaults to “all” in `APP_ENV=local`, “secrets-only” for `k8s-local/staging/production`. Control via `CONFIG_ENV_OVERRIDE_MODE`.
- Azure Key Vault (optional)
  - Enable with `USE_AZURE_KEYVAULT=true` and `AZURE_KEYVAULT_URI`/`KEYVAULT_NAME`. Secrets like `OPENAI_API_KEY`, `GROK_API_KEY` are mapped in the loader.

## Domain-Specific Conventions Summary
See linked instruction files for comprehensive guidelines:
- **Architecture**: Design patterns, deployment strategies, IaC conventions
- **Backend (Python)**: Flask blueprints, model factory, pytest patterns, ConfigLoader usage
- **Frontend (React)**: Component architecture, hooks, Socket.IO, Jest + RTL testing
- **Infrastructure & Deployment**: Docker, Kubernetes/Helm, Terraform, CI/CD pipelines, monitoring
- **Testing**: Unit, integration, E2E, performance, security testing across all stacks

## Common Pitfalls & Platform-Specific Gotchas

### Windows Development
- **Reserved port ranges**: Ports 27017-27018 may be blocked by Windows; use `docker-compose.override.yml` to map alternate host ports (e.g., 27034)
- **Line endings**: Configure Git to handle CRLF/LF properly (`core.autocrlf=true` or `.gitattributes`)
- **Path separators**: Use `pathlib.Path` in Python or forward slashes in configs for cross-platform compatibility

### MongoDB Authentication
- **Restricted users**: User may lack `listCollections` permission; use `db.command("listCollections")` with fallback, not `list_collection_names()`
- **Auth source**: Always specify `authSource` in connection string (e.g., `?authSource=stock_assistant`)
- **Connection string format**: Ensure proper URL encoding for passwords with special characters

### Import & Dependency Issues
- **Relative imports**: Break pytest discovery and packaging; always use absolute `from src.*` imports
- **PYTHONPATH**: Ensure `src` is on PYTHONPATH for tests outside VS Code: `$env:PYTHONPATH = "$PWD\src"` (PowerShell)
- **Circular dependencies**: Refactor using dependency injection or interface/protocol abstraction

### Testing Anti-Patterns
- **Real API keys**: Tests should mock external services; if keys are needed, inject via fixtures or use test-only keys
- **Network dependencies**: Tests must run offline; mock all HTTP calls, database connections, and external APIs
- **Test data pollution**: Use transaction rollbacks, separate test databases, or cleanup fixtures to avoid state leakage

## Quality Gates & Definition of Done

### Pre-Commit Checklist
- [ ] **Code compiles/imports**: Verify no syntax errors or broken imports (`python -c "from src.main import main"`)
- [ ] **Tests pass locally**: Run full test suite (`pytest -v`) with 100% pass rate
- [ ] **No secrets exposed**: Scan for hardcoded credentials, API keys, or sensitive data
- [ ] **Logging not printing**: No `print()` statements; use `logging` module with appropriate levels
- [ ] **Type hints present**: Public functions and APIs have type annotations (where applicable)

### Pull Request Requirements
- [ ] **Descriptive title & description**: Explain what, why, and impact
- [ ] **Tests updated/added**: New behavior has test coverage; changed behavior has updated tests
- [ ] **Documentation updated**: README, inline docs, OpenAPI specs reflect changes
- [ ] **Breaking changes noted**: Explicit callout of backward-incompatible changes with migration guidance
- [ ] **Verification steps included**: How to test/verify the change works (commands, URLs, expected output)
- [ ] **Small & focused**: PR addresses one logical change; large changes split into reviewable chunks

### CI/CD Pipeline Expectations
- **Build**: Clean import/compilation; no errors or warnings
- **Lint**: Style guide compliance (PEP 8, ESLint) with zero violations
- **Type Check**: Static type analysis passes (mypy for Python, tsc for TypeScript) - lightweight enforcement
- **Tests**: All automated tests pass with >80% meaningful coverage
- **Security Scan**: No high/critical vulnerabilities in dependencies

## References
- API surface: `docs/openapi.yaml`
- Model routing: `.github/MODEL_ROUTING.md`, `.github/copilot-model-config.yaml`, `src/utils/model_router.py`
- DB setup: README “DB setup and migration” section
- IaC/K8s: `IaC/helm/dp-stock`, `IaC/infra/terraform`

## Quick verification snippets
- Agent streaming (Python REPL):
  ```python
  from core.agent import StockAgent
  from core.data_manager import DataManager
  from utils.config_loader import ConfigLoader
  cfg = ConfigLoader.load_config(); dm = DataManager(cfg); agent = StockAgent(cfg, dm)
  for chunk in agent.process_query_streaming("Latest news on AAPL"): print(chunk, end="")
  ```
- Health check (once app runs): `GET /api/health` → `{ "status": "healthy" }`

This guide is living documentation—update it when you add patterns, services, or workflows the assistant should follow.
