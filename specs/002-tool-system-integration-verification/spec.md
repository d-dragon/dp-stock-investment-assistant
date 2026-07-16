# Feature Specification: Tool System Integration and Verification

**Feature Directory**: `specs/002-tool-system-integration-verification`

**Feature Branch**: `002-tool-system-integration-verification`

**Created**: 2026-07-09

**Status**: Verified

**Input**: User description: "tool system integration and verification"

## Governance Context *(mandatory)*

**Source Requirements**:
- `FR-2.4.1` through `FR-2.4.6` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-24-tool-gateway-and-tool-exposure) for model-visible descriptors, route-filtered exposure, gateway admission, descriptor integrity, and current-runtime compatibility.
- `FR-2.5.1` through `FR-2.5.5` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-25-tool-output-normalization-and-toolcontextpack) for normalized outputs, request-scoped context, generated artifacts, and degraded states.
- `FR-2.6.1` through `FR-2.6.6` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-26-vietnam-market-tool-coverage) for Vietnam symbol, market-data, visualization-adjacent routing, and Vietnamese or mixed-language coverage.
- `FR-2.7.1` through `FR-2.7.5` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-27-provider-selection-and-source-attribution) for provider class, provider policy, Vietnam-first priority, attribution, and cache freshness metadata.
- `FR-2.8.1` through `FR-2.8.4` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-28-tradingview-visualization) for TradingView visualization provenance and non-evidence boundaries.
- `FR-4.1.3` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-41-query-classification) for meaning-based route classification accuracy.
- `NFR-2.3.5` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#nfr-23-data-integrity) for data freshness.
- `NFR-5.2.12` and `NFR-5.2.13` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#nfr-52-tracing) for gateway/provider traces.
- `NFR-5.3.8` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#nfr-53-metrics) for attribution metrics.
- `NFR-6.1.3` and `NFR-6.1.4` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#nfr-61-code-quality) for coverage gates.
- `CON-6`, `CON-7`, `CON-9`, and `CON-10` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#4-constraints) for provider licensing and data integrity constraints.
- `AC-9.1` through `AC-9.11`, `AC-9.14`, `AC-9.16`, and `AC-9.17` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#ac-9-tool-system-architecture-and-vietnam-market-integration) for tool-system acceptance and safety boundaries.

**Authoritative Inputs**:
- [PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#2b0-tool-system-goals-boundaries-and-gates), especially [Milestone Gates](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#milestone-gates), [2B.5 Concrete Market Data and Visualization Tools](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#2b5-concrete-market-data-and-visualization-tools), and [2B.9 Verification and Quality Gates](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#2b9-verification-and-quality-gates).
- [ARCHITECTURE_DESIGN.md](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#485a-tool-gateway-and-evidence-admission-boundary), [section 4.3.4](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#434-tool-provider-selection-and-fallback-view), [section 5.3](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#53-terminology-and-concept-evolution), and [section 7](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#7-architecture-considerations-and-planned-evolution) for current-vs-target semantics and provider-hidden tool boundaries.
- [TECHNICAL_DESIGN.md](../../docs/domains/agent/TECHNICAL_DESIGN.md#322-target-phase-2b-runtime-flow), [section 3.2.3](../../docs/domains/agent/TECHNICAL_DESIGN.md#323-tool-and-adapter-responsibility-split), [section 3.2.4](../../docs/domains/agent/TECHNICAL_DESIGN.md#324-target-tool-contract-and-failure-realization), [section 3.2.5](../../docs/domains/agent/TECHNICAL_DESIGN.md#325-tool-data-model-and-persistent-storage-realization), and [section 4.2](../../docs/domains/agent/TECHNICAL_DESIGN.md#42-routing-output-and-prompt-evolution) for realization-level boundaries and verification surfaces.
- [TOOLS_RESEARCH_AND_PROPOSAL.md](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#7-target-tool-system-architecture), [section 8](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#8-technical-design-proposal), [section 9](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#9-tool-data-architecture-and-integrity-design), and [section 12](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#12-implementation-roadmap) for tool gateway, provider adapter, normalized context, and source-integrity design.
- [.specify/memory/constitution.md](../../.specify/memory/constitution.md#vietnam-market-data-and-visualization-evidence-gates), [.specify/memory/architecture.md](../../.specify/memory/architecture.md#current-target-planned-and-gated-labels), and the five architecture view memory files for current/target labels, provider-hidden execution, request-scoped context, cache freshness, visualization provenance, and verification gates.
- Verified predecessor evidence in [specs/tool-system-implementation-m2b.1/spec.md](../tool-system-implementation-m2b.1/spec.md), [specs/tool-system-implementation-m2b.1/.verify-done](../tool-system-implementation-m2b.1/.verify-done), [specs/tool-system-m2b.2/spec.md](../tool-system-m2b.2/spec.md), [specs/tool-system-m2b.2/.verify-done](../tool-system-m2b.2/.verify-done), [specs/tool-system-m2b.3/spec.md](../tool-system-m2b.3/spec.md), and [specs/tool-system-m2b.3/.verify-done](../tool-system-m2b.3/.verify-done).

**Traceability Target**: Add a new `002-tool-system-integration-verification` feature entry to `specs/spec-traceability.yaml` after specification acceptance. Expected mapped SRS items are `FR-2.4.1` through `FR-2.8.4`, `FR-4.1.3`, `NFR-2.3.5`, `NFR-5.2.12`, `NFR-5.2.13`, `NFR-5.3.8`, `NFR-6.1.3`, `NFR-6.1.4`, `CON-6`, `CON-7`, `CON-9`, `CON-10`, `AC-9.1` through `AC-9.11`, `AC-9.14`, `AC-9.16`, and `AC-9.17`. Keep `coverage_status: partial` because this feature verifies integrated Phase 2B tool-system behavior and intentionally does not deliver M2B.4 reporting, generic web evidence, observability dashboards, remote/MCP admission, symbol-store writes, or production provider enablement.

**Sync Targets**: `specs/spec-traceability.yaml`, `specs/spec-sync-status.md`, and `docs/domains/agent/SRS_SPEC_TRACEABILITY.md` must be regenerated with `python scripts/sync_spec_status.py --gate` when this feature is added to the manifest or promoted through lifecycle states. Long-lived architecture and technical-design documents are sync targets only if verification proves stable current-state behavior that changes the documented baseline.

**Contract Impact**: No public REST, SSE, Socket.IO, or OpenAPI contract change is expected. Planning may define feature-local verification contracts for integrated route fixtures, gateway admission matrices, provider/freshness trace audits, visualization provenance assertions, and release-readiness evidence.

**Lifecycle Status Rule**: Starts as `Draft`; promote through `Clarified`, `Planned`, `Implemented`, and `Verified` only after the matching Spec Kit phase evidence exists. Verification must confirm that the feature integrates and validates already governed tool-system capabilities without silently broadening scope into later roadmap milestones.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - End-to-End Tool-System Readiness (Priority: P1)

A release owner needs one integrated readiness view showing that the verified M2B.1, M2B.2, and M2B.3 tool-system slices work together as one coherent agent capability set.

**Why this priority**: Individual milestone verification can miss regressions at the boundaries between route filtering, gateway admission, provider policy, normalized outputs, and response composition.

**Independent Test**: Execute an integrated fixture set covering symbol lookup, Vietnam quote/history, fundamentals, breadth/flow, disclosures, TradingView visualization, degraded provider paths, and Vietnamese or mixed-language prompts; verify every scenario reaches the expected route, tool family, output classification, source-attribution state, and user-facing outcome.

**Acceptance Scenarios**:

1. **Given** verified M2B.1, M2B.2, and M2B.3 evidence exists, **When** the integrated readiness suite is reviewed, **Then** each predecessor capability is represented by at least one cross-boundary scenario and any missing coverage is recorded as a blocker or explicit deferred item.
2. **Given** an integrated scenario exercises multiple tool-system boundaries, **When** the scenario completes, **Then** route selection, exposed tool family, gateway decision, provider posture, normalized output kind, warnings, and final response outcome are all inspectable.
3. **Given** any integrated scenario fails, **When** readiness is assessed, **Then** the feature cannot be promoted to `Verified` until the failure is fixed or an approved governed exception identifies the residual risk.

---

### User Story 2 - Financial Answer Evidence Audit (Priority: P1)

A compliance reviewer needs to confirm that factual market answers remain source-attributed, freshness-aware, and free of unsupported recommendations across integrated tool-system flows.

**Why this priority**: Financial answer safety depends on the composed behavior, not only on individual tools returning the right fields.

**Independent Test**: Run answer fixtures for successful market facts, stale cache, provider outage, missing source, license-blocked data, and unsupported recommendation language; verify the response either includes complete evidence metadata or degrades safely.

**Acceptance Scenarios**:

1. **Given** a factual market answer is produced, **When** the answer evidence is audited, **Then** every market fact includes provider/source, source URL or reference, retrieved timestamp, source or effective timestamp where available, exchange, currency, freshness, license posture, and warnings where applicable.
2. **Given** evidence is unavailable, stale, license-blocked, missing mandatory fields, or unsupported, **When** the assistant responds, **Then** it returns a machine-detectable degraded result or safe warning instead of fabricating or silently omitting evidence.
3. **Given** the assistant generates investment language, **When** finance-safety expectations are checked, **Then** unsupported recommendations, guaranteed-return language, hype language, and unsupported certainty are blocked or conservatively rewritten.

---

### User Story 3 - Route and Tool Exposure Regression Control (Priority: P1)

An agent maintainer needs confidence that route-filtered tool exposure remains stable across English, Vietnamese, and mixed-language prompts after tool-system capabilities are composed.

**Why this priority**: The model should see only route-eligible tools; a route regression can expose the wrong provider path or hide the correct market-data family.

**Independent Test**: Evaluate route fixtures for price, chart, fundamentals, disclosures, breadth, flow, report-like prompts, ambiguous prompts, and unsupported requests; verify expected route, tool-family exposure, and degradation behavior.

**Acceptance Scenarios**:

1. **Given** a supported market prompt is classified, **When** the tool surface is inspected, **Then** only route-eligible and policy-admitted tool families are exposed for that request.
2. **Given** Vietnamese or mixed-language route fixtures are evaluated, **When** results are measured, **Then** meaning-based classification accuracy is at least 85% and route-tool exposure failures are reported separately from language-classification failures.
3. **Given** a prompt is ambiguous or unsupported, **When** route confidence or policy admission is insufficient, **Then** the assistant degrades or asks for disambiguation rather than exposing unrelated tool families.

---

### User Story 4 - Visualization and Non-Evidence Boundary Verification (Priority: P1)

A reviewer needs assurance that TradingView and other visualization outputs support inspection while never becoming canonical evidence for factual market answers by default.

**Why this priority**: Visualization payloads can contain numeric values that look authoritative unless the integrated response path preserves the `VisualizationProvenance` boundary.

**Independent Test**: Run chart, widget, deep-link, ticker-tape, heatmap, screener, symbol-validation, and factual-answer fixtures; verify visualization outputs are classified as provenance and numeric facts are sourced from admitted market-data evidence or degraded.

**Acceptance Scenarios**:

1. **Given** a visualization request succeeds, **When** the output is inspected, **Then** the payload includes symbol, view configuration, validation status, generated timestamp, warnings, and `VisualizationProvenance` classification.
2. **Given** a visualization payload includes numeric values, **When** the assistant composes a factual answer, **Then** those values are not used as canonical market evidence unless a future approved policy explicitly admits them.
3. **Given** visualization validation fails, **When** the assistant responds, **Then** it returns a degraded visualization state without inventing a chart or market fact.

---

### User Story 6 - Architecture Compliance and Boundary Preservation (Priority: P1)

An architecture owner needs integrated proof that the tool system preserves key architectural boundaries: provider-class authority levels are respected, tool risk classes are enforced, raw payloads are excluded from prompt context, symbol and market-data tool separation is maintained, the gateway stays adapter-agnostic, the registry remains the inventory authority, and market facts are excluded from memory.

**Why this priority**: Architecture violations at composed runtime boundaries (risk class downgrade, provider class promotion, raw payload leakage, tool boundary blurring) are harder to detect without dedicated cross-boundary verification.

**Independent Test**: Run integrated inspection scenarios for provider classes (7 levels with correct admission/degradation), risk classes (4 levels with gateway enforcement and no policy downgrade), prompt boundary safety (raw payloads excluded), `StockSymbolTool` separation (symbol identity only), `ToolGateway` purity (no provider-specific parsing), `ToolRegistry` integrity (not replaced), and STM evidence freedom (no market facts stored). Each scenario must pass without architecture boundary violations.

**Acceptance Scenarios**:

1. **Given** integrated tool-system scenarios exercise all seven provider classes, **When** provider admission and degraded-state behavior are inspected, **Then** each class produces the correct architectural behavior — in-system and official sources admitted, licensed sources admitted, Vietnam-native public web admitted where policy allows, wrapper/prototype producing appropriate caveats, visualization producing `VisualizationProvenance`, international fallback producing comparison-only context — and no adapter is silently promoted to a higher authority class.
2. **Given** tools registered in `ToolRegistry` are inspected for risk class declaration, **When** the registry and gateway admission logs are audited, **Then** each tool declares `read_only_evidence` or `bounded_transformation`, gateway admission enforces the risk-class ceiling, and prompt-facing tool policy does not reclassify any tool below its registry-declared class.
3. **Given** integrated scenarios that produce provider results, visualization payloads, and tool descriptor content, **When** the prompt assembly input is inspected, **Then** raw provider payloads, chart widget content, tool descriptors, and document instructions are not present — only normalized `ToolContextPack` content reaches the prompt boundary.
4. **Given** integration scenarios exercise symbol lookup and market-data requests, **When** the routing path is inspected, **Then** `StockSymbolTool` handles symbol identity, aliases, exchange/currency, coverage, and tags, while quote/history/fundamental/breadth/flow requests route through market-data tool families.
5. **Given** gateway admission scenarios exercise tool calls across provider classes, **When** the gateway implementation is inspected, **Then** `ToolGateway` does not contain provider-specific parsing logic — all provider-specific fetch, health, licensing, and parsing resides in the adapter layer.
6. **Given** the tool inventory is inspected across the verified M2B baselines, **When** the registry boundary is audited, **Then** `ToolRegistry` remains the authoritative inventory and enablement boundary, and no replacement or bypass mechanism is observed.
7. **Given** integration scenarios produce market facts through tool calls, **When** the STM checkpoint state and conversation metadata stores are inspected, **Then** market facts (prices, ratios, valuations, OHLCV data) are not present in checkpoint state or conversation metadata collections — they remain request-scoped tool outputs or explicitly retained artifacts with source lineage.

---

### User Story 5 - Release Evidence and Sync Closeout (Priority: P2)

A project maintainer needs the integration-verification feature to leave clear lifecycle evidence, traceability mappings, and sync reports for future planning and audit.

**Why this priority**: The feature is valuable only if its verification result is durable and visible to downstream Spec Kit workflows.

**Independent Test**: Inspect feature-local review evidence, checklist status, traceability manifest entry, generated sync reports, and lifecycle markers; verify they agree on feature status and mapped SRS coverage.

**Acceptance Scenarios**:

1. **Given** integration verification completes, **When** lifecycle evidence is inspected, **Then** the feature directory contains the required specification, plan, tasks, implementation evidence, review or verification evidence, and status markers for its current phase.
2. **Given** traceability is regenerated, **When** the reverse trace is inspected, **Then** mapped SRS items point to this feature only for integration-verification evidence and do not overwrite verified ownership from predecessor features.
3. **Given** a long-lived architecture or technical-design claim would change from target to current, **When** closeout is performed, **Then** the claim is updated only after verification evidence proves the new current-state behavior.

### Edge Cases

- A predecessor feature is marked verified but its `.verify-done`, review evidence, task status, or sync output no longer agrees with the traceability report.
- A scenario passes at the tool level but fails after route filtering, gateway admission, normalization, response composition, or public warning rendering.
- A provider-backed result contains values but lacks source URL/reference, timestamp, freshness, exchange, currency, license posture, or warning metadata.
- A cache hit is faster than live retrieval but has missing or stale freshness metadata.
- An international fallback provider is selected even though an admitted Vietnam-native or official source is available.
- TradingView, chart, heatmap, screener, or widget payload values are accidentally used as market evidence.
- Vietnamese or mixed-language prompts pass broad route classification but expose the wrong tool family.
- A report-like prompt is included as a routing fixture and accidentally expands scope into full report generation or persistence.
- Generic web fetch, remote/MCP admission, symbol-store writes, production provider enablement, or observability dashboards are proposed as shortcuts for integration verification.
- Public response surfaces leak provider credentials, raw provider payloads, parser internals, hidden traces, or unsafe implementation details.
- Raw provider payloads, chart widgets, or document instructions are accidentally injected into internal prompt context as behavioral instructions rather than normalized evidence.
- A provider adapter from one provider class (e.g., wrapper/prototype) is silently promoted to a higher authority class (e.g., licensed commercial) without governing policy review.
- A tool's registry-declared risk class (`read_only_evidence`, `bounded_transformation`, `workflow_mutation`, `external_side_effect`) is silently downgraded by prompt-facing tool policy to bypass admission controls.
- `StockSymbolTool` handles live quote/history/fundamental data alongside symbol identity lookups, blurring the architecture-mandated separation between symbol-store and market-data tool boundaries.
- Provider-specific parsing logic is embedded inside `ToolGateway` instead of in the provider adapter layer, violating the adapter-gateway separation contract.
- `ToolRegistry` is replaced or bypassed by a new inventory mechanism, breaking the registry-backed execution contract.
- STM checkpoints or conversation metadata stores retain market facts (prices, ratios, valuations) that should remain request-scoped tool outputs rather than persistent memory content.
- Prompt-facing tool policy reclassifies a tool below its registry-declared architectural risk class, allowing lower-policy paths to execute higher-risk actions.

## Requirements *(mandatory)*

### Functional Requirements

- **TSIV-FR-001**: The feature MUST verify integrated behavior across the verified M2B.1, M2B.2, and M2B.3 tool-system baselines without redefining those predecessor feature scopes.
- **TSIV-FR-002**: The feature MUST include an integrated scenario inventory that covers descriptor-backed exposure, route filtering, gateway admission, provider policy, normalized output classification, request-scoped context, warnings, and degraded states.
- **TSIV-FR-003**: The feature MUST verify that route-filtered tool exposure presents only route-eligible, enabled, policy-admitted tool families before model tool selection.
- **TSIV-FR-004**: The feature MUST verify that gateway admission blocks invalid arguments, disallowed route/tool combinations, blocked risk classes, license-unclear sources, unsupported providers, descriptor drift, and unapproved remote descriptors with explicit degraded outcomes.
- **TSIV-FR-005**: The feature MUST verify that provider selection remains below the model-visible tool layer and that provider adapters are not exposed as flat model-visible tools.
- **TSIV-FR-006**: The feature MUST verify that Vietnam-market requests prefer admitted Vietnam-native, official, or licensed sources where available and use international providers only as governed fallback or comparison sources.
- **TSIV-FR-007**: The feature MUST verify that every market fact used in an answer, cache result, trace, retained derivative, or report input preserves provider/source, URL or reference, retrieved timestamp, source or effective timestamp where available, exchange, currency, freshness, license posture, and warnings or degraded-state reason.
- **TSIV-FR-008**: The feature MUST verify that stale, expired, freshness-unknown, anonymous, blocked-license, missing-field, parser-limited, and provider-unavailable outcomes produce deterministic fallback or explicit degraded states.
- **TSIV-FR-009**: The feature MUST verify that cached market-data results preserve source, retrieval, freshness, TTL or expiry, warning, and degraded-state metadata so cache hits do not hide stale or unsupported evidence.
- **TSIV-FR-010**: The feature MUST verify that TradingView chart, widget, deep-link, ticker-tape, heatmap, screener, and symbol-validation outputs are classified as `VisualizationProvenance`.
- **TSIV-FR-011**: The feature MUST verify that TradingView payload values are not treated as canonical evidence for factual market answers by default.
- **TSIV-FR-012**: The feature MUST verify Vietnamese and mixed-language route fixtures for price, chart, fundamentals, disclosures, breadth, flow, report-like prompts, ambiguous prompts, and unsupported prompts.
- **TSIV-FR-013**: The feature MUST measure meaning-based route classification accuracy at or above 85% and separately report route-tool exposure precision, recall, or equivalent acceptance outcomes.
- **TSIV-FR-014**: The feature MUST verify that public response surfaces omit credentials, secrets, raw provider payloads, parser internals, hidden trace details, and unsafe implementation details.
- **TSIV-FR-015**: The feature MUST verify that unsourced recommendations, guaranteed-return language, hype language, and unsupported certainty are blocked or conservatively rewritten in tool-backed answers.
- **TSIV-FR-016**: The feature MUST preserve the single ReAct runtime and must not introduce a second runtime, public REST/SSE/Socket.IO/OpenAPI changes, generic web fetch, reporting persistence, remote/MCP-style admission, production symbol-store writes, or production provider enablement.
- **TSIV-FR-017**: The feature MUST record integration-verification evidence in feature-local artifacts and update traceability/sync outputs without overwriting predecessor feature ownership.
- **TSIV-FR-018**: The feature MUST keep long-lived architecture or technical-design updates limited to verified current-state behavior; target, planned, gated, and gap labels must remain explicit.
- **TSIV-FR-019**: The feature MUST verify that all seven provider classes (in-system persistent data, official exchange/depository, licensed commercial, Vietnam-native public web, wrapper/prototype, visualization provider, international fallback) produce correct admission, fallback, and degraded-state behavior per their architectural authority level, and that no provider adapter is silently promoted to a higher authority class without governing policy review.
- **TSIV-FR-020**: The feature MUST verify that: (a) each tool in `ToolRegistry` declares a correct architectural risk class (`read_only_evidence`, `bounded_transformation`, `workflow_mutation`, `external_side_effect`), (b) `ToolGateway` filters or blocks calls exceeding the admitted risk class for the current route/prompt, and (c) prompt-facing tool policy cannot reclassify a tool below its registry-declared risk class. `external_side_effect` tools remain prohibited in the current baseline and are not tested in this feature scope.
- **TSIV-FR-021**: The feature MUST verify that raw provider payloads, chart widget content, tool descriptor text, and document/page instructions are NOT injected into the internal prompt assembly as behavioral instructions or policy authority — only normalized `ToolContextPack` content (normalized facts, snippets, system records, provenance markers) reaches the prompt boundary.
- **TSIV-FR-022**: The feature MUST verify that `StockSymbolTool` is separated from live market-data retrieval: symbol identity, aliases, exchange/currency identity, coverage, tags, and stored snapshots route through `StockSymbolTool` (or its internal adapter), while quote, history, fundamentals, breadth, flow, and indicator requests route through market-data tool families with provider-backed evidence.
- **TSIV-FR-023**: The feature MUST verify that `ToolGateway` does not contain provider-specific parsing logic; provider-specific fetch, health, licensing, and parsing remain in the provider adapter layer below the gateway boundary.
- **TSIV-FR-024**: The feature MUST verify that `ToolRegistry` remains the authoritative inventory and enablement boundary for all tools; no replacement or bypass mechanism is introduced in the current feature scope.
- **TSIV-FR-025**: The feature MUST verify that STM checkpoints (LangGraph `MongoDBSaver`) and conversation metadata stores (`conversations` collection) do not retain market facts (prices, ratios, valuations, OHLCV data) as persistent memory content; market facts remain request-scoped tool outputs or explicitly retained artifacts with source lineage.

### Key Entities *(include if feature involves data)*

- **Integrated Tool-System Scenario**: A fixture or review case that crosses route selection, tool exposure, gateway admission, provider policy, normalization, response composition, and user-visible outcome.
- **Gateway Admission Matrix**: Verification artifact that records route, exposed tool family, selected tool, admission decision, blocked reason, degraded-state reason, and expected user outcome.
- **Evidence Audit Record**: Reviewable result showing source attribution, timestamps, exchange, currency, freshness, license posture, warnings, and degraded-state behavior for market facts.
- **Visualization Boundary Record**: Reviewable result proving that visualization payloads are classified as provenance and do not become canonical evidence by default.
- **Route Evaluation Result**: Measured outcome for English, Vietnamese, or mixed-language prompts with expected route, exposed tool family, ambiguity label, and pass/fail reason.
- **Release Readiness Evidence**: Feature-local evidence package that connects specification, plan, tasks, tests or reviews, traceability, sync reports, and lifecycle markers.
- **Governed Exception**: Explicitly approved residual risk or deferred item that names the requirement, reason, user impact, owner, and follow-up condition.
- **Provider Class Verification Record**: Reviewable proof that each of the seven provider classes (in-system, official, licensed, Vietnam-native public web, wrapper/prototype, visualization, international fallback) produces correct admission, fallback, or degraded behavior per its architectural authority level, and that no adapter is silently promoted without policy review.
- **Risk Class Audit Record**: Reviewable proof that each tool declares a correct risk class in `ToolRegistry`, that `ToolGateway` enforces the admitted risk-class ceiling, and that prompt-facing policy cannot reclassify a tool below its registry-declared class.
- **Prompt-Boundary Safety Record**: Reviewable proof that raw provider payloads, chart widgets, tool descriptors, and document instructions are excluded from the prompt assembly boundary and that only normalized `ToolContextPack` content reaches the LLM context.
- **Symbol-Tool Separation Record**: Reviewable proof that `StockSymbolTool` handles symbol identity and internal metadata only, while quote/history/fundamental/breadth/flow requests route through market-data tool families.
- **Gateway Purity Record**: Reviewable proof that `ToolGateway` does not contain provider-specific parsing logic and that provider-specific behavior is confined to the adapter layer.
- **Registry Integrity Record**: Reviewable proof that `ToolRegistry` remains the authoritative inventory boundary and is not replaced or bypassed.
- **STM Evidence-Free Record**: Reviewable proof that market facts (prices, ratios, OHLCV, valuations) are not stored in STM checkpoint state or conversation metadata collections.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of integrated readiness scenarios identify expected route, exposed tool family, gateway decision, provider posture, output classification, warning/degraded state, and final user-facing outcome.
- **SC-002**: 100% of predecessor capability areas from verified M2B.1, M2B.2, and M2B.3 have at least one integrated cross-boundary scenario or an explicit governed exception.
- **SC-003**: 100% of successful factual market-answer scenarios include complete source attribution, freshness, exchange/currency where applicable, license posture, and warning metadata, or are classified as degraded no-source outcomes.
- **SC-004**: 100% of provider outage, stale-source, stale-cache, missing-field, parser-limited, blocked-license, unsupported-source, and validation-failed scenarios produce admitted fallback or machine-detectable degraded states.
- **SC-005**: 100% of TradingView and visualization scenarios are classified as `VisualizationProvenance`, and 0 factual answer scenarios use visualization payload values as canonical evidence by default.
- **SC-006**: Vietnamese and mixed-language route fixtures achieve at least 85% meaning-based classification accuracy, with route-tool exposure failures measured separately.
- **SC-007**: Public response and trace-review scenarios show 0 leaks of credentials, secrets, raw provider payloads, parser internals, hidden trace details, or unsafe implementation details.
- **SC-008**: Finance-safety scenarios show 100% blocking or conservative rewriting for unsupported recommendations, guaranteed-return language, hype language, and unsupported certainty.
- **SC-009**: Traceability and sync reports agree with the feature lifecycle state before promotion to `Verified`, and no predecessor feature ownership is overwritten by this integration-verification feature.
- **SC-010**: The feature scope remains bounded to integration and verification; 0 accepted tasks introduce generic web fetch, reporting persistence, remote/MCP-style admission, production symbol-store writes, production provider enablement, or public contract changes without a separate governed feature.
- **SC-011**: All 7 provider classes (in-system, official, licensed, Vietnam-native public web, wrapper/prototype, visualization, international fallback) produce correct admission or degraded behavior per their architectural authority level in integrated scenarios; 0 provider adapters are silently promoted to a higher authority class without governing policy review.
- **SC-012**: 100% of current tools in `ToolRegistry` declare a correct architectural risk class; 100% of gateway admission scenarios enforce the admitted risk-class ceiling; 0 scenarios show prompt-facing tool policy reclassifying a tool below its registry-declared risk class.
- **SC-013**: 100% of prompt-context inspection scenarios confirm that raw provider payloads, chart widgets, tool descriptors, and document instructions are not present in the prompt assembly input — only normalized `ToolContextPack` content reaches the prompt boundary.
- **SC-014**: 100% of integration scenarios confirm that `StockSymbolTool` handles symbol identity/internal metadata only, while quote/history/fundamental/breadth/flow requests route through market-data tool families.
- **SC-015**: 100% of gateway inspection scenarios confirm that `ToolGateway` does not contain provider-specific parsing logic.
- **SC-016**: 100% of registry inspection scenarios confirm that `ToolRegistry` remains the authoritative inventory boundary and is not replaced or bypassed.
- **SC-017**: 100% of STM and conversation metadata inspection scenarios confirm that market facts (prices, ratios, OHLCV data) are not present in checkpoint state or conversation metadata stores.

## Assumptions

- M2B.1, M2B.2, and M2B.3 remain the verified predecessor baselines for tool descriptors, route filtering, gateway admission, symbol identity, provider policy, normalized outputs, Vietnam market-data coverage, TradingView provenance, and Vietnamese or mixed-language route fixtures.
- This feature is a verification and integration hardening slice, not the next product expansion milestone.
- Existing traceability may map predecessor requirements to verified features; this feature adds integration evidence without claiming exclusive ownership of already verified requirements.
- Report-like prompts may appear only as route/evaluation fixtures. Full report composition, persistence, and artifact lifecycle remain outside this feature.
- Generic web fetch, observability dashboards, remote/MCP-style tool admission, production provider enablement, and symbol-store writes remain deferred unless a later governed specification explicitly admits them.
- Long-lived architecture and technical-design documents should change only when integration verification proves stable implemented behavior that should be promoted from target, planned, or gated status to current status.
