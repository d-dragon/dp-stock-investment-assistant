# Research: Tool Contract and Gateway Baseline - M2B.1

## Decision: Keep M2B.1 Strict To TS-01 And TS-02

**Rationale**: The feature spec and roadmap milestone gate define M2B.1 as descriptor inventory, route-filtered exposure, and gateway admission around existing registry-backed tools. This is enough to make descriptor integrity, route filtering, and degraded-state admission testable before provider-backed model-visible tools are added.

**Alternatives considered**:
- Include `TS-03` to `TS-05`: rejected because symbol-store evolution, provider policy, normalized output, and `ToolContextPack` belong to M2B.2 and later gates.
- Add public API metadata now: rejected because gateway traces are internal and public surfaces may expose only safe degraded/warning metadata.

## Decision: Represent Descriptors As Reviewed Local Artifacts

**Rationale**: Local first-party descriptors keep descriptor integrity reviewable, testable, and independent from remote or provider-supplied descriptors. A canonical serialized descriptor can produce a deterministic version/hash for exposure and admission traces.

**Alternatives considered**:
- Derive descriptors only from LangChain tool `name` and `description`: rejected because it cannot carry policy fields, risk class, route coverage, freshness, or integrity markers.
- Accept remote descriptors directly: rejected because unapproved remote descriptors are a trust surface and must fail closed in M2B.1.

## Decision: Split Capability Descriptors From Policy Descriptors

**Rationale**: The model-visible capability descriptor needs safe tool purpose, input shape, route coverage, output kind, examples, locale coverage, enabled/non-exposed state, and descriptor identity. Internal policy descriptors need risk, license, freshness, cache, timeout, credential owner, mutation policy, required metadata, enabled environments, exposure status, and integrity controls. Keeping these separate prevents provider and security policy from leaking to the model.

**Alternatives considered**:
- One combined descriptor: rejected because it would either expose internal policy fields to the model or force missing admission data.
- Policy-only descriptors: rejected because the model still needs a safe compact capability description.

## Decision: Build Tool Surfaces Before ReAct Invocation

**Rationale**: Route-filtered exposure must happen before the model receives tools. The builder should use route, locale, feature flags, context availability, descriptor state, registry enablement, and admitted risk class to return only allowed model-visible tool capabilities.

**Alternatives considered**:
- Let ReAct receive all enabled registry tools and rely on prompt guidance: rejected because it does not meet `FR-2.4.3` or `AC-9.2`.
- Expose scaffolded tools for unsupported routes: rejected because clarified requirements require no exposed tool when a route has no admitted M2B.1 tool.

## Decision: Keep ToolGateway Thin And In-Process

**Rationale**: The gateway should admit, reject, trace, and wrap execution around `ToolRegistry` without becoming a provider parser, second agent runtime, remote service, business workflow owner, or prompt-policy author. This matches the architecture and technical design boundary.

**Alternatives considered**:
- Separate gateway service: rejected because M2B.1 has no operational scaling or ownership need for a remote boundary.
- Replace `ToolRegistry`: rejected because current compatibility requires registry-backed execution.

## Decision: Treat Placeholder Tools As Described But Non-Exposed

**Rationale**: `TradingViewTool` is part of the M2B.1 baseline inventory even though it is currently a placeholder and commented out of runtime registration. It still needs descriptors so the inventory is complete, but descriptor state must make disabled/non-exposed behavior explicit.

**Alternatives considered**:
- Exclude placeholders from descriptors: rejected because it hides future baseline inventory and breaks `SC-001`.
- Expose placeholders as degraded tools: rejected because clarified requirements say routes with no admitted M2B.1 tool expose no scaffolded substitute.

## Decision: Keep Gateway Traces Internal By Default

**Rationale**: `NFR-5.2.12` requires trace completeness, but M2B.1 traces only need to populate fields that exist in the current baseline or are conditionally applicable. Internal traces can include route, exposure, selected tool, adapter identity where applicable, descriptor identity, admission outcome, cache/freshness status where applicable, latency, warning, and degraded reason. Public surfaces should reveal only safe degraded-state or warning metadata unless a later public contract change is planned.

**Alternatives considered**:
- Emit full trace metadata in REST/SSE/WebSocket responses: rejected because this may expose internal policy and implementation details.
- Omit trace fields until observability milestones: rejected because M2B.1 needs trace evidence to prove descriptor and gateway behavior.
