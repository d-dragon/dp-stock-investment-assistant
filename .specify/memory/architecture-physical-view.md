# Physical View — DP Stock Investment Assistant

**Input**: `.specify/memory/architecture-process-view.md`, `.specify/memory/architecture-development-view.md`

**Purpose**: Derive deployment, hosting, external system, fact-source, observability, and operational boundaries from process and development views.

## Architecture Intent

This view preserves the deployment-level separation where application logic (API, agent, frontend), persistence (MongoDB, Redis), external dependencies (LLM providers, financial data sources), and governance artifacts (docs/, specs/, IaC/) are deployed and operated through independent hosting units with explicit health, observability, and release boundaries.

## Core Tensions

| Tension | Current Tradeoff Direction | Physical Consequence |
|---------|----------------------------|----------------------|
| Local Docker Compose vs production AKS | Local dev uses docker-compose with hot-reload; production uses AKS with Helm | Two deployment topologies exist; probe paths, port mappings, and config overlays must stay aligned across both |
| MongoDB for both application data and checkpoint state | MongoDB serves both business metadata (conversations, sessions, workspaces) and LangGraph checkpoint state | A single persistent store carries two distinct logical ownership surfaces (service-layer lifecycle + agent-runtime state) |
| Redis as cache backend vs in-memory fallback | CacheBackend prefers Redis but falls back to in-memory dict if unavailable | Cache degradation is transparent to application logic but in-memory fallback does not survive process restart |
| Eventlet for WebSocket vs gevent for production | Dockerfile.api uses gunicorn+eventlet for Socket.IO; Helm templates reference the same combination | The WSGI server choice is coupled to Socket.IO compatibility; changing the async worker requires Socket.IO parity validation |

## Stable Boundaries

| Boundary | Must Remain Stable Because | Explicitly Does Not Carry |
|----------|----------------------------|---------------------------|
| API service (Flask + gunicorn) | All REST and Socket.IO traffic routes through the API service; frontend and agent both depend on it | Agent reasoning state, financial data persistence, prompt asset storage |
| Agent runtime (background container) | The agent reasoning loop runs in its own container with health endpoint on port 7000 | API transport concerns, lifecycle metadata persistence (in agent container), frontend rendering |
| Frontend (Nginx-served React) | All user-facing UI is served as static assets through Nginx | API service state, agent-runtime state, persistence layer internals |
| MongoDB cluster | All authoritative business data, checkpoints, and application state persist in MongoDB | Cache state (Redis), prompt asset files, spec-kit artifacts |
| Redis cache | Tool results, model list, and session data are cached with TTL | Authoritative business state, checkpoint data, long-term memory |
| External LLM provider endpoints (OpenAI/Grok) | Model inference is outsourced to external providers; the application does not run models locally | Financial data retrieval, tool execution, lifecycle governance |
| External financial data sources (Yahoo Finance) | Market data and fundamentals are fetched from external APIs through tool-invocation interfaces | LLM reasoning, prompt composition, user preference storage |
| Spec-kit and docs registry (file system) | All governed delivery artifacts and long-lived docs live in the repository file system under specs/ and docs/ | Application runtime state, deployment configuration |


## Change Axes

| Expected Change | Isolated By | Physical Impact |
|-----------------|-------------|-----------------|
| AKS cluster scaling (HPA) | Horizontal Pod Autoscaler based on CPU/memory metrics; independently scales API, agent, and frontend pods | Pod replica counts change but service endpoints and health probes remain stable |
| MongoDB Atlas migration | Connection URI changes; application code uses the same repository pattern | Only the MONGODB_URI environment variable changes; no application code changes required |
| Redis cluster or Sentinel upgrade | CacheBackend uses the same Redis protocol; Sentinel provides high availability | Only the REDIS_HOST/REDIS_PORT/ REDIS_PASSWORD environment variables change |
| New LLM provider integration | New provider endpoint URL registered in ModelClientFactory config | External dependency boundary expands; no existing provider paths change |
| Azure Key Vault enforcement | USE_AZURE_KEYVAULT=true moves secrets from env vars to Key Vault | Environment variable resolution order changes (env→Key Vault); no code changes required |
| Frontend CDN distribution | Nginx-served static assets can be cached at CDN edge | Frontend deployment unit remains Nginx-served; CDN is an optional acceleration layer |

## Invariants

| Invariant | Source Deployment / External / Fact Boundary | Risk If Violated |
|-----------|----------------------------------------------|------------------|
| API health endpoint must be reachable at /api/health on port 5000 | Dockerfile.api and Helm probe configuration both use this path | Kubernetes probes fail; containers are marked unhealthy and restarted |
| Agent health endpoint must be reachable at /health on port 7000 | Dockerfile.agent exposes port 7000; Helm probes use /health on port 7000 | Agent container is marked unhealthy; agent reasoning becomes unavailable |
| Frontend health endpoint must be reachable at /healthz on port 80 | Nginx config and Helm probes both use /healthz on port 80 | Frontend container is marked unhealthy; users cannot reach the UI |
| MongoDB connection must specify authSource | Connection string includes ?authSource=stock_assistant | Authentication fails in restricted MongoDB environments |
| Secrets must not appear in code, logs, or version control | Constitution Golden Rule 4; all environments use env vars or Key Vault | Credential exposure; security review failure |
| Cross-references between specs/ and docs/ must use section-level anchors | Constitution Document Referencing rules; links must be precise and durable | Agentic workflows lose traceability; inaccurate implementations may result |

## Non-goals / Anti-patterns

| Non-goal / Anti-pattern | Why It Is Out of Scope or Harmful |
|-------------------------|-----------------------------------|
| Local model serving | The architecture does not run LLMs locally; all model inference is outsourced to OpenAI/Grok |
| Monolithic deployment | The three-container pattern (API, agent, frontend) supports independent scaling and deployment; a monolithic deployment would remove that flexibility |
| Hard-delete persistence | Archive-over-delete semantics apply at the logical level; physical deletion is infrastructure-level cleanup only |

## Deployment and Hosting Boundaries

| Runtime / Hosting Unit | Carries | Boundary | Depends On | Release / Migration Impact |
|------------------------|---------|----------|------------|----------------------------|
| API container (gunicorn + eventlet) | Flask blueprints, Socket.IO handlers, service layer, ModelClientFactory | Port 5000; health endpoint /api/health; gunicorn with eventlet worker | MongoDB (business data + checkpoints), Redis (cache), LLM providers (model invocation) | API code changes require container rebuild; environment config changes require pod restart only |
| Agent container (background worker) | Agent reasoning runtime, tool implementations, checkpointer | Port 7000; health endpoint /health | MongoDB (checkpoints), Redis (tool cache), LLM providers (model invocation) | Agent code changes require container rebuild; tool additions require agent container update |
| Frontend container (Nginx) | Static React build, Nginx configuration | Port 80; health endpoint /healthz; Nginx reverse proxy for /api/* | API service for backend requests | Frontend code changes require static build and container rebuild; Nginx config changes require container rebuild |
| MongoDB (container or Atlas) | Business collections, LangGraph checkpoints, time-series market data | Port 27017 (container); connection URI configurable | Storage volume for data persistence | Schema migrations run via db_setup.py; index changes are additive; rollback requires data restore |
| Redis (container or Sentinel) | Tool result cache, model list cache, session data cache (TTL-managed) | Port 6379 (container); connection config via REDIS_* env vars | None (in-memory store); CacheBackend auto-falls back to in-memory if unavailable | Cache is ephemeral; TTL expiration is the normal lifecycle; no migration needed |
| GitHub repository (file system) | Source code, specs/, docs/, IaC/, .github/, .specify/ | Repository root at g:\00_Work\Projects\dp-stock-investment-assistant | Git for version control; CI/CD for build and deploy | Feature work creates branches; merge triggers CI/CD; long-lived doc updates are manual via step 17 |
| Spec kit runtime (.specify/ templates and extensions) | Constitution, templates, extension hooks, workflow definitions, scripts | Located at repository root under .specify/ | Spec Kit CLI (specify command) | Template or constitution changes are governed by the amendment process; extension updates managed via specify CLI |

## External System Collaboration

| External System | Purpose | Exchanged Content | Authoritative Fact | Failure Impact | Isolation / Substitute Boundary |
|-----------------|---------|-------------------|--------------------|----------------|---------------------------------|
| OpenAI API | Primary LLM inference provider | Prompt content → generated response (streamed or complete) | Model-generated text (not authoritative for market facts) | Provider failure triggers Grok fallback; complete outage → error response | ModelClientFactory fallback sequence; provider selection is isolated from application logic |
| Grok/xAI API | Secondary (fallback) LLM inference provider | Prompt content → generated response | Model-generated text (not authoritative for market facts) | Grok failure while OpenAI is also failing → all-providers-unavailable error | Same fallback isolation boundary as OpenAI |
| Yahoo Finance (via yfinance) | Primary financial data source for prices, fundamentals, news | Symbol → price, financial statements, news headlines | Authoritative source for market data | Tool failure returns cached data or "data unavailable" message | Tool layer with TTL-based caching isolates failure from agent reasoning |
| LangSmith API (optional) | LLM call tracing and observability | Trace data including prompts, responses, latency, token counts | Observability metadata | Trace loss (no user-visible effect) | LangSmith SDK is optional; traces degrade silently without affecting application behavior |

## Fact Sources and Observability

| Fact / Event | Authoritative Source | Observable Location | Consumers | Traceability Requirement |
|--------------|----------------------|---------------------|-----------|--------------------------|
| Stock price | Yahoo Finance (via tool invocation) | Tool response; optionally cached in Redis | Agent reasoning for user-facing answers | Tool result includes freshness metadata; cache TTL determines staleness |
| Financial fundamentals | Yahoo Finance (via tool invocation) | Tool response; optionally cached in Redis | Agent reasoning for analysis | Same as stock price; fundamentals cache TTL is longer (600s) |
| Conversation lifecycle status | Service layer (conversations collection in MongoDB) | API response body; checkpointer state | ChatService for archive/ownership validation; management API consumers | Lifecycle transitions are persisted; archive is irreversible |
| LLM provider selection outcome | ModelClientFactory fallback sequence | Provider client instance; response metadata | Agent runtime for response generation | Selected provider and model name are returned in response metadata |
| Guardrail outcome | ResponseGuardrailMiddleware (planned) | GuardrailResult emitted to response surface and trace sink | Transport layer for response emission; trace sink for observability | triggered_rules and status must be attributable |
| Spec sync status | sync_spec_status.py execution | spec-sync-status.md (human-readable); spec-traceability.yaml (machine-readable) | System operator, governance review | Sync gate pass/fail determines whether delivery is complete |
| Health status (API) | /api/health endpoint | JSON response with component health | Kubernetes probes, monitoring, operator | Health endpoint must report degraded state if a critical dependency is unavailable |
| Health status (Agent) | /agent/health endpoint | JSON response with agent runtime health | Kubernetes probes, operator | Agent health must reflect model provider availability |
| Request tracing | Logging, optional LangSmith, planned OpenTelemetry | Logs, LangSmith traces (optional), OTEL spans (planned) | Operator for debugging; LangSmith for LLM observability | Request ID correlation across logs is not yet implemented |

## Operations and Release Boundaries

| Operational Concern | Responsible Boundary | Trigger | Affected Views | Architecture Consequence |
|---------------------|----------------------|---------|----------------|--------------------------|
| Feature delivery and doc sync | Spec-kit governance (step 15-17) | Implementation verified (step 14 passes) | Development, Physical | Long-lived docs, traceability, and API contracts are synchronized with verified implementation |
| Deployment (local) | docker-compose up/build | Developer command or CI trigger | Physical | Container images rebuilt; environment overlays determine config |
| Deployment (production) | Helm upgrade via CI/CD | Main branch push to ACR | Physical | Rolling update of API, agent, and frontend pods; Helm values.yaml overrides control environment |
| Health monitoring | Kubernetes liveness/readiness probes | Probes execute on configured intervals | Physical | Probe failure triggers container restart or traffic removal |
| Data migration | db_setup.py execution | Schema change or new collection requirement | Development, Physical | Migration is manual; no automated rollback built in |
| Reconciliation | reconcile_stm_runtime.py (operator script) | Drift detection between checkpoints and conversation metadata | Process, Development, Physical | Operator-only; not automated in the request path |
| Alerting and metrics | Planned Prometheus + Grafana | Currently not implemented | Physical | No automated alerting exists; health status is poll-based |
| Secret rotation | Environment variable update or Key Vault rotation | Security policy or key expiration | Physical | Zero-downtime secret rotation requires Key Vault; env var changes need pod restart |

## Physical View Gaps

| Gap | Affected Deployment / External Boundary | Why It Matters |
|-----|-----------------------------------------|----------------|
| No Prometheus metrics or Grafana dashboards | API, Agent, Frontend containers | Health and performance observability is limited to health endpoints and logs; no request-rate, latency, or error-rate dashboards exist |
| No automated alerting (PagerDuty/Slack) | Operations boundary | Degraded or unhealthy states are detected via polled health checks or manual observation; no proactive notification |
| No HPA configured | AKS deployment (physical) | The Helm chart has no HorizontalPodAutoscaler templates; auto-scaling is not available in any deployment topology |
| No PodDisruptionBudget | AKS deployment (physical) | Availability during voluntary disruptions (node updates, cluster upgrades) is not guaranteed |
| No NetworkPolicy | AKS deployment (physical) | Pod-to-pod traffic is not restricted; any compromised pod can reach any other pod |
| Azure Key Vault is disabled by default | Secret management boundary | Production relies on environment variables rather than managed identity secrets; env var-based secrets are less resilient to rotation |
| No SBOM or image signing | CI/CD pipeline | Container image provenance is not verifiable; supply-chain integrity is not enforced |

## Prohibited Content

Do not write Kubernetes YAML, cloud resource manifests, machine sizes, service SKUs, deployment scripts, runbooks, or concrete infrastructure configuration here.
