# Architecture Synthesis: DP Stock Investment Assistant

**Input Views**:
- Scenario: `.specify/memory/architecture-scenario-view.md`
- Logical: `.specify/memory/architecture-logical-view.md`
- Process: `.specify/memory/architecture-process-view.md`
- Development: `.specify/memory/architecture-development-view.md`
- Physical: `.specify/memory/architecture-physical-view.md`

**Authority Basis**: This synthesis reflects the current agent-domain target design stated in `ARCHITECTURE_DESIGN.md`, `TECHNICAL_DESIGN.md`, and the SRS. Repository facts may explain existing implementation evidence, but this refresh does not edit the repository-facts artifact.

## View Index

| View | File | Purpose | Current Status |
|------|------|---------|----------------|
| Scenario | `.specify/memory/architecture-scenario-view.md` | Actor goals, user-observable behavior, boundary scenarios, and acceptance outcomes | Refreshed 2026-07-06 |
| Logical | `.specify/memory/architecture-logical-view.md` | Architecture objects, ownership boundaries, invariants, and non-responsibilities | Refreshed 2026-07-06 |
| Process | `.specify/memory/architecture-process-view.md` | Runtime collaborations, fail-closed branches, and response-boundary handoffs | Refreshed 2026-07-06 |
| Development | `.specify/memory/architecture-development-view.md` | Package intent, dependency direction, and forbidden compile-time crossings | Refreshed 2026-07-06 |
| Physical | `.specify/memory/architecture-physical-view.md` | External systems, operational stores, provider classes, and deployment constraints | Refreshed 2026-07-06 |

## Architecture Intent

The architecture stabilizes an agent-domain target design where a single ReAct-style runtime remains the reasoning topology, while service orchestration, prompt policy, tool exposure, gateway admission, provider mediation, normalization, request-scoped context, persistence, and governance remain separate responsibilities. Current behavior remains explicitly distinguished from implemented, gated, target, and planned behavior so architecture memory does not overstate delivery status.

The main architectural shift is the move from broad tool availability toward route-filtered, descriptor-backed, policy-governed tool execution. Tools remain model-visible capabilities only at the descriptor surface; provider adapters, provider policies, normalized evidence, retained artifacts, and degraded execution states stay below that surface.

## Central Design Forces

| Force | Architectural Meaning | Cross-View Consequence |
|-------|-----------------------|------------------------|
| Single-agent topology with governed capabilities | The current agent topology is one ReAct runtime, not a multi-agent system | Scenario and process views route the query before tool exposure; development view keeps orchestration and tool execution separate |
| Service-layer lifecycle authority | Lifecycle, ownership, archive guards, and session context belong to service orchestration | Logical, process, and development views forbid the agent runtime and checkpointer from setting lifecycle state |
| Checkpointer as STM only | Conversation-scoped short-term memory persists runtime state only | Physical and logical views separate checkpoint state from service-owned metadata, retained artifacts, and governance artifacts |
| Evidence before response | Market facts flow through admitted tools, provider policy, normalization, context packaging, and prompt boundaries | Tool outputs must carry lineage, freshness, and degraded-state semantics before they influence a response |
| Provider authority hierarchy | Official or licensed Vietnam-market providers have higher authority than public web, wrapper, visualization, or international fallback sources | Physical and logical views require provider class and freshness semantics to remain visible in normalized outputs |
| Visualization as provenance, not default evidence | TradingView is visualization provenance unless explicitly admitted for a visual or chart-backed task | Scenario, logical, and physical views prevent chart widgets from becoming canonical market evidence by default |
| Governance as delivery boundary | Spec Kit artifacts, traceability, and sync status are part of the architecture change control path | Development and scenario views keep governance separate from runtime code and require verified status before downstream synchronization |

## Primary Tradeoffs

| Tradeoff | Chosen Direction | Consequence | Review Trigger |
|----------|------------------|-------------|----------------|
| Single ReAct runtime vs specialized agents | Keep one ReAct runtime with route-filtered capability exposure | Lower coordination complexity, but no specialist-agent parallelism | Revisit when routes require materially different reasoning loops |
| Thin gateway vs heavy workflow engine | Gateway performs admission, policy checks, and envelope handling; registry and providers do the work | Keeps the execution boundary small and auditable | Revisit if multi-step tool workflows require orchestration beyond admission |
| Request-scoped context vs durable evidence store | `ToolContextPack` is scoped to one request; durable evidence is retained as artifact metadata where required | Reduces memory leakage and stale evidence reuse | Revisit if cross-request evidence reuse becomes a requirement |
| Visualization provider vs canonical source | TradingView remains visualization provenance by default | Prevents chart availability from overriding source authority | Revisit if a signed or licensed visualization feed becomes canonical |
| Deny-by-default generic web fetch vs broad research access | Generic web fetch is admitted only through policy and normalized output | Reduces untrusted evidence injection risk | Revisit if broad web research becomes a governed product feature |
| Prompt guardrails as planned middleware vs current prompt baseline | Current baseline remains in effect; gated M1/M2 behavior and planned guardrails are layered explicitly | Avoids claiming middleware exists before implementation | Revisit when executable prompt guardrail contracts are approved |
| Provider fallback before response vs mid-stream fallback | Fallback is modeled before committed output; mid-stream fallback remains an explicit gap | Streaming failures may require degraded completion or retry | Revisit before high-reliability streaming commitments |

## Stable Boundaries

| Boundary | Owner | Must Remain Stable Because | Forbidden Crossing |
|----------|-------|----------------------------|--------------------|
| Transport boundary | Transport package | It adapts clients to service workflows without owning domain policy | Transport must not bypass service lifecycle, ownership, archive, or session-context checks |
| Service orchestration boundary | Service layer | It owns lifecycle, ownership, archive guards, and session context | Agent runtime, tools, and checkpointer must not set lifecycle state |
| Agent runtime boundary | ReAct runtime | It selects among exposed capabilities and composes responses | Runtime must not see provider adapters directly or infer hidden tools |
| Prompt policy boundary | Prompt assets and planned guardrails | It shapes behavior without becoming a fact store | Prompts must not become canonical price, ratio, forecast, or provider metadata stores |
| Tool surface and gateway boundary | Tool system | It exposes route-filtered descriptors and admits execution envelopes | Providers must not be exposed directly as model-visible tools |
| Provider policy and adapter boundary | Provider layer | It resolves market authority, freshness, access posture, and fallback ordering | Adapters must not return raw provider-specific payloads to the prompt boundary |
| Normalization and context boundary | Evidence/context layer | It packages lineage, freshness, degraded states, and retained artifact references for one request | `ToolContextPack` must not become persistent STM or lifecycle metadata |
| Persistence and artifact metadata boundary | Persistence layer | It stores conversations, checkpoints, metadata, and artifact references with different ownership semantics | Artifact content stores must not become service metadata authority |
| Governance boundary | Spec Kit workflow | It controls feature readiness and traceability | Runtime packages must not import or depend on governance artifacts |

## Cross-View Architecture Model

| Concept | Scenario Meaning | Logical Interpretation | Runtime Role | Development Boundary | Physical Constraint |
|---------|------------------|------------------------|--------------|----------------------|---------------------|
| User request | Investment or management task initiated by a user | Request with ownership, session, route, and archive context | Enters service orchestration before agent work | Transport to service orchestration | Client-facing transport surfaces |
| Route classification | Determines task family and expected capabilities | Route label with confidence and allowed capability categories | Filters tool descriptors before ReAct selection | Agent orchestration and tool surface packages | No dedicated external system required |
| Tool surface | User-visible capability set for one request | Descriptor set with capability, policy, risk, and provider expectations | Constrains the model-visible action space | Tool surface and gateway packages | In-process boundary in the current architecture |
| Gateway admission | Execution approval for one selected tool call | Envelope with admitted parameters, policy decision, and degraded-state path | Fails closed before registry execution when policy is unmet | Tool gateway package | No provider credentials exposed at model boundary |
| Registry execution | Concrete tool capability invocation | Registered capability contract below the gateway | Calls provider policy and normalization paths as needed | Tool registry package | Runs inside application runtime |
| Provider policy | Market and authority decision point | Provider descriptor with class, license posture, freshness, and fallback order | Selects adapters and handles fallback before normalization | Provider policy package | Yahoo current path; target Vietnam-first and fallback providers |
| Provider adapter | External data integration | Source-specific boundary below tools | Fetches provider data but does not shape final prompt context | Provider adapter package | External official, licensed, public-web, wrapper, international, or visualization systems |
| Normalized output | Evidence package returned by tools | Provider-neutral output with lineage, freshness, confidence, and degraded state | Supplies response context and retained metadata | Normalization and context packages | Cache, metadata, and artifact stores retain supporting information where required |
| `ToolContextPack` | Request-scoped evidence and artifact context | Non-persistent context bundle for response composition | Feeds prompt/response boundary for the active request only | Normalization/context package | Not a database, cache, or long-term memory store |
| Visualization provenance | Chart or visual source support | Provenance record for visualization-backed output | Supports charts and reports without becoming default evidence | Reporting and visualization packages | TradingView and retained visualization artifacts |
| Mutation receipt | Confirmation of governed side effects | Receipt with actor, target, status, and audit metadata | Returned after admitted mutation-oriented tool execution | Tool gateway, service orchestration, and persistence boundaries | Stored as metadata where retention policy requires |
| Artifact metadata | Retained report or visualization references | Metadata about generated output and evidence lineage | Enables reporting continuity and traceability | Persistence/artifact packages | Metadata in database; large generated content in filesystem storage |
| Degraded state | User-visible limitation when evidence or provider access is incomplete | State marker with cause, affected capability, and safe fallback | Shapes response boundary and prevents silent omission | Gateway, provider, normalization, and prompt packages | Observability and metadata should record the condition |

## Architecture Conclusions

| Conclusion | Affected Views | Boundary/Owner | Consequence |
|------------|----------------|----------------|-------------|
| The agent remains a single ReAct runtime | Scenario, Process, Development | Agent runtime | Tool-system enhancement is capability governance, not a multi-agent redesign |
| Service orchestration and checkpointer remain separate authorities | Logical, Process, Development, Physical | Service layer and checkpointer | Lifecycle and archive behavior cannot be recovered from STM alone |
| Provider adapters remain hidden behind tools | Logical, Process, Development, Physical | Tool gateway and provider layer | The model sees capabilities and descriptors, not provider-specific integration surfaces |
| Normalized context is the response contract | Scenario, Logical, Process | Normalization/context boundary | Responses depend on source lineage, freshness, and degraded-state metadata rather than raw provider payloads |
| Visualization must preserve provenance | Scenario, Logical, Physical | Visualization/reporting boundary | TradingView-backed artifacts support visual explanation but do not supersede canonical evidence by default |
| Reporting composes retained context | Scenario, Logical, Development, Physical | Reporting and artifact metadata boundaries | Reports should use normalized context and retained artifact metadata, not direct provider scraping |
| Governance is part of architecture readiness | Scenario, Development, Physical | Spec Kit boundary | Verified feature state and synchronized traceability are required before architecture memory claims completion |

## Current, Target, Planned, And Gated Labels

| Label | Meaning In This Architecture Memory | Examples |
|-------|-------------------------------------|----------|
| Current | Existing baseline behavior stated by the authority documents | Single ReAct runtime, service-owned lifecycle, conversation-scoped STM, current registry-backed cache-aware tools, Yahoo-backed current market path |
| Implemented or gated | Behavior the authority documents explicitly mark delivered or activation-gated | Prompt M1/M2 externalization and route-skill assembly where enabled; feature verification status does not by itself promote target Phase 2B tool concepts to current architecture |
| Target | Agreed architecture direction that guides near-term implementation until authority documents mark it current | Provider policy, descriptors, gateway admission, route-filtered tool surface, normalized output, degraded states, Vietnam-first provider strategy |
| Planned | Designed but not yet treated as implemented | Prompt guardrail middleware, future LTM/RAG, executable IR-3 schemas, production observability controls |
| Gap | Known missing capability or unresolved operational posture | Socket.IO lifecycle parity, mid-stream provider fallback, production provider licensing, production observability hardening |

## Open Risks And Review Triggers

| Risk Or Trigger | Missing Evidence Or Change Condition | Affected Views | Required Architecture Review |
|-----------------|--------------------------------------|----------------|------------------------------|
| Socket.IO lifecycle parity remains unresolved | Streaming path lacks the same lifecycle and archive guarantees as service-managed flows | Scenario, Process, Development | Required before Socket.IO becomes the primary managed streaming path |
| Mid-stream provider fallback is undefined | Provider failure after response streaming begins lacks an approved handoff model | Process, Development, Physical | Required before high-reliability streaming guarantees are made |
| Future LTM/RAG is not active architecture | Long-term memory and retrieval remain reserved future capabilities | Scenario, Logical, Process, Development | Required before persistent investment facts or retrieval context are introduced |
| Prompt guardrail middleware is planned | Guardrail policy exists as target behavior but not as fully executable middleware | Scenario, Logical, Process, Development | Required before claiming automated prompt-policy enforcement |
| Production provider licensing posture is unresolved | Official, licensed, public-web, wrapper, and international fallback sources have different legal and reliability characteristics | Logical, Physical | Required before production Vietnam-market provider commitments |
| Executable IR-3 schemas are not complete | Tool descriptors and policy descriptors need machine-checkable contracts for full governance | Logical, Development | Required before broad third-party or remote tool expansion |
| Production observability controls are incomplete | Trace, metrics, alerting, and degraded-state telemetry are not yet production-grade | Process, Physical | Required before operational SLA commitments |

## Architecture Review Triggers

Re-run this architecture synthesis when any of the following changes occur:

- The agent topology changes from one ReAct runtime to multiple coordinated agents.
- Tool execution moves out of the in-process gateway boundary.
- Provider adapters become directly visible to model prompts or user-facing routing.
- TradingView or another visualization source is promoted to canonical evidence.
- Generic web fetch is admitted for broad research without provider-class normalization.
- Conversation memory expands from STM into durable LTM/RAG.
- Prompt guardrails become executable middleware or change response commitment rules.
- Production provider licensing, caching, retention, or observability posture changes materially.
