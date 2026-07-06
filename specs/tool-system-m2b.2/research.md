# Phase 0 Research: Internal Symbol and Normalization Backbone - M2B.2

## Decision 1: Extend the verified M2B.1 tool boundary instead of creating a second runtime

**Decision**: Build M2B.2 on the existing descriptor, route-filtered surface, gateway admission, and registry-backed execution baseline.

**Rationale**: The architecture and technical design preserve a single ReAct runtime and place tool governance around the existing tool boundary. A second runtime would violate the architecture memory and make provider policy harder to audit.

**Alternatives Rejected**:
- New provider-specific tools exposed directly to the model: rejected because provider adapters must remain below model-visible tools.
- Independent execution runtime for normalized outputs: rejected because M2B.1 already supplies the gateway surface and trace point.

## Decision 2: Reposition StockSymbolTool toward internal symbol-store lookup

**Decision**: Plan `StockSymbolTool` target behavior around internal symbol-store lookup, normalization, alias/search, coverage, identifiers, exchange/currency identity, tags, and stored metadata. Live quote, history, and fundamental retrieval stay out of this tool.

**Rationale**: The roadmap, architecture, and technical design separate symbol identity from market-data facts. `StockSymbolTool` should produce normalized `SystemRecord` outputs from internal records while future market-data tools own live facts.

**Alternatives Rejected**:
- Continue treating Yahoo/DataManager live access as the target symbol path: rejected because the target design explicitly separates internal symbol records from external market-data providers.
- Add Vietnam quote/history/fundamental tools in M2B.2: rejected because those belong to downstream `TS-06` and later milestones.

## Decision 3: Model provider policy as internal descriptors plus deterministic selection

**Decision**: Add internal provider adapter descriptors and provider selection policy that classify provider class, market support, data categories, licensing, credential ownership, parser limits, source-attribution requirements, production eligibility, freshness posture, fallback eligibility, and fail-closed conditions.

**Rationale**: The model should select tools, not providers. Provider policy must stay deterministic, reviewable, and hidden below the tool gateway.

**Alternatives Rejected**:
- Expose provider lists directly to prompts: rejected due model-visible surface and licensing risks.
- Silently fallback between providers: rejected because degraded states and source metadata must record fallback posture.

## Decision 4: Use feature-local internal contracts for envelopes, normalized outputs, and ToolContextPack

**Decision**: Define internal Python contracts using enums, dataclasses, and validation helpers, with serializers where tests and traceability need machine-readable evidence. Do not update public OpenAPI contracts.

**Rationale**: M2B.2 is an internal agent/tool boundary milestone. The SRS requires inspectable envelopes and normalized output classes, but the feature spec explicitly says no public REST/SSE/Socket.IO contract change is expected.

**Alternatives Rejected**:
- Public API schema update: rejected because no public transport change is in scope.
- Persist full `ToolContextPack`: rejected because the technical design says it is request-scoped and not durable truth.

## Decision 5: Treat source metadata as a backbone, not full market-data attribution closure

**Decision**: Normalize source metadata fields required by output kind and retained derivatives, while deferring full answer-level market-data attribution and cache-freshness closure to `TS-06`/M2B.3.

**Rationale**: `FR-2.7.4`, `NFR-5.2.13`, `CON-9`, and `AC-9.8` are intentionally not mapped to M2B.2. M2B.2 must create the structure those later features consume without claiming downstream coverage.

**Alternatives Rejected**:
- Claim full source-attribution compliance in M2B.2: rejected because it would drift from the roadmap.
- Skip source metadata entirely: rejected because normalized output and retention rules need source lineage fields.

## Decision 6: Keep mutation receipts disabled by default

**Decision**: Define mutation classification and receipt contracts, but keep production symbol-store write behavior disabled or degraded by default.

**Rationale**: `TS-11` is included only in a non-mutating form. Mutation receipt shape is needed for future route admission and audit behavior, but M2B.2 must not enable production writes without authorization and confirmation policy.

**Alternatives Rejected**:
- Enable symbol-store writes now: rejected because route admission, authorization, confirmation, and audit policy are not in this milestone.
- Omit mutation receipts: rejected because `FR-2.11.5`, `FR-2.11.6`, `AC-9.15`, and `IR-3.9` are mapped to this feature.

## Decision 7: Verification should be focused and compatibility-preserving

**Decision**: Add M2B.2 focused tests for symbol normalization, provider policy, normalized outputs, context assembly, degraded states, raw-payload exclusion, mutation receipt disabled behavior, and M2B.1 regression compatibility.

**Rationale**: Existing M2B.1 tests already prove descriptor/surface/gateway compatibility. M2B.2 must prove the new backbone behavior without depending on downstream external providers or public API changes.

**Alternatives Rejected**:
- Full external provider integration tests: rejected because production provider enablement is not in M2B.2.
- Only documentation checks: rejected because normalized output and policy behavior must be executable and machine-checkable.
