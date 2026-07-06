# Physical View - DP Stock Investment Assistant

**Input**: `.specify/memory/architecture-process-view.md`, `.specify/memory/architecture-development-view.md`

**Purpose**: Derive deployment, hosting, external system, fact-source, observability, and operational boundaries from process and development views.

## Architecture Intent

This view preserves the physical separation between client-facing runtimes, agent/application runtimes, persistence stores, cache layers, external model providers, external market/evidence providers, retained artifact content, and governance artifacts. It records where facts and operational signals live without prescribing deployment manifests, service sizes, scripts, or vendor-specific runbooks.

## Core Tensions

| Tension | Current Tradeoff Direction | Physical Consequence |
|---------|----------------------------|----------------------|
| Shared infrastructure vs distinct authority | Business metadata, checkpoint state, cache data, prompt assets, and artifacts may share platforms but remain separate authority classes | Physical co-location does not imply logical ownership equivalence |
| Current Yahoo path vs target provider ecosystem | Yahoo-backed market data remains current; target posture adds Vietnam-first official/licensed/public-web/wrapper/visualization/fallback classes | External source boundaries must preserve authority, licensing, freshness, and attribution |
| Cache acceleration vs source authority | Redis/in-memory cache accelerates tools and providers but is not market truth | Cached facts need freshness/source metadata and degraded-state behavior |
| Artifact content vs artifact metadata | Filesystem may carry artifact content; metadata and lineage are durable records | Reports and retained derivatives need source lineage without retaining full request context |
| Optional observability vs production confidence | Logs, health, and optional traces exist; stronger metrics/alerts/correlation remain gaps | Production readiness cannot be claimed from health signals alone |
| Environment portability vs secret governance | Configuration can vary by environment; secrets must not be embedded in code, docs, logs, or architecture artifacts | Physical deployment must preserve least-privilege and rotation boundaries |

## Stable Boundaries

| Boundary | Must Remain Stable Because | Explicitly Does Not Carry |
|----------|----------------------------|---------------------------|
| Client Runtime Boundary | Users interact through client surfaces, not internal stores or providers | Provider credentials, lifecycle metadata authority, tool policy |
| API and Service Runtime Boundary | Request admission, lifecycle, session context, and metadata receipts run before agent work | Checkpoint authority, raw provider payload storage, market provider ownership |
| Agent Runtime Boundary | Reasoning, route classification, prompt/tool/model orchestration, and checkpoint participation run inside controlled runtime | Public transport ownership, source authority, durable artifact storage |
| Persistent Metadata Store | Conversation lifecycle, business metadata, checkpoints, artifact metadata, snapshots, receipts, and traces may be stored as separate logical authorities | Cache state, prompt-policy source of truth, raw Tool Context Pack by default |
| Cache Boundary | Tool and provider acceleration can store TTL-governed entries | Authoritative market facts, lifecycle state, durable memory |
| Prompt Asset Storage Boundary | Prompt policy assets and route skills are versioned behavior inputs | Market facts, provider payloads, user lifecycle metadata |
| External LLM Provider Boundary | Model inference happens outside the system and returns generated language | Market fact authority, lifecycle governance, source attribution |
| Market and Evidence Provider Boundary | External source classes supply market data, documents, visualization, or fallback evidence | Prompt policy, model reasoning, conversation lifecycle |
| Artifact Content Boundary | Retained report or evidence content can live outside metadata records | Source authority by itself, full request context, raw unsafe provider payloads |
| Governance Artifact Boundary | Architecture memory, specs, traceability, and long-lived docs live in repository-managed files | Runtime state, provider credentials, deployment secrets |

## Change Axes

| Expected Change | Isolated By | Physical Impact |
|-----------------|-------------|-----------------|
| New LLM provider | External LLM Provider Boundary and model-provider configuration | Adds external inference dependency without changing source authority or lifecycle stores |
| Vietnam-first market sources | Market and Evidence Provider Boundary | Adds official, licensed, public-web, wrapper/prototype, visualization, and fallback source classes |
| TradingView enablement | Visualization provider class | Adds visualization provenance output without canonical market-fact authority |
| Generic web evidence | Allowlisted web evidence boundary | Adds parser-limited external source access with quarantine and normalization |
| Artifact/report retention | Artifact Content and Metadata Boundaries | Adds retained derivative content and lineage without storing full Tool Context Pack |
| Diagnostic tool traces | Persistent metadata store with retention limits | Adds TTL-scoped operational evidence while excluding raw payloads and secrets |
| Observability hardening | Health, metrics, trace, and alerting boundaries | Adds proactive operations signal without changing request semantics |
| Secret-management hardening | Secret boundary and environment-specific configuration | Improves rotation and least privilege without changing architecture flows |

## Invariants

| Invariant | Source Deployment / External / Fact Boundary | Risk If Violated |
|-----------|----------------------------------------------|------------------|
| External LLM providers are not market-fact authorities | External LLM Provider Boundary | Model output becomes unsupported financial truth |
| Market facts require source, timestamp/freshness, license posture, and warnings where applicable | Market and Evidence Provider Boundary | User receives stale or unattributed facts |
| Cache entries are performance artifacts | Cache Boundary | Cached stale data becomes durable truth |
| Tool Context Pack is not persisted wholesale by default | Persistent Metadata Store and Retention Boundary | Request-scoped evidence becomes memory or market record |
| TradingView is visualization provenance unless policy admits otherwise | Visualization provider class | Chart output is treated as canonical evidence |
| Raw web/provider content must be quarantined before prompt use | Web evidence and normalization boundary | Prompt injection or untrusted instructions enter model context |
| Secrets remain outside code, docs, logs, and artifacts | Secret Boundary | Credential exposure and compliance failure |
| Governance artifacts stay outside runtime state | Governance Artifact Boundary | Delivery files become operational dependencies |

## Non-goals / Anti-patterns

| Non-goal / Anti-pattern | Why It Is Out of Scope or Harmful |
|-------------------------|-----------------------------------|
| Local model-serving as current architecture | Current authority docs treat LLM providers as external inference services |
| Raw provider data lake by default | Raw payload retention weakens privacy, prompt safety, and source-lineage rules |
| Cache as authoritative financial store | Cache TTL and fallback behavior make it unsuitable for durable market truth |
| Provider credentials in prompt/tool descriptors | Credentials and provider policy must remain internal to source and secret boundaries |
| Artifact content without metadata lineage | Retained reports or files without source lineage cannot be audited |
| Deployment manifest detail in architecture memory | Physical view records boundaries and constraints, not infrastructure configuration |

## Deployment and Hosting Boundaries

| Runtime / Hosting Unit | Carries | Boundary | Depends On | Release / Migration Impact |
|------------------------|---------|----------|------------|----------------------------|
| Client Application Runtime | User interface, request initiation, streaming display, terminal-state handling | Client Runtime Boundary | API/service runtime | Client changes should not alter lifecycle, tool, or provider authority |
| API and Service Runtime | Transport admission, lifecycle, session context, metadata receipts, service orchestration | API and Service Runtime Boundary | Persistent metadata store, cache, agent/model/tool boundaries | Contract or lifecycle changes require governed sync |
| Agent Application Runtime | Reasoning, route classification, prompt/tool/model orchestration, checkpoint participation | Agent Runtime Boundary | Persistent metadata store, cache, prompt assets, external providers | Tool/prompt/provider boundary changes require architecture and traceability review |
| Persistent Metadata Store | Business metadata, checkpoints, approved artifact metadata, snapshots, receipts, diagnostic traces | Metadata Store Boundary | Storage platform and retention policies | New retained metadata requires governed schema/retention design |
| Cache Layer | TTL-governed tool/provider acceleration and freshness-aware cache records | Cache Boundary | Cache platform or in-memory fallback | Cache loss degrades performance/freshness but must not corrupt authority |
| Prompt Asset Store | Baseline prompt assets, implemented/gated route skills, future variants and locale assets | Prompt Asset Storage Boundary | Repository or controlled asset storage | Prompt promotion follows prompt-governance gates |
| Artifact Content Store | Retained report files, generated artifacts, extracted evidence content when admitted | Artifact Content Boundary | Metadata and retention policies | Artifact content requires lineage, checksum/identity posture, and retention class |
| Governance Repository | Architecture memory, specs, long-lived docs, traceability, workflow templates | Governance Artifact Boundary | Version control and Spec Kit tooling | Architecture/doc updates do not alter runtime until implemented separately |

## External System Collaboration

| External System | Purpose | Exchanged Content | Authoritative Fact | Failure Impact | Isolation / Substitute Boundary |
|-----------------|---------|-------------------|--------------------|----------------|---------------------------------|
| External LLM Providers | Generate language from governed prompts and request-scoped context | Prompt/context -> generated draft or stream | Not authoritative for market facts or lifecycle state | Fallback or safe provider failure response | Model-provider selection boundary |
| Current Market Data Provider Path | Provide current baseline market data where admitted | Symbol/data request -> market fields and metadata | Source facts only when attributed and fresh enough | Cache use, fallback, or degraded state | Tool/provider boundary and cache boundary |
| Official Vietnam-Market Sources | Target canonical provider class for exchange/depository records | Market request -> official records and timestamps | High-authority market and corporate records | Degraded state if unavailable and no admitted fallback | Provider policy boundary |
| Licensed Commercial Providers | Target provider class for licensed data coverage | Market request -> licensed market/fundamental data | Authoritative within license and coverage posture | Degraded state or fallback depending on policy | License and provider policy boundary |
| Vietnam-Native Public-Web or Wrapper Sources | Target research/evidence provider class after review | Allowlisted request -> normalized snippets/documents or records | Supportive evidence only when terms and parser posture allow | Blocked, parser-limited, or degraded state | Web evidence policy and normalizer |
| TradingView Visualization Provider | Provide charts, widgets, screeners, links, and visualization context | Visualization request -> Visualization Provenance | Visualization provenance, not canonical numeric evidence by default | Visualization degraded state | Visualization provider boundary |
| International Fallback Providers | Provide cross-market or fallback coverage when admitted | Market request -> fallback evidence with caveats | Lower-priority evidence with explicit caveats | Degraded state if unsupported | Provider selection policy |
| Observability Provider or Trace Sink | Capture runtime diagnostics when configured | Trace/latency/event metadata -> diagnostics | Operational signal, not user truth | Trace loss should not block user response unless policy requires | Observability boundary |

## Fact Sources and Observability

| Fact / Event | Authoritative Source | Observable Location | Consumers | Traceability Requirement |
|--------------|----------------------|---------------------|-----------|--------------------------|
| Conversation lifecycle status | Service lifecycle authority | Persistent metadata and service responses | Service, operators, client | Lifecycle changes must be attributable and archive terminality preserved |
| Conversation runtime state | STM checkpoint boundary | Checkpoint storage | Agent runtime | Bound to one conversation; no lifecycle or market truth |
| Prompt identity and route behavior | Prompt policy boundary | Response metadata, trace metadata, governance evidence | Agent, operator, verification | Baseline/gated/planned state must be explicit |
| Tool exposure and admission | Tool surface/gateway boundary | Internal trace and safe warning metadata | Agent, operator, verification | Descriptor identity, route, selected tool, admission, and degraded reason are traceable |
| Market data fact | Provider and normalization boundary | Normalized output and optionally cache/metadata | Prompt/report consumers | Source, timestamp/freshness, license posture, warnings, and provider class required |
| Visualization output | Visualization provider boundary | Visualization provenance and artifact metadata when retained | User/report consumers | Must not masquerade as canonical evidence |
| Report or generated artifact | Reporting/retention boundary | Artifact metadata and content store | User/operator | Source lineage, warnings, retention posture, and generated-by context required |
| Mutation outcome | Future mutation/receipt boundary | Mutation receipt metadata | User/operator/governance | Approval, actor/route, target, before/after summary, and result required |
| Sync status | Spec Kit governance boundary | Sync reports and architecture memory | Operators and future feature work | Derived status and evidence paths must stay current |
| Degraded operation | Tool, provider, prompt, transport, or cache boundary | Safe response metadata, traces, health/ops signals | User/operator | Machine-detectable reason and responsible boundary required |

## Operations and Release Boundaries

| Operational Concern | Responsible Boundary | Trigger | Affected Views | Architecture Consequence |
|---------------------|----------------------|---------|----------------|--------------------------|
| Feature delivery and architecture sync | Governance Artifact Boundary | Verified delivery or explicit target-design refresh | Scenario, Logical, Development | Architecture memory and traceability stay aligned with authority documents |
| Provider onboarding | Provider Policy and External Source Boundaries | New provider class or production enablement | Logical, Process, Physical | Requires source authority, terms, licensing, freshness, and fallback posture |
| Prompt rollout | Prompt Asset Store and Prompt Policy Boundary | New baseline, route skill, locale, or experiment | Scenario, Process, Development | Behavior changes are gated and traceable without becoming fact stores |
| Tool-system rollout | Tool Surface/Gateway and Normalization Boundaries | New descriptor, tool, output kind, or gateway policy | Logical, Process, Development, Physical | Model-visible exposure and execution admission remain governed |
| Report/artifact retention | Retention and Artifact Content Boundaries | Generated report, retained evidence, or audit receipt | Logical, Development, Physical | Durable derivatives require lineage and retention posture |
| Cache degradation | Cache Boundary | Cache unavailable or stale | Process, Physical | System can continue with fresh source, degraded state, or explicit caveat |
| Observability improvement | Trace/Health/Metrics Boundaries | Need for production-grade operations | Process, Physical | Adds proactive signal while preserving user-flow semantics |
| Secret rotation | Secret Boundary | Credential rotation or provider onboarding | Physical | No architecture artifact or runtime log may expose secrets |

## Physical View Gaps

| Gap | Affected Deployment / External Boundary | Why It Matters |
|-----|-----------------------------------------|----------------|
| Production provider licensing posture | Market and Evidence Provider Boundary | Official/licensed/public-web/wrapper providers need terms, credential, and redistribution review before production use |
| Generic web execution posture | Web Evidence Boundary | Domain allowlists, parser limits, quarantine behavior, and attribution policy must be executable before web evidence is trusted |
| Artifact content retention policy | Artifact Content and Metadata Boundaries | Retained reports/evidence need explicit retention, checksum/identity, storage, and lineage posture |
| Tool execution trace retention | Persistent Metadata Store and Observability Boundary | Diagnostic traces need retention limits and payload exclusion rules before broad enablement |
| Socket.IO lifecycle parity | API/Service Runtime Boundary | Realtime transport needs the same lifecycle receipts before parity can be claimed |
| Mid-stream provider fallback | External LLM Provider Boundary and Transport Runtime | Streaming provider failures need defined terminal or handoff behavior |
| Production observability controls | Observability Boundary | Health checks alone do not provide full metrics, alerting, or trace correlation |
| Future LTM/RAG deployment | Memory and Retrieval Boundaries | Personalization and sourced retrieval require separate storage/authority planning |

## Prohibited Content

Do not write deployment manifests, service sizing, concrete infrastructure configuration, scripts, operational procedures, or cloud-resource definitions here.
