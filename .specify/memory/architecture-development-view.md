# Development View — DP Stock Investment Assistant

**Input**: `.specify/memory/architecture-logical-view.md`, `.specify/memory/architecture-process-view.md`

**Purpose**: Derive architecture-level components, package boundary intent, contract/artifact semantics, and dependency rules from logical and process views.

## Architecture Intent

This view preserves the component-level separation where transport, orchestration, reasoning, tool execution, memory, prompt policy, and governance are distinct development boundaries with explicit dependency direction and forbidden crossings.

## Core Tensions

| Tension | Current Tradeoff Direction | Development Consequence |
|---------|----------------------------|-------------------------|
| Single agent runtime vs tool expansion | Current ToolRegistry contains two active tools (StockSymbol, Reporting); TradingView is Phase 2 | Tool package boundary must support additive tool registration without requiring agent-runtime changes for each new tool |
| Factory/service/repository layering vs cross-layer shortcuts | All backend data access must flow through repositories; routes must not issue ad-hoc queries | Three distinct package boundaries exist (routes, services, repositories) with strict dependency direction; violations break testability |
| REST blueprint registration vs growing endpoint surface | Blueprints registered in app factory; new blueprints are additive | Component boundary for each new route package must follow the immutable-context registration pattern; no global state injection |
| Prompt-system evolution from inline to compiler path | Current prompt assets live under src/prompts/; planned compiler path adds loader, assembler, and middleware | Prompt-system component boundary will expand from one package to three cooperating components; each remains independent of agent-runtime packages |

## Stable Boundaries

| Boundary | Must Remain Stable Because | Explicitly Must Not Own |
|----------|----------------------------|-------------------------|
| Transport layer (Flask blueprints) | All inbound requests and streaming responses flow through blueprints with immutable DI context | Request authorization, service orchestration, agent reasoning, tool execution, lifecycle metadata, prompt policy |
| Service layer | ServiceFactory wires repositories and caches into services; all business orchestration lives here | Transport concerns, agent-runtime state, checkpoint persistence, prompt asset storage |
| Agent runtime | StockAssistantAgent and LangGraph bootstrap own reasoning and tool orchestration | Lifecycle authority, durable metadata, transport framing, prompt variant selection |
| Repository layer | MongoGenericRepository base class; all database access through RepositoryFactory singletons | Business logic, transport concerns, agent reasoning, cache management |
| Tool package | CachingTool base class; tools registered in singleton ToolRegistry | LLM provider selection, lifecycle governance, checkpoint management, prompt composition |
| Prompt assets and compiler path | Current src/prompts/ for inline assets; planned compiler path adds three packages | Agent-runtime state, tool execution, metadata persistence, provider selection |
| Spec-kit governance | specs/ owns delivery artifacts; docs/ owns long-lived references; .specify/ owns runtime and templates | Implementation code, runtime configuration, deployment manifests |

## Change Axes

| Expected Change | Isolated By | Development Impact |
|-----------------|-------------|--------------------|
| New agent tool added | ToolRegistry with register() pattern; add one tool class under src/core/tools/ | Only the tool package boundary changes; agent runtime, prompt assembly, and provider selection are unaffected |
| New Flask blueprint added | Blueprint factory with immutable APIRouteContext; register in app factory sequence | Only the route package boundary changes; service, repository, and agent boundaries are unaffected |
| New MongoDB repository added | RepositoryFactory with repository class extending MongoGenericRepository | Only the repository package boundary changes; the data access pattern remains consistent |
| New LLM provider added | ModelClientFactory with provider-specific client class; registered in provider map | Only the provider client boundary changes; agent reasoning, routing, and tool execution are unaffected |
| Prompt compiler path activated (planned) | Three additive package boundaries (loader, assembler, middleware); existing src/prompts/ remains for baseline | Prompt-system package boundary expands without modifying agent-runtime or service-layer packages |

## Invariants

| Invariant | Source Boundary / Contract / Dependency Rule | Risk If Violated |
|-----------|----------------------------------------------|------------------|
| Routes must not issue database queries directly | Repository pattern constitution rule; all persistence goes through repositories | Ad-hoc queries bypass indexing, health checks, and logging conventions |
| Services must not import route-level types | Dependency direction: routes→services→repositories | Circular dependencies break DI patterns and testability |
| Provider clients must be obtained through ModelClientFactory | Factory cache keyed by {provider}:{model_name}; direct provider instantiation bypasses fallback | Provider fallback stops working; caching is duplicated |
| Tools must extend CachingTool base class | CachingTool provides caching and base run/arun contract | Tool caching and health-check patterns become inconsistent |
| Spec-kit artifacts in specs/ must not be used as long-lived documentation | Constitution artifact boundaries; stable knowledge is promoted to docs/ only after verification | Delivery artifacts become stale reference material; docs/ and specs/ drift |

## Non-goals / Anti-patterns

| Non-goal / Anti-pattern | Why It Is Out of Scope or Harmful |
|-------------------------|-----------------------------------|
| Ad-hoc provider instantiation outside ModelClientFactory | Would bypass caching and fallback; every direct instantiation is a missed fallback path |
| Route-level database queries bypassing repositories | Would break the layered architecture; routes would own persistence concerns that belong in repositories |
| Agent runtime setting conversation lifecycle status | Lifecycle is a service-layer concern; the agent must not change active/archived status |
| Spec-kit tools extending into runtime code | Governance tools live in scripts/ and specs/; they must not be imported by application code |

## Architecture-Level Components

| Component / Capability Package | Responsibility | Input / Output Boundary | Collaborators | Explicitly Must Not Own | Source View Evidence |
|--------------------------------|----------------|-------------------------|---------------|--------------------------|----------------------|
| Transport package (Flask blueprints / Socket.IO handlers) | Accept HTTP/Socket.IO requests, manage SSE streaming, provide health surfaces | Inbound HTTP/Socket.IO → normalized request; response → SSE stream or JSON | Service layer through immutable context | Authorization, business orchestration, agent reasoning, tool execution, prompt assembly | RL-1, RL-11, R1-R4 (Process View) |
| Service orchestration package | Validate lifecycle, resolve session context, record metadata, reconcile runtime | Validated request → agent invocation; lifecycle outcomes → persistence | Repository package, CacheBackend, Agent runtime | Transport framing, checkpoint state, tool execution, prompt variant selection | RL-2, RL-3, H2 (Process View); Capability: Service Orchestration (Logical View) |
| Agent reasoning package | Route classification, ReAct loop, tool orchestration, checkpoint management, fallback handling | Validated work item → generated response (streamed or complete); checkpoint state → MongoDB | ModelClientFactory, ToolRegistry, Checkpointer, Guardrail middleware (planned) | Lifecycle authority, durable metadata, prompt variant storage | RL-3, RL-4, RL-5, RL-7, RL-8, RL-9 (Process View) |
| Provider client package (ModelClientFactory + clients) | Provider selection, model binding, client caching, fallback sequence | Prompt content → model completion; provider config → cached client | Agent runtime as consumer; external LLM providers as targets | Tool execution, lifecycle governance, prompt asset selection, checkpoint state | RL-6, RL-7, H3, F1, F2 (Process View) |
| Tool package | Implement domain-specific tools with caching and health contracts | Tool request → structured data result; tool result → agent runtime | Agent runtime, CacheBackend, external financial data sources | LLM reasoning, policy enforcement, checkpoint management | RL-8, F8 (Process View) |
| Checkpoint and memory package | Persist and retrieve thread-local agent state via LangGraph MongoDBSaver | Thread-id, conversation-turn data → persisted checkpoint; thread-id → loaded checkpoint | Agent runtime as primary consumer, MongoDB as storage | Lifecycle metadata, session context, tool-cache content, provider client instances | RL-9, F10 (Process View) |
| Repository package | Provide CRUD access to MongoDB collections through typed repositories | CRUD operations on domain entities → persisted documents | Service package, RepositoryFactory singleton | Business logic, transport concerns, agent reasoning, cache management | RL-2 (indirectly); Capability: Metadata Persistence (Logical View) |
| Prompt asset and compiler package (current + planned) | Current: inline prompt templates under src/prompts/. Planned: PromptAssetLoader, PromptAssembler, ResponseGuardrailMiddleware | Route classification, request envelope → compiled prompt; model draft → guardrail result | Agent runtime, Trace/metadata sink | State management, tool execution, metadata persistence, provider selection | RL-5, RL-10, H4, F4, F5, F6 (Process View) |
| Spec-kit governance package | Author and maintain specs/, manage traceability and synchronization | Feature requirements → spec.md, plan.md, tasks.md, review.md, sync artifacts | docs/ (sync targets), specs/traceability, .github/instructions/ | Application code, runtime configuration, deployment state | RL-12, H5, F9 (Process View); UC-6 (Scenario View) |
| Frontend application package | Render UI, manage client-side state, stream responses, provide user interaction surface | User input → REST/WebSocket request; SSE chunks → progressive UI | Backend transport endpoints | Backend lifecycle authority, agent reasoning, data persistence | R1-R4 (Process View) |

## Package Boundary Intent

| Package / Boundary | Abstraction Level | Owned Concepts | May Depend On | Must Not Depend On | Evolution Rule |
|--------------------|-------------------|----------------|---------------|--------------------|----------------|
| Transport | Entry-point | Request routing, response framing, streaming connections, health surfaces | Service orchestration package (APIRouteContext) | Agent runtime, repository package, provider clients | Additive: new blueprints register via factory; existing blueprints are not modified |
| Service orchestration | Business logic | Lifecycle validation, session context resolution, metadata recording | Repository package, CacheBackend, protocol interfaces | Transport internals, agent runtime checkpoints, provider clients | Additive: new services extend BaseService and register in ServiceFactory |
| Agent reasoning | Core orchestration | Route classification, ReAct loop, tool orchestration, fallback handling | ModelClientFactory (interface), ToolRegistry (interface), Checkpointer, Guardrail | Service layer internals, transport specifics, repository internals | Additive: new routes, tools, or providers do not require agent-runtime changes |
| Provider clients | Provider abstraction | Provider selection, model binding, client caching, fallback sequence | External LLM SDKs (httpx, openai) | Agent reasoning internals, service orchestration, tool execution | Additive: new providers register in the provider map in ModelClientFactory |
| Tools | Domain data access | Tool implementation, caching, health checks | CacheBackend, external data SDKs (yfinance) | Agent reasoning internals, lifecycle governance, prompt composition | Additive: new tools extend CachingTool and register in ToolRegistry |
| Repository | Data access | CRUD operations, MongoDB queries, document normalization | MongoDB driver (pymongo) | Service internals, transport specifics, agent reasoning | Additive: new repositories extend MongoGenericRepository and register in RepositoryFactory |
| Prompt assets | Policy | Prompt templates, behavior policy, guardrail rules (planned) | File system (current); manifest/lineage sources (planned) | Agent reasoning internals, tool execution, lifecycle governance | Additive: compiler path packages are added without modifying existing runtime packages |
| Spec-kit governance | Delivery management | Feature specs, plans, tasks, traceability, sync reports | docs/ and specs/ file system, sync scripts | Application code, runtime config, deployment manifests | Additive: new features create new specs/ directories; no modification to existing features' artifacts |
| Frontend | Presentation | UI rendering, client state, SSE/WebSocket streaming | Backend transport endpoints via HTTP/WebSocket | Backend service internals, agent runtime, repositories | Additive: new components do not require changes to backend packages |

## Contracts and Artifacts

| Contract / Artifact | Semantics | Producer | Consumer | Lifecycle | Architecture Consequence |
|---------------------|-----------|----------|----------|-----------|--------------------------|
| APIRouteContext (immutable dataclass) | Dependency injection contract for all Flask blueprints; provides agent, factories, config, logger | api_server.py (app factory) | All Flask route blueprints | Created once per app factory; reused across all routes | Every blueprint depends on the same DI contract; changing APIRouteContext affects all blueprints |
| REST API endpoints (defined in OpenAPI) | Public HTTP contract for chat, models, users, workspaces, sessions, conversations, health | Flask blueprints | Frontend, external clients, tests | Evolves via constitution delivery sync gates; must stay synchronized with docs/openapi.yaml | REST API changes require traceability and doc sync; undocumented endpoints are unsupported |
| Socket.IO events (chat_message, connect, disconnect) | Real-time event contract for chat streaming | Socket.IO handler in chat_events.py | Frontend webSocketService.ts | Not yet at full lifecycle parity with REST | Socket.IO events bypass ChatService lifecycle validation; parity gap is a known process gap |
| SSE streaming format (text/event-stream) | Streaming response contract with chunk and terminal events | Flask SSE response via stream_with_context | Frontend restApiClient.js | Governed by streaming admission and guardrail rules | Streaming semantics differ from Socket.IO; two streaming surfaces exist with different lifecycle coverage |
| Provider selection envelope | Contract between agent runtime and ModelClientFactory for provider resolution | Agent runtime | ModelClientFactory | Per-request; cached by {provider}:{model_name} key | Provider selection is opaque to transport and service layers |
| Tool invocation contract | Contract between agent runtime and tool implementations for evidence acquisition | Agent runtime (ReAct loop) | Tool implementations (CachingTool subclasses) | Per-tool-call; tool results are data-only context | Tool output shape determines how evidence is presented to the LLM; tool caching affects freshness |
| Spec feature artifacts (spec.md, plan.md, tasks.md, review.md) | Delivery-scoped governed artifacts for feature implementation | Speckit commands (speckit.specify, speckit.plan, speckit.tasks) | Implementation, verification, and sync agents | Created per feature; verified after implementation; may trigger doc updates during sync | Every non-trivial feature must produce these artifacts; stale artifacts create drift |
| Long-lived docs (docs/) | Stable reference requirements, architecture, design, ADRs, contracts, runbooks | Authors via SDD lifecycle (step 17 sync) | Future feature work, governance reviews, operator guidance | Updated during step 17 (docs sync) after verified implementation | Outdated long-lived docs are authoritative artifacts that create false confidence |
| Traceability manifest (spec-traceability.yaml) | Machine-readable SRS-to-feature mapping with status gates | Sync script (sync_spec_status.py) | Sync reports, governance reviews | Updated when feature scope or verification status changes | Stale traceability is a verification failure under constitution rules |

## Dependency Rules

| Rule | Allowed Direction | Forbidden Direction | Reason | Risk If Violated |
|------|-------------------|---------------------|--------|------------------|
| Routes → Services → Repositories | Routes import services; services import repositories; repositories import database driver | Repositories importing routes; services importing transport types; routes importing agent runtime directly | Layered architecture ensures testability and clear responsibility boundaries | Circular dependencies, untestable layers, ad-hoc data access |
| Agent runtime → ModelClientFactory (interface) | Agent depends on ModelClientFactory interface for provider selection; does not instantiate providers directly | ModelClientFactory depending on agent-runtime internals | Provider selection is a separate concern; the agent must not know provider implementation details | Provider selection logic becomes coupled to agent reasoning flow |
| Agent runtime → ToolRegistry (interface) | Agent depends on ToolRegistry to list and invoke tools; does not instantiate tools directly | Tool implementations depending on agent-runtime internals | Tool registration and execution are separate from reasoning orchestration | Adding a new tool requires agent-runtime changes |
| Services → Repository interface | Services depend on repository interfaces (protocols); not on concrete repository classes | Repositories depending on service types | Protocol-based DI prevents circular imports and enables mock injection | Direct coupling between concrete classes prevents isolated testing |
| Frontend → Backend endpoints | Frontend communicates through HTTP REST and Socket.IO events; never imports backend packages | Backend importing frontend types | Frontend and backend are separately deployable units; no shared code between them | Build-time coupling prevents independent deployment |
| Spec-kit → Code (governance only) | Spec-kit artifacts reference code via file paths and requirement IDs; never import code packages | Code importing from specs/ or .specify/ | Governance artifacts are metadata about code, not runtime dependencies | Runtime imports from governance artifacts would couple delivery workflow to application behavior |

## Development View Gaps

| Gap | Affected Component / Boundary | Why It Matters |
|-----|-------------------------------|----------------|
| Socket.IO handler does not use ChatService lifecycle path | Transport package, Socket.IO handler | Socket.IO chat bypasses the service-orchestration boundary; the Socket.IO handler invokes the agent directly without archive or ownership validation |
| Mid-stream provider fallback undefined for SSE streaming | Provider client package, Agent reasoning package | The current request-granularity fallback cannot handle a provider failure that occurs during an SSE streaming session |
| No protocol-based contract for prompt compiler path components | Prompt asset and compiler package (planned) | The planned PromptAssetLoader, PromptAssembler, and ResponseGuardrailMiddleware interfaces are not yet defined; their integration contracts are speculative |
| Frontend has no package boundary for its test infrastructure | Frontend application package | Zero frontend tests exist; the frontend test boundary is entirely absent |

## Prohibited Content

Do not write source file paths, concrete package trees, classes, functions, implementation tasks, framework-specific wiring, or code generation notes here.
