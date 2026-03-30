# ADR-Frontend-001: Adopt a Modular Application Frontend Before Any Micro-Frontend Decomposition

## Status

- Proposed

## Date

- 2026-03-27

## Decision Owners

- Engineering
- Architecture
- Frontend maintainers

## Context

The current frontend is a single React SPA with growing feature scope. It already supports important cross-cutting behaviors such as shared session behavior, streaming interactions, model selection, and centralized API communication.

The product domain imposes constraints that make frontend fragmentation expensive:

- High UX consistency is important for trust and clarity in a finance-oriented assistant.
- Shared session and streaming behavior are part of the primary user journey.
- Cross-feature workflows are still tightly connected.
- The current codebase would benefit more from explicit internal boundaries than from deployment-time decomposition.

At the same time, the frontend needs stronger modularity so it can scale beyond a root-heavy SPA structure.

Research and analysis in the companion report indicate that the current system does not yet show the main signals that justify true micro-frontends, such as multiple frontend teams requiring independent releases, mature and stable domain boundaries, or sustained deployment bottlenecks caused by a shared frontend release train.

## Decision

- Adopt a modular application architecture for the frontend.
- Keep a single deployable frontend shell.
- Organize the codebase around bounded feature modules and a controlled platform layer.
- Use route composition, shared providers, and typed platform services as the primary integration mechanism.
- Defer micro-frontend extraction until explicit readiness triggers are met.

## Decision Statement

The frontend will evolve as a bounded-context modular SPA, not as independently deployed micro-frontends in the near term.

In practical terms, this means:

- one React runtime
- one deployable frontend artifact
- one shared application shell
- multiple internal feature modules with explicit boundaries
- future extraction capability preserved through disciplined module contracts

## Rationale

- A monolith-first strategy is lower risk when boundaries are not yet stable, and it allows the team to discover real seams before turning them into expensive deployment boundaries ([Monolith First](https://martinfowler.com/bliki/MonolithFirst.html)).
- React's scaling model supports internal modular growth through providers, contexts, reducers, and custom hooks, which maps well to a modular application design ([React: Scaling Up with Reducer and Context](https://react.dev/learn/scaling-up-with-reducer-and-context)).
- True micro-frontends are most justified when independently deliverable frontend applications are needed for autonomous teams and independent release cycles; that is not the current pressure profile of this repository ([Martin Fowler: Micro Frontends](https://martinfowler.com/articles/micro-frontends.html)).
- Modernizing the existing SPA into a modular application is a smaller and safer architectural step than introducing distributed frontend composition prematurely.

## Consequences

### Positive

- Lower near-term architecture risk
- Faster modernization path from the current SPA
- Better UX consistency across assistant, data, and workspace features
- Better control of shared session, streaming lifecycle, notifications, and configuration
- Reduced platform and deployment complexity compared to micro-frontends
- Preserved future optionality if extraction later becomes justified

### Negative

- Independent frontend deployment is deferred
- Teams continue to coordinate through one deployable frontend artifact
- Governance discipline is required to maintain real module boundaries
- Build, release, and bundle-growth pressure remain centralized until the architecture evolves further

## Implementation Direction

The intended architectural form is:

- shared shell in `app/`
- controlled platform layer in `platform/`
- bounded business modules in `modules/`

Recommended enabling stack:

- [Vite](https://vite.dev/guide/) for modern frontend build tooling
- [React Router](https://reactrouter.com/start/declarative/installation) for route composition
- [TanStack Query](https://tanstack.com/query/latest/docs/framework/react/overview) for server-state orchestration
- React Context plus `useReducer` plus feature hooks for modular internal state scaling

## Guardrails

- Require public entry points for each feature module.
- Prevent sibling modules from importing each other's internals.
- Keep domain logic inside domain modules, not in shared UI or shared platform helpers.
- Keep the platform layer controlled; it must not become a dumping ground.
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

## Related Documents

- [frontend-architecture-evolution-report.md](./frontend-architecture-evolution-report.md)

## References

- [Monolith First](https://martinfowler.com/bliki/MonolithFirst.html)
- [Martin Fowler: Micro Frontends](https://martinfowler.com/articles/micro-frontends.html)
- [React: Scaling Up with Reducer and Context](https://react.dev/learn/scaling-up-with-reducer-and-context)
- [Vite Guide](https://vite.dev/guide/)
- [React Router Installation](https://reactrouter.com/start/declarative/installation)
- [TanStack Query Overview](https://tanstack.com/query/latest/docs/framework/react/overview)