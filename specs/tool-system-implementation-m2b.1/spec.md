# Feature Specification: Tool Contract and Gateway Baseline - M2B.1

**Feature Directory**: `specs/tool-system-implementation-m2b.1`

**Feature Branch**: `feature/tool-system-implementation-m2b.1`

**Created**: 2026-07-01

**Status**: Planned

**Input**: User requested a feature specification for the Phase 2B enhanced tool system, scoped to milestone `M2B.1` in [PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#milestone-gates), with SRS, traceability, tool proposal, architecture, and repository SDD methodology inputs.

## Governance Context *(mandatory)*

**Source Requirements**:
- `FR-2.4.1` through `FR-2.4.6` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-24-tool-gateway-and-tool-exposure): AgentTool baseline, capability descriptors, route-filtered surface, execution-time admission, descriptor integrity, and current runtime preservation.
- `FR-4.2.1` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-42-route-based-behavior): route-based optimized tool selection.
- `NFR-5.2.12` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#nfr-52-tracing): tool gateway trace completeness.
- `NFR-6.2.6` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#nfr-62-extensibility): reviewable descriptor and policy artifacts with traceable versions or integrity markers.
- `CON-6`, `CON-9`, and `CON-10` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#4-constraints): licensing review, source-attributed market facts, and request-scoped tool context boundaries.
- `AC-9.1` through `AC-9.4` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#ac-9-tool-system-architecture-and-vietnam-market-integration): descriptors, route-filtered exposure, gateway admission, and descriptor drift handling.
- `IR-3.1` and `IR-3.2` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#ir-3-tool-system-contracts): `ToolCapabilityDescriptor` and `ToolPolicyDescriptor` contract requirements.

**Authoritative Inputs**:
- [PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#phase-2b-enhanced-tool-system-feature-implementations), especially [2B.1 AgentTool Baseline and Descriptor Inventory](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#2b1-agenttool-baseline-and-descriptor-inventory), [2B.2 Route-Filtered Tool Surface and Thin Gateway](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#2b2-route-filtered-tool-surface-and-thin-gateway), and [Milestone Gates](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#milestone-gates).
- [TOOLS_RESEARCH_AND_PROPOSAL.md](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#7-target-tool-system-architecture), especially [AgentTool](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#112-agenttool), [ToolCapabilityDescriptor](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#113-toolcapabilitydescriptor), [ToolSurfaceBuilder](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#114-toolsurfacebuilder), [ToolPolicyDescriptor](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#115-toolpolicydescriptor), [Phase 1](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#122-phase-1-agenttool-baseline-and-descriptor-inventory), [Phase 2](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#123-phase-2-route-filtered-tool-surface-and-thin-gateway), and [Verification Strategy](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#13-verification-strategy).
- [ARCHITECTURE_DESIGN.md](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#411a-external-and-internal-interface-diagram-architecture-level) for the tool invocation and provider-normalization boundaries, plus [Tooling and Data Access Evolution](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#71-tooling-and-data-access-evolution).
- [.specify/memory/constitution.md](../../.specify/memory/constitution.md#agent-tool-system-and-architecture-governance), [.specify/memory/constitution.md](../../.specify/memory/constitution.md#document-referencing-in-spec-kit-workflows), and [.specify/memory/constitution.md](../../.specify/memory/constitution.md#spec-kit-lifecycle-obligations).
- [spec-kit HOW-TO.md](../../docs/spec-driven%20development%20%28SDD%29/spec-kit%20HOW-TO.md#332-spec-authoring-and-planning) and [project-documentation-and-specification-methodology.md](../../docs/study-hub/project-documentation-and-specification-methodology.md#71-the-18-step-sdd-lifecycle-with-spec-kit) for repository-specific Spec Kit placement, traceability, and lifecycle rules.

**Traceability Target**: Add `specs/tool-system-implementation-m2b.1` to `specs/spec-traceability.yaml` during planning with mapped SRS items `FR-2.4.1` through `FR-2.4.6`, `FR-4.2.1`, `NFR-5.2.12`, `NFR-6.2.6`, `CON-6`, `CON-9`, `CON-10`, `AC-9.1` through `AC-9.4`, `IR-3.1`, and `IR-3.2`. Update [SRS_SPEC_TRACEABILITY.md](../../docs/domains/agent/SRS_SPEC_TRACEABILITY.md#fr-2) and [SRS_SPEC_TRACEABILITY.md](../../docs/domains/agent/SRS_SPEC_TRACEABILITY.md#ac-9) as the feature moves through planned, implemented, and verified states.

**Sync Targets**: `specs/spec-traceability.yaml`, `specs/spec-sync-status.md`, `docs/domains/agent/SRS_SPEC_TRACEABILITY.md`, and any affected realization sections in `docs/domains/agent/ARCHITECTURE_DESIGN.md` or companion technical design after implementation verification. `docs/openapi.yaml` is a sync target only if user-facing response metadata or public API schemas change.

**Contract Impact**: No public REST, SSE, or WebSocket contract change is expected from the M2B.1 baseline. Planning should define feature-local contracts under `specs/tool-system-implementation-m2b.1/contracts/` for tool descriptors, route exposure, gateway admission outcomes, and internal trace metadata before implementation begins. User-visible degraded-state disclosure is limited to safe status or warning metadata unless a later plan explicitly introduces a public contract change.

**Lifecycle Status Rule**: Starts as `Draft`; promote through `Clarified`, `Planned`, `Implemented`, and `Verified` only after the matching Spec Kit phase evidence exists.

## Clarifications

### Session 2026-07-01

- Q: Should M2B.1 require descriptors for `TradingViewTool` even though it is placeholder code and commented out of runtime registration? -> A: Yes; require descriptors plus disabled and non-exposed status, without implying runtime capability.
- Q: For routes without a real admitted tool today, should the surface expose no tools or expose scaffolded tools that return degraded states? -> A: Expose no tools unless specifically admitted, with the filtering reason recorded in trace metadata.
- Q: Must M2B.1 verification cover both REST/SSE and Socket.IO agent entry paths, or only the shared agent/tool boundary? -> A: Cover the shared agent/tool boundary only; Socket.IO lifecycle parity remains a separate architecture gap.
- Q: Are gateway traces internal-only, or can degraded-state/admission metadata appear in public API or streaming responses? -> A: Keep gateway traces internal, with only safe degraded-state status or warning metadata allowed on public response surfaces.
- Q: Should this spec remain strictly `TS-01` to `TS-02`, or include contract stubs for `TS-05`, `ToolExecutionEnvelope`, and `ToolContextPack` because the roadmap immediate slice mentions `TS-01` to `TS-05`? -> A: Keep scope strict to `TS-01` and `TS-02`; define only feature-local placeholder contracts needed for M2B.1 planning.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Existing Tools Have Governed Descriptors (Priority: P1)

An agent maintainer needs every M2B.1 baseline tool to declare a reviewed public capability description and a separate internal policy description, while preserving current registry-based tool behavior for end users. Placeholder or scaffolded baseline tools may be descriptor-declared as disabled and non-exposed without implying runtime capability.

**Why this priority**: This is the first `TS-01` milestone item and is the prerequisite for route-filtered tool exposure. Without descriptors, downstream gateway admission and traceability cannot prove which capability and policy were active for a tool run.

**Independent Test**: Inspect the M2B.1 baseline inventory for `StockSymbolTool`, `TradingViewTool`, and `ReportingTool`; verify each has a model-safe capability descriptor, an internal policy descriptor, and a traceable descriptor version or integrity marker. Verify placeholder or scaffolded tools carry disabled and non-exposed status when not admitted to runtime. Execute the existing compatibility fixtures and confirm user-facing behavior remains unchanged except for safe metadata, warnings, or degraded-state fields.

**Acceptance Scenarios**:

1. **Given** the M2B.1 baseline names `StockSymbolTool`, `TradingViewTool`, and `ReportingTool`, **When** the tool inventory is inspected, **Then** each baseline tool has a capability descriptor and policy descriptor with a traceable version or integrity marker, and any placeholder or disabled tool is explicitly marked non-exposed.
2. **Given** a tool capability descriptor is exposed to the model, **When** its fields are inspected, **Then** it includes model-safe name, purpose, input shape, route coverage, output kind, and descriptor version, and excludes credentials, provider fallback rules, parser limits, and license-policy details.
3. **Given** an existing supported tool call is executed through the registry path, **When** M2B.1 descriptor support is enabled, **Then** the user-facing result remains backward-compatible and the run includes descriptor metadata for traceability.

---

### User Story 2 - Route-Filtered Tool Exposure Before Agent Invocation (Priority: P1)

An investor asks different kinds of stock questions, and the assistant should only see the tools that fit the classified route, enabled state, locale, feature flags, available context, and admitted risk class for that turn.

**Why this priority**: This is the core `TS-02` exposure requirement. Route filtering reduces irrelevant tool selection, limits accidental provider leakage, and prepares the system for later Vietnam-market and reporting tools without changing the agent runtime model.

**Independent Test**: Run route fixtures for the current static `StockQueryRoute` values: `price_check`, `technical_analysis`, `fundamentals`, `market_watch`, `portfolio`, `news_analysis`, `ideas`, and `general_chat`. For each fixture, verify the model-visible surface contains only expected existing tool families, hides disabled or unrelated tools, and never exposes provider adapters as standalone model-visible tools.

**Acceptance Scenarios**:

1. **Given** a query is classified as a price or symbol lookup route, **When** the model-visible tool surface is built, **Then** only route-eligible, enabled, policy-admitted existing tool capabilities are exposed.
2. **Given** a query is classified to a route with no admitted tool for the M2B.1 baseline, **When** the tool surface is built, **Then** no scaffolded or unrelated tool is exposed as a substitute and the assistant can proceed with no model-visible tool for that route.
3. **Given** a tool is disabled, internal-only, above the admitted risk class, or blocked by feature flag, **When** the tool surface is built, **Then** that tool is not visible to the model and the filtering reason is available in trace metadata.

---

### User Story 3 - Gateway Admission Blocks Unsafe Tool Calls (Priority: P1)

An agent maintainer needs tool execution to pass through a thin admission boundary that validates the selected tool, route match, arguments, risk class, licensing posture, provider or cache state where applicable, and timeout budget before any registry-backed execution happens.

**Why this priority**: Admission is the safety half of `TS-02`. Route filtering controls what the model can see, but execution-time admission handles malformed, stale, drifted, or adversarial calls that still reach the tool boundary.

**Independent Test**: Submit fixture calls with invalid arguments, disallowed route-tool combinations, blocked risk classes, license-unclear posture, unsupported provider or cache state where applicable, and descriptor drift. Verify each disallowed call returns a machine-detectable degraded state, does not execute the underlying tool, and records the admission outcome.

**Acceptance Scenarios**:

1. **Given** the model selects a tool that is not admitted for the classified route, **When** gateway admission evaluates the call, **Then** the call is denied and returned as a degraded state without executing the tool.
2. **Given** the model selects an admitted tool but supplies invalid arguments, **When** gateway admission evaluates the call, **Then** validation fails closed and the response can disclose the limitation without exposing internals.
3. **Given** a descriptor version or integrity marker does not match the reviewed descriptor source, **When** the tool is considered for exposure or execution, **Then** the tool is blocked or degraded and trace metadata identifies the descriptor integrity failure.

---

### User Story 4 - Runtime Compatibility and Auditability (Priority: P1)

An operator needs the M2B.1 baseline to preserve the current ReAct execution model while adding enough trace evidence to audit exposed tools, selected tools, descriptor versions, admission outcomes, cache and freshness status where available, warnings, and degraded states.

**Why this priority**: The milestone gate explicitly requires descriptors, route filtering, and degraded-state admission to be testable before new provider-backed model-visible tools are added. Runtime preservation prevents this baseline from becoming a broader agent rewrite.

**Independent Test**: Compare representative pre-M2B.1 and M2B.1 tool interactions at the shared agent/tool boundary. Verify the same registry-backed tool path is used, no second agent runtime or external gateway service is introduced, Socket.IO lifecycle parity is not required for this milestone, and at least 95% of governed tool runs include required and conditionally applicable internal trace fields with no sensitive user data or secrets.

**Acceptance Scenarios**:

1. **Given** M2B.1 is enabled, **When** the assistant executes an allowed existing tool call, **Then** execution remains registry-backed and does not require a second agent runtime or separate gateway service.
2. **Given** a governed tool run completes, **When** trace metadata is inspected, **Then** it includes route, exposed tools, selected tool, descriptor version or hash, admission outcome, latency, and any applicable selected-adapter, cache, freshness, warning, or degraded-state fields without requiring a full future execution envelope.
3. **Given** trace metadata is captured for a tool run, **When** the trace is inspected for sensitive content, **Then** secrets, credentials, and sensitive user data are absent.
4. **Given** a gateway denial or degraded-state admission result exists, **When** the response is emitted through a public API or streaming surface, **Then** only safe status or warning metadata may be exposed and internal gateway trace details remain internal.

### Edge Cases

- Missing capability or policy descriptor for an existing model-visible tool fails the descriptor inventory check and blocks route exposure for that tool.
- Missing capability or policy descriptor for a baseline placeholder or scaffolded tool, including `TradingViewTool`, fails the descriptor inventory check even when that tool remains disabled or non-exposed.
- Malformed descriptor fields, duplicate tool names, unknown route coverage, or missing descriptor integrity markers fail closed into a degraded or non-exposed state.
- Disabled tools and tools outside the admitted route or risk class remain hidden even if they are still registered.
- Routes with no admitted M2B.1 tool expose no tool surface rather than exposing scaffolded tools to manufacture a degraded response.
- Ambiguous or general-chat routes receive only the baseline-safe tool surface for that route; unrelated financial tools are not exposed as a fallback shortcut.
- Provider adapter names, credentials, license posture, parser limits, and provider fallback policy must not appear in model-visible descriptors.
- Descriptor tampering, unapproved remote descriptors, and descriptor drift must not be exposed or executed without local admission and traceable descriptor identity.
- Cache or provider health information may influence admission, but cache entries must not become market-data authority or conversation memory.
- Public REST, SSE, and WebSocket surfaces must not expose internal gateway trace details unless a later public contract change is explicitly planned.
- Socket.IO lifecycle parity remains a documented architecture gap and is not closed by M2B.1 shared agent/tool boundary verification.
- No new provider-backed model-visible tools, generic web fetch, symbol-store mutation, report persistence, full `ToolExecutionEnvelope` or `ToolContextPack` backbone, or remote/MCP-style admission is enabled by this milestone.

## Requirements *(mandatory)*

### Functional Requirements

- **M2B1-FR-001**: The system MUST expose the current model-visible tools through the target `AgentTool` capability terminology while preserving existing cache-aware and registry-backed behavior. Placeholder or scaffolded baseline tools may remain disabled and non-exposed. *(FR-2.4.1, FR-2.4.6, AC-9.1)*
- **M2B1-FR-002**: Each M2B.1 baseline tool MUST declare a model-safe `ToolCapabilityDescriptor` with name, purpose, input schema, route coverage, output kind, examples where useful, locale coverage where applicable, descriptor version, and enabled or non-exposed status. *(FR-2.4.2, IR-3.1)*
- **M2B1-FR-003**: Model-visible capability descriptors MUST NOT expose credentials, provider fallback rules, parser limits, internal license policy, credential ownership, or provider-specific implementation details. *(FR-2.4.2, AC-9.1)*
- **M2B1-FR-004**: Each M2B.1 baseline tool MUST declare an internal `ToolPolicyDescriptor` covering risk class, license mode, freshness policy, cache policy, timeout budget, credential or scope owner, mutation policy where applicable, required metadata, enabled environments, exposure status, and descriptor integrity marker. *(IR-3.2, NFR-6.2.6)*
- **M2B1-FR-005**: The system MUST build the model-visible tool surface before agent invocation from the classified route, locale, enabled state, feature flags, allowed user/session context, capability descriptors, and admitted risk class, and MUST record route-filter evidence sufficient to compare the filtered surface against the unfiltered baseline tool inventory. *(FR-2.4.3, FR-4.2.1, AC-9.2)*
- **M2B1-FR-006**: The route-filtered surface MUST hide unrelated tools, disabled tools, internal diagnostics, blocked tools, and provider adapters that are not model-visible tools. *(FR-2.4.3, AC-9.2)*
- **M2B1-FR-015**: Routes with no admitted M2B.1 tool MUST expose no model-visible tool rather than exposing a scaffolded or unrelated substitute. The filtering reason MUST be available in internal trace metadata. *(FR-2.4.3, AC-9.2)*
- **M2B1-FR-007**: The gateway admission boundary MUST validate selected tool, route-tool match, input arguments, risk class, license posture, freshness expectation, provider or cache state when applicable, descriptor integrity, and timeout budget before execution. *(FR-2.4.4, AC-9.3)*
- **M2B1-FR-008**: Disallowed tool calls MUST be blocked or returned as a machine-detectable degraded state and MUST NOT silently execute or silently fall back to an unrelated tool. *(FR-2.4.4, AC-9.3)*
- **M2B1-FR-009**: Descriptor version, hash, or equivalent integrity marker MUST be recorded for both model-visible exposure and execution-time admission. *(FR-2.4.5, NFR-6.2.6, AC-9.4)*
- **M2B1-FR-010**: Descriptor tampering, unapproved remote descriptors, and descriptor drift MUST fail closed by blocking exposure or execution and recording the degraded-state reason. *(FR-2.4.5, AC-9.4)*
- **M2B1-FR-011**: Allowed tool calls MUST continue through the current registry-backed ReAct tool execution path and MUST NOT require a second agent runtime or separate gateway service. *(FR-2.4.6)*
- **M2B1-FR-012**: Internal governed tool traces MUST include route, exposed tools, selected tool, descriptor version or hash, admission outcome, and latency; selected adapter, cache status, freshness, warning, and degraded-state reason MUST be populated when applicable or recorded as safely not applicable. *(NFR-5.2.12)*
- **M2B1-FR-013**: Tool trace metadata MUST exclude secrets, credentials, and sensitive user data. *(NFR-4.2.3)*
- **M2B1-FR-014**: The M2B.1 baseline MUST NOT add new provider-backed model-visible tools, enable generic web fetch, enable symbol-store mutations, persist reports or artifacts, or admit remote/MCP-style tools. Those remain behind later Phase 2B gates. *(Roadmap M2B.1 gate)*
- **M2B1-FR-016**: M2B.1 verification MUST cover the shared agent/tool boundary and MUST NOT be treated as closing Socket.IO lifecycle parity or other transport-specific architecture gaps. *(Roadmap M2B.1 gate)*
- **M2B1-FR-017**: Public API and streaming response surfaces MAY expose only safe degraded-state status or warning metadata from gateway admission; internal gateway trace details MUST remain internal unless a later public contract change is planned. *(NFR-5.2.12)*
- **M2B1-FR-018**: Feature-local planning contracts MAY define placeholders for descriptor, route exposure, gateway admission, and trace metadata, but MUST NOT implement the full `ToolExecutionEnvelope`, normalized output, or `ToolContextPack` backbone in M2B.1. *(Roadmap M2B.1 gate)*

### Key Entities

- **Baseline Tool Inventory**: The M2B.1 named inventory of `StockSymbolTool`, `TradingViewTool`, and `ReportingTool`, including enabled tools, disabled tools, and placeholder or scaffolded tools that require descriptors before any route exposure.
- **AgentTool Capability**: A repo-owned agent-callable tool capability that preserves existing cache-aware execution behavior while exposing descriptor and health metadata for gateway use.
- **ToolCapabilityDescriptor**: Model-visible descriptor for a tool capability. It contains safe public capability information and excludes sensitive internal policy or provider details.
- **ToolPolicyDescriptor**: Internal descriptor for gateway admission. It contains risk, license, freshness, cache, timeout, metadata, environment, credential ownership, and integrity controls.
- **Route-Filtered Tool Surface**: The compact set of tools visible to the model for one turn after route, enablement, context, feature flag, and risk filtering.
- **Gateway Admission Decision**: The allowed, blocked, or degraded outcome produced before a selected tool call is executed.
- **Degraded State**: A machine-detectable non-success state for blocked, invalid, drifted, stale, license-unclear, provider-unavailable, or timeout-constrained tool outcomes.
- **Tool Trace Record**: Audit metadata for exposure and execution, including route, exposed tools, selected tool, descriptor identity, admission result, cache/freshness state, warnings, and degraded-state reason.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of the existing M2B.1 tool inventory (`StockSymbolTool`, `TradingViewTool`, and `ReportingTool`) has both a model-safe capability descriptor and an internal policy descriptor; placeholder or scaffolded tools are explicitly marked disabled and non-exposed.
- **SC-002**: 100% of existing compatibility fixtures for currently supported tool calls pass with no user-facing behavior regression except added metadata, warnings, or degraded-state disclosures.
- **SC-003**: Route-filter fixture coverage shows 100% of tested routes expose only expected existing tool families, hide unrelated, disabled, internal-only, and risk-blocked tools, and demonstrate at least 20% fewer model-visible tool candidates than the unfiltered M2B.1 baseline inventory where the baseline has more than one candidate.
- **SC-004**: 100% of disallowed call fixtures return a degraded state or blocked admission outcome without executing the underlying tool.
- **SC-005**: 100% of descriptor drift or tampering fixtures block exposure or execution and include descriptor identity plus failure reason in trace metadata.
- **SC-006**: At least 95% of governed tool runs include required internal M2B.1 trace fields from `NFR-5.2.12`, with conditional fields populated or safely marked not applicable.
- **SC-007**: 0 trace fixtures contain secrets, credentials, raw provider policy details, or sensitive user data.
- **SC-008**: Route-filtered surface construction and gateway admission add no more than 50 ms to representative non-provider tool-selection flows.
- **SC-009**: 100% of public API and streaming response fixtures expose no internal gateway trace details while still allowing safe degraded-state status or warning metadata.
- **SC-010**: Planning evidence keeps M2B.1 scoped to `TS-01` and `TS-02`, with any full `ToolExecutionEnvelope`, normalized output, `ToolContextPack`, provider-policy, or transport-parity work deferred to later milestones.

## Assumptions

- The M2B.1 existing tool inventory is `StockSymbolTool`, `TradingViewTool`, and `ReportingTool`, matching the Phase 2B roadmap baseline.
- `TradingViewTool` is included in descriptor inventory even if it remains placeholder code, disabled, unregistered, or non-exposed at runtime.
- The current static route taxonomy remains authoritative for this milestone; dynamic route discovery is not part of M2B.1.
- `TradingViewTool` and `ReportingTool` may be partially implemented or scaffolded; descriptors can represent current enabled or disabled status without implying full future capability.
- Routes without an admitted M2B.1 tool expose no tool surface; scaffolded tools are not exposed merely to produce degraded responses.
- Locale, user/session context, and feature flags are used only where available in the current request context. Missing optional context must not broaden tool exposure.
- A degraded-state shape sufficient for admission denial is in scope; the full normalized output and `ToolContextPack` backbone belongs to later Phase 2B milestones.
- Public API and streaming contracts do not change unless implementation adds or changes user-visible response metadata; gateway traces remain internal by default.
- Shared agent/tool boundary verification is sufficient for M2B.1; Socket.IO lifecycle parity remains a separate architecture gap.
- Later scopes include provider policy, Vietnam-market providers, internal symbol-store evolution, normalized outputs, reporting from `ToolContextPack`, generic web evidence, mutation receipts, and optional remote/MCP-style tool admission.
