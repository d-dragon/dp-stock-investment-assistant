<!--
SYNC IMPACT REPORT
==================
Version Change: 2.5.0 -> 2.6.0 (MINOR)
Bump Rationale: Added explicit Structured Output Subsystem governance, Route-Adapted Custom Response
  Tool rules, Two-Stage Fallback Formatter constraints, checkpointer payload exclusion hygiene, and
  transport edge streaming suppression rules based on ADR-AGENT-005, ARCHITECTURE_DESIGN.md,
  TECHNICAL_DESIGN.md v1.2, and SRS v2.9 (FR-1.2.5–1.2.9, AC-10).

Modified Principles:
- Layered Boundaries and Explicit Ownership -> Layered Boundaries and Explicit Ownership
  (expanded with checkpointer payload exclusion hygiene rule excluding AgentStructuredOutput from STM)
- Prompts, Memory, and Fine-Tuning Control Behavior, Not Truth -> Prompts, Memory, and Fine-Tuning
  Control Behavior, Not Truth (expanded with explicit separation between Output Contract Schema
  Validation and ResponseGuardrailMiddleware behavioral enforcement)
- Deterministic Tools and Contracted Interfaces -> Deterministic Tools and Contracted Interfaces
  (expanded with control-plane response tool admission under RiskClass.BOUNDED_NON_MUTATING and
  return_direct=True)

Added Sections:
- Structured Output Subsystem and Response Tool Governance

Removed Sections:
- None

Template Consistency Check:
- .specify/templates/plan-template.md: checked; no structural change required
- .specify/templates/spec-template.md: checked; no structural change required
- .specify/templates/tasks-template.md: checked; no structural change required
- .specify/templates/checklist-template.md: checked; no structural change required
- .specify/templates/agent-file-template.md: checked; no structural change required
- .specify/templates/constitution-template.md: checked; no structural change required
- .specify/templates/commands/*.md: not present in this repository
- AGENTS.md and relevant .github/instructions/*.md: checked; no structural change required

Follow-up TODOs:
- None
-->


# DP Stock Investment Assistant Constitution

> **Purpose**: This constitution defines the governing principles for the DP Stock Investment
> Assistant project. It establishes hard rules for spec-driven delivery, architecture boundaries,
> financial-AI safety, contract synchronization, and quality gates that all contributors and AI
> agents MUST follow.

---

## Core Principles

These seven principles govern practical current development across backend, agent, frontend,
data, operations, documentation, and infrastructure. They are **non-negotiable**.

### I. Spec-Driven, Traceable Delivery
Every non-trivial change MUST start from governed artifacts and named authorities. `docs/` owns
long-lived requirements, architecture, technical design, contracts, policy, and runbooks;
`specs/` owns delivery-scoped feature artifacts and verification evidence; `.specify/` owns Spec
Kit runtime files, templates, extensions, and workflows. Delivered work MUST refresh affected
traceability and long-lived artifacts before it is considered complete. Rationale: this
repository uses Spec Kit as its delivery governance engine, so unsourced or unsynchronized work
creates drift across code, contracts, and docs.

### II. Layered Boundaries and Explicit Ownership
Implementation MUST respect ownership boundaries across frontend, backend, agent, data,
operations, and IaC surfaces. Backend request flow MUST remain `routes -> services ->
repositories -> database`; cross-cutting dependencies MUST be injected via factories,
protocols, or immutable context objects; cross-domain behavior MUST be implemented in the owning
surface rather than through ad-hoc reach-through. Service orchestration owns lifecycle,
ownership, archive guards, and reusable session context; the agent runtime consumes those
controls and MUST NOT absorb them. The checkpointer owns conversation-scoped STM only and MUST
NOT become authority for lifecycle metadata, ownership, session context, retained artifacts, or
market evidence. Typed JSON response payloads (`AgentStructuredOutput`) MUST be explicitly excluded
from conversation-scoped STM checkpointer serialization (`agent_checkpoints`) to prevent state
corruption, schema drift, and database bloat (`FR-1.2.8`). Rationale: the current codebase already
depends on blueprint, service, repository, factory, and checkpointer boundaries, and preserving
those seams keeps change reviewable and testable.

### III. Evidence-Grounded Financial Intelligence
Financial outputs MUST be grounded in approved external sources, governed internal data stores,
retrieved documents with provenance, or deterministic tool output. The assistant MUST NOT invent
prices, metrics, forecasts, or investment certainty, and all outputs MUST remain informational
rather than manipulative. Market facts in answers, report inputs, retained artifacts, snapshots,
traces, and cache-backed responses MUST preserve provider/source identity, source reference,
timestamps, exchange and currency where applicable, freshness, license posture, and warnings or
degraded-state reason. Visualization provenance, including TradingView output, MUST NOT be
treated as canonical market evidence by default. Rationale: in this finance domain, unsourced,
anonymous, stale, or visualization-derived facts are safety failures.

### IV. Prompts, Memory, and Fine-Tuning Control Behavior, Not Truth
Prompt assets, memory, and fine-tuning MAY shape behavior, structure, routing, and
personalization, but they MUST NOT become hidden fact stores. Memory retains preferences and
session context only; retrieval retains sourced documents; fine-tuning reinforces format or tone
rather than factual content. Prompt behavior MUST preserve explicit status labels: the current
baseline, implemented or gated M1/M2 prompt assets and route skills, planned guardrail
middleware, and future experiment controls are different authority states. Output contract schema
validation (parsing typed JSON into `AgentResponse.structured_content`) MUST remain strictly
separated from behavioral policy enforcement (`ResponseGuardrailMiddleware`), ensuring contract
parsing does not swallow or substitute behavioral guardrail failures. Rationale: the
repository's current prompt-system and memory work assumes this separation, and governance must
keep implemented, gated, planned, and future behavior explicit.

### V. Deterministic Tools and Contracted Interfaces
Deterministic tools MUST fetch or compute facts; the model interprets them. Current registry-
backed cache-aware tools MUST be labeled separately from target Phase 2B boundaries such as
route-filtered exposure, `ToolSurfaceBuilder`, `ToolGateway`, provider policy, normalized
outputs, and `ToolContextPack` until authority documents and implementation evidence promote
them. Agent tools MUST be exposed through route-filtered, policy-admitted surfaces rather than
broad provider lists when that target boundary is in scope. Control-plane custom response tools
(`submit_stock_analysis`, `submit_recommendation`, `submit_general_chat`) MUST be registered in
`ToolRegistry` under codebase enum `RiskClass.BOUNDED_NON_MUTATING` with `return_direct=True` (0%
extra token overhead) to act as direct output contract boundaries (`ADR-AGENT-005`). Provider-specific
fetching, parsing, licensing, freshness, fallback, and health behavior MUST stay behind
deterministic provider policies and adapters. Tool results MUST be normalized into typed,
source-attributed, freshness-aware, warning-aware context before entering prompt assembly. Public
interfaces such as REST endpoints, streaming responses, WebSocket events, and machine-readable
contracts MUST remain explicit, version-aware, and synchronized with implementation. Provider-backed
market-data tools MUST pass source-attribution, freshness, license-posture, cache, and
degraded-state gates before production use, and visualization-only tools MUST remain outside
canonical evidence paths unless governed policy explicitly admits them. Rationale: the project
relies on OpenAPI, route registration, streaming surfaces, auditable tool results, and
finance-domain source integrity; opaque interface, tool, or status drift is operational risk.

### VI. Testability and Observability Are First-Class
Every material behavior MUST be verifiable and diagnosable. Focused tests, health endpoints,
structured logging, prompt or request trace metadata, and explicit degraded-mode outcomes MUST
make failures explainable across API, agent, data, frontend, and deployment surfaces.
Rationale: hidden state and silent failure block safe delivery in a multi-surface system.

### VII. Secure, Simple, Reversible Change
Changes MUST default to least privilege, minimal scope, backward-compatible evolution, and clear
rollback or migration paths. Complexity MUST be justified against a simpler modular or additive
alternative. Rationale: the current project spans microservice-style deployment, persistent data,
and evolving AI behavior, so irreversible or over-broad changes multiply risk.

---

## Project Operating Standards

### Golden Development Rules

These nine rules govern all day-to-day project development. Violations MUST be corrected before
merge.

#### 1. Start From Governing Artifacts
For every non-trivial task, identify the controlling SRS, architecture or technical design, ADR,
contract, runbook, or feature spec before changing code, docs, or IaC.

#### 2. Respect Artifact Lifecycles and Locations
`docs/` is the long-lived baseline, `specs/` is the governed delivery evidence area, and
`.specify/` is runtime and tooling support. Stable knowledge is promoted from `specs/` to `docs/`
only after verification. Active feature specs remain living artifacts until closeout; verified
feature directories become delivery evidence and SHOULD flow forward into long-lived documents
rather than being repeatedly rewritten.

#### 3. Keep Contracts and Sync Artifacts Current
When stable behavior changes, update `docs/openapi.yaml`, `specs/spec-traceability.yaml`,
`specs/spec-sync-status.md`, affected reverse-trace documents, and impacted technical design or
runbook artifacts in the same delivery cycle when relevant. The sync report MUST be regenerated
with `python scripts/sync_spec_status.py --gate` when requirement coverage, feature lifecycle
status, or evidence paths change.

#### 4. Protect Secrets and Privileged Access
Secrets MUST NOT appear in source, logs, docs, or test fixtures. Use environment variables,
approved secret stores, and least-privilege credentials for local and production access.

#### 5. Validate With Executable Evidence First
Prefer focused tests, diagnostics, type or lint checks, schema validation, or health checks over
manual inspection. Docs-only work MUST at least pass the file diagnostics available in the
environment.

#### 6. Log and Expose Safe Operational State
Use structured logging, safe user-visible errors, health probes, and machine-detectable degraded
states. Silent failures and raw internal errors on public surfaces are prohibited.

#### 7. Preserve Architecture Seams
Routes handle transport concerns, services own business logic, repositories own persistence, and
factories or immutable context objects own dependency wiring. Do not bypass those seams with
ad-hoc shortcuts.

#### 8. Prefer Additive Migration and Backward-Compatible Rollout
Use aliases, migration scripts, versioning, fallback lineages, or staged rollout when public,
persisted, or prompt-governed behavior changes.

#### 9. Keep Changes Small, Focused, and Reviewable
Each change set MUST stay scoped to one logical outcome, include its required doc or contract or
test updates, and justify any unavoidable complexity against a simpler alternative.

### Artifact and Documentation Boundaries

- `docs/` is authoritative for long-lived requirements, architecture, technical design, ADRs,
  policy, runbooks, and executable contracts.
- `specs/` is authoritative for governed feature delivery artifacts, review evidence, and sync
  status.
- `.specify/` is the project-local Spec Kit runtime and configuration area and MUST NOT be used
  as the canonical store for governed feature delivery evidence.
- `docs/openapi.yaml` is the current canonical REST contract. A future move to
  `docs/domains/backend/api/openapi.yaml` MUST be handled as a governed migration that updates
  references, validation paths, CI or scripts, and contributor guidance in one change set.
- If code, specs, contracts, and long-lived docs disagree, fix the authoritative artifact first,
  then reconcile dependent references.

### Document Referencing in Spec-Kit Workflows

Cross-references between spec-kit artifacts (in `specs/`) and long-lived documents (in `docs/`)
MUST be precise and durable. Vague or unanchored references reduce traceability and break
agentic workflow context.

#### Cross-Reference Precision Rules

1. **Use section-level anchors, not document-level paths alone.** Every reference to a `docs/`
   document from a spec, plan, task, or review artifact MUST include an anchor pointing to the
   specific section, requirement ID, or heading that contains the governing content. For example,
   `docs/domains/agent/TECHNICAL_DESIGN.md#35-prompt-realization-and-guardrails` is valid;
   `docs/domains/agent/TECHNICAL_DESIGN.md` alone is not sufficient for non-trivial references.
2. **Anchor precision applies to all spec-kit phases.** `speckit.specify`, `speckit.plan`,
   `speckit.tasks`, implementation, verification, and sync artifacts MUST all use anchor-level
   references when linking to long-lived documents. Generic document-level references are
   permitted only when the entire document is the authority for the referenced concern.
3. **Repository-relative paths.** Use paths relative to the repository root (e.g.,
   `docs/domains/agent/TECHNICAL_DESIGN.md`) rather than absolute or ambiguous labels, so
   references remain valid across branches and agent sessions.
4. **Anchor validity is a sync responsibility.** When a section heading, requirement ID, or
   anchor label changes in a `docs/` document, every inbound cross-reference from `specs/`,
   other `docs/` files, and customization files MUST be updated in the same change set or in an
   immediately following maintenance change.

#### Lifecycle Obligations by Spec-Kit Phase

| Spec-Kit phase | Document-referencing obligation |
|----------------|--------------------------------|
| `speckit.specify` | The `## Governance Context` section MUST identify governing `docs/` documents with section-level anchors for every referenced authority. |
| `speckit.plan` | The Constitution Check MUST list which `docs/` documents are affected and whether their section anchors or requirement IDs will need updates. |
| `speckit.tasks` | Task descriptions MUST include explicit cross-reference validation or anchor-checking steps when feature work references or changes `docs/` documents. |
| `speckit.implement` | Code or documentation changes that modify section headings, requirement IDs, or anchor labels in `docs/` MUST be paired with updates to all inbound references. |
| `speckit.verify.run` | Verification MUST check that cross-references between `specs/` artifacts and `docs/` documents resolve to valid, non-broken anchors. |
| Steps 15-17 (sync) | The traceability-refresh and documentation-sync steps MUST validate all cross-references and flag any stale or broken anchors for correction. |

#### Agentic Workflow Guidance

- When contributing to a spec-kit artifact that references a `docs/` document, always read the
  target section first to confirm the reference is accurate and the anchor resolves to the
  intended content.
- When renaming a section heading in a `docs/` document, use grep or equivalent search to find
  all inbound references across `specs/`, other `docs/` files, and `.github/` customization
  files before committing the rename.
- Placeholder or template-style references such as `link to relevant design doc` MUST NOT
  survive into a published spec, plan, or task artifact. Every reference MUST be resolved to a
  concrete file path and section anchor before the artifact leaves draft status.

### Spec Persistence and Feature Status Semantics

Feature directories under `specs/` MUST use lifecycle status names consistently. `Draft`,
`Clarified`, `Planned`, `Implemented`, `Verified`, `Backfilled`, and `Superseded` are the
approved status vocabulary for feature `spec.md` headers, traceability notes, and sync
discussion.

- `Draft` applies before clarification and planning have completed.
- `Clarified` applies when ambiguity has been resolved and planning can proceed.
- `Planned` applies when `plan.md` exists and the design direction is accepted.
- `Implemented` applies when tasks are complete and implementation evidence exists, but the
  final verification marker is absent.
- `Verified` applies only when `review.md`, `.verify-done`, complete tasks, and the sync gate
  all support the verified state.
- `Backfilled` applies only to governance restoration for pre-existing behavior.
- `Superseded` applies when a feature directory is retained for history and points to its
  replacement authority.

Active feature work MAY flow backward from implementation findings into `spec.md`, `plan.md`, or
`tasks.md`, but that reconciliation MUST be followed by analysis or sync review. Verified feature
directories SHOULD flow forward into `docs/`, contracts, traceability, roadmap, or ADRs instead
of being mutated as active design documents. Material behavior changes after verification MUST
use a follow-up feature, governed doc update, or explicit supersession link.

### Architecture Current/Target Status Semantics

Long-lived architecture and technical design documents MUST preserve the status labels used by
their authority chain. A concept MAY be described as `Current`, `Implemented`, `Implemented /
gated`, `Target`, `Planned`, or `Gap`, but those labels are not interchangeable.

- `Current` applies only to baseline behavior the authority documents identify as active in the
  runtime, such as the single ReAct runtime, service-owned lifecycle/session/archive controls,
  conversation-scoped STM, current registry-backed cache-aware tools, and the current external
  market-data path.
- `Implemented` or `Implemented / gated` applies only when the authority documents identify
  delivery evidence and any activation gate. Gated behavior MUST name the gate or condition
  rather than being presented as unconditional baseline behavior.
- `Target` applies to approved architecture direction that constrains implementation but is not
  yet current by default. Target Phase 2B tool concepts include route-filtered tool exposure,
  thin in-process gateway admission, provider policy, provider adapters, normalized output,
  request-scoped `ToolContextPack`, and degraded-state handling unless the authority documents
  explicitly promote a subset.
- `Planned` applies to designed future behavior such as prompt guardrail middleware, future
  LTM/RAG, executable tool-contract schemas, broader prompt experiments, production
  observability controls, and provider licensing hardening.
- `Gap` applies to known missing or unresolved behavior such as Socket.IO lifecycle parity,
  mid-stream provider fallback, production provider licensing posture, and production-grade
  observability controls.

Feature verification, task completion, or a traceability status update MUST NOT by itself
promote a target architecture concept to current. Promotion requires consistent implementation
evidence, updated long-lived architecture or technical design, and synchronized traceability
where requirement mappings are affected.

### Memory and AI Runtime Boundaries

These boundaries govern prompt-system, memory, and agent-runtime work so personalization,
control-plane logic, and factual data remain separated.

#### Long-Term Memory (LTM) — Allowed
- User risk profile and investment preferences
- Investment goals, time horizon, and sector interests
- Output style, language, and verbosity preferences
- Stable workspace or personalization defaults

#### Short-Term Memory (STM) — Allowed
- Current conversation context and approved assumptions
- Active routing or tool-selection state
- In-progress analysis state that is bounded to the request or conversation
- Temporary session continuity metadata

#### Explicitly Prohibited in Memory
These items MUST stay in retrieval, tools, or governed data stores rather than LTM or STM:
- Real-time or historical prices
- Financial ratios, valuations, and calculated metrics
- Raw filings, news bodies, or sourced document text used as evidence
- Forecasts, price targets, or analytical conclusions
- Investment recommendations presented as durable stored truth

#### Retrieval, Prompts, and Fine-Tuning
- Retrieval stores sourced documents with provenance and reviewable origin.
- Prompt assets encode policy, role behavior, output contracts, and guardrails rather than facts.
- Fine-tuning or reusable prompt assets MAY reinforce structure and tone but MUST NOT become a
  hidden knowledge base.
- Deterministic tools fetch and compute facts; the model interprets, frames, and cites them.

### Agent Tool System and Architecture Governance

Agent tool-system work MUST preserve the target Phase 2B architecture unless an ADR explicitly
changes it. This section governs `ToolRegistry`, target `AgentTool`, `ToolSurfaceBuilder`,
`ToolGateway`, provider adapters, normalized outputs, reporting, TradingView, generic web
evidence, and future remote or MCP-style tool admission.

#### Tool Architecture Boundary Rules

1. **Route-filtered exposure before model invocation.** The model-visible tool surface MUST be
   derived from the classified route, locale, feature flags, session state where allowed, and
   reviewed capability descriptors. The model MUST NOT receive every tool, provider adapter, or
   utility by default.
2. **Gateway as thin in-process policy boundary.** `ToolGateway` MAY admit, reject, trace, and
   wrap tool execution, but it MUST NOT become a second agent runtime, a separate service by
   default, a provider parser, a prompt-policy author, or a business lifecycle owner.
3. **Registry remains inventory authority.** `ToolRegistry` remains the inventory and enablement
   boundary for repo-owned tools. New tools MUST register through the existing registry pattern
   or an approved successor, not through ad-hoc model prompts.
4. **Tools hide providers from the model.** Agent-facing tools MUST express stable capabilities
   such as symbol lookup, market data, visualization, reporting, or web evidence. Provider
   adapters such as official exchange sources, licensed providers, public-web sources, wrappers,
   TradingView, Yahoo, or future Vietnam-market connectors MUST remain below the tool layer.
5. **Provider policy is deterministic.** Provider ordering, fallback eligibility, market-session
   rules, license posture, freshness expectations, timeout/retry budget, and degraded-state
   mapping MUST be decided by application policy, not by LLM prompt text.
6. **Adapters own source-specific behavior.** Provider adapters own credentials, source fetch,
   parsing, health, source metadata, and field mapping. Gateway, reporting, and prompt assembly
   MUST NOT embed provider-specific parsing logic.

#### Tool Contracts and Data Integrity

1. Every admitted tool MUST have a reviewed capability descriptor and policy descriptor covering
   model-visible name, description, input schema, output kind, route coverage, descriptor
   version or integrity marker, risk class, license mode, freshness policy, cache policy,
   timeout budget, credential owner, mutation policy, and required metadata where applicable.
2. Every provider adapter used by a production path MUST declare supported markets, data
   categories, provider class, license posture, credential owner, parser limits,
   source-attribution requirements, production eligibility, and an integrity marker.
3. Tool execution MUST return an envelope that records selected route, selected tool, selected
   adapter where applicable, descriptor versions or hashes, admission outcome, normalized output
   reference, cache status, warnings, degraded-state reason, and trace metadata.
4. Raw provider payloads, raw HTML, raw PDFs, page scripts, hidden text, and untrusted page
   instructions MUST NOT enter prompt context. Prompt assembly may consume only normalized,
   data-only tool context.
5. `ToolContextPack` is request-scoped by default. It MUST NOT be persisted wholesale as
   conversation memory or durable market truth. Durable retention is allowed only for approved
   derivatives such as domain records, retained sourced artifacts, reports, mutation receipts,
   audit metadata, trace metadata, or approved market snapshots with source lineage.
6. Cache entries are performance artifacts, not authority. Market-data caches MUST preserve
   enough source timestamp, provider, exchange/currency where applicable, freshness, warnings,
   and degraded-state metadata to avoid stale or anonymous facts.

#### Source Authority and Provider Posture

1. Vietnam-market data work MUST prefer official exchange/depository sources and approved
   licensed providers for canonical records. Public web sources and wrappers MAY support
   research or evidence only after terms, licensing, parser, and source-attribution posture are
   reviewed.
2. International fallback providers such as Yahoo Finance or Alpha Vantage MAY be used only when
   the route, coverage, license posture, and user-facing caveats permit fallback. They MUST NOT
   silently replace a Vietnam-native provider when that would weaken source authority.
3. TradingView outputs MUST be classified as `VisualizationProvenance` unless a future approved
   policy explicitly admits a specific TradingView data path as canonical evidence.
4. Generic web fetch MUST be deny-by-default, domain-allowlisted, parser-limited,
   source-attributed, prompt-injection quarantined, and normalized into snippets, documents, or
   degraded states before use.
5. Reporting tools MUST compose from `ToolContextPack`, visualization provenance, generated
   artifacts, and retained source lineage. Reporting tools MUST NOT fetch or scrape provider
   data directly.

#### Vietnam Market Data and Visualization Evidence Gates

These gates apply whenever a feature adds or changes Vietnam-market tools, market-data answers,
TradingView visualization, provider-backed traces, or Vietnamese/mixed-language route coverage.

1. **Market-data tools are separate from symbol identity.** Vietnam quote, history,
   fundamentals, breadth, flow, disclosure, corporate-action, and indicator evidence MUST be
   owned by approved market-data tool families and provider policy, not by the internal symbol
   lookup boundary.
2. **Vietnam-first source posture is mandatory.** Official, depository, Vietnam-native, or
   approved licensed sources MUST be preferred where available. International providers such as
   Yahoo Finance or Alpha Vantage MAY be fallback or cross-market comparison sources only when
   provider policy, license posture, source attribution, freshness, and user-facing caveats
   allow that use.
3. **Production provider enablement is gated.** A Vietnam provider MUST NOT be promoted to a
   production evidence source until license or terms-of-use posture, credential scope,
   redistribution posture, freshness behavior, source-attribution fields, parser limits, and
   degraded-state behavior have been reviewed.
4. **Market facts require answer-level attribution.** Any market fact used in an answer, report
   input, artifact, snapshot, trace, cache hit, or retained derivative MUST carry provider/source,
   source URL or reference, retrieved timestamp, source/published/effective timestamp where
   available, exchange, currency, freshness category, license posture, and warnings or degraded
   reason where applicable. Missing mandatory attribution MUST fail closed to a degraded no-source
   outcome.
5. **Cache freshness is part of evidence authority.** Cached market-data entries MUST preserve
   provider/source, source timestamp where available, retrieved timestamp, freshness category,
   TTL or expiry, warnings, and degraded-state reason where applicable. Stale, expired,
   freshness-unknown, or anonymous cache hits MUST refresh through admitted policy or degrade.
6. **TradingView remains visualization provenance.** TradingView charts, widgets, deep links,
   ticker tape, heatmaps, screeners, symbol validation, and similar payloads MUST be classified as
   `VisualizationProvenance`. Numeric values from those payloads MUST NOT be used as canonical
   market evidence unless a future approved policy explicitly admits a specific data category.
7. **Vietnamese and mixed-language routing must be measured.** Features affecting Vietnam-market
   price, chart, fundamentals, disclosures, breadth, flow, or report-like routes MUST include
   Vietnamese and mixed-language route fixtures, expected tool-family mappings, ambiguity handling,
   and route-tool precision/recall or equivalent acceptance targets before verification.

#### Structured Output Subsystem and Response Tool Governance

These rules govern all machine-readable structured JSON output generation, route response tools,
fallback post-processing formatters, checkpointer state hygiene, and transport edge serialization.

1. **Route-Adapted Custom Response Tools as Primary Strategy.** Structured output generation MUST
   prefer route-adapted control-plane response tools (`submit_stock_analysis`, `submit_recommendation`,
   `submit_general_chat`) registered in `ToolRegistry` under codebase enum `RiskClass.BOUNDED_NON_MUTATING`
   with `return_direct=True`. Response tools MUST be injected dynamically per route by `ToolSurfaceBuilder`
   to achieve **0% extra prompt token overhead** during single-turn ReAct reasoning (`ADR-AGENT-005`).
2. **Two-Stage Service-Layer Fallback Formatter.** When LLM models omit response tool calls and output
   plain markdown text, `StockAssistantAgent.process_query_structured()` MUST transparently trigger an
   out-of-band post-processing fallback call (`model.with_structured_output()`) in `ChatService`.
3. **Graceful Degradation and PARTIAL Status.** Malformed or unparseable structured extractions MUST
   fail gracefully into `ResponseStatus.PARTIAL` with raw text preserved in `AgentResponse.content`,
   preventing active conversation thread crashes or unhandled exceptions (`ERR-1.4`).
4. **STM Checkpointer Payload Exclusion Hygiene.** LangGraph `MongoDBSaver` checkpointer state
   (`agent_checkpoints`) MUST NOT serialize heavy Pydantic `AgentStructuredOutput` JSON objects. Typed
   structured payloads MUST be attached to `AgentResponse` at the output contract boundary only,
   protecting checkpointer state from schema drift and MongoDB document bloat (`FR-1.2.8`).
5. **Phased Architecture Strategy.** All functional structured output requirements (`FR-1.2.5`–`FR-1.2.9`,
   `AC-10`) MUST be fulfilled on the factory-wrapped `create_agent` ReAct baseline (`SO.M1`) before custom
   compiled `StateGraph` nodes and in-graph self-repair loops (`SO.M2`) are promoted to current runtime
   behavior.
6. **Transport Edge Token Suppression and Discrete Frame Emission.** Streaming edges (REST SSE and
   WebSocket) MUST filter raw JSON tool argument streaming tokens out of natural language chat bubbles and
   emit a discrete `structured_completion` event frame upon turn completion (`IR-1.14`, `IR-3.11`).

#### Mutation, Remote Tools, and Security

1. State-changing tools, including future symbol-store upserts, coverage updates, alias merges,
   tag updates, or retirements, MUST require route admission, authorization, explicit mutation
   policy, audit metadata, and confirmation policy before enablement.
2. Remote or MCP-style tools are untrusted until locally admitted. They MUST use the same
   descriptor integrity, gateway admission, risk classification, normalized output, tracing, and
   degraded-state controls as local tools.
3. Tool descriptor drift, missing source lineage, unclear license posture, stale data beyond the
   policy threshold, blocked parser limits, or failed normalized-output validation MUST fail
   closed into a machine-detectable degraded state.

#### Tool Verification Gates

Agent tool-system plans and implementations MUST include focused evidence for:

- route-filtered tool exposure and static route preservation;
- gateway admission, rejection, and degraded-state behavior;
- descriptor integrity and descriptor drift handling;
- tool-versus-adapter separation and hidden provider fallback;
- source attribution, timestamp/freshness, cache metadata, and warning propagation;
- market-data answer attribution coverage, stale-cache behavior, provider fault handling, and
  degraded no-source outcomes;
- normalized output classification before prompt assembly;
- TradingView non-evidence classification;
- TradingView visualization provenance classification for every chart, widget, deep-link,
  ticker-tape, heatmap, screener, or symbol-validation payload;
- generic web prompt-injection resistance;
- reporting source discipline and degraded report behavior;
- request-scoped `ToolContextPack` retention boundaries;
- mutation receipt integrity for state-changing tools;
- Vietnamese and mixed-language route coverage where Vietnam-market tools are affected;
- finance-safety checks for unsourced recommendations, guaranteed-return language, and hype.

### Architecture and Design Constraints

- Use `ModelClientFactory`, `RepositoryFactory`, `ServiceFactory`, and immutable route or socket
  context objects for dependency wiring rather than manual global coupling.
- All database access MUST flow through `src/data/repositories/`; routes and presentation layers
  MUST NOT issue ad-hoc persistence queries.
- Cross-service dependencies MUST prefer protocols and composition over inheritance except for
  established base classes.
- Application code MUST use absolute imports and preserve tool-friendly import structure.
- Health endpoints, streaming surfaces, and deployment probes MUST stay aligned across code and
  IaC.

#### SOLID Constraints

- **Single Responsibility**: one concern per layer or module.
- **Open/Closed**: extend behavior with new modules or registrations instead of unrelated edits.
- **Liskov Substitution**: implementations MUST honor their published contracts.
- **Interface Segregation**: use lean interfaces and protocols instead of broad shared surfaces.
- **Dependency Inversion**: depend on abstractions and injected collaborators, not hard-coded
  concrete implementations.

---

## Workflow and Quality Gates

### Spec Kit Lifecycle Obligations

- Non-trivial work MUST follow the repository's Spec-Driven Development chain: governed
  requirements and design inputs, `speckit.constitution`, `speckit.specify`, clarification and
  checklist steps when needed, `speckit.plan`, `speckit.tasks`, implementation,
  `speckit.verify-tasks.run`, `speckit.verify.run`, and delivery synchronization.
- Plans MUST identify governing artifacts, affected domains, sync targets, validation strategy,
  architecture impact, and rollback or migration implications.
- Tasks MUST include tests, contract updates, traceability refresh, and long-lived doc sync work
  whenever those surfaces are affected.
- All references to `docs/` documents in spec-kit artifacts MUST use section-level anchors, not
  document-level paths alone. The lifecycle table under Document Referencing in Spec-Kit
  Workflows defines the responsibility per phase.
- Documentation-first work MAY start from documentation-focused agents or workflows, but it MUST
  obey the same artifact boundaries and sync duties.

### Current Spec Kit Command Surface

The constitution governs the current local command surface, not only upstream examples. As of the
current repository state, contributors MUST use these normalized surfaces unless a governed Spec
Kit upgrade changes installed commands and managed files:

- Pre-implementation review: `speckit.fleet.review`; historical `speckit.review` is shorthand
  only.
- Phantom completion detection: `speckit.verify-tasks.run`; historical `speckit.verify-tasks`
  is shorthand only.
- Post-implementation verification: `speckit.verify.run`; historical `speckit.verify` is
  shorthand only.
- Traceability and sync gate: `python scripts/sync_spec_status.py --gate`; `speckit.sync.*` is
  not an installed/enabled surface until `specify extension list` confirms adoption.
- Upstream convergence commands such as `speckit.converge` are upgrade-gated and MUST NOT be
  documented as locally available until the CLI, prompts, skills, and managed files expose them.

Copilot remains the default integration unless changed by a governed `specify integration use`
operation. Codex may remain installed as a secondary integration for portability, but mixed-agent
delivery MUST preserve one coherent feature workflow and one authoritative artifact set.

### Verification and Delivery Gates

- REST API changes MUST update `docs/openapi.yaml` and be checked against the actual registered
  public route surface.
- Prompt or agent behavior changes MUST preserve prompt identity, fallback or degradation
  metadata, and finance-safety guardrail expectations where those surfaces exist.
- Agent tool-system changes MUST validate route-filtered exposure, gateway admission,
  descriptor integrity, provider policy, normalized output classification, source lineage,
  degraded states, and request-scoped retention before production enablement.
- Data schema, migration, or cache behavior changes MUST include migration or initialization
  evidence and compatibility checks.
- Frontend, backend, agent, and IaC changes MUST validate the affected user or operator journey
  with the narrowest executable evidence available.
- Docs-only changes MUST pass diagnostics on the touched files and keep anchors or links current.
- Cross-references between `specs/` artifacts and `docs/` documents MUST be validated for anchor
  correctness during verification. Stale or broken section-level references are a verification
  failure, not optional cleanup.

### Pre-Merge Checklist

- [ ] Governing artifacts and affected domains are identified.
- [ ] Focused executable validation or diagnostics have been run.
- [ ] Required contracts, long-lived docs, and sync artifacts are updated.
- [ ] Agent tool-system changes include descriptor, route, provider, normalized-output, source
  lineage, and degraded-state evidence where applicable.
- [ ] Cross-references in spec-kit artifacts use section-level anchors and resolve to valid targets.
- [ ] No secrets or unsafe internal details are exposed.
- [ ] Any migration, fallback, rollout, or breaking-change path is documented.
- [ ] The change remains one logical slice or explicitly justifies broader scope.

### Delivery Sync Gates

- `docs/openapi.yaml` MUST be synchronized when REST API behavior changes.
- `specs/spec-traceability.yaml` and `specs/spec-sync-status.md` MUST be synchronized when
  requirement coverage or feature verification status changes.
- Domain reverse-trace documents, such as `docs/domains/agent/SRS_SPEC_TRACEABILITY.md`, MUST be
  updated when their requirement mappings change.
- `python scripts/sync_spec_status.py --gate` MUST pass before mapped requirement-linked feature
  work is considered synchronized.
- Affected technical design, architecture, or runbook documents MUST be synchronized when stable
  behavior becomes part of the long-lived baseline.

---

## Governance

### Supremacy
This constitution supersedes project-local defaults, templates, and prompt guidance. When
conflicts arise, constitutional principles take precedence, and the authoritative source for the
specific concern MUST then be reconciled across dependent artifacts.

### Amendment Process
1. Propose the amendment with rationale, affected principles, and semantic-version bump
  reasoning.
2. Validate the proposal against current repository context, templates, runtime guidance, and any
  affected long-lived docs or contracts.
3. Update the constitution, dependent templates, and any required sync references in the same
  change.
4. Record the amendment date and any deferred follow-up items in the Sync Impact Report.

### Compliance Verification
- `/speckit.plan` MUST pass the Constitution Check before research or design is treated as ready.
- `/speckit.tasks`, implementation, review, and post-implementation verification MUST confirm
  that required tests, contracts, traceability, and long-lived doc sync tasks are present when
  relevant.
- `speckit.verify-tasks.run`, `speckit.verify.run`, and
  `python scripts/sync_spec_status.py --gate` are the current closeout gates for implemented
  feature work when those surfaces apply.
- Any approved deviation MUST be written as an explicit justification in the affected plan,
  review, ADR, or equivalent governing artifact.

### Version Control
- **MAJOR**: Breaking changes to core principles or backward-incompatible governance changes
- **MINOR**: New articles, principles, or materially expanded guidance
- **PATCH**: Clarifications, typo fixes, non-semantic refinements

**Version**: 2.6.0 | **Ratified**: 2026-01-27 | **Last Amended**: 2026-07-22
