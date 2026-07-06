# Scenario View - DP Stock Investment Assistant

**Purpose**: Produce the use-case semantics for the architecture workflow. This view is the source for the logical, process, development, and physical views.

## Architecture Intent

This view stabilizes the user, operator, and governance scenarios that the agent-domain architecture must support. The current architecture keeps one ReAct-style reasoning runtime, conversation-scoped short-term memory, service-owned lifecycle controls, and current prompt/tool baselines, while the target architecture makes route-aware prompt behavior, governed tool exposure, provider mediation, normalized tool context, source lineage, and degraded-state handling explicit.

## Core Tensions

| Tension | Current Tradeoff Direction | Scenario Consequence |
|---------|----------------------------|----------------------|
| Single runtime vs specialist expansion | Keep one ReAct-style agent runtime; specialize through route classification, prompt skills, route-filtered tools, and gateway admission | Scenarios assume one reasoning boundary; specialist agents require a future routing contract |
| Broad tool access vs governed tool exposure | Current registry-backed tools remain the inventory baseline; target exposure is route-filtered and policy-admitted | Users see tool-backed answers, but the model should only see capabilities admitted for the turn |
| Evidence authority vs provider convenience | Current Yahoo-backed data path remains a fact source; target provider posture is Vietnam-first, source-attributed, license-aware, and normalized | Market answers must identify source, freshness, warnings, and degraded states rather than silently substituting sources |
| Prompt agility vs prompt authority | Current baseline prompt is stable; M1 assets are implemented, M2 route skills are implemented but gated, and response guardrails remain planned | Prompt variants or route skills must never weaken shared policy or treat runtime evidence as instruction authority |
| Streaming responsiveness vs lifecycle and safety parity | REST/SSE path has stronger service-layer lifecycle control; Socket.IO parity remains a gap | Streaming scenarios must preserve safe terminal outcomes, and transport parity remains a review trigger |
| Delivery velocity vs traceable governance | Non-trivial changes use Spec Kit artifacts and sync after verification | Architecture updates must stay traceable to SRS, architecture, technical design, and verification evidence |

## Stable Boundaries

| Boundary | Must Remain Stable Because | Explicitly Does Not Cover |
|----------|----------------------------|---------------------------|
| Service-owned lifecycle and session context | Ownership, archive guards, reusable parent context, and conversation metadata must be enforced before agent work | Agent reasoning, checkpoint state, model-provider choice, tool execution |
| Conversation-scoped STM | The checkpointer owns recoverable runtime state for one conversation only | Session context, long-term personalization, market facts, lifecycle metadata |
| Agent reasoning runtime | One reasoning loop coordinates route classification, prompt context, model invocation, and tool selection | Business lifecycle authority, provider adapter internals, durable market truth |
| Tool surface and gateway boundary | Model-visible tool exposure and execution admission must be reviewable, traceable, and fail-closed | Provider parsing, prompt authoring, lifecycle management, second agent runtime |
| Provider adapter and normalization boundary | Source selection, licensing, freshness, fallback, and normalized outputs stay below model-visible tools | Flat provider lists exposed to the model, raw provider payloads in prompts |
| Prompt policy boundary | Shared policy, route skills, segment classes, locale posture, and future guardrails shape behavior | Financial facts, tool outputs as policy, lifecycle state, provider credentials |
| Spec Kit governance boundary | Delivery artifacts and long-lived docs stay synchronized after verification | Runtime behavior, application state, deployment operations |

## Change Axes

| Expected Change | Isolated By | Scenario Impact |
|-----------------|-------------|-----------------|
| Vietnam-market provider rollout | Provider policy and adapter boundary below tools | Market-evidence scenarios gain official, licensed, public-web, visualization, and fallback source classes without exposing providers as tools |
| Tool normalization and reporting | Tool gateway, output classification, and request-scoped context boundary | Reports and answers compose from normalized facts, snippets, provenance, artifacts, warnings, and degraded states |
| Prompt route-context rollout | Prompt asset and route-skill boundary with gating | Route-aware persona and instructions become available without replacing the baseline prompt path |
| Future LTM/RAG activation | Separate personalization and sourced-document boundaries | User preference and retrieval scenarios expand without changing conversation-scoped STM authority |
| Socket.IO lifecycle parity | Transport path adopts service-layer lifecycle receipt | Streaming scenarios become consistent across REST/SSE and Socket.IO |
| Production observability hardening | Trace, health, metrics, and alerting boundaries | Operators gain proactive drift/failure visibility without changing scenario semantics |

## Invariants

| Invariant | Scenario Evidence | Risk If Violated |
|-----------|-------------------|------------------|
| Financial facts come from tools, approved stores, or sourced documents | Stock inquiry, market evidence, report, and visualization scenarios | Model output invents prices, ratios, forecasts, or unsupported certainty |
| Provider adapters remain hidden below model-visible tools | Governed tool execution and market evidence scenarios | The model selects providers directly and bypasses license, freshness, and fallback policy |
| Tool outputs and retrieved content are data-only prompt inputs | Prompt-governed response and generic-web scenarios | Untrusted page or provider text changes policy, tool behavior, or refusal posture |
| `ToolContextPack` is request-scoped by default | Report, tool context, and memory continuity scenarios | Request evidence is persisted as memory or durable market truth |
| TradingView is visualization provenance by default | Visualization scenario | Chart or widget values are treated as canonical market evidence without approved policy |
| Lifecycle validation precedes agent work | Conversation management, resume, and streaming scenarios | Archived or unauthorized conversations accept new turns |
| Sync follows verification | Spec Kit delivery scenario | Long-lived docs and traceability report unverified behavior as current |

## Non-goals / Anti-patterns

| Non-goal / Anti-pattern | Why It Is Out of Scope or Harmful |
|-------------------------|-----------------------------------|
| Multi-agent orchestrator for the current target slice | Current scenarios are served by one reasoning runtime with route-aware specialization; a second runtime would add coordination risk without scenario authority |
| Provider-specific tools exposed directly to the model | Collapses provider policy into prompt/tool selection and weakens licensing, freshness, and source-authority controls |
| Generic web fetch as open browsing | Web evidence must be deny-by-default, allowlisted, parser-limited, normalized, and quarantined from prompt authority |
| Reporting tools scraping providers directly | Reports must compose from normalized context and retained artifact metadata, not bypass provider policy |
| Prompt assets as fact stores | Prompts shape behavior and output contracts; they do not own market facts or durable user truth |
| Checkpoint store as lifecycle or session authority | STM state is conversation-scoped runtime state, not business metadata or parent context |

## Actors and Participants

| Actor / Participant | Goal | Responsibility | Boundary |
|---------------------|------|----------------|----------|
| End User | Ask stock, market, chart, report, and portfolio questions | Submit requests and interpret safe, source-attributed answers | Client-side consumer of transport contracts |
| Agent Runtime | Produce responses using route-aware reasoning, prompt policy, tools, memory, and providers | Classify intent, select admitted tools, invoke providers, and save conversation-scoped state | Internal reasoning boundary |
| Service Layer | Govern lifecycle, ownership, session context, and per-turn metadata | Admit or reject work before agent invocation and record business metadata | Internal orchestration boundary |
| Tool Boundary | Expose and execute governed tool capabilities | Filter tool surface, admit selected calls, trace descriptor/admission/degraded outcomes | Internal tool-policy boundary |
| Provider and Evidence Boundary | Acquire market data or evidence through approved source classes | Apply provider policy, source attribution, freshness, license posture, and normalization | Internal source-authority boundary |
| Prompt Policy Boundary | Shape behavior, route instructions, segment authority, and future guardrails | Resolve prompt assets, compose route-aware policy, and evaluate response safety where active | Internal behavior-policy boundary |
| System Operator | Maintain health, traceability, delivery state, and drift visibility | Review sync reports, health status, degraded states, and architecture gaps | Operational boundary |
| External LLM Provider | Generate language from governed prompts and data-only context | Return model output, not market authority or lifecycle truth | External reasoning service |
| External Market/Evidence Provider | Supply source data, visualization, documents, or provider outputs | Return source material under provider-specific terms and reliability | External evidence source |

## Use Cases

| Use Case | Actor | Goal | Preconditions | Scope Boundary |
|----------|-------|------|---------------|----------------|
| UC-1: Ask governed stock inquiry | End User | Receive a safe, source-attributed answer to a stock question | Request is admitted; conversation is active; provider/tool boundaries are available | Service, agent, prompt, tool, provider, and response boundaries |
| UC-2: Stream analysis result | End User | Receive progressive output with safe terminal state | Streaming surface is active; lifecycle has been checked where parity exists | Transport and agent response boundary |
| UC-3: Resume conversation from STM | End User | Continue a prior conversation with conversation-local context | Conversation exists and is active; checkpoint may exist | Service lifecycle and checkpointer boundaries |
| UC-4: Manage workspace and conversation lifecycle | End User | Create, close, archive, and inspect hierarchy records | Ownership chain is valid | Service and persistence boundaries only |
| UC-5: Use governed tool execution | Agent Runtime | Invoke only admitted tools for the route and context | Query has route classification; descriptors and policies are available | Tool surface, gateway, registry, and trace boundaries |
| UC-6: Acquire provider-backed market evidence | Tool Boundary | Retrieve source-attributed facts, snippets, documents, or degraded states | Provider policy admits at least one source | Provider adapter and normalization boundary |
| UC-7: Produce visualization or report | End User | Get chart provenance or generated report output | Normalized context or visualization source is available | Visualization/reporting boundary; no direct provider scraping |
| UC-8: Apply prompt-governed behavior | Agent Runtime | Use baseline or gated route-specific prompt context without weakening shared policy | Prompt assets/configuration are valid for the route | Prompt policy boundary |
| UC-9: Handle provider, cache, or tool degradation | Agent Runtime | Return a machine-detectable limitation instead of silent substitution | Failure, stale data, blocked license, or invalid call is detected | Tool, provider, prompt, and response boundaries |
| UC-10: Sync governed delivery | System Operator | Keep architecture, requirements, specs, and traceability aligned after delivery | Feature evidence is verified or gap is recorded | Spec Kit governance boundary |

## Scenario Paths

| Scenario | Main Path | Successful Outcome | Alternative / Failure Branches |
|----------|-----------|--------------------|--------------------------------|
| S1: Source-attributed answer | User submits query -> service validates lifecycle -> agent classifies route -> prompt policy contributes active context -> tool surface exposes admitted capabilities -> gateway admits selected call -> provider boundary returns normalized context -> model responds -> response emits | User receives answer with source, freshness, and caveats where applicable | Ambiguous route narrows tools; no admitted tool yields no tool surface; degraded provider yields explicit limitation |
| S2: Streaming answer | User requests stream -> service validates lifecycle where parity exists -> agent produces response incrementally -> terminal state records completion, cancellation, block, or degradation | User receives progressive response with safe end state | Client cancels; mid-stream provider failure cannot switch seamlessly; transport parity gap remains |
| S3: Tool admission denial | Model selects unavailable, mismatched, invalid, or high-risk tool call -> gateway denies before execution -> degraded state is recorded | Underlying tool is not executed and user-facing output can disclose limitation safely | Descriptor drift, license uncertainty, stale provider, or blocked risk class all fail closed |
| S4: Visualization and report | User asks for chart or report -> tool boundary admits visualization/report capability -> output is classified as provenance or generated artifact -> report composes from normalized context and source lineage | User receives visualization provenance or report with warnings and source lineage | TradingView numeric values are not used as canonical evidence; insufficient normalized context yields degraded report |
| S5: Memory continuity | User resumes active conversation -> service validates lifecycle -> agent loads conversation-scoped checkpoint -> response uses prior conversation context only | Same conversation retains continuity | Missing checkpoint starts fresh; sibling conversations do not share thread state; session context is not checkpoint memory |
| S6: Provider fallback | Primary model or market provider is unavailable -> deterministic fallback policy chooses admitted substitute or returns degraded state | Response uses fallback with traceable limitation, or fails safely | Mid-stream model fallback is undefined; production provider licensing remains a gating concern |
| S7: Spec Kit delivery sync | Requirement change is traced -> feature artifacts are produced -> implementation is verified -> sync reports and long-lived docs are refreshed | Architecture memory and traceability reflect verified or target-labeled behavior | Sync gap or stale mapping blocks promotion until corrected |

## Acceptance Semantics

| Acceptance Scenario | Observable Result | Must Hold | Not Covered |
|---------------------|-------------------|-----------|-------------|
| User receives tool-backed financial answer | Response contains sourced facts or explicit degraded-state caveats | Tools/provider outputs are normalized and data-only; prompt policy remains authoritative | Guarantee of investment outcome |
| Model sees route-filtered tools | Only route-eligible, enabled, policy-admitted capabilities are visible | Provider adapters, credentials, license policy, and parser limits stay hidden | Future remote tool admission |
| Gateway blocks unsafe tool call | Blocked or degraded result appears without underlying execution | Descriptor integrity, route match, risk, license, freshness, and argument posture are checked | Full future mutation workflow |
| Visualization is emitted | Chart/widget/deep-link provenance is available | Visualization is not treated as canonical market fact by default | Approved future data-category exception |
| Report is generated | Report output carries source lineage, warnings, and retained artifact metadata where applicable | Report composes from normalized context and does not scrape providers directly | Full report persistence implementation details |
| Conversation resumes | Prior conversation context is available in same conversation | Checkpoint is scoped to conversation; service owns lifecycle | Cross-conversation personalization |
| Delivery sync completes | Architecture memory and traceability are current | Verification evidence or explicit gap exists before sync | Automatic drift repair |

## Scenario Gaps

| Gap | Affected Scenario | Why It Matters |
|-----|-------------------|----------------|
| Socket.IO lifecycle parity remains unresolved | S2, S5 | The WebSocket-style path does not yet provide the same lifecycle and metadata receipts as the REST/SSE service path |
| Mid-stream provider fallback is undefined | S2, S6 | A provider failure during streaming cannot be replaced without a restart or safe terminal state |
| Full provider licensing posture is unresolved | S1, S6 | Production provider enablement needs terms, credential scope, license posture, and source-attribution decisions |
| Executable IR-3 schema realization is unresolved | S3, S4 | Descriptor, envelope, normalized output, mutation, and artifact contracts require implementation-level specs before full enforcement |
| Prompt guardrail middleware remains planned | S1, S2, S8 | Route skills and prompt assets exist/gate behavior, but final response guardrail enforcement is not yet universal |
| Future LTM/RAG remains planned | S5 | Cross-conversation personalization and sourced retrieval are not current STM behavior |
| Production observability controls remain incomplete | S7, S9 | Operators need stronger metrics, alerting, and trace correlation before production-grade monitoring claims |

## Prohibited Content

Do not write architecture components as code-level designs, persistence structures, implementation tasks, verification plans, deployment mechanics, or framework-specific configuration here.
