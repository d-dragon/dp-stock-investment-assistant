# Logical View - DP Stock Investment Assistant

**Input**: `.specify/memory/architecture-scenario-view.md`

**Purpose**: Derive capability boundaries, domain objects, states, relationships, and invariants from the scenario view.

## Architecture Intent

This view preserves the logical separation between transport admission, service-owned lifecycle, agent reasoning, prompt policy, conversation-scoped STM, governed tools, provider mediation, normalized evidence, metadata retention, and delivery governance. The target design must allow richer tools and providers without collapsing source authority, prompt policy, memory, and lifecycle into the reasoning runtime.

## Core Tensions

| Tension | Current Tradeoff Direction | Logical Consequence |
|---------|----------------------------|---------------------|
| One reasoning runtime vs route specialization | Keep one agent runtime and specialize through route, prompt, and tool policies | Route Classification becomes a shared logical input to prompt and tool boundaries, not a new orchestrator |
| Registry-backed tools vs gateway-governed tools | Preserve registry inventory while adding route surface, descriptors, and gateway admission | Tool Inventory, Tool Surface, and Tool Admission are distinct logical boundaries |
| Provider convenience vs source authority | Provider policy and adapters remain below model-visible tools | Provider Adapter Descriptor and Provider Selection Policy are internal policy objects, not model capabilities |
| Raw output vs normalized context | Tool results must be classified before prompt use | Normalized Output and Tool Context Pack become the logical bridge from tools to prompt assembly |
| Current prompt baseline vs governed prompt evolution | Current baseline remains stable; M1/M2 are implemented or gated; guardrails remain planned | Prompt Asset, Route Skill, and Guardrail Result carry different lifecycle states |
| STM continuity vs durable truth | Checkpoints persist conversation runtime state only | Conversation, Session Context, Checkpoint, Tool Context Pack, and retained artifacts are different logical objects |

## Stable Boundaries

| Boundary | Must Remain Stable Because | Explicitly Does Not Own |
|----------|----------------------------|-------------------------|
| Transport Admission | Normalizes inbound work and response modes before service orchestration | Business lifecycle, provider policy, tool admission, prompt policy |
| Service Lifecycle Authority | Owns ownership, active/archived status, parent context, and per-turn metadata | Checkpoint state, prompt asset lineage, provider adapter decisions |
| Agent Reasoning Boundary | Owns route classification, reasoning loop, tool selection, model interaction, and checkpoint participation | Lifecycle status, provider parsing, durable market records |
| STM Checkpoint Boundary | Owns recoverable state for one conversation thread | Session context, LTM personalization, raw tool outputs, Tool Context Pack persistence |
| Prompt Policy Boundary | Owns shared policy, route skills, segment authority, locale posture, prompt identity, and future guardrail outcomes | Financial facts, provider credentials, cache freshness, lifecycle metadata |
| Tool Surface Boundary | Owns model-visible capability selection for one turn | Provider order, parser limits, credentials, source scraping, prompt authoring |
| Tool Gateway Boundary | Owns execution admission, descriptor integrity, risk/license/freshness checks, degraded outcomes, and trace metadata | Provider parsing, lifecycle management, second agent runtime |
| Provider and Normalization Boundary | Owns source selection, provider class, license posture, freshness, source attribution, output classification | Model-visible tool names, prompt policy, conversation memory |
| Retention Boundary | Owns retained reports, artifacts, snapshots, mutation receipts, and diagnostic traces when admitted | Wholesale Tool Context Pack or raw provider payload persistence |

## Change Axes

| Expected Change | Isolated By | Logical Impact |
|-----------------|-------------|----------------|
| New market provider class | Provider Adapter Descriptor and Provider Selection Policy | Provider coverage expands without changing model-visible tools |
| Vietnam-market coverage | Market Provider Authority Class and Symbol Authority | More source classes and symbol normalization states appear below tools |
| Generic web evidence | Deny-by-default Web Evidence Policy | Web sources can produce normalized snippets/documents only when admitted |
| TradingView enablement | Visualization Provenance object | Visualization expands without becoming canonical evidence by default |
| Report generation | Generated Artifact and Artifact Metadata objects | Reports retain lineage and warnings without persisting raw request context |
| Prompt route contexts | Prompt Asset and Route Skill lifecycle | Gated route behavior expands while shared prompt policy remains authoritative |
| Future mutation tools | Mutation Policy and Mutation Receipt objects | State-changing actions require approval and audit semantics before enablement |

## Invariants

| Invariant | Source Scenario / Object / State | Risk If Violated |
|-----------|----------------------------------|------------------|
| Conversation lifecycle is service-owned | UC-3, UC-4, Conversation state | Agent or checkpointer could accept archived writes |
| Route Classification does not execute tools | UC-1, UC-5, Route Classification | Routing becomes a hidden execution path |
| Capability descriptors are model-safe only | UC-5, Tool Capability Descriptor | Credentials, provider fallback, license policy, or parser limits leak to the model |
| Policy descriptors are internal only | UC-5, Tool Policy Descriptor | Model-visible text exposes risk, credential, or provider-policy internals |
| Provider adapters are not model-visible tools | UC-6, Provider Adapter Descriptor | The model bypasses deterministic provider policy |
| Normalized Output is the prompt-facing evidence unit | UC-1, UC-6, Normalized Output | Raw provider payloads, pages, or parser artifacts enter prompt context |
| Tool Context Pack is request-scoped by default | UC-7, Tool Context Pack | Runtime evidence becomes durable memory or market truth |
| Degraded State is machine-detectable | UC-9, Tool Admission Decision | Failures silently fall back or appear as valid facts |

## Non-goals / Anti-patterns

| Non-goal / Anti-pattern | Why It Is Out of Scope or Harmful |
|-------------------------|-----------------------------------|
| Treating descriptor contracts as prompt text | Descriptors govern exposure and admission; they are not a policy layer for model behavior |
| Persisting full normalized context as memory | Request-scoped context can contain stale or route-specific evidence and must not become durable truth |
| Folding provider policy into tools or prompts | Provider order, fallback, licensing, freshness, and credentials belong below the tool capability boundary |
| Using visualization as canonical market evidence | Visualization provenance is useful context, but numeric facts require approved evidence or computation |
| Letting reports fetch market data directly | Reporting composes retained and normalized inputs; direct provider scraping bypasses policy and lineage |
| Treating future LTM as expanded STM | LTM is cross-conversation personalization; STM is conversation-local runtime continuity |

## Capability Boundaries

| Capability / Boundary | Responsibility | Input | Output | Explicitly Does Not Own | Scenario Source |
|-----------------------|----------------|-------|--------|--------------------------|-----------------|
| Transport Admission | Accept user requests and response-mode choices | User message, transport metadata | Normalized work item or safe rejection | Business lifecycle and agent reasoning | UC-1, UC-2 |
| Service Lifecycle Authority | Validate ownership, active/archive status, and session context | Normalized work item | Admitted agent work item and metadata receipt | Checkpoint state and provider policy | UC-1, UC-3, UC-4 |
| Agent Reasoning | Classify route, coordinate prompt context, model reasoning, and selected tool calls | Admitted work item and checkpoint context | Draft response, tool-call requests, checkpoint update | Lifecycle state and provider adapter internals | UC-1, UC-5 |
| Prompt Policy | Apply shared policy, route skills, segment authority, locale posture, and future guardrails | Route, request context, model draft | Prompt contract, guardrail outcome, prompt metadata | Market facts and tool execution | UC-8 |
| Tool Inventory | Maintain repo-owned tool capabilities and enablement | Tool registration and health state | Available tool inventory | Route admission and provider selection | UC-5 |
| Tool Surface | Build model-visible capability list for one turn | Route, locale, context, descriptors, feature posture | Filtered model-visible tool surface and hidden reasons | Provider order and execution | UC-5 |
| Tool Gateway | Admit or deny selected calls before execution | Tool call, route, descriptors, risk/license/freshness policy | Admission decision, trace, degraded state, or allowed execution | Provider parsing and prompt authoring | UC-5, UC-9 |
| Provider Policy and Adapters | Select and invoke admitted source classes below tools | Tool intent, market, provider posture | Provider result or provider degraded state | Model-visible capability selection | UC-6 |
| Normalization and Context | Classify tool/provider outputs and assemble request-scoped data-only context | Tool results, source metadata, warnings | Normalized outputs and Tool Context Pack | Durable memory and raw payload retention | UC-1, UC-6, UC-7 |
| Retained Artifact and Audit Metadata | Preserve explicitly retained report/artifact/mutation/trace lineage | Normalized context, approved retention trigger | Artifact metadata, mutation receipt, diagnostic trace | Full request context persistence | UC-7, UC-10 |
| Spec Kit Governance | Keep requirements, architecture, delivery evidence, and traceability synchronized | SRS/design inputs and verified delivery evidence | Governed artifacts and sync reports | Runtime execution | UC-10 |

## Domain Objects and Relationships

| Object | Meaning | Owning Capability | Key Relationships | Fact Source | Invariants |
|--------|---------|-------------------|-------------------|-------------|------------|
| Conversation | User-owned reasoning thread with lifecycle and checkpoint identity | Service Lifecycle Authority | Belongs to session/workspace; maps to one checkpoint identity | Service metadata and checkpointer | Active required for new turns; archive is terminal |
| Session Context | Reusable parent business context for related conversations | Service Lifecycle Authority | May inform a turn; does not merge conversation threads | Service metadata | Not persisted inside checkpoint state |
| Checkpoint | Recoverable conversation-local runtime state | STM Checkpoint Boundary | Bound to one conversation | Checkpointer | No lifecycle metadata, market facts, or Tool Context Pack wholesale |
| Route Classification | Semantic route assigned to a user query | Agent Reasoning | Drives prompt route skill and tool surface | Agent classification boundary | Does not execute tools |
| Prompt Asset | Governed behavior policy segment with lineage and status | Prompt Policy | Shared policy, route skills, locale and variant lineage | Prompt governance | Data-only inputs cannot override it |
| Tool Capability Descriptor | Model-safe declaration of a tool capability | Tool Surface | Paired with internal policy descriptor | Reviewed descriptor source | No internal provider, credential, license, or parser details |
| Tool Policy Descriptor | Internal admission policy for a tool | Tool Gateway | Paired with capability descriptor | Reviewed policy source | Hidden from model-visible surface |
| Provider Adapter Descriptor | Internal source connector posture | Provider Policy and Adapters | Supports provider selection policy | Provider governance | Not exposed as a model-visible tool |
| Tool Execution Envelope | Runtime wrapper for governed tool outcome | Tool Gateway | References route, selected tool, adapter where applicable, admission, cache/freshness, warnings | Tool gateway trace | Used for inspection, not as prompt policy |
| Normalized Output | Admitted data-only output kind from a tool/provider result | Normalization and Context | May become fact, snippet, document, system record, mutation receipt, visualization provenance, artifact, or degraded state | Normalizer | Raw payloads and page instructions excluded |
| Tool Context Pack | Request-scoped bundle of normalized outputs and warnings | Normalization and Context | Consumed by prompt assembly for the current request | Tool boundary | Not persisted wholesale |
| Degraded State | Machine-detectable limitation or denied outcome | Tool Gateway or Provider Policy | Appears in envelope, context, traces, and safe response metadata | Detection boundary | Cannot be silently treated as successful evidence |
| Visualization Provenance | Chart/widget/deep-link provenance output | Provider Policy and Adapters | May be used by reports and responses as visualization context | Visualization provider boundary | Not canonical evidence by default |
| Generated Artifact | Retained or emitted user-facing generated output | Retained Artifact and Audit Metadata | Carries source lineage and warnings | Reporting boundary | Cannot hide degraded-state or source-lineage gaps |
| Mutation Receipt | Audit object for future approved state-changing tool actions | Retained Artifact and Audit Metadata | Linked to approval, route, actor, and target record | Mutation policy boundary | Required before durable mutation is accepted |
| Market Provider Authority Class | Logical class of external source authority | Provider Policy and Adapters | Official, licensed, public-web, wrapper/prototype, visualization, fallback | SRS/provider posture | Determines licensing, freshness, fallback, and attribution |

## State and Lifecycle

| Object / Flow | State | Entered When | Exited When | Forbidden Transition | Responsible Boundary |
|---------------|-------|--------------|-------------|----------------------|----------------------|
| Conversation | Active | Created or reopened under allowed lifecycle rules | Closed or archived | Archived to active | Service Lifecycle Authority |
| Conversation | Archived | User or parent lifecycle archives it | None | Archived to any writable state | Service Lifecycle Authority |
| Checkpoint | Available | A conversation turn has persisted runtime state | State is unavailable or intentionally cleared | Checkpoint becomes lifecycle authority | STM Checkpoint Boundary |
| Prompt Asset | Baseline | Approved stable behavior path is available | Replaced by newer approved baseline | Data-only evidence promotes to baseline | Prompt Policy |
| Prompt Route Skill | Gated | Asset exists but activation depends on configuration and route | Promoted or disabled | Lower-authority route skill weakens shared policy | Prompt Policy |
| Guardrail Result | Planned/Active By Slice | Response-policy boundary is enabled for a slice | Response is committed or blocked | Blocked output committed as normal response | Prompt Policy |
| Tool Capability | Exposed | Surface admits capability for route/context | Turn ends or condition blocks it | Disabled/internal capability exposed | Tool Surface |
| Tool Call | Admitted | Gateway approves route, descriptor, risk, license, freshness, and arguments | Execution completes | Denied call executes | Tool Gateway |
| Provider Result | Normalized | Provider output passes policy and normalization | Tool context consumed for the request | Raw provider payload enters prompt | Provider and Normalization Boundary |
| Tool Context Pack | Request-scoped | Normalized outputs are assembled for one request | Request completes | Persisted wholesale as memory or market truth | Normalization and Context |
| Artifact or Receipt | Retained | Explicit retention, report, or mutation policy admits it | Retention policy expires or supersedes it | Retained without lineage | Retained Artifact and Audit Metadata |

## Logical Decisions

| Decision | Scope | Owner / Boundary | Affected Objects or Flows | Consequence |
|----------|-------|------------------|---------------------------|-------------|
| Keep one agent runtime and specialize by route/prompt/tool policy | Agent topology | Agent Reasoning | Route Classification, Prompt Asset, Tool Surface | Avoids multi-agent complexity while requiring strong admission boundaries |
| Preserve registry inventory while adding surface and gateway controls | Tool architecture | Tool Inventory, Tool Surface, Tool Gateway | Capability Descriptor, Policy Descriptor, Tool Call | Separates inventory from exposure and execution admission |
| Keep provider policy below tool capabilities | Source authority | Provider Policy and Adapters | Provider Descriptor, Market Provider Authority Class | Prevents provider lists and credentials from becoming model-visible choices |
| Normalize before prompt assembly | Evidence boundary | Normalization and Context | Normalized Output, Tool Context Pack, Degraded State | Preserves data-only context and source-lineage discipline |
| Treat Tool Context Pack as request-scoped | Memory and retention | Normalization and Retention Boundaries | Tool Context Pack, Artifact Metadata, Checkpoint | Avoids storing transient evidence as memory or market truth |
| Represent unresolved capabilities as gaps, not current behavior | Architecture governance | Spec Kit Governance | Prompt guardrails, LTM/RAG, provider licensing, IR-3 schemas | Keeps target design accurate without overclaiming implementation state |

## Logical Gaps

| Gap | Affected Capability / Object | Why It Matters |
|-----|------------------------------|----------------|
| Socket.IO lifecycle parity | Transport Admission, Service Lifecycle Authority | Same user scenario can bypass lifecycle receipts depending on transport path |
| Mid-stream provider fallback | Provider Policy, Transport Admission | Streaming failure cannot safely hand off to fallback without explicit protocol |
| Production provider licensing posture | Provider Descriptor, Market Provider Authority Class | Provider enablement cannot be production-safe without terms, credential scope, and redistribution posture |
| Executable IR-3 realization | Descriptors, Envelope, Normalized Output, Context Pack, Receipts, Artifacts | Architecture names contracts, but implementation specs must define enforceable shape and validation |
| Prompt guardrail middleware | Prompt Policy, Guardrail Result | Final response safety is not universal until the boundary is active across target paths |
| Future LTM/RAG | Memory and Retrieval Boundaries | Personalization and sourced retrieval remain planned and must not be confused with STM |
| Production observability controls | Tool Trace, Provider Trace, Request Trace | Operators lack full metrics/alerting/correlation for architecture-level degraded modes |

## Prohibited Content

Do not write code constructs, transport routes, persistence fields, method names, source locations, or implementation data structures here.
