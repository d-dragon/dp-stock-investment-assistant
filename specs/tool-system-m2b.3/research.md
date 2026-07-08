# Phase 0 Research: Vietnam Market and Visualization Coverage - M2B.3

## Decision: Add Vietnam market-data capability families below the existing tool gateway

**Rationale**: The roadmap requires concrete Vietnam quote/history/fundamental coverage while architecture and technical design require provider adapters to remain below model-visible tools. Building a market-data tool family behind the existing descriptor, surface, gateway, provider-policy, and normalization boundaries preserves the single ReAct runtime and prevents `StockSymbolTool` from becoming a market-data fetcher.

**Alternatives considered**:
- Reuse `StockSymbolTool` for live market data: rejected because M2B.2 makes symbol identity a separate boundary.
- Expose provider-specific tools directly: rejected because provider choice, license posture, and freshness are deterministic policy concerns.
- Start with generic web fetch: rejected because roadmap places generic web evidence in M2B.4.

## Decision: Treat provider onboarding as posture-gated fixture/adaptor work, not production enablement

**Rationale**: The roadmap names `vnstock`, Vietstock, CafeF, FiinGroup/FiinTrade/FiinQuant, VSDC, HOSE, and HNX where terms and licensing allow, while constitution and architecture require provider license/ToS, credential, redistribution, freshness, and degraded-state review before production use. Planning therefore supports descriptors, deterministic fixture adapters, approved non-production adapters, or degraded states without claiming production readiness.

**Alternatives considered**:
- Add live provider calls by default: rejected because credentials and licensing are not guaranteed.
- Use Yahoo/Alpha Vantage as primary Vietnam sources: rejected because they are fallback or cross-market comparison sources for this scope.
- Block all provider work until contracts are signed: rejected because deterministic fixtures and descriptor/posture tests can verify the architecture safely.

## Decision: Extend M2B.2 normalized outputs for market facts, freshness cache records, and attribution traces

**Rationale**: M2B.2 already introduced normalized output, execution envelope, provider policy, and request-scoped `ToolContextPack` semantics. M2B.3 should extend these contracts for quote/history, fundamentals, breadth/flow, disclosures/corporate actions, cache freshness, and provider-backed trace metadata rather than inventing a parallel output shape.

**Alternatives considered**:
- Return raw provider payloads to prompt assembly: rejected by constitution and technical design.
- Store `ToolContextPack` wholesale for reuse: rejected because it is request-scoped and may contain stale evidence.
- Use only response prose for attribution: rejected because observability and cache metadata need machine-detectable fields.

## Decision: Keep TradingView as `VisualizationProvenance`

**Rationale**: SRS `FR-2.8.4`, `CON-7`, roadmap gates, and architecture memory all prohibit treating TradingView values as canonical market evidence by default. The plan expands TradingView chart/widget/deep-link/symbol-validation outputs as inspectable visualization provenance only.

**Alternatives considered**:
- Use TradingView numeric values as fallback quote evidence: rejected unless a future approved policy admits a specific data category.
- Keep TradingView disabled entirely: rejected because M2B.3 explicitly covers visualization provenance.
- Persist TradingView payloads as market snapshots: rejected because visualization provenance is not canonical evidence.

## Decision: Verify Vietnamese and mixed-language route behavior through deterministic fixture sets

**Rationale**: `FR-4.1.3` and `AC-9.16` require measurable route classification before new model-visible market-data and visualization tools are considered verified. Deterministic fixtures avoid dependence on live model/provider behavior and can measure route/tool-family mapping, ambiguity handling, precision, recall, and at least 85% meaning-based classification accuracy.

**Alternatives considered**:
- Rely only on existing English route tests: rejected because M2B.3 is Vietnam and mixed-language specific.
- Use live semantic-router embeddings as the only proof: rejected because local test determinism matters.
- Fold report-like prompts into report generation: rejected because reporting composition and persistence are M2B.4 scope.

## Decision: Keep public transport contracts unchanged

**Rationale**: M2B.3 operates inside the agent/tool boundary. The spec explicitly says no REST, SSE, Socket.IO, or OpenAPI contract change is expected. Safe user-visible warnings may appear through existing response paths, while internal traces and provider details remain private.

**Alternatives considered**:
- Add public provider metadata fields now: rejected because the plan does not require public contract expansion.
- Add dedicated market-data API endpoints: rejected because M2B.3 is an agent tool-system feature.
- Expose internal traces in streaming output: rejected because trace details may include provider policy internals.
