# Development View - DP Stock Investment Assistant

**Input**: `.specify/memory/architecture-logical-view.md`, `.specify/memory/architecture-process-view.md`

**Purpose**: Derive architecture-level components, package boundary intent, contract/artifact semantics, and dependency rules from logical and process views.

## Architecture Intent

This view preserves development-time ownership boundaries so teams and agents extend the system through the correct package responsibilities: transport admits requests, services govern lifecycle, the agent reasons, prompt policy shapes behavior, tools expose capabilities, gateway/policy boundaries admit execution, provider adapters fetch source data, normalization creates request-scoped context, retention stores approved derivatives, and Spec Kit governs delivery evidence.

## Core Tensions

| Tension | Current Tradeoff Direction | Development Consequence |
|---------|----------------------------|-------------------------|
| Additive evolution vs rewrites | Keep the current agent/runtime structure and add route, prompt, tool, and provider boundaries around it | New capabilities extend owning packages instead of replacing the runtime |
| Tool expansion vs agent coupling | Tool inventory, tool surface, gateway admission, provider policy, and normalization are separate packages | Adding providers or output kinds should not require agent reasoning changes |
| Prompt assets vs runtime policy | Prompt asset resolution and route skills are separate from reasoning, tools, and memory | Prompt changes remain behavior-policy changes, not state or data-access changes |
| Service lifecycle vs checkpoint state | Service and checkpoint packages have different ownership even when sharing storage infrastructure | Development dependencies must not make checkpoint code responsible for lifecycle |
| Architecture memory vs implementation detail | 4+1 memory captures boundary intent, not source layout or task plans | Generated architecture artifacts must avoid code-level ownership claims |

## Stable Boundaries

| Boundary | Must Remain Stable Because | Explicitly Must Not Own |
|----------|----------------------------|-------------------------|
| Transport Package | It owns request/response framing and streaming surfaces | Business lifecycle, provider policy, tool admission, persistence internals |
| Service Orchestration Package | It owns ownership, lifecycle, archive guards, session context, and metadata receipts | Reasoning state, model provider selection, prompt assets, provider parsing |
| Agent Reasoning Package | It owns route classification, one reasoning runtime, model interaction, tool selection, and checkpoint participation | Lifecycle state, provider adapter details, durable market records |
| STM and Memory Package | It owns conversation-scoped checkpoint continuity and future memory boundary integration | Session context, LTM truth, market evidence retention, lifecycle metadata |
| Prompt Policy Package | It owns prompt lineage, route-skill policy, segment authority, locale posture, fallback metadata, and future guardrails | Tool execution, provider credentials, conversation lifecycle |
| Tool Inventory Package | It owns repo-owned tool capabilities and enablement | Route-specific exposure decisions, provider selection, prompt assembly |
| Tool Surface and Gateway Package | It owns model-visible filtering, descriptor integrity, execution admission, traces, and degraded outcomes | Provider parsing, lifecycle management, second agent runtime |
| Provider Policy and Adapter Package | It owns source classes, provider posture, fallback eligibility, licensing, freshness, and source attribution | Model-visible tool list, prompt policy, durable memory |
| Normalization and Context Package | It owns output classification and request-scoped context assembly | Raw provider retention, lifecycle metadata, prompt policy authority |
| Retention and Audit Package | It owns retained artifact metadata, mutation receipts, approved snapshots, and diagnostic traces | Full request context persistence or raw provider payload stores |
| Governance Package | It owns spec artifacts, architecture memory, traceability, and sync reports | Application runtime behavior, deployment state |

## Change Axes

| Expected Change | Isolated By | Development Impact |
|-----------------|-------------|--------------------|
| New prompt variant, route skill, or locale | Prompt Policy Package | Prompt package evolves; tools, providers, services, and memory remain stable |
| New tool capability | Tool Inventory plus Tool Surface/Gateway Package | Inventory gains capability; exposure/admission policies decide visibility and execution |
| New source provider | Provider Policy and Adapter Package | Provider set expands below tools; model-visible capabilities remain stable |
| New normalized output kind | Normalization and Context Package | Prompt/report consumers receive classified context without parsing providers |
| Report and artifact retention | Retention and Audit Package | Approved derivatives gain lineage without persisting full request context |
| Future mutation capability | Gateway, Approval, and Retention Packages | State-changing action requires admission, confirmation, and receipt before any durable effect |
| Transport parity improvement | Transport and Service Packages | WebSocket-style flow adopts lifecycle receipt without changing agent reasoning |
| Production observability | Retention/Trace and Operations Packages | Cross-boundary degraded modes become observable without changing business logic |

## Invariants

| Invariant | Source Boundary / Contract / Dependency Rule | Risk If Violated |
|-----------|----------------------------------------------|------------------|
| Transport depends on services, not directly on agent/tool/provider internals | Transport and service boundary | Lifecycle and metadata receipts are bypassed |
| Services own lifecycle and may not depend on checkpoint internals | Service lifecycle boundary | Checkpoint format becomes business metadata authority |
| Agent reasoning depends on prompt/tool/model abstractions, not provider adapters | Agent reasoning boundary | Provider details leak into reasoning and prompt selection |
| Tool surface depends on descriptors and policy, not prompt text | Tool surface boundary | Prompt assets can widen tool exposure beyond governance |
| Gateway depends on descriptors, route, and policy before execution | Tool gateway boundary | Disallowed calls execute or fail silently |
| Provider adapters are hidden below tools | Provider policy boundary | The model sees provider choices and bypasses source posture |
| Normalization precedes prompt/report consumption | Normalization boundary | Raw payloads or untrusted instructions enter prompt or report output |
| Governance artifacts are not runtime dependencies | Spec Kit governance boundary | Application behavior becomes coupled to delivery artifacts |

## Non-goals / Anti-patterns

| Non-goal / Anti-pattern | Why It Is Out of Scope or Harmful |
|-------------------------|-----------------------------------|
| Building a second agent runtime for tool gateway | Gateway is an admission boundary, not a reasoning or orchestration package |
| Placing provider fallback in prompt assets | Fallback is deterministic provider policy, not prompt instruction |
| Making reports a provider-integration package | Reports should consume normalized context and artifacts, not source providers directly |
| Storing raw provider payloads in retention packages by default | Retention packages store approved derivatives and lineage, not unbounded source payloads |
| Letting governance files drive runtime decisions | Governance guides delivery and traceability; runtime decisions belong in application packages |
| Documenting code paths in architecture memory | 4+1 artifacts describe boundary intent and tradeoffs, not implementation file layout |

## Architecture-Level Components

| Component / Capability Package | Responsibility | Input / Output Boundary | Collaborators | Explicitly Must Not Own | Source View Evidence |
|--------------------------------|----------------|-------------------------|---------------|--------------------------|----------------------|
| Transport Edge | Admit user and operator requests; expose complete, streaming, and realtime response surfaces | User request -> normalized work item; response outcome -> client | Service Orchestration | Lifecycle policy, reasoning, provider policy | UC-1, UC-2, RL-1 |
| Service Orchestration | Validate ownership/lifecycle, resolve session context, and record metadata receipts | Normalized work item -> admitted agent work item or safe rejection | Transport Edge, Agent Reasoning, Persistence | Checkpoint format, prompt lineage, tool admission | UC-3, UC-4, RL-2 |
| Agent Reasoning | Maintain one reasoning runtime, classify route, coordinate prompt context, model calls, and selected tool calls | Admitted work item -> draft/streamed response and tool-call requests | Prompt Policy, Tool Surface/Gateway, Model Provider Boundary, STM | Lifecycle status, provider parsing, durable market truth | UC-1, UC-5, RL-3 through RL-7 |
| STM and Memory | Provide conversation-local continuity and planned future memory integration boundaries | Conversation identity -> checkpoint state or fresh-state receipt | Agent Reasoning, Service Orchestration | Session context, market facts, full Tool Context Pack | UC-3, RL-3 |
| Prompt Policy | Manage baseline prompt, implemented/gated route skills, segment authority, locale posture, fallback metadata, and planned guardrails | Route/request context/model draft -> prompt contract or guardrail result | Agent Reasoning, Normalization and Context | Provider credentials, tool execution, lifecycle metadata | UC-8, RL-6, RL-12 |
| Tool Inventory | Own repo tool capabilities, enablement, and health semantics | Registered capability state -> inventory | Tool Surface/Gateway | Route admission, provider order, prompt policy | UC-5, RL-5 |
| Tool Surface and Gateway | Build model-visible surfaces, admit selected calls, record descriptor/admission traces, and return degraded states | Route/context/tool call -> exposed capability, allowed execution, or degraded result | Agent Reasoning, Tool Inventory, Provider Policy | Provider parsing, prompt authoring, lifecycle changes | UC-5, UC-9, RL-5 through RL-8 |
| Provider Policy and Adapters | Govern source classes, license posture, fallback eligibility, freshness, credentials, and source attribution | Admitted source request -> provider result or degraded state | Tool Surface/Gateway, Normalization and Context | Model-visible tool surface, prompt policy | UC-6, RL-9 |
| Normalization and Context | Convert tool/provider results into data-only normalized outputs and request-scoped context | Provider/tool result -> normalized output and context pack | Provider Policy, Prompt Policy, Reporting/Retention | Raw payload retention, policy authority, lifecycle state | UC-6, UC-7, RL-10 |
| Reporting and Artifact Retention | Compose reports from normalized context and retain approved artifacts, lineage, warnings, and receipts | Normalized context/retention trigger -> generated artifact metadata or receipt | Normalization and Context, Service Orchestration | Direct provider scraping, full context persistence | UC-7, RL-13 |
| Governance and Traceability | Preserve requirements, architecture, Spec Kit feature evidence, and sync reports | Authority documents and verified evidence -> updated architecture memory/traceability | All delivery participants | Runtime state, source providers, deployment execution | UC-10, RL-14 |

## Package Boundary Intent

| Package / Boundary | Abstraction Level | Owned Concepts | May Depend On | Must Not Depend On | Evolution Rule |
|--------------------|-------------------|----------------|---------------|--------------------|----------------|
| Transport | Entry and response framing | Request shape, response mode, streaming terminal state | Service Orchestration | Agent/tool/provider internals | Add response surfaces without bypassing service lifecycle |
| Service Orchestration | Business lifecycle | Ownership, archive state, session context, metadata receipt | Persistence, Agent abstraction | Checkpoint internals, provider adapters | Add lifecycle rules in service boundary only |
| Agent Reasoning | Reasoning orchestration | Route classification, one runtime loop, model interaction, selected tool calls | Prompt Policy, Tool Surface, Model Provider, STM | Service internals, provider adapters | Specialize through route/prompt/tool policy, not second runtime |
| Prompt Policy | Behavior governance | Shared policy, route skills, segment classes, locale, prompt identity, guardrail outcome | Agent Reasoning, Normalized Context | Provider credentials, lifecycle metadata | Promote assets only through governance gates |
| Tools | Capability inventory | Repo-owned tool capability and enablement | Cache/performance boundary, Gateway | Provider policy, prompt policy | Add tools as capabilities; provider choice stays lower |
| Tool Surface/Gateway | Exposure and admission policy | Capability descriptors, policy descriptors, admission decisions, degraded state, trace | Tool Inventory, Provider Policy | Prompt authoring, lifecycle authority | Add rules without replacing registry-backed execution |
| Provider Policy/Adapters | Source integration | Provider descriptor, provider order, license/freshness, source attribution | Tool Gateway, external source classes | Model-visible tool surface | Add providers behind policy and descriptor review |
| Normalization/Context | Evidence shaping | Normalized output, Tool Context Pack, warnings, degraded states | Provider Policy, Prompt Policy | Durable memory, raw source storage | Add output kinds before consumers depend on them |
| Retention/Audit | Approved durable derivatives | Artifact metadata, mutation receipt, retained snapshot, diagnostic trace | Normalized Context, Service Orchestration | Full request context, raw provider payloads by default | Retain only explicitly admitted derivatives |
| Governance | Delivery control | Architecture memory, specs, traceability, sync status | Authority documents and verified evidence | Runtime application packages | Update after verification or explicit target-design authority |

## Contracts and Artifacts

| Contract / Artifact | Semantics | Producer | Consumer | Lifecycle | Architecture Consequence |
|---------------------|-----------|----------|----------|-----------|--------------------------|
| Public Transport Contract | User-facing request, response, streaming, and realtime semantics | Transport Edge | Client and service boundary | Evolves through governed contract sync | Transport changes cannot bypass service lifecycle |
| Conversation Lifecycle Receipt | Proof that ownership/status/session context were resolved | Service Orchestration | Agent Reasoning and audit/metadata surfaces | Per request | Agent receives admitted work rather than raw user traffic |
| Prompt Lineage and Route Skill Artifact | Governed behavior policy and route-specific context | Prompt Policy | Agent Reasoning | Baseline/current/gated/planned states | Prompt evolution remains auditable and reversible |
| Tool Capability Descriptor | Model-safe capability declaration | Tool Surface/Gateway | Agent Reasoning and model-visible tool surface | Reviewed and versioned | Keeps model surface safe and compact |
| Tool Policy Descriptor | Internal admission and risk policy | Tool Surface/Gateway | Gateway Admission | Reviewed and traceable | Keeps risk/license/freshness policy out of prompt text |
| Provider Adapter Descriptor | Internal source connector posture | Provider Policy | Provider selection and adapter boundary | Reviewed before production enablement | Keeps provider classes hidden and auditable |
| Tool Execution Envelope | Runtime inspection wrapper for a governed tool call | Tool Gateway | Normalization, traces, safe metadata | Per call | Admission, freshness, warnings, and degraded states are inspectable |
| Normalized Output | Data-only classified tool/provider output | Normalization and Context | Prompt Policy, Reporting | Per request unless retained derivative exists | Prompt/report consumers do not parse raw providers |
| Tool Context Pack | Request-scoped normalized context bundle | Normalization and Context | Prompt Policy and response assembly | Per request | Prevents wholesale persistence of dynamic evidence |
| Artifact Metadata | Retained derivative lineage and reference | Retention/Audit | Users, operators, reports | Retained by policy | Reports and artifacts remain source-attributed |
| Mutation Receipt | Audit record for approved future state-changing tool action | Retention/Audit | User/operator/governance | Durable when mutation is admitted | Mutations cannot be silent or unaudited |
| Architecture Memory Artifact | 4+1 architecture reasoning and synthesis | Governance | Feature planning, review, and agents | Updated through architecture workflow | Architecture claims remain traceable and boundary-focused |

## Dependency Rules

| Rule | Allowed Direction | Forbidden Direction | Reason | Risk If Violated |
|------|-------------------|---------------------|--------|------------------|
| Transport -> Service -> Agent | Requests flow through service lifecycle before reasoning where parity exists | Transport directly owning lifecycle bypass or provider/tool execution | Keeps admission, ownership, and metadata centralized | Archived or unauthorized work reaches agent |
| Agent -> Prompt/Tool/Model abstractions | Reasoning consumes governed boundaries | Prompt/tools/providers depending on agent internals for policy | Keeps specialization additive | Tool or prompt changes require runtime rewrites |
| Tool Surface/Gateway -> Tool Inventory and Provider Policy | Exposure/admission reads descriptors and source posture | Tool inventory deciding route exposure alone | Separates inventory from model visibility and execution safety | Broad tool exposure or unsafe execution |
| Provider Policy -> External Source Classes | Provider boundary owns source access | External source classes exposed as model-visible capabilities | Keeps source authority and license posture internal | Model selects providers directly |
| Normalization -> Prompt/Reporting | Consumers receive data-only normalized context | Prompt/report consumers parsing raw provider payloads | Maintains instruction-authority separation | Prompt injection and source-lineage loss |
| Retention -> Normalized Derivatives Only | Durable stores hold approved artifacts, traces, receipts, snapshots | Retention storing full Tool Context Pack or raw payloads by default | Preserves memory and market-truth boundaries | Stale or unsafe evidence becomes durable truth |
| Governance -> Runtime by guidance only | Specs/docs guide implementation and sync | Runtime importing or executing governance artifacts | Keeps delivery workflow separate from application behavior | Runtime breaks when governance files change |

## Development View Gaps

| Gap | Affected Component / Boundary | Why It Matters |
|-----|-------------------------------|----------------|
| Socket.IO lifecycle parity | Transport Edge, Service Orchestration | Realtime transport must adopt the same lifecycle receipt before parity can be claimed |
| Mid-stream provider fallback contract | Agent Reasoning, Model Provider Boundary, Transport Edge | Streaming failure closure needs a defined handoff or terminal policy |
| Production provider admission contracts | Provider Policy and Adapters | Provider classes need licensing, credential scope, terms, and source-authority review |
| Executable IR-3 implementation contracts | Tool Surface/Gateway, Normalization, Retention | Architecture-level contracts need implementation specs before full validation |
| Prompt guardrail activation | Prompt Policy | Route-skill and prompt asset implementation does not equal universal response-guardrail enforcement |
| Observability package maturity | Tool Gateway, Provider Policy, Prompt Policy, Retention | Cross-boundary trace correlation and proactive alerts remain incomplete |

## Prohibited Content

Do not write source file paths, concrete package trees, classes, functions, implementation tasks, framework-specific wiring, code generation notes, or tests here.
