# Feature Specification: Vietnam Market and Visualization Coverage - M2B.3

**Feature Directory**: `specs/tool-system-m2b.3`

**Feature Branch**: `feature/tool-system-m2b.3`

**Created**: 2026-07-07

**Status**: Planned

**Input**: User requested a follow-up feature specification for milestone `M2B.3`, continuing after verified `M2B.1` and `M2B.2`, scoped to the Phase 2B roadmap, SRS, traceability, architecture, and tool-system research documents.

## Governance Context *(mandatory)*

**Source Requirements**:
- `FR-2.6.2` through `FR-2.6.6` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-26-vietnam-market-tool-coverage) for Vietnam quote/history, fundamentals, breadth/flow, disclosure/corporate-action, and Vietnamese/mixed-language routing coverage.
- `FR-2.7.3` through `FR-2.7.5` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-27-provider-selection-and-source-attribution) for Vietnam-first provider priority, market-fact attribution, and cache freshness metadata.
- `FR-2.8.1` through `FR-2.8.4` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-28-tradingview-visualization-tooling) for TradingView visualization provenance, chart/widget payloads, symbol validation, and non-evidence classification.
- `FR-4.1.3` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#fr-41-core-semantic-routing) for meaning-based route classification accuracy across Vietnamese and mixed-language stock-market requests.
- `NFR-2.3.5` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#nfr-23-data-integrity) for source timestamp, retrieved timestamp, freshness category, provider/source, degraded warning, and stale-cache metadata.
- `NFR-5.2.13` and `NFR-5.3.8` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#nfr-52-tracing) for provider-backed tool trace metadata and source-attribution observability coverage.
- `NFR-6.1.3` and `NFR-6.1.4` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#nfr-61-code-quality) for agent-core and tool-layer coverage gates on touched M2B.3 surfaces.
- `CON-7` and `CON-9` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#4-constraints) for TradingView non-evidence status and source-attributed market facts.
- `AC-9.8`, `AC-9.9`, `AC-9.11`, and `AC-9.16` in [SOFTWARE_REQUIREMENTS_SPECIFICATION.md](../../docs/domains/agent/SOFTWARE_REQUIREMENTS_SPECIFICATION.md#ac-9-tool-system-architecture-and-vietnam-market-integration) for market-data answer attribution, fallback/degraded behavior, TradingView classification, and Vietnamese/mixed-language tool-family routing.

**Authoritative Inputs**:
- [PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#phase-2b-enhanced-tool-system-feature-implementations), especially [Milestone Gates](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#milestone-gates), [2B.5 Concrete Market Data and Visualization Tools](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#2b5-concrete-market-data-and-visualization-tools), and [2B.9 Verification and Quality Gates](../../docs/domains/agent/PHASE_2_AGENT_ENHANCEMENT_ROADMAP.md#2b9-verification-and-quality-gates).
- [ARCHITECTURE_DESIGN.md](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#485a-tool-gateway-and-evidence-admission-boundary), [section 4.3.4](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#434-tool-provider-selection-and-fallback-view), and [section 7](../../docs/domains/agent/ARCHITECTURE_DESIGN.md#7-architecture-considerations-and-planned-evolution) for target tool/provider boundaries, evidence admission, TradingView visualization provenance, and current-vs-target status discipline.
- [TECHNICAL_DESIGN.md](../../docs/domains/agent/TECHNICAL_DESIGN.md#322-target-phase-2b-runtime-flow), [section 3.2.3](../../docs/domains/agent/TECHNICAL_DESIGN.md#323-tool-and-adapter-responsibility-split), [section 3.2.4](../../docs/domains/agent/TECHNICAL_DESIGN.md#324-target-tool-contract-and-failure-realization), and [section 3.2.5](../../docs/domains/agent/TECHNICAL_DESIGN.md#325-tool-data-model-and-persistent-storage-realization) for provider-hidden execution, normalized outputs, freshness metadata, and request-scoped context boundaries.
- [TOOLS_RESEARCH_AND_PROPOSAL.md](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#7-target-tool-system-architecture), especially [Technical Design Proposal](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#8-technical-design-proposal), [Tool Data Architecture and Integrity Design](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#9-tool-data-architecture-and-integrity-design), and [Implementation Roadmap](../../docs/domains/agent/TOOLS_RESEARCH_AND_PROPOSAL.md#12-implementation-roadmap) for tool gateway, provider adapter, normalized context, and source-integrity design.
- [.specify/memory/constitution.md](../../.specify/memory/constitution.md#architecture-currenttarget-status-semantics), [.specify/memory/architecture.md](../../.specify/memory/architecture.md#current-target-planned-and-gated-labels), and the five `.specify/memory/architecture-*-view.md` files for current/target labels, provider-hidden tool architecture, request-scoped context, and visualization provenance boundaries.
- [.github/instructions/documentation-and-specification.instructions.md](../../.github/instructions/documentation-and-specification.instructions.md), [.github/instructions/architecture.instructions.md](../../.github/instructions/architecture.instructions.md), [.github/instructions/backend-python.instructions.md](../../.github/instructions/backend-python.instructions.md), [.github/instructions/langchain-python.instructions.md](../../.github/instructions/langchain-python.instructions.md), and [.github/instructions/testing.instructions.md](../../.github/instructions/testing.instructions.md) for repository documentation, architecture, backend, LangChain, and testing conventions.
- [spec-kit HOW-TO.md](../../docs/spec-driven%20development%20%28SDD%29/spec-kit%20HOW-TO.md) and [project-documentation-and-specification-methodology.md](../../docs/study-hub/project-documentation-and-specification-methodology.md) for repository-local Spec Kit lifecycle, authority, traceability, and long-lived versus delivery-scoped document boundaries.
- Verified predecessor evidence in [specs/tool-system-implementation-m2b.1/spec.md](../tool-system-implementation-m2b.1/spec.md), [specs/tool-system-implementation-m2b.1/.verify-done](../tool-system-implementation-m2b.1/.verify-done), [specs/tool-system-m2b.2/spec.md](../tool-system-m2b.2/spec.md), and [specs/tool-system-m2b.2/.verify-done](../tool-system-m2b.2/.verify-done). M2B.1 provides the descriptor, route surface, gateway admission, and registry-backed execution baseline; M2B.2 provides the symbol-store, provider-policy, execution-envelope, normalized-output, `ToolContextPack`, and degraded-state backbone.

**Traceability Target**: Add a new `tool-system-m2b.3` feature entry to `specs/spec-traceability.yaml` after specification acceptance. Expected mapped SRS items are `FR-2.6.2` through `FR-2.6.6`, `FR-2.7.3` through `FR-2.7.5`, `FR-2.8.1` through `FR-2.8.4`, `FR-4.1.3`, `NFR-2.3.5`, `NFR-5.2.13`, `NFR-5.3.8`, `NFR-6.1.3`, `NFR-6.1.4`, `CON-7`, `CON-9`, `AC-9.8`, `AC-9.9`, `AC-9.11`, and `AC-9.16`. `IR-3.8` remains deferred to generic web fetch work outside M2B.3 unless a later clarification explicitly changes scope.

**Sync Targets**: `specs/spec-traceability.yaml`, `specs/spec-sync-status.md`, and `docs/domains/agent/SRS_SPEC_TRACEABILITY.md` must be regenerated with `python scripts/sync_spec_status.py --gate` after this feature is added to the manifest or later promoted through lifecycle states. Long-lived architecture or technical design documents are sync targets only after implementation evidence proves current-state behavior that the long-lived docs should promote.

**Contract Impact**: No public REST, SSE, Socket.IO, or OpenAPI contract change is expected from this specification. Planning should define feature-local contracts for Vietnam market-data tool outputs, provider-backed market-fact attribution, cache freshness metadata, TradingView `VisualizationProvenance`, and Vietnamese/mixed-language route evaluation fixtures. Any later public response metadata change must be called out explicitly in `plan.md` before implementation.

**Lifecycle Status Rule**: Starts as `Draft`; promote through `Clarified`, `Planned`, `Implemented`, and `Verified` only after the matching Spec Kit phase evidence exists. M2B.3 verification must not promote generic web fetch, reporting persistence, remote or MCP-style admission, symbol-store writes, or production provider licensing posture beyond the approved M2B.3 scope.

## Clarifications

### Session 2026-07-07

- Q: Should `TS-07` breadth, flow, disclosure, and corporate-action coverage carry the same delivery priority as quote/history and fundamentals? -> A: No; keep `TS-07` in M2B.3 scope but represent it as a P2 independently testable slice while quote/history, fundamentals, attribution, TradingView authority, and route evaluation remain P1 gates.
- Q: What exact route-classification threshold applies to Vietnamese and mixed-language M2B.3 fixtures? -> A: Use the SRS `FR-4.1.3` threshold of at least 85% meaning-based classification accuracy, with route-tool precision and recall targets defined before verification.
- Q: What identity must market facts bind to before answer, cache, trace, or retained-derivative use? -> A: Market facts must bind to canonical symbol identity from the M2B.2 boundary: symbol plus exchange and currency where applicable; ambiguous ticker-only identity must disambiguate or degrade.
- Q: Which provider candidates constrain Vietnam-first planning without implying production approval? -> A: Use the roadmap candidate set where terms and licensing allow: `vnstock`, Vietstock, CafeF, FiinGroup/FiinTrade/FiinQuant, VSDC, HOSE, and HNX; each still needs provider-posture review before production evidence use.
- Q: How should provider rate limits, throttling, or timeout-budget failures be treated? -> A: They follow deterministic fallback or explicit degraded-state behavior; they must not produce silent stale, anonymous, or license-unclear evidence.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Vietnam Quote and Price History Evidence (Priority: P1)

An investor asks for Vietnam stock quotes, historical prices, OHLCV data, or deterministic indicators, and the assistant should answer using approved market-data tool families instead of `StockSymbolTool`, raw provider payloads, or TradingView values.

**Why this priority**: `TS-06` starts with concrete Vietnam quote/history coverage, and all later fundamentals, visualization, and report workflows depend on trustworthy market-price evidence.

**Independent Test**: Run supported symbol fixtures such as `FPT`, `HOSE:FPT`, `HNX:SHS`, and `UPCOM:BSR`; verify the request routes to the Vietnam market-data tool family, uses Vietnam-first provider policy where admissible, emits normalized evidence facts, includes source and freshness metadata, and degrades when no approved source is available.

**Acceptance Scenarios**:

1. **Given** a supported Vietnam equity or index symbol, **When** the user requests quote or price history, **Then** the tool result includes price or OHLCV data, exchange, VND currency where applicable, provider/source identity, URL or reference, retrieved timestamp, source timestamp where available, freshness category, and warnings.
2. **Given** a deterministic technical indicator is requested, **When** approved price-history input is available, **Then** the indicator is computed from that input and preserves the input source lineage instead of treating the indicator as an unsourced market fact.
3. **Given** local providers are unavailable, stale, license-blocked, parser-limited, or missing required fields, **When** the quote/history tool is evaluated, **Then** provider policy either selects an admitted fallback or returns a degraded state with the reason and safe user-facing warning.

---

### User Story 2 - Vietnam Fundamentals Evidence (Priority: P1)

An investor asks for company fundamentals or statements, and the assistant should route those questions to the right Vietnam market-data tool family with source attribution, period metadata, license posture, and degraded-state handling.

**Why this priority**: Fundamentals are part of the P1 `TS-06` milestone and must be separated from symbol lookup, generic web fetch, and visualization-only output before broader analysis tools can rely on them.

**Independent Test**: Run fixtures for fundamentals and statements; verify each request routes to the intended tool family, returns normalized outputs with required source metadata, and does not silently scrape or infer missing facts.

**Acceptance Scenarios**:

1. **Given** a user requests fundamentals or statements for a Vietnam-listed company, **When** an approved source is available, **Then** the output includes period, provider/source, URL or reference, retrieved timestamp, published or effective timestamp where available, freshness, license posture, and missing-field warnings.
2. **Given** a requested fundamental field is missing, stale, parser-limited, or license-blocked, **When** the tool responds, **Then** the output includes a machine-detectable degraded state or missing-field warning instead of fabricating the field.

---

### User Story 3 - Vietnam Breadth, Flow, Disclosures, and Corporate Actions (Priority: P2)

An investor asks for market breadth, foreign or market flow, disclosures, official notices, dividends, rights, splits, listing changes, or other corporate-action evidence, and the assistant should route those questions to approved Vietnam market-data tool families when source posture allows.

**Why this priority**: These requirements are part of `TS-07` and complete M2B.3 market coverage, but the SRS marks breadth, flow, disclosures, and corporate actions as P2 relative to the P1 quote/history, fundamentals, attribution, and route-evaluation gates.

**Independent Test**: Run breadth, flow, disclosure, and corporate-action fixtures; verify each request routes to the intended tool family, returns normalized outputs with required source metadata, and degrades when no approved or parser-safe source is available.

**Acceptance Scenarios**:

1. **Given** a user requests market breadth or flow, **When** source data is available, **Then** the output includes time window, exchange or market, provider/source, freshness, and degraded-state warnings where applicable.
2. **Given** a user requests disclosures or corporate actions, **When** an approved source is available, **Then** the output includes event type, source reference, published timestamp, effective timestamp where available, provider class, parser warnings, and normalized evidence classification.
3. **Given** no approved breadth, flow, disclosure, or corporate-action source is available, **When** the request is evaluated, **Then** the system returns a degraded state instead of falling back to generic web fetch or unsupported inference.

---

### User Story 4 - TradingView Visualization Provenance (Priority: P1)

An investor asks for charts, widgets, symbol validation, ticker tape, heatmaps, screeners, or TradingView deep links, and the assistant should return visualization provenance that supports inspection without using TradingView values as canonical evidence.

**Why this priority**: The roadmap explicitly permits TradingView visualization coverage while the SRS and architecture prohibit treating TradingView visualization data as default canonical market evidence.

**Independent Test**: Run TradingView chart, widget, deep-link, symbol-validation, ticker-tape, heatmap, and screener fixtures; verify all outputs are classified as `VisualizationProvenance`, include provenance metadata, and never become evidence facts for numeric answers unless a future approved policy says otherwise.

**Acceptance Scenarios**:

1. **Given** a user asks for a chart or TradingView widget, **When** the visualization tool responds, **Then** the output includes symbol, interval or view configuration, widget or deep-link payload, generated timestamp, validation status, and `VisualizationProvenance` classification.
2. **Given** a TradingView payload includes numeric market values, **When** the assistant composes a factual answer, **Then** those values are not used as canonical evidence and the answer relies on approved market-data evidence or reports a degraded state.
3. **Given** a requested TradingView symbol or visualization is unsupported, **When** validation fails, **Then** the response provides a degraded visualization state without fabricating a chart or market fact.

---

### User Story 5 - Vietnamese and Mixed-Language Route Evaluation (Priority: P1)

An investor asks Vietnam-market questions in Vietnamese, English, or mixed language, and the assistant should classify the intent into price, chart, fundamentals, disclosures, breadth, flow, or report-related tool families with measurable route accuracy.

**Why this priority**: `TS-12`, `FR-2.6.6`, `FR-4.1.3`, and `AC-9.16` require concrete route fixtures before adding or verifying the new model-visible market-data and visualization tools.

**Independent Test**: Run Vietnamese and mixed-language fixtures covering price, chart, fundamentals, disclosures, breadth, flow, and report-style queries; verify intended route/tool-family selection, route-tool precision/recall targets, and safe fallback for ambiguous or unsupported utterances.

**Acceptance Scenarios**:

1. **Given** a Vietnamese or mixed-language prompt asks for price, chart, fundamentals, disclosures, breadth, flow, or report-like output, **When** semantic routing runs, **Then** the route and tool family match the expected intent for at least 85% meaning-based classification accuracy.
2. **Given** a route fixture asks for report-style output, **When** M2B.3 handles the request, **Then** the request is classified to the report family only as a route/evaluation fixture; full reporting composition and persistence remain deferred unless a later feature enables them.
3. **Given** a fixture is ambiguous between quote, chart, and fundamentals, **When** route confidence is insufficient, **Then** the tool surface degrades or asks for disambiguation rather than exposing unrelated tool families.

---

### User Story 6 - Attribution, Freshness, Cache, and Trace Coverage (Priority: P1)

A compliance reviewer needs market-data answers, cache hits, tool traces, and generated artifacts to preserve source attribution, freshness, provider posture, and warnings without leaking internal provider policy or raw payloads.

**Why this priority**: `CON-9`, `AC-9.8`, `AC-9.9`, `NFR-2.3.5`, `NFR-5.2.13`, and `NFR-5.3.8` make attribution and observability part of the market-data feature, not an optional later cleanup.

**Independent Test**: Run provider-backed success, fallback, stale-cache, outage, missing-field, blocked-license, and unsupported-source fixtures; verify answer metadata, trace metadata, cache freshness metadata, and observability counters cover required fields while public surfaces expose only safe warnings.

**Acceptance Scenarios**:

1. **Given** a market-data answer includes facts, **When** the answer or retained derivative is inspected, **Then** each market fact has provider/source, URL or reference, retrieved timestamp, published or effective timestamp where available, exchange, currency, freshness, license posture, and warnings where applicable.
2. **Given** a result comes from cache, **When** freshness metadata is inspected, **Then** the cache record includes provider/source, source timestamp where available, retrieved timestamp, freshness category, TTL or expiry, warnings, and degraded-state reason where applicable.
3. **Given** a provider-backed tool call is traced, **When** internal trace metadata is inspected, **Then** it includes provider class, license mode, source reference, retrieved timestamp, source/published/effective timestamp where available, selected adapter, fallback or degraded-state reason, and safe omission of credentials and raw payloads.

### Edge Cases

- A Vietnam ticker is ambiguous across exchanges, aliases, market segments, or language-specific forms.
- A market-data fact cannot be bound to canonical symbol identity with symbol, exchange, and currency where applicable.
- A requested symbol is supported by the symbol store but no approved market-data provider is available.
- Vietnam-native or official providers are blocked by license posture, unavailable, stale, parser-limited, missing fields, or outside credentials scope.
- A provider is rate-limited, throttled, or exceeds the admitted timeout budget.
- Yahoo or Alpha Vantage is selected for a Vietnam-market fact even though a local approved provider is available.
- A cache hit has missing source timestamp, missing retrieved timestamp, unknown freshness, expired TTL, or stale data.
- A provider returns values without exchange, currency, provider/source, URL/reference, or timestamp metadata.
- A fundamental, disclosure, or corporate-action source has missing period, missing effective date, inconsistent parser output, or no redistribution posture.
- TradingView returns numeric values, indicators, heatmaps, or screener rows that could be mistaken for canonical evidence.
- A TradingView symbol, interval, widget type, heatmap, or screener is unsupported or fails validation.
- A Vietnamese or mixed-language prompt is ambiguous between price, chart, fundamentals, disclosures, breadth, flow, and report routes.
- A user asks for report generation, artifact persistence, generic web evidence, or remote tool admission during this feature.
- Public response metadata attempts to expose internal provider order, credentials, parser limits, raw traces, or raw provider payloads.

## Requirements *(mandatory)*

### Functional Requirements

- **M2B3-FR-001**: The feature MUST build on verified M2B.1 and M2B.2 behavior, including descriptors, route-filtered exposure, gateway admission, provider-hidden policy, execution envelopes, normalized outputs, request-scoped `ToolContextPack`, and degraded-state handling. *(M2B.1/M2B.2 verified baseline)*
- **M2B3-FR-002**: Vietnam quote and price-history requests MUST be handled by approved market-data tool families separate from `StockSymbolTool`. *(FR-2.6.2, FR-2.11.1 carry-forward boundary)*
- **M2B3-FR-003**: Quote and price-history outputs MUST include price or OHLCV values, exchange, currency, provider/source, URL or reference, retrieved timestamp, source timestamp where available, freshness category, and warnings. *(FR-2.6.2, FR-2.7.4, AC-9.8)*
- **M2B3-FR-004**: Vietnam-market provider policy MUST prefer Vietnam-native, official, or licensed sources where available, including roadmap candidates such as `vnstock`, Vietstock, CafeF, FiinGroup/FiinTrade/FiinQuant, VSDC, HOSE, and HNX where terms and licensing allow, and MUST restrict Yahoo, Alpha Vantage, or international sources to fallback or cross-market comparison roles. *(FR-2.7.3)*
- **M2B3-FR-005**: If no approved provider can satisfy a market-data request because of availability, freshness, missing fields, license posture, credentials, or parser limits, the system MUST select an admitted fallback or return a machine-detectable degraded state with a safe warning. *(AC-9.9, NFR-2.3.5)*
- **M2B3-FR-006**: Deterministic technical indicators in scope MUST be computed only from approved price-history inputs and MUST preserve input source lineage, timestamp, freshness, exchange, currency, and warnings. *(FR-2.6.2, CON-9)*
- **M2B3-FR-007**: Fundamentals and financial-statement outputs MUST include period, provider/source, URL or reference, retrieved timestamp, published or effective timestamp where available, freshness, license posture, and missing-field warnings. *(FR-2.6.3, FR-2.7.4, AC-9.8)*
- **M2B3-FR-008**: Breadth and flow outputs MUST include time window, exchange or market, provider/source, retrieved timestamp, freshness, and degraded-state warnings where applicable. *(FR-2.6.4, AC-9.8, AC-9.9)*
- **M2B3-FR-009**: Disclosure and corporate-action outputs MUST include event type, source URL or reference, published timestamp, effective timestamp where available, provider class, parser warnings, freshness, and license posture. *(FR-2.6.5, FR-2.7.4)*
- **M2B3-FR-010**: Every market fact used in answers, retained derivatives, traces, artifacts, snapshots, or report inputs MUST preserve provider/source, URL or reference, retrieved timestamp, published or effective timestamp where available, exchange, currency, freshness, license posture, and warnings or degraded-state reason where applicable. *(FR-2.7.4, CON-9, AC-9.8)*
- **M2B3-FR-011**: Cached market-data results MUST preserve provider/source, source timestamp where available, retrieved timestamp, freshness category, TTL or expiry, warnings, and degraded-state reason where applicable. *(FR-2.7.5, NFR-2.3.5)*
- **M2B3-FR-012**: Provider-backed tool traces MUST include provider class, license mode, source URL or reference, retrieved timestamp, source/published/effective timestamp where available, selected adapter, fallback or degraded-state reason, and safe omission of credentials, secrets, parser internals, and raw payloads. *(NFR-5.2.13)*
- **M2B3-FR-013**: The feature MUST track source-attribution coverage for market-data answers and report inputs, including counts for complete attribution, degraded no-source outcomes, stale-cache outcomes, and provider/license blocked outcomes. *(NFR-5.3.8)*
- **M2B3-FR-014**: TradingView chart, widget, deep-link, ticker-tape, heatmap, screener, and symbol-validation outputs MUST be classified as `VisualizationProvenance`. *(FR-2.8.1, FR-2.8.2, AC-9.11)*
- **M2B3-FR-015**: TradingView visualization payloads MUST include symbol, exchange or market where available, interval or view configuration, widget or deep-link payload, generated timestamp, validation status, warnings, and provenance metadata. *(FR-2.8.2, FR-2.8.3)*
- **M2B3-FR-016**: TradingView values MUST NOT be treated as canonical evidence for market facts by default; factual answers MUST use approved market-data evidence or return degraded states when no admitted evidence exists. *(FR-2.8.4, CON-7, AC-9.11)*
- **M2B3-FR-017**: TradingView symbol validation MUST accept supported Vietnam and international symbols only when validation succeeds and MUST return degraded visualization states for unsupported or ambiguous symbols. *(FR-2.8.3)*
- **M2B3-FR-018**: Vietnamese and mixed-language prompts for price, chart, fundamentals, disclosures, breadth, flow, and report-like requests MUST route to the expected tool family or degrade/disambiguate when confidence is insufficient. *(FR-2.6.6, AC-9.16)*
- **M2B3-FR-019**: Route evaluation for M2B.3 MUST measure meaning-based classification accuracy against the SRS threshold of at least 85% and define route-tool exposure precision and recall targets before new market-data or visualization tools are considered verified. *(FR-4.1.3, AC-9.16, Roadmap 2B.9)*
- **M2B3-FR-020**: Market-data and visualization tools MUST remain behind M2B.1 gateway admission and M2B.2 provider/normalization policy; provider adapters MUST NOT be exposed as flat model-visible tools. *(M2B.1/M2B.2 baseline, architecture boundary)*
- **M2B3-FR-021**: Public REST, SSE, Socket.IO, and OpenAPI contracts MUST remain unchanged unless the plan explicitly introduces a public contract change and names the sync path. *(Contract boundary)*
- **M2B3-FR-022**: M2B.3 MUST NOT enable generic web fetch, report generation or persistence, remote/MCP-style tool admission, production symbol-store writes, or production provider enablement without documented license/ToS posture and follow-up governance. *(Roadmap M2B.3 gate and deferred scope)*
- **M2B3-FR-023**: Market-data evidence MUST bind to canonical symbol identity from the M2B.2 boundary, including symbol plus exchange and currency where applicable; ambiguous ticker-only identity MUST disambiguate or degrade before any market fact is used in an answer, cache entry, trace, or retained derivative. *(FR-2.6.1 carry-forward, FR-2.7.4, CON-9)*
- **M2B3-FR-024**: Provider rate limits, throttling, and timeout-budget failures MUST follow deterministic fallback or explicit degraded-state behavior and MUST NOT produce silent stale, anonymous, or license-unclear evidence. *(AC-9.9, NFR-2.3.5)*
- **M2B3-FR-025**: Verification evidence MUST include agent-core touched-surface coverage at or above 80% for route/agent code affected by M2B.3 and tool-layer coverage at or above 70%, or record an explicit governed exception before lifecycle promotion. *(NFR-6.1.3, NFR-6.1.4)*

### Key Entities *(include if feature involves data)*

- **Vietnam Market Data Tool Family**: Model-visible capability family for quote/history, fundamentals, breadth/flow, disclosure/corporate-action, and deterministic indicator outputs backed by approved provider policy.
- **Market Provider Authority**: Internal provider classification and posture, including Vietnam-native, official exchange, licensed commercial, public-web, international fallback, visualization-only, research/prototype, and blocked/degraded.
- **Market Fact**: Normalized evidence fact used in answers or retained derivatives with symbol identity, value payload, exchange, currency, provider/source, timestamps, freshness, license posture, and warnings.
- **Price History Series**: Ordered OHLCV market-data evidence with source lineage, exchange, currency, source/retrieved timestamps, cache metadata, and freshness category.
- **Fundamental Evidence**: Normalized company fundamental or statement evidence with period, source reference, provider posture, missing-field warnings, and freshness metadata.
- **Breadth and Flow Evidence**: Market-wide or segment-wide breadth/flow evidence with time window, exchange or market, provider/source, freshness, and degraded-state handling.
- **Disclosure and Corporate Action Evidence**: Event-oriented evidence with event type, source URL or reference, published timestamp, effective timestamp where available, provider class, parser warnings, freshness, and license posture.
- **VisualizationProvenance**: Non-evidence output describing TradingView visualization payloads, links, widget configuration, symbol validation status, generated timestamp, and warnings.
- **Freshness Cache Record**: Cache metadata preserving provider/source, source timestamp where available, retrieved timestamp, freshness category, TTL or expiry, warnings, and degraded-state reason where applicable.
- **Route Evaluation Fixture**: Vietnamese, English, or mixed-language prompt with expected route, expected tool family, symbol context, ambiguity label, and acceptance outcome.
- **Degraded State**: Machine-detectable result for unavailable, stale, missing-field, parser-limited, provider-down, license-blocked, validation-failed, unsupported, ambiguous, or deferred-scope paths.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of supported symbol fixtures for `FPT`, `HOSE:FPT`, `HNX:SHS`, `UPCOM:BSR`, Vietnam indexes, and ambiguous ticker forms route to the expected market-data or visualization tool family and bind to canonical symbol identity, or return an explicit degraded/disambiguation result.
- **SC-002**: At least 95% of successful market-data answer fixtures include provider/source, URL or reference, retrieved timestamp, exchange, currency, freshness, license posture, and warnings where applicable; the remaining fixtures must be explicit degraded no-source outcomes.
- **SC-003**: 100% of provider outage, stale-source, stale-cache, missing-field, parser-limited, blocked-license, unsupported-source, and validation-failed fixtures produce an admitted fallback or a machine-detectable degraded state.
- **SC-004**: 100% of cache-hit market-data fixtures preserve provider/source, source timestamp where available, retrieved timestamp, freshness category, TTL or expiry, warnings, and degraded-state reason where applicable.
- **SC-005**: 100% of TradingView fixtures are classified as `VisualizationProvenance`, and 0 factual answer fixtures use TradingView payload values as canonical market evidence.
- **SC-006**: Vietnamese and mixed-language route fixtures for price, chart, fundamentals, disclosures, breadth, flow, and report-like prompts achieve at least 85% meaning-based classification accuracy and have explicit route-tool precision/recall targets recorded before verification.
- **SC-007**: Provider-backed trace fixtures show 0 credential, secret, raw provider payload, parser-internal, or unsafe trace leaks on public response surfaces.
- **SC-008**: The specification, plan, and tasks keep M2B.3 scoped to `TS-06`, `TS-07`, `TS-08`, and `TS-12`, with generic web fetch, reporting persistence, remote admission, symbol-store writes, and production provider enablement deferred unless explicitly governed later.
- **SC-009**: Final review evidence records `core.stock_query_router` touched-surface coverage at >=80% and `core.tools` coverage at >=70%, or includes an explicit governed exception explaining why the broader coverage gate cannot apply in this phase.

## Assumptions

- M2B.1 and M2B.2 are treated as verified predecessor baselines for descriptors, route filtering, gateway admission, provider policy, normalized outputs, request-scoped context, and degraded states.
- Production provider enablement depends on license, terms-of-use, credential scope, redistribution posture, freshness, and operational review; specification can define required behavior without implying every named provider is production-approved.
- Vietnam-native, official, and licensed providers may be represented by fixtures, approved adapters, research/prototype posture, or degraded states during planning and test design if live access is unavailable.
- Yahoo, Alpha Vantage, or other international providers are fallback or cross-market comparison sources for Vietnam-market requests, not primary Vietnam-market sources when approved local sources are available.
- TradingView is visualization provenance only by default; any future policy that admits TradingView-derived values as evidence must be governed outside this M2B.3 specification.
- Report-like Vietnamese or mixed-language prompts are route/evaluation fixtures only; full report composition, persistence, and artifact lifecycle changes remain outside M2B.3.
- Generic web fetch and remote/MCP-style tool admission are deferred to later milestones and must not be introduced as shortcuts for missing Vietnam provider coverage.
