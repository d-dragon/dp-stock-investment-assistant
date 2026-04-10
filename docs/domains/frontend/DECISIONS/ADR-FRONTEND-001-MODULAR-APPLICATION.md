# ADR-Frontend-001: Adopt a Modular Application Frontend Before Any Micro-Frontend Decomposition

## Document Control

| Field | Value |
|-------|-------|
| **ADR ID** | ADR-Frontend-001 |
| **Domain** | Frontend |
| **Standards Stance** | Practice-Based ADR discipline |
| **Status** | Proposed |
| **Date** | 2026-03-27 |
| **Last Updated** | 2026-04-01 |
| **Decision Owners** | Engineering · Architecture · Frontend maintainers |

## Context

The current frontend is a single React SPA with growing feature scope. It already supports important cross-cutting behaviors such as shared session behavior, streaming interactions, model selection, and centralized API communication.

The product domain imposes constraints that make frontend fragmentation expensive:

- High UX consistency is important for trust and clarity in a finance-oriented assistant.
- Shared session and streaming behavior are part of the primary user journey.
- Cross-feature workflows are still tightly connected.
- The current codebase would benefit more from explicit internal boundaries than from deployment-time decomposition.

At the same time, the frontend needs stronger modularity so it can scale beyond a root-heavy SPA structure.

Research and analysis in the companion report indicate that the current system does not yet show the main signals that justify true micro-frontends, such as multiple frontend teams requiring independent releases, mature and stable domain boundaries, or sustained deployment bottlenecks caused by a shared frontend release train.

The deeper modernization research also clarifies that Option B should not remain an abstract "modular frontend" direction. The preferred realization is now a **contract-first modular SPA** with:

- one application shell
- one controlled platform layer
- bounded feature modules with public APIs
- route-based composition
- typed platform services and contract-generated frontend-backend types

This ADR therefore captures the architectural direction, while the modernization stack and delivery approach are captured separately in [ADR-Frontend-002](./ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md).

## Decision

- Adopt a modular application architecture for the frontend.
- Keep a single deployable frontend shell.
- Organize the codebase around bounded feature modules and a controlled platform layer.
- Use route composition, shared providers, and typed platform services as the primary integration mechanism.
- Prefer a contract-first modular SPA realization of the modular application architecture.
- Defer micro-frontend extraction until explicit readiness triggers are met.

## Decision Statement

The frontend will evolve as a bounded-context modular SPA, not as independently deployed micro-frontends in the near term.

In practical terms, this means:

- one React runtime
- one deployable frontend artifact
- one shared application shell
- multiple internal feature modules with explicit boundaries
- platform-owned shared technical capabilities such as routing, configuration, query orchestration, streaming, and UI primitives
- contract-generated frontend-backend types at the platform boundary where practical
- future extraction capability preserved through disciplined module contracts

## Rationale

- A monolith-first strategy is lower risk when boundaries are not yet stable, and it allows the team to discover real seams before turning them into expensive deployment boundaries ([Monolith First](https://martinfowler.com/bliki/MonolithFirst.html)).
- React's scaling model supports internal modular growth through providers, contexts, reducers, and custom hooks, which maps well to a modular application design ([React: Scaling Up with Reducer and Context](https://react.dev/learn/scaling-up-with-reducer-and-context)).
- True micro-frontends are most justified when independently deliverable frontend applications are needed for autonomous teams and independent release cycles; that is not the current pressure profile of this repository ([Martin Fowler: Micro Frontends](https://martinfowler.com/articles/micro-frontends.html)).
- The repository already maintains an OpenAPI contract and currently shows duplicated API-access patterns. A contract-first modular SPA reduces drift between frontend and backend and creates more durable platform boundaries.
- Modernizing the existing SPA into a modular application is a smaller and safer architectural step than introducing distributed frontend composition prematurely.

## Consequences

### Positive

- Lower near-term architecture risk
- Faster modernization path from the current SPA
- Better UX consistency across assistant, data, and workspace features
- Better control of shared session, streaming lifecycle, notifications, and configuration
- Reduced platform and deployment complexity compared to micro-frontends
- Stronger long-term module seams through explicit public APIs and contract-backed platform services
- Preserved future optionality if extraction later becomes justified

### Negative

- Independent frontend deployment is deferred
- Teams continue to coordinate through one deployable frontend artifact
- Governance discipline is required to maintain real module boundaries
- Contract discipline is required to keep generated types and platform APIs authoritative
- Build, release, and bundle-growth pressure remain centralized until the architecture evolves further

## Implementation Direction

The intended architectural form is:

- shared shell in `app/`
- controlled platform layer in `platform/`
- bounded business modules in `modules/`
- module public entry points as the only supported integration surface
- typed platform-owned API and streaming adapters rather than ad hoc feature-local clients

Preferred realization of this ADR:

- contract-first modular SPA
- one browser shell, one React runtime, and one deployable artifact
- route-composed feature ownership
- platform services that own API contracts, query orchestration, config, streaming, and shared UI primitives

The selected modernization stack, tooling, and migration sequence for implementing this direction are defined in [ADR-Frontend-002](./ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md).

## Guardrails

- Require public entry points for each feature module.
- Prevent sibling modules from importing each other's internals.
- Keep domain logic inside domain modules, not in shared UI or shared platform helpers.
- Keep the platform layer controlled; it must not become a dumping ground.
- Keep contract ownership and generated API types in the platform boundary, not scattered across feature modules.
- Limit truly global state to cross-cutting concerns that cannot reasonably stay module-local.
- Review module boundaries as features evolve.

## Reconsideration Triggers

This decision should be revisited if several of the following become true at the same time:

- Three or more frontend teams need release autonomy.
- Shared frontend release cadence becomes a measurable bottleneck.
- Domain boundaries remain stable across multiple release cycles.
- Module APIs and platform governance are mature enough to support safe extraction.
- One deployable frontend becomes operationally or organizationally limiting.

## Alternatives Considered

### Continue as a single SPA without structural change

Rejected because it preserves current coupling and does not address root-heavy application growth.

### Adopt true micro-frontends now

Rejected because the current repository does not yet justify the deployment, governance, and integration overhead of independently delivered frontend applications.

## Requirement Alignment

This decision serves the following system requirement families without owning them. Requirements are defined and governed in the [master system SRS](../../../system/SYSTEM_REQUIREMENTS_SPECIFICATION.md); this section records the traceability link only.

| Requirement Family | Relevance |
|--------------------|-----------|
| **SR-1**: User Interaction and Experience Continuity | Modular SPA preserves UX consistency and shared session behavior across all frontend features |
| **SR-5**: Real-Time Delivery and Streaming Behavior | Shared platform layer centralizes streaming lifecycle instead of fragmenting it across micro-frontends |
| **SNR-4**: Maintainability, Modularity, and Evolvability | Bounded feature modules with explicit public APIs directly address modularity and evolvability obligations |
| **SNR-7**: Usability, Accessibility, and Design Governance | Single application shell and controlled platform layer support consistent UX governance |

## Related Documents

- [Frontend Architecture Evolution Report](../../../frontend/frontend-architecture-evolution-report.md)
- [Frontend Modernization and Modularization Strategy Research](../../../frontend/frontend-modernization-and-modularization-strategy-research.md)
- [ADR-Frontend-002: Modernize the Frontend Foundation with a Contract-First Modular Stack](./ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md)
- [Frontend Domain Technical Design](../TECHNICAL_DESIGN.md)
- [Master System SRS](../../../system/SYSTEM_REQUIREMENTS_SPECIFICATION.md)
- [Documentation Methodology](../../../study-hub/project-documentation-and-specification-methodology.md)

## References

- [Monolith First](https://martinfowler.com/bliki/MonolithFirst.html)
- [Martin Fowler: Micro Frontends](https://martinfowler.com/articles/micro-frontends.html)
- [React: Scaling Up with Reducer and Context](https://react.dev/learn/scaling-up-with-reducer-and-context)
- [Feature-Sliced Design](https://feature-sliced.design/)
- [openapi-typescript Introduction](https://openapi-ts.dev/introduction)

## Revision History

| Version | Date | Author | Change Summary |
|---------|------|--------|----------------|
| 0.1 | 2026-03-27 | Engineering | Initial ADR proposed |
| 0.2 | 2026-04-01 | Engineering | Refined context with contract-first SPA realization and companion ADR-002 linkage |
| 0.3 | 2026-04-13 | Engineering | Standardized to project ADR discipline; migrated to `docs/domains/frontend/DECISIONS/`; added Document Control, Requirement Alignment, and Revision History |
