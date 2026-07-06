# Feature Specification: Internal Symbol and Normalization Backbone - M2B.2

**Feature Branch**: `feature/tool-system-m2b.2`

**Created**: 2026-07-06

**Status**: Planned

**Input**: User requested a follow-up feature specification for milestone `M2B.2`, continuing after verified `M2B.1`, scoped to the Phase 2B roadmap, SRS, traceability, architecture, and tool-system research documents.

## Governance Context *(mandatory)*

**Source Requirements**:
- `FR-2.5.1` through `FR-2.5.5` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-25-tool-output-normalization-and-toolcontextpack) for tool execution envelopes, normalized output classification, request-scoped `ToolContextPack` assembly, raw-payload exclusion, and degraded-state reporting.
- `FR-2.6.1` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-26-vietnam-market-tool-coverage) for Vietnam symbol and index normalization.
- `FR-2.7.1` and `FR-2.7.2` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-27-provider-selection-and-source-attribution) for provider classes and provider selection policy below the model-visible tool layer.
- `FR-2.11.1` through `FR-2.11.6` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-211-tool-data-integrity-and-mutation-receipts) for internal symbol-store ownership, symbol identity integrity, request-scoped context retention, mutation classification, and mutation receipt behavior.
- `NFR-2.2.6` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#nfr-22-fault-tolerance) for explicit degraded-state behavior instead of silent success.
- `NFR-2.3.4` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#nfr-23-data-integrity) for source lineage on retained facts, reports, artifacts, and mutation receipts.
- `NFR-5.2.15` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#nfr-52-tracing) for mutation trace metadata where mutation receipt paths are represented by this backbone.
- `NFR-6.2.5` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#nfr-62-extensibility) for adding provider adapters behind existing model-visible tools without exposing provider-specific tools to the model.
- `CON-6` and `CON-10` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#4-constraints) for provider licensing posture and request-scoped `ToolContextPack` boundaries.
- `AC-9.5`, `AC-9.6`, `AC-9.7`, `AC-9.10`, `AC-9.14`, and `AC-9.15` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#ac-9-tool-system-architecture-and-vietnam-market-integration) for internal symbol-store lookup, Vietnam symbol normalization, provider-hidden tools, normalized output kinds, context retention, and mutation controls.
- `IR-3.3` through `IR-3.7` and `IR-3.9` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#ir-3-tool-system-contracts) for provider descriptors, provider policies, execution envelopes, normalized outputs, `ToolContextPack`, and `MutationReceipt`.

**Authoritative Inputs**:
- [PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#phase-2b-enhanced-tool-system-feature-implementations), especially [Milestone Gates](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#milestone-gates), [Immediate Delivery Slice](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#immediate-delivery-slice), [2B.3 Evolved StockSymbolTool over Internal Symbol Store](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#2b3-evolved-stocksymboltool-over-internal-symbol-store), and [2B.4 Provider Policy and Normalized Output Backbone](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#2b4-provider-policy-and-normalized-output-backbone).
- [ARCHITECTURE_DESIGN.md](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#485a-tool-gateway-and-evidence-admission-boundary), [section 4.3.4](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#434-tool-provider-selection-and-fallback-view), and [section 7](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#7-architecture-considerations-and-planned-evolution) for target tool-system boundaries, provider policy, normalized context, source authority, and current-vs-target status rules.
- [TECHNICAL_DESIGN.md](../../docs/domains/agent/TECHNICAL_DESIGN.md#322-target-phase-2b-runtime-flow), [section 3.2.3](../../docs/domains/agent/TECHNICAL_DESIGN.md#323-tool-and-adapter-responsibility-split), [section 3.2.4](../../docs/domains/agent/TECHNICAL_DESIGN.md#324-target-tool-contract-and-failure-realization), and [section 3.2.5](../../docs/domains/agent/TECHNICAL_DESIGN.md#325-tool-system-persistence-and-data-model-realization) for target runtime flow, tool/adaptor responsibility split, failure handling, and request-scoped retention rules.
- [TOOLS_RESEARCH_AND_PROPOSAL.md](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#7-target-tool-system-architecture), especially [Categorization Mechanism](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#78-categorization-mechanism), [Gateway Phase Ownership](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#79-gateway-phase-ownership), [Technical Design Proposal](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#8-technical-design-proposal), [Tool Data Architecture and Integrity Design](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#9-tool-data-architecture-and-integrity-design), and [Implementation Roadmap](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#12-implementation-roadmap).
- [.specify/memory/constitution.md](../../.specify/memory/constitution.md#architecture-currenttarget-status-semantics) and [.specify/memory/architecture.md](../../.specify/memory/architecture.md#current-target-planned-and-gated-labels) for current/target status discipline.
- [spec-kit HOW-TO.md](../../docs/spec-driven%20development%20%28SDD%29/spec-kit%20HOW-TO.md) for repository-local Spec Kit lifecycle, artifact location, and synchronization rules.
- [project-documentation-and-specification-methodology.md](../../docs/study-hub/project-documentation-and-specification-methodology.md) for long-lived versus delivery-scoped artifact boundaries, requirement authority, and traceability methodology.
- Verified M2B.1 evidence in [specs/tool-system-implementation-m2b.1/spec.md](../tool-system-implementation-m2b.1/spec.md#success-criteria-mandatory), [review.md](../tool-system-implementation-m2b.1/review.md#final-verification-re-run-verdict), and [.verify-done](../tool-system-implementation-m2b.1/.verify-done).

**Traceability Target**: Add a new `tool-system-m2b.2` feature entry to `specs/spec-traceability.yaml` after specification acceptance. Expected mapped SRS items are `FR-2.5.1` through `FR-2.5.5`, `FR-2.6.1`, `FR-2.7.1`, `FR-2.7.2`, `FR-2.11.1` through `FR-2.11.6`, `NFR-2.2.6`, `NFR-2.3.4`, `NFR-5.2.15`, `NFR-6.2.5`, `CON-6`, `CON-10`, `AC-9.5`, `AC-9.6`, `AC-9.7`, `AC-9.10`, `AC-9.14`, `AC-9.15`, `IR-3.3` through `IR-3.7`, and `IR-3.9`. `FR-2.7.4`, `NFR-5.2.13`, `CON-9`, and `AC-9.8` remain downstream market-data attribution requirements for `TS-06`/M2B.3; M2B.2 only defines the normalized source-metadata backbone those later market-data tools will use. The coverage status remains mapped/partial while this feature is planned because later market-data attribution and provider capabilities are intentionally deferred.

**Sync Targets**: `specs/spec-traceability.yaml`, `specs/spec-sync-status.md`, and `docs/domains/agent/SRS_SPEC_TRACEABILITY.md` must be regenerated with `python scripts/sync_spec_status.py --gate` after this feature is added to the manifest or later promoted through lifecycle states.

**Contract Impact**: No public REST, SSE, Socket.IO, or OpenAPI contract change is expected from the specification. Planning should define feature-local contracts for provider adapter descriptors, provider selection policy, tool execution envelopes, normalized outputs, request-scoped `ToolContextPack`, and disabled mutation receipt behavior.

**Lifecycle Status Rule**: This feature started as `Draft`, advanced to `Clarified` after cross-document alignment, and is now `Planned` after implementation planning artifacts were generated. Promote to `Implemented` and `Verified` only after matching Spec Kit evidence exists. M2B.2 must not be treated as current architecture solely because the spec or plan exists.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Resolve Internal Symbol Identity (Priority: P1)

An agent maintainer needs symbol lookup and normalization to use the in-system symbol boundary so Vietnam symbols, indices, aliases, exchange, and currency are handled consistently before any live market-data tool is selected.

**Why this priority**: M2B.2 cannot safely add provider policy or normalized evidence if symbol identity remains ticker-only or mixed with live market-data ownership.

**Independent Test**: Submit symbol lookup, search, and normalization scenarios for Vietnam and cross-market identifiers; verify the outcome is an internal system record or a degraded state, not a live quote/history/fundamental lookup.

**Acceptance Scenarios**:

1. **Given** a user enters `FPT`, `HOSE:FPT`, `HNX:SHS`, `UPCOM:BSR`, VNINDEX, VN30, HNXINDEX, or UPINDEX, **When** the symbol identity is normalized, **Then** the result includes canonical symbol, exchange, and currency where applicable.
2. **Given** a ticker is ambiguous or lacks required exchange/currency context, **When** symbol identity cannot be resolved safely, **Then** the system returns a degraded state or asks for disambiguation instead of retaining ticker-only identity.
3. **Given** a user asks for live price, history, or fundamentals, **When** the request is classified, **Then** those market facts route to market-data tool families, not the internal symbol lookup capability.

---

### User Story 2 - Govern Providers Below Tools (Priority: P1)

An agent maintainer needs provider classes, provider adapter descriptors, and provider selection policy to operate below model-visible tools so the model sees stable capabilities while the application controls provider order, fallback, licensing, freshness, and degraded states.

**Why this priority**: M2B.3 depends on provider-backed Vietnam market data, but M2B.2 must first establish provider-hidden policy and descriptor rules.

**Independent Test**: Inspect provider-backed scenarios and descriptors; verify provider adapters are classified internally, provider selection is deterministic, provider names are not exposed as a flat model-visible tool list, and license-unclear or unsupported provider posture fails closed.

**Acceptance Scenarios**:

1. **Given** a model-visible tool is eligible for provider-backed execution, **When** the tool surface is built, **Then** the model sees the capability and not the provider adapter list.
2. **Given** multiple candidate provider classes exist, **When** policy selects a provider, **Then** the decision follows deterministic provider order, fallback eligibility, license posture, freshness expectations, timeout budget, and degraded-state mapping.
3. **Given** a provider has unclear terms, unsupported credential scope, or blocked production posture, **When** execution requires that provider, **Then** the tool returns a degraded state or research/prototype limitation rather than silently treating the provider as production-approved.

---

### User Story 3 - Normalize Tool Results Before Prompt Use (Priority: P1)

An agent operator needs every governed tool result to be wrapped, classified, and assembled into request-scoped normalized context before the response boundary so raw provider payloads, web content, or tool dictionaries do not become prompt authority.

**Why this priority**: Normalized outputs and `ToolContextPack` are the backbone for later market data, visualization, reporting, and web evidence milestones.

**Independent Test**: Execute representative governed tool outcomes for system records, evidence facts, snippets/documents, visualization provenance, generated artifacts, mutation receipt placeholders, and degraded states; verify prompt assembly receives only normalized, data-only context.

**Acceptance Scenarios**:

1. **Given** a governed tool call completes, **When** the outcome is inspected, **Then** it is represented by a `ToolExecutionEnvelope` with selected route, selected tool, selected adapter where applicable, descriptor identity, admission outcome, cache/freshness status, warnings, degraded-state reason, and trace metadata.
2. **Given** a tool result contains evidence, system records, visualization provenance, generated artifact metadata, mutation receipt data, or an error condition, **When** the output is classified, **Then** it becomes one of the admitted normalized output kinds before prompt assembly.
3. **Given** raw provider payloads, raw HTML, raw PDF bytes, hidden page text, scripts, or instruction-shaped external text are present, **When** prompt context is assembled, **Then** those raw inputs are excluded and only normalized facts, snippets, documents, warnings, citations, or degraded states can reach the prompt boundary.

---

### User Story 4 - Preserve Request-Scoped Context and Source Lineage (Priority: P1)

A compliance reviewer needs normalized tool context, retained derivatives, traces, and source metadata to preserve lineage without storing the full `ToolContextPack` as memory or durable market truth.

**Why this priority**: M2B.2 establishes the retention boundary that later reporting, artifacts, snapshots, and mutation receipts must obey.

**Independent Test**: Inspect context retention scenarios; verify `ToolContextPack` remains request-scoped by default and only approved derivatives retain source lineage or explicit no-source degraded reasons.

**Acceptance Scenarios**:

1. **Given** a request-scoped `ToolContextPack` is assembled, **When** the request completes, **Then** the full pack is not persisted as conversation memory or durable market truth.
2. **Given** a retained derivative such as a report input, artifact metadata, snapshot, mutation receipt, audit metadata, trace metadata, or domain record is allowed, **When** it is retained, **Then** it preserves source lineage or an explicit no-source degraded-state reason.
3. **Given** a cache hit or stale provider result is used, **When** freshness or source metadata is missing or invalid, **Then** the output refreshes through admitted policy or returns a degraded state rather than appearing as fresh evidence.

---

### User Story 5 - Keep Symbol Mutations Disabled Until Governed (Priority: P1)

An operator needs symbol-store write actions to be recognized as high-risk future workflow mutations but disabled by default until route admission, authorization, confirmation, audit metadata, and mutation receipt behavior are fully defined.

**Why this priority**: The roadmap includes TS-11 in M2B.2, but the milestone gate explicitly blocks symbol-store writes until mutation controls exist.

**Independent Test**: Attempt write-like symbol actions; verify they are classified as disabled or blocked `workflow_mutation` / `internal_state_mutation` requests, produce a degraded state, and do not modify symbol records unless a later feature explicitly enables the complete approval and receipt flow.

**Acceptance Scenarios**:

1. **Given** a symbol upsert, alias merge, tag update, coverage update, or retirement marker is requested, **When** mutation controls are not enabled, **Then** the action is blocked or degraded and no durable write occurs.
2. **Given** future mutation policy is represented, **When** its contract is inspected, **Then** it names workflow mutation classification, internal state mutation subtype, authorization/confirmation requirement, audit metadata, and `MutationReceipt` shape.
3. **Given** a test-only or future approved mutation path is admitted, **When** the mutation executes, **Then** a mutation receipt identifies target record, action, actor/route, approval status, audit metadata, timestamp, and result.

### Edge Cases

- Ambiguous ticker-only input maps to multiple exchanges or currencies.
- Internal symbol record is missing, stale, duplicated, or has conflicting aliases.
- Requested symbol is an index rather than an equity.
- Provider policy has no admissible provider for the requested market, freshness, license posture, or production environment.
- Provider result is stale, missing required fields, parser-limited, provider-down, license-unclear, or validation-failed.
- Cache metadata lacks source timestamp, freshness category, warning, or degraded-state reason.
- Normalized output is generated from visualization or generated artifact metadata but is mistakenly treated as evidence.
- Raw provider payload, raw web content, raw PDF bytes, scripts, hidden text, or page instructions are present in an upstream result.
- Public response metadata attempts to expose internal provider policy, credentials, parser limits, or raw trace details.
- Any code path attempts to persist the full `ToolContextPack` as memory or durable market truth.
- Symbol-store write action is requested before authorization, confirmation, and mutation receipt controls are enabled.

## Requirements *(mandatory)*

### Functional Requirements

- **M2B2-FR-001**: The feature MUST build on verified M2B.1 descriptor, route surface, gateway admission, and registry-backed execution behavior without regressing M2B.1 compatibility evidence. *(M2B.1 verified baseline)*
- **M2B2-FR-002**: `StockSymbolTool` target behavior MUST use the internal symbol-store boundary for symbol lookup, search, normalization, listing, coverage, aliases, identifiers, tags, and stored symbol/snapshot metadata. *(FR-2.11.1, AC-9.5)*
- **M2B2-FR-003**: Live quote, history, and fundamental retrieval MUST NOT be owned by the evolved `StockSymbolTool`; those requests MUST route to market-data tool families and provider policy in later milestones. *(FR-2.11.1, FR-2.11.2, AC-9.5)*
- **M2B2-FR-004**: Yahoo, YahooFinance, DataManager-style live market access MUST NOT be the target adapter path for evolved `StockSymbolTool`; such providers may only remain fallback or comparison providers for external market-data tools where approved. *(FR-2.11.2)*
- **M2B2-FR-005**: Symbol identity MUST use at least symbol, exchange, and currency where applicable, and ticker-only ambiguity MUST be normalized, disambiguated, or degraded before retention. *(FR-2.6.1, FR-2.11.3, AC-9.6)*
- **M2B2-FR-006**: Symbol outputs from the internal store MUST be classified as `SystemRecord` normalized outputs and include source/record identity, listing context, aliases, identifiers, coverage, tags, and stored snapshot metadata where available. *(FR-2.5.2, FR-2.11.1, IR-3.6)*
- **M2B2-FR-007**: Provider adapter descriptors MUST classify provider class, supported markets, supported data categories, license posture, credential/scope owner, freshness policy, parser limits, source-attribution requirements, production eligibility, and integrity marker. *(FR-2.7.1, IR-3.3)*
- **M2B2-FR-008**: Provider adapters MUST remain hidden below model-visible tools; provider-specific tools or flat provider lists MUST NOT be exposed directly to the model. *(NFR-6.2.5, AC-9.7)*
- **M2B2-FR-009**: Provider selection policy MUST define provider order, fallback eligibility, fail-closed conditions, market-session rules, freshness expectations, timeout budget, and degraded-state mapping below the model-visible tool layer. *(FR-2.7.2, IR-3.4, AC-9.7)*
- **M2B2-FR-010**: Providers without reviewed licensing, terms-of-use, credential scope, redistribution posture, or production eligibility MUST NOT be silently used as production sources. *(CON-6)*
- **M2B2-FR-011**: Every governed tool call in scope MUST return or be wrapped in a `ToolExecutionEnvelope` that records route, selected tool, selected adapter where applicable, descriptor versions or hashes, admission outcome, normalized output reference, cache status, warnings, degraded-state reason, and trace metadata. *(FR-2.5.1, IR-3.5)*
- **M2B2-FR-012**: Every governed tool result MUST be classified before prompt assembly as exactly one admitted normalized output kind: `EvidenceFact`, `EvidenceSnippet`, `EvidenceDocument`, `SystemRecord`, `MutationReceipt`, `VisualizationProvenance`, `GeneratedArtifact`, or `DegradedState`. *(FR-2.5.2, IR-3.6, AC-9.10)*
- **M2B2-FR-013**: `ToolContextPack` MUST assemble request-scoped normalized outputs, warnings, citations, freshness metadata, source metadata, and degraded states for prompt assembly instead of raw provider, web, or tool payloads. *(FR-2.5.3, IR-3.7, CON-10)*
- **M2B2-FR-014**: Raw HTML, raw PDF bytes, scripts, hidden page text, untrusted page instructions, unvalidated provider payloads, and raw parser artifacts MUST NOT be injected into prompt context. *(FR-2.5.4)*
- **M2B2-FR-015**: Stale, missing, parser-limited, provider-down, blocked, license-unclear, validation-failed, or freshness-unknown outcomes MUST produce a machine-detectable `DegradedState` instead of silent fallback or silent success. *(FR-2.5.5, NFR-2.2.6)*
- **M2B2-FR-016**: Normalized outputs and retained derivatives produced by the backbone MUST carry provider/source metadata fields required by their output kind, including source URL or reference where available, retrieved timestamp, source/published/effective timestamp where available, symbol identity, exchange, currency, freshness, license posture, warnings, and degraded-state reason where applicable; full market-data answer attribution remains a downstream `TS-06`/M2B.3 closure item. *(FR-2.5.3, IR-3.6, IR-3.7)*
- **M2B2-FR-017**: `ToolContextPack` MUST remain request-scoped and MUST NOT be persisted wholesale as conversation memory or durable market truth. *(FR-2.11.4, CON-10, AC-9.14)*
- **M2B2-FR-018**: Only approved derivatives such as reports, artifacts, mutation receipts, audit metadata, trace metadata, approved snapshots, or domain records MAY be retained, and retained derivatives MUST preserve source lineage or explicit no-source degraded-state reason. *(FR-2.11.4, NFR-2.3.4, AC-9.14)*
- **M2B2-FR-019**: Symbol-store write actions MUST be classified as `workflow_mutation` with `internal_state_mutation` subtype and MUST remain disabled or degraded by default until route admission, authorization/confirmation policy, and audit metadata are defined. *(FR-2.11.5, AC-9.15)*
- **M2B2-FR-020**: Approved future in-system mutations MUST emit a `MutationReceipt` with mutation ID, target record, action, before/after summary, actor/route, approval status, audit metadata, timestamp, and result; M2B.2 may define the contract without enabling production writes. *(FR-2.11.6, IR-3.9, NFR-5.2.15, AC-9.15)*
- **M2B2-FR-021**: M2B.2 MUST NOT enable concrete Vietnam quote/history/fundamental tools, TradingView chart/widget expansion, reporting persistence, generic web fetch, remote/MCP-style admission, or production provider enablement beyond the contracts and policy backbone required for `TS-03` through `TS-05` and non-mutating `TS-11`. *(Roadmap M2B.2 gate)*
- **M2B2-FR-022**: Public REST, SSE, Socket.IO, and OpenAPI contracts MUST remain unchanged unless a later plan explicitly introduces a public contract change; internal provider policy, raw traces, credentials, parser limits, and descriptor internals MUST remain non-public. *(Architecture and constitution boundary)*

### Key Entities

- **Internal Symbol Record**: In-system representation of a stock, index, alias set, listing context, coverage state, tag set, or stored snapshot metadata owned by the symbol-store boundary.
- **Canonical Symbol Identity**: Symbol identity made from symbol plus exchange plus currency where applicable; ticker-only identity is insufficient for durable market facts and Vietnam-market workflows.
- **Provider Adapter Descriptor**: Internal descriptor for a source connector, including provider class, supported markets/data categories, license posture, credential/scope owner, freshness policy, parser limits, attribution requirements, production eligibility, and integrity marker.
- **Provider Selection Policy**: Deterministic policy for provider order, fallback eligibility, market-session posture, freshness expectations, timeout budget, fail-closed conditions, and degraded-state mapping.
- **Tool Execution Envelope**: Inspectable wrapper for a governed tool call outcome, including selected route, selected tool, selected adapter where applicable, descriptor identities, admission outcome, cache/freshness status, normalized output reference, warnings, degraded-state reason, and trace metadata.
- **Normalized Output**: One classified data-only output kind admitted for prompt assembly or retained derivatives: `EvidenceFact`, `EvidenceSnippet`, `EvidenceDocument`, `SystemRecord`, `MutationReceipt`, `VisualizationProvenance`, `GeneratedArtifact`, or `DegradedState`.
- **ToolContextPack**: Request-scoped bundle of normalized outputs, citations, source metadata, freshness metadata, warnings, and degraded states passed toward prompt assembly.
- **Source Metadata**: Provider/source identity, provider class, source URL or reference, retrieved timestamp, source/published/effective timestamp where available, symbol identity, freshness, license posture, and quality warnings.
- **DegradedState**: Machine-detectable outcome for blocked, stale, missing, parser-limited, provider-down, license-unclear, validation-failed, unsupported, or disabled paths.
- **MutationReceipt**: Audit record for a future approved in-system write action; in M2B.2 the receipt shape is defined while production symbol-store writes remain disabled by default.
- **Retained Derivative**: Approved durable output derived from request-scoped context, such as report metadata, artifact metadata, approved snapshots, mutation receipt, audit metadata, trace metadata, or domain records.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of M2B.1 focused gateway/descriptor compatibility evidence remains valid after M2B.2 backbone planning and implementation.
- **SC-002**: 100% of symbol normalization fixtures for `FPT`, `HOSE:FPT`, `HNX:SHS`, `UPCOM:BSR`, VNINDEX, VN30, HNXINDEX, UPINDEX, and ambiguous ticker-only inputs produce canonical identity or an explicit degraded/disambiguation result.
- **SC-003**: 100% of `StockSymbolTool` target behavior fixtures return internal symbol `SystemRecord` outputs or degraded states, and 0 fixtures treat live quote/history/fundamental retrieval as the evolved symbol tool's target responsibility.
- **SC-004**: 100% of provider adapter descriptors in scope declare provider class, market/data coverage, license posture, credential/scope owner, freshness policy, parser limits, production eligibility, and integrity marker.
- **SC-005**: 100% of provider selection fixtures prove provider choice occurs below the model-visible tool layer and provider adapters are not exposed as model-visible tools.
- **SC-006**: 100% of governed in-scope tool outcomes have a `ToolExecutionEnvelope` and exactly one admitted normalized output kind before prompt assembly.
- **SC-007**: 0 prompt-context fixtures contain raw provider payloads, raw web/PDF bytes, scripts, hidden text, untrusted page instructions, credentials, parser internals, or raw external instructions.
- **SC-008**: 100% of stale, missing-field, provider-down, parser-limited, blocked-license, freshness-unknown, validation-failed, and unsupported-provider fixtures return machine-detectable degraded states rather than silent success.
- **SC-009**: 100% of retained-derivative fixtures preserve source lineage or explicit no-source degraded-state reason, and 0 fixtures persist the full `ToolContextPack` as conversation memory or durable market truth.
- **SC-010**: 100% of symbol-store write-action fixtures remain blocked or degraded by default unless an explicit future mutation policy enables them; no production write behavior is enabled by this milestone.
- **SC-011**: 100% of mutation receipt contract fixtures identify mutation ID, target record, action, before/after summary, actor/route, approval status, audit metadata, timestamp, and result for any admitted test-only or future approved mutation path.
- **SC-012**: Specification and planning evidence keep M2B.2 scoped to `TS-03` through `TS-05` and non-mutating `TS-11`, with M2B.3/M2B.4/M2B.5 capabilities explicitly deferred.

## Assumptions

- M2B.1 is treated as verified baseline evidence for descriptors, route-filtered surface, thin gateway admission, safe internal trace metadata, and registry-backed execution.
- `StockSymbolTool` may continue to have legacy runtime behavior until implementation changes are planned, but M2B.2 target requirements reposition it toward internal symbol-store lookup and normalization.
- Internal symbol-store reads and normalization are in scope; production symbol-store writes are disabled by default.
- Provider policy and descriptors are in scope; production enablement of Vietnam providers is not in scope unless licensing and terms posture are approved later.
- Tool output normalization and `ToolContextPack` are in scope as a request-scoped backbone; reporting persistence, generic web fetch, TradingView visualization expansion, and concrete market-data provider tools are deferred.
- M2B.2 source metadata requirements define normalized contract shape only; concrete market-data source attribution, cache freshness coverage, and answer-level attribution for `FR-2.7.4`, `NFR-5.2.13`, `CON-9`, and `AC-9.8` are deferred to M2B.3 with `TS-06`.
- Source metadata may be empty only when the output kind explicitly carries a degraded-state reason explaining why no source is available.
- Public contract changes are not expected during specify; if planning later identifies public metadata changes, the plan must name the impacted contract and sync path.
