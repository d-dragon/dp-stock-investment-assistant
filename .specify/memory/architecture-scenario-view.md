# Scenario View — DP Stock Investment Assistant

**Purpose**: Produce the UC semantics for the architecture workflow. This view is the source for the logical, process, development, and physical views.

## Architecture Intent

This view stabilizes the user-facing and operator-facing scenarios that the system must support, so the logical, process, development, and physical views derive capability boundaries and runtime collaboration from scenario-level meaning rather than from implementation assumptions.

## Core Tensions

| Tension | Current Tradeoff Direction | Scenario Consequence |
|---------|----------------------------|----------------------|
| Single-agent simplicity vs multi-agent extensibility | Current architecture uses one ReAct agent with route-aware skills; multi-agent orchestrator is deferred until prompt contracts materially diverge | Scenarios assume a single reasoning boundary today; future scenarios requiring specialist handoffs will need a routing contract that does not exist yet |
| Streaming vs non-streaming parity | REST chat supports SSE streaming; Socket.IO is wired but not at full lifecycle parity with the REST service-layer path | Two response paths exist with different guardrail and metadata behavior; scenarios must treat both until parity is closed |
| Session context vs conversation memory separation | Service layer owns session-level parent context; checkpoints own conversation-scoped runtime state; these are distinct authorities | Scenarios crossing session boundaries (e.g., context inheritance) expose whether session-context resolution survives across sibling conversations |
| Prompt policy as inline baseline vs external compiler path | Current runtime uses inline prompt; target design externalizes assets via a compiler path of PromptAssetLoader→PromptAssembler→ResponseGuardrailMiddleware | Scenarios involving prompt variant selection, experiment assignment, or guardrail outcomes cannot rely on the current baseline for those behaviors |

## Stable Boundaries

| Boundary | Must Remain Stable Because | Explicitly Does Not Cover |
|----------|----------------------------|---------------------------|
| Conversation is the STM identity unit | All agent runtime, checkpointer, service-layer lifecycle, and management API surfaces use conversation_id→thread_id. Changing this invalidates runtime memory, service-layer archive guards, and all management endpoints. | Session-level cross-conversation context injection; future LTM personalization |
| Backend routes→services→repositories→database layering | All existing blueprints, service factories, and repository singletons assume this ordering. Violating it breaks DI contracts, testability via protocol mocks, and health-check aggregation. | Frontend-component state management; agent-internal tool orchestration |
| Tools compute facts; LLM reasons about them | Enforced by ADR-001; prevents fabricated figures and keeps computation auditable. Violating it reintroduces hallucination risk. | Prompt-level truth injection; model-native retrieval |
| Spec-driven, traceable delivery | Enforced by project constitution v2.1.0; all non-trivial changes start from governed artifacts and refresh long-lived docs. Violating it creates drift across code, contracts, and documentation. | Real-time chat latency; cache-eviction policy |

## Change Axes

| Expected Change | Isolated By | Scenario Impact |
|-----------------|-------------|-----------------|
| Provider model expansion (new LLM providers) | ModelClientFactory with provider registration and cache-by-key pattern | New providers appear as alternative model sources with no change to routing, tooling, or memory scenarios |
| Prompt compiler path rollout (externalized assets) | ADR-002 (Skills pattern) and ADR-003 (externalized assets) govern the transition without breaking the current baseline | Scenarios gain prompt variant, experiment, and guardrail metadata options; the compiler path is additive to the current baseline |
| Frontend modernization (CRA→Vite, design system) | Frontend communicates exclusively through REST endpoints and Socket.IO events; no frontend changes affect backend or agent boundaries | User-interface scenarios remain stable because transport contracts do not change |
| Memory tier expansion (LTM, RAG) | ADR-001 reserves LTM and RAG as distinct future layers; they are not extensions of the current checkpoint boundary | Cross-conversation personalization scenarios gain support incrementally without reshaping conversation-scoped STM |
| Load and scale changes | Kubernetes HPA, connection pooling, and cache TTL jitter isolate deployment-layer changes from application logic | Throughput and latency scenarios vary by deployment topology but not by application behavior |

## Invariants

| Invariant | Scenario Evidence | Risk If Violated |
|-----------|-------------------|------------------|
| Memory never stores prices, ratios, forecasts, or recommendations | ADR-001 and project constitution Principle III and Principle IV; all memory scenarios limit LTM to preferences and STM to conversation state | Financial hallucination and compliance failure |
| Deterministic tools compute numbers; LLM reasons about them | All tool-use scenarios show the agent invoking tool execution for data retrieval; the LLM does not fabricate metrics | Fabricated figures become indistinguishable from sourced data |
| Session context is parent business context, not checkpoint state | All session lifecycle scenarios show the service layer resolving reusable context independently from checkpoint-managed runtime state | Sibling conversations share thread state and violate memory isolation |
| Every non-trivial change starts from governed artifacts | Constitution Principle I; all feature scenarios in the SDD lifecycle reference SRS IDs, architecture/technical design sources | Code, contracts, and documentation drift without detection |
| Cross-references between docs use section-level anchors | Constitution Document Referencing rules; all design and spec artifacts must precisely identify governing sections | Agentic workflows lose traceability and produce inaccurate implementations |

## Non-goals / Anti-patterns

| Non-goal / Anti-pattern | Why It Is Out of Scope or Harmful |
|-------------------------|-----------------------------------|
| Multi-agent orchestrator with specialist agent handoff | Scenarios do not yet require orchestrated specialist handoffs; the single ReAct agent with route-aware skills covers all current use cases. Premature multi-agent architecture would add routing complexity without scenario evidence. |
| Hard-delete semantics for conversations or sessions | All lifecycle scenarios use archive-over-delete. Hard deletion would invalidate audit trails, checkpoint recovery, and cascade behavior across the hierarchy. |
| Full LTM/RAG implementation as runtime dependency | LTM and RAG remain planned boundaries under ADR-001. Making them required runtime dependencies before scenario demand exists would add deployment and data-management overhead without user-visible benefit. |
| Real-time market data streaming | Current scenarios use request-response tool calls against Yahoo Finance. Real-time streaming would require a different fact-source architecture (WebSocket feeds, push ingestion) that no scenario currently requires. |

## Actors and Participants

| Actor / Participant | Goal | Responsibility | Boundary |
|---------------------|------|----------------|----------|
| End User (Investor) | Obtain stock investment insights, analysis, and portfolio information through natural language | Submits queries, receives streaming or non-streaming responses, manages workspaces and conversations | Client-side; interacts through REST and Socket.IO transport |
| AI Assistant (Agent) | Answer queries using tool orchestration, memory, and LLM reasoning | Routes queries, selects and invokes tools, manages conversation state, generates streaming or complete responses | Agent runtime boundary; consumes service-layer lifecycle metadata |
| System Operator | Maintain, monitor, and reconcile system state | Runs reconciliation scripts, reviews health endpoints, manages API contracts and deployment | Operational boundary outside the request-response user flow |
| LLM Provider (OpenAI/Grok) | Generate reasoned responses from prompts and tool results | Processes prompt content, returns model completions; subject to provider fallback policy | External; accessed through ModelClientFactory |
| Financial Data Source (Yahoo Finance) | Supply market data, prices, and financial fundamentals | Returns structured financial data on request through tool execution paths | External; accessed through controlled tool-invocation interfaces |
| Service Layer (ChatService, ConversationService) | Govern conversation lifecycle, ownership, archive integrity, and metadata | Validates request, resolves session context, enforces archive guards, records per-turn metadata | Internal service boundary between transport and agent runtime |
| Prompt Governance (Planned Prompt Compiler) | Control behavioral policy, response guardrails, and prompt variant selection | Resolves prompt assets, composes deterministic prompt contracts, enforces guardrail rules at final response boundary | Planned internal policy boundary; current baseline uses inline prompts |

## Use Cases

| Use Case | Actor | Goal | Preconditions | Scope Boundary |
|----------|-------|------|---------------|----------------|
| UC-1: Ask stock inquiry | End User | Get natural-language response to a stock-related question | User is authenticated; conversation exists or is created; agent runtime is available | Request flows from transport through service layer, agent runtime, tools, LLM, and guardrails |
| UC-2: Stream analysis results | End User | Receive incremental response during complex analysis | Same as UC-1; request specifies streaming mode | Includes SSE framing, admission windows, and terminal guardrail evaluation |
| UC-3: Manage workspace hierarchy | End User | Create, list, update, archive workspaces, sessions, and conversations | User is authenticated; parent exists for create operations; ownership chain is valid | Management API surface only; does not involve agent reasoning |
| UC-4: Resume conversation from memory | End User | Continue a prior conversation with retained context | Conversation exists and is active; checkpointer has stored prior state | Agent runtime retrieves checkpoint; service layer validates lifecycle |
| UC-5: Handle provider failure | System (Agent Runtime) | Degrade gracefully when primary LLM provider fails | Primary provider returns error or times out; fallback providers are configured | Triggered inside model factory fallback loop; user receives response from fallback or error message |
| UC-6: Sync spec-driven delivery | System Operator | Keep traceability and documentation aligned after delivery | Feature is implemented and verified; spec-kit artifacts exist; long-lived docs are identified | Synchronization boundary between specs/ and docs/; governed by constitution delivery sync gates |
| UC-7: Archive conversation | End User | Finalize a conversation thread as immutable record | Conversation exists and is active or summarized | Service layer enforces cascade rules; checkpointer preserves readonly state |
| UC-8: Apply prompt variant | System (Planned Prompt Compiler) | Select and apply a prompt experiment or locale variant for controlled rollout | Prompt compiler path is active; variant is registered in manifest | Planned prompt-system boundary; does not affect current inline baseline |

## Scenario Paths

| Scenario | Main Path | Successful Outcome | Alternative / Failure Branches |
|----------|-----------|--------------------|--------------------------------|
| S1: Basic Q&A (UC-1) | User submits query → transport routes to service layer → service resolves conversation → agent runtime classifies route → agent selects and invokes tools → LLM generates response → guardrail evaluates → response surfaces to user | User sees accurate, sourced answer with provenance | A1: Route is ambiguous → falls back to GENERAL_CHAT with reduced tool scope. A2: Tool call fails → agent returns cached data or explains unavailability. A3: Guardrail blocks output → user receives safe refusal with explanation. |
| S2: Streaming analysis (UC-2) | Same tool and LLM path as S1 but response is emitted incrementally through SSE chunks → admission windows evaluate partial output → final guardrail commitment completes the stream | User sees progressive tokens with smooth completion | A1: Mid-stream blocker detected → emission stops, safe terminal frame emitted. A2: Client cancels → generation halts, cancelled state recorded. A3: Transport interrupted → terminal error frame with safe messaging. |
| S3: Full management lifecycle (UC-3, UC-7) | Create workspace → create session → create conversations → send messages → close session → archive conversation → verify immutability | User creates, manages, and archives the full workspace hierarchy with consistent ownership enforcement | A1: Create on archived parent → 409 conflict with explanation. A2: Access other user's resource → 403/404. A3: Archive cascade → child conversations also archive. |
| S4: Memory continuity (UC-4) | User sends message → agent retrieves checkpoint → tool call + LLM incorporates prior context → checkpoint saved → subsequent message continues from updated state | Agent retains conversation-scoped memory; sibling conversations are isolated | A1: Checkpoint unavailable → agent starts with fresh state, previous context not available. A2: Stateless request → no memory used. |
| S5: Provider fallback (UC-5) | Primary provider times out → model factory detects failure → fallback provider is selected → agent retries with fallback → response returned | User receives response from fallback provider with transparent degradation | A1: All providers fail → user receives error message. A2: Partial stream failure → fallback takes over mid-stream behavior is undefined by current architecture. |
| S6: Spec-driven feature delivery (UC-6) | SRS requirement identified → speckit.constitution → speckit.specify → speckit.plan → speckit.tasks → implement → verify → sync docs and traceability | Feature is traceable from requirement through implementation, and long-lived docs reflect the change | A1: Docs-only change → lighter path through speckit phases. A2: Sync gap detected → drift is flagged in traceability report. |

## Acceptance Semantics

| Acceptance Scenario | Observable Result | Must Hold | Not Covered |
|---------------------|-------------------|-----------|-------------|
| User receives a financial analysis response | Text response appears in the UI with cited sources | Tool calls executed, LLM reasoned about the result, response passed guardrail evaluation | Multi-turn conversation beyond the current exchange |
| Streaming response renders progressively | SSE chunks appear incrementally in the UI, stream ends with a terminal event | Admission windows pass, final guardrail commits, terminal state is either "completed" or "cancelled" or "blocked" | WebSocket path has the same guardrail and lifecycle behavior |
| Conversation continues with prior context | Agent references earlier messages in the same conversation | Checkpoint is loaded, thread_id matches conversation_id | Cross-conversation context injection |
| Provider fails and fallback takes over | Response is generated by a different model provider | ModelFactory fallback loop is triggered, user is informed of provider change | Mid-stream provider switching |
| Workspace hierarchy is created and archived | API returns correct records, archive state is immutable | Ownership chain validated, cascade rules enforced, 403/404 for cross-user access | Soft-delete or recovery from archive |
| Feature work updates traceability | spec-traceability.yaml and spec-sync-status.md reflect the new state | Sync script runs, delivery sync gates pass | Fully automated drift repair |

## Scenario Gaps

| Gap | Affected Scenario | Why It Matters |
|-----|-------------------|----------------|
| Socket.IO streaming parity with REST lifecycle guards | S2 (streaming analysis) | The Socket.IO path currently calls the agent directly without ChatService archive or ownership validation. This means streaming via WebSocket has weaker guard behavior than streaming via SSE. |
| Mid-stream provider switching is undefined | S5 (provider fallback) | If a provider fails mid-stream during SSE emission, the architecture has no defined behavior for switching to a fallback provider without restarting the request. Current fallback only works at request granularity. |
| No prompt variant or experiment assignment in current baseline | UC-8 (Apply prompt variant) | All prompt-related scenarios beyond the current inline baseline are planned behavior. The architecture cannot yet select, evaluate, or roll back prompt variants through the compiler path. |

## Prohibited Content

Do not write architecture components, class designs, APIs, database tables, implementation tasks, test strategy, deployment scripts, or framework choices here.
