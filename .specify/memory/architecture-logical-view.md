# Logical View — DP Stock Investment Assistant

**Input**: `.specify/memory/architecture-scenario-view.md`

**Purpose**: Derive capability boundaries, domain objects, states, relationships, and invariants from the scenario view.

## Architecture Intent

This view preserves the logical separation between transport, orchestration, reasoning, tool execution, memory, policy, and persistence so that each capability boundary can evolve independently without collapsing concerns into a shared layer.

## Core Tensions

| Tension | Current Tradeoff Direction | Logical Consequence |
|---------|----------------------------|---------------------|
| Single agent runtime vs route-aware specialization | One ReAct agent handles all routes via skill selection; multi-agent orchestration is deferred | Logical boundaries around reasoning and tool orchestration must accommodate route-aware skills without creating a separate orchestrator boundary |
| Service-layer lifecycle governance vs agent-runtime checkpoint authority | ChatService owns archive guards and metadata; agent runtime owns checkpoint-managed reasoning state | Two distinct authority surfaces exist for the same conversation; their correspondence is correspondence-based, not unified |
| Inline prompt policy vs external compiler path | Current runtime uses a single governed prompt; compiler path adds asset loader, assembler, and guardrail middleware | Prompt policy semantics are split across current and planned boundaries; the current baseline does not expose variant or experiment selection |
| REST vs streaming vs WebSocket transport parity | REST includes full lifecycle guards; SSE supports streaming with partial guard coverage; Socket.IO has limited lifecycle parity | Transport-specific boundaries introduce different safety surfaces for the same logical capability |

## Stable Boundaries

| Boundary | Must Remain Stable Because | Explicitly Does Not Own |
|----------|----------------------------|-------------------------|
| Transport-layer request admission | All inbound requests pass through transport before orchestration; this boundary isolates transport concerns from reasoning, state, and policy | Request validation, authorization, lifecycle governance, agent reasoning, prompt composition, tool execution |
| Service-layer lifecycle and ownership | Conversation existence, archive status, ownership chain, and session context resolution are enforced before and after agent execution | Agent-runtime state, tool execution results, prompt behavior, LLM provider selection |
| Agent-runtime reasoning and tool orchestration | The ReAct loop selects tools, invokes LLM providers, and manages thread-local checkpoint state | Lifecycle authority, transport semantics, durable metadata persistence, prompt policy selection |
| Checkpoint-managed conversation state | MongoDB checkpointer stores thread-local agent state scoped to conversation_id | Service-layer lifecycle metadata, session context, cross-conversation state, prompt policies |
| Tool-invocation evidence acquisition | Tools fetch financial data from external sources through controlled interfaces and return results for LLM interpretation | Caching policy, provider selection, checkpoint persistence, response guardrails |
| Prompt policy and guardrail enforcement | Inline prompt defines behavior; planned compiler path separates asset resolution, composition, and guardrail evaluation | State management, tool execution, metadata persistence, provider selection |
| Spec-kit artifact governance | Delivery-scoped artifacts in specs/ and long-lived docs in docs/ are governed by the constitution | Implementation code, runtime configuration, deployment manifests |

## Change Axes

| Expected Change | Isolated By | Logical Impact |
|-----------------|-------------|----------------|
| New LLM provider added | ModelClientFactory with provider registration pattern | Provider selection boundary expands but transport, routing, tool, and memory boundaries are unaffected |
| Prompt compiler path activated (planned) | ADR-002 and ADR-003 govern additive introduction without breaking current baseline | Prompt policy boundary gains selection and composition semantics without changing current runtime behavior |
| Frontend framework migration | Transport contract stability; REST and Socket.IO events do not change | No logical boundary impact; only the transport-layer client implementation changes |
| LTM/RAG tier implementation (planned) | ADR-001 reserves LTM and RAG as dedicated surfaces; they do not extend checkpoint or service boundaries | Memory domain expands with a cross-conversation personalization surface and a sourced-evidence surface |
| Conversation lifecycle expansion (summarized state) | Schema supports summarized status and fields, but automated summarization trigger is not yet wired | Lifecycle boundary gains a planned transition path without altering current active/archived semantics |

## Invariants

| Invariant | Source Scenario / Object / State | Risk If Violated |
|-----------|----------------------------------|------------------|
| Service layer enforces lifecycle before agent runtime | S1, S3, S4: ChatService validates conversation existence and archive status before invoking the agent | Archived conversations accept new turns; ownership chain is bypassed |
| Checkpoint stores only thread-local reasoning state | S4: Checkpoints are keyed by conversation_id→thread_id and do not contain session context or lifecycle metadata | Checkpoints become the source of truth for ownership and break service-layer lifecycle authority |
| Tool results are data-only context, not policy segments | S1: Tool outputs are injected as evidence for the LLM to interpret, not as instruction-bearing prompt content | Tool outputs can override behavioral policy or be treated as higher-authority instructions |
| Spec-kit artifacts reference docs/ documents with section-level anchors | S6: Cross-references between specs/ and docs/ must be precise and durable under constitution rules | Agentic workflow loses traceability; references break when headings change |
| Guardrail evaluation precedes response commitment | S1, S2: Guardrails execute after model generation but before any response is committed to the response surface | Unsafe output reaches the user; guardrail outcomes are not attributable |

## Non-goals / Anti-patterns

| Non-goal / Anti-pattern | Why It Is Out of Scope or Harmful |
|-------------------------|-----------------------------------|
| Checkpointer as lifecycle authority | Would collapse two distinct logical boundaries (runtime state and business governance) into one store, creating coupling between checkpointer schema and lifecycle policy |
| Agent runtime owning session context | Would duplicate service-layer authority inside the reasoning loop, making session-context resolution dependent on agent availability |
| Prompt assets as fact store | Would violate ADR-001 separation; prompts control behavior, not domain truth |
| Tool layer caching as persistence | Tool caches have TTLs and are not authoritative for any logical object's lifecycle or ownership |
| Specs/ as long-lived documentation | Would mix delivery-scoped evidence with stable reference material; only stable verified knowledge is promoted to docs/ |

## Capability Boundaries

| Capability / Boundary | Responsibility | Input | Output | Explicitly Does Not Own | Scenario Source |
|-----------------------|----------------|-------|--------|--------------------------|-----------------|
| Transport and Request Admission | Accept inbound requests, route to correct handler, manage streaming connections | HTTP requests, Socket.IO events, SSE connections | Normalized work items routed to service layer | Request validation, lifecycle governance, agent reasoning, tool execution | UC-1, UC-2 |
| Service Orchestration and Lifecycle | Validate conversation existence and archive status, resolve session context, record per-turn metadata | Normalized conversation-id and request payload | Validated work item for agent runtime, lifecycle outcomes recorded | Checkpoint state, tool results, prompt composition, provider selection | UC-1, UC-2, UC-3, UC-4, UC-7 |
| Agent Reasoning and Tool Orchestration | Route classification, tool selection and invocation, LLM provider interaction, checkpoint management | Validated work item from service layer, thread-id from conversation binding | Generated response content (streamed or complete), checkpoint state saved | Lifecycle authority, durable metadata, transport framing, prompt variant selection | UC-1, UC-2, UC-4, UC-5 |
| Checkpoint and Memory Management | Persist and retrieve thread-local agent execution state scoped to conversation_id | Thread-id, conversation-turn data | Checkpoint state for recovery | Lifecycle metadata, session context, tool execution results, prompt policy | UC-4 |
| Tool-Invocation Evidence Acquisition | Fetch financial data from external sources through governed interfaces, cache results | Normalized tool request with symbol and parameters | Structured data result with provenance | LLM reasoning, policy enforcement, checkpoint management, provider selection | UC-1, UC-2 |
| Provider Selection and Model Invocation | Select LLM provider based on configuration, manage provider fallback sequence, cache client instances | Prompt content, model selection parameters | Model-generated content (streamed or complete) | Tool execution, lifecycle governance, prompt asset selection, checkpoint state | UC-1, UC-2, UC-5 |
| Prompt Policy and Guardrail Enforcement | Compose prompt from policy assets, control behavior and output contracts, enforce guardrails at response boundary | Route classification, request context, model draft | Compiled prompt, guardrail result | State management, tool execution, metadata persistence, provider selection | UC-1, UC-2, UC-8 |
| Metadata Persistence | Store conversation lifecycle state, ownership data, session linkage, and per-turn counters | CRUD operations on conversation metadata | Persistent conversation records with lifecycle and ownership fields | Checkpoint state, tool results, LLM provider cache, prompt state | UC-3, UC-7 |
| Spec-Kit Artifact Governance | Manage delivery-scoped specs, plans, tasks, review evidence, and synchronization with long-lived docs | Feature requirements, architecture and design inputs | Governed artifacts in specs/, synchronized docs/ and traceability | Implementation code, runtime configuration, deployment state | UC-6 |
| Financial Data Source Provision | Supply market data, prices, and fundamentals through external API access | Symbol and data-type parameters | Structured financial data with freshness metadata | Prompt composition, lifecycle governance, checkpoint persistence | UC-1 |

## Domain Objects and Relationships

| Object | Meaning | Owning Capability | Key Relationships | Fact Source | Invariants |
|--------|---------|-------------------|-------------------|-------------|------------|
| Conversation | A scoped reasoning thread with lifecycle status, ownership metadata, and checkpoint-managed agent state | Service Orchestration and Lifecycle | Belongs to a session; has a checkpoint (1:1 via conversation_id=thread_id); owns per-turn metadata (message_count, total_tokens) | Service layer creates and manages; checkpoint stores runtime state | Must have an active status to accept new turns; archive is irreversible; owned by exactly one user through workspace→session hierarchy |
| Session | A parent business grouping for related conversations with reusable context | Service Orchestration and Lifecycle | Contains conversations; belongs to a workshop; owns assumptions, pinned_intent, focused_symbols | Service layer manages session context independently from checkpoint state | Cannot be deleted while conversations exist; archive cascades to all child conversations |
| Workspace | A top-level user-owned organizational container for sessions | Service Orchestration and Lifecycle | Owns sessions; belongs to exactly one user | Service layer creates and manages | Archive cascades to all child sessions and conversations |
| Checkpoint | Serialized agent-runtime state for a single conversation thread | Checkpoint and Memory Management | Maps 1:1 to conversation via thread_id | LangGraph MongoDBSaver stores and retrieves | Contains only thread-local reasoning state; no lifecycle metadata, session context, or tool-cache content |
| Route Classification | The semantic category assigned to a user query for skill selection | Agent Reasoning and Tool Orchestration | Determines which tools the agent may invoke and which route skill is activated | Agent runtime classifies via semantic-router | Does not execute tools or persist state; may be overridden by explicit routing hints |
| Prompt Asset (planned) | A versioned, reviewed prompt fragment with metadata (locale, parity, selection mode) | Prompt Policy and Guardrail Enforcement | Belongs to a lineage; shares a parity group with locale siblings | Prompt compiler path manages through manifest and frontmatter | Must pass review before promotion; baseline variant exists for fallback |
| Guardrail Result | The outcome of response-policy checks against the model draft | Prompt Policy and Guardrail Enforcement | Originates from ResponseGuardrailMiddleware; is consumed by the response surface | Guardrail evaluation at the final response boundary | Status must be "pass", "warn", "block", or "degraded"; must preserve triggered rule identifiers |
| Provider Client | A cached LLM provider instance bound to a specific model | Provider Selection and Model Invocation | Keyed by {provider}:{model_name}; retrieved from ModelClientFactory cache | ModelClientFactory creates and caches | May be replaced via cache invalidation; fallback sequence is configured via config |
| Spec Feature Artifact | A delivery-scoped specification, plan, or task artifact under specs/ | Spec-Kit Artifact Governance | References SRS IDs, architecture/design docs via section-level anchors; drives implementation evidence | Created and maintained through the SDD lifecycle | Must pass constitution check before planning; must be synchronized with long-lived docs after delivery |
| Long-Lived Doc | A stable reference document under docs/ for requirements, architecture, design, ADRs, contracts, or runbooks | Spec-Kit Artifact Governance | Receives updates from spec-kit sync phase; provides section-level anchors for spec references | Maintained through the SDD delivery-and-sync lifecycle | Must be updated in the same delivery cycle when stable behavior changes |

## State and Lifecycle

| Object / Flow | State | Entered When | Exited When | Forbidden Transition | Responsible Boundary |
|---------------|-------|--------------|-------------|----------------------|----------------------|
| Conversation | active | Created via management API or first message in stateless flow | User closes, session closes, or archive is requested | archived→active | Service Orchestration and Lifecycle |
| Conversation | closed | Parent session is closed; existing conversations remain read-write but no new conversations may be created | Archived | closed→active | Service Orchestration and Lifecycle |
| Conversation | archived | User requests archive or parent session/workspace is archived | None (terminal) | archived→any | Service Orchestration and Lifecycle |
| Session | active | Created via management API | Closed or archived | archived→active | Service Orchestration and Lifecycle |
| Session | closed | User requests close; existing conversations continue, new conversation creation blocked | Archived | closed→active | Service Orchestration and Lifecycle |
| Session | archived | User requests archive or parent workspace is archived | None (terminal) | archived→any | Service Orchestration and Lifecycle |
| Workspace | active | Created via management API | Archived | archived→active | Service Orchestration and Lifecycle |
| Workspace | archived | User requests archive | None (terminal) | archived→any | Service Orchestration and Lifecycle |
| Checkpoint (thread) | active | First agent invocation for a conversation | No checkpoint data remains (purge or cleanup) | N/A | Checkpoint and Memory Management |
| Checkpoint (thread) | saved | After each agent turn | Next turn overwrites | N/A | Checkpoint and Memory Management |
| Prompt Asset (planned) | draft | Created for new or variant prompt content | Submitted for review | N/A | Prompt Policy and Guardrail Enforcement |
| Prompt Asset | reviewed | Passed review gate | Promoted to approved lineage or returned to draft | N/A | Prompt Policy and Guardrail Enforcement |
| Prompt Asset | approved | Active in the prompt lineage for a role/route | Deprecated by newer version | N/A | Prompt Policy and Guardrail Enforcement |
| Prompt Asset | deprecated | Replaced by newer version | Removed from manifest | deprecated→approved | Prompt Policy and Guardrail Enforcement |
| Provider Client | cached | Created by ModelClientFactory on first use | Removed via cache invalidation or config change | N/A | Provider Selection and Model Invocation |
| Provider Client | available | Provider endpoint is reachable and returns valid results | Consecutive failures trigger fallback | N/A | Provider Selection and Model Invocation |
| Provider Client | degraded | Provider is reachable but has elevated latency or error rate | Recovery or fallback activation | N/A | Provider Selection and Model Invocation |

## Logical Decisions

| Decision | Scope | Owner / Boundary | Affected Objects or Flows | Consequence |
|----------|-------|------------------|---------------------------|-------------|
| conversation_id→thread_id as canonical STM binding | Memory and lifecycle | Service Orchestration, Checkpoint Management, Agent Runtime | Conversation, Session, Checkpoint | Creates a two-authority model where service layer owns lifecycle and checkpointer owns runtime state; requires correspondence management |
| Archive-over-delete for all lifecycle objects | Lifecycle governance | Service Orchestration | Conversation, Session, Workspace | Prevents permanent data loss; supports audit and recovery; complicates storage management over time |
| Route-aware skills pattern instead of multi-agent | Agent reasoning | Agent Runtime | Route Classification, Prompt Asset | Keeps reasoning in one agent with route-specific prompt context; defers orchestrator complexity; limits parallelism |
| Provider fallback at request granularity not mid-stream | Provider selection | Provider Selection | Provider Client, Conversation | Simplifies fallback logic but means mid-stream provider failures are not recoverable within a single request |
| Spec-kit governance for all non-trivial changes | Delivery governance | Spec-Kit Artifact Governance | Spec Feature Artifact, Long-Lived Doc | Ensures traceability but adds process overhead; requires synchronization discipline during step 17 |

## Logical Gaps

| Gap | Affected Capability / Object | Why It Matters |
|-----|------------------------------|----------------|
| Socket.IO lifecycle parity with REST | Service Orchestration, Transport | Socket.IO chat bypasses ChatService archive/ownership checks; the same logical capability has two different safety surfaces |
| Mid-stream provider fallback undefined | Provider Selection, Transport | If a provider fails during streaming, there is no defined handoff to a fallback provider mid-stream |
| Automated summarization trigger not wired | Service Orchestration, Memory | The summarized state exists in schema but is not automatically triggered; lifecycles have a gap between active and archived |
| Prompt compiler path not yet implemented | Prompt Policy | All prompt variant, experiment, and guardrail middleware scenarios are planned behavior; current architecture uses inline prompts only |
| LTM/RAG not implemented | Memory | Cross-conversation personalization and sourced-evidence retrieval are architecturally reserved but not available at runtime |

## Prohibited Content

Do not write classes, DTOs, database tables, fields, method names, endpoints, schemas, or implementation data structures here.
