# ADR-Frontend-002: Modernize the Frontend Foundation with a Contract-First Modular Stack

## Document Control

| Field | Value |
|-------|-------|
| **ADR ID** | ADR-Frontend-002 |
| **Domain** | Frontend |
| **Standards Stance** | Practice-Based ADR discipline |
| **Status** | Proposed |
| **Date** | 2026-04-01 |
| **Last Updated** | 2026-04-13 |
| **Decision Owners** | Engineering · Architecture · Frontend maintainers |

## Context

[ADR-Frontend-001](./ADR-FRONTEND-001-MODULAR-APPLICATION.md) establishes that the frontend should evolve as a modular application rather than adopt micro-frontends now. That architectural direction is necessary, but not sufficient. The repository also needs an explicit decision on the modernization foundation that will implement that architecture.

The current frontend foundation has several delivery and maintainability constraints:

- Create React App is deprecated and remains the active build tool
- there is no route-based shell composition yet
- JavaScript and TypeScript coexist unevenly in active paths
- API access is duplicated across multiple clients
- frontend-backend types are not synchronized through the existing OpenAPI contract
- there is no frontend test foundation

The modernization research concludes that the best fit is not just a generic tool refresh, but a **contract-first modular SPA stack** that reduces current risk while reinforcing the internal boundaries required by ADR-Frontend-001.

## Decision

- Modernize the frontend foundation with a contract-first modular SPA stack.
- Replace Create React App with [Vite](https://vite.dev/guide/).
- Introduce [React Router](https://reactrouter.com/start/declarative/installation) for shell and route composition.
- Use React Context plus `useReducer` plus feature hooks for module-scoped client state.
- Use [TanStack Query](https://tanstack.com/query/latest/docs/framework/react/overview) for REST-backed server-state orchestration.
- Generate frontend-backend TypeScript contracts from the existing OpenAPI specification via [openapi-typescript](https://openapi-ts.dev/introduction).
- Keep SSE and WebSocket flows explicit through typed platform clients and feature-facing hooks.
- Adopt CSS Modules plus a token layer as the primary styling baseline.
- Adopt [Vitest](https://vitest.dev/) plus React Testing Library as the primary frontend test foundation.
- Treat Progressive Web Application enablement as an optional later-phase capability layered on the SPA, not as a separate architecture choice.
- Treat [MSW](https://mswjs.io/docs/), [Storybook](https://storybook.js.org/docs), and [Radix UI](https://www.radix-ui.com/) as planned accelerators for later phases rather than phase-0 prerequisites.

## Decision Statement

The frontend modernization program will implement ADR-Frontend-001 through a foundation-first migration built on:

- Vite for build and test integration
- React Router for shell and route composition
- Context plus `useReducer` for module-local client state
- TanStack Query for server state
- contract-generated TypeScript types for platform APIs
- typed streaming adapters for chat and real-time interactions
- CSS Modules plus design tokens for baseline styling governance
- Vitest plus React Testing Library for executable frontend quality gates
- optional later-phase PWA capability where installability and carefully scoped offline behavior are justified

This ADR defines the preferred modernization stack and delivery baseline. It does not change the architectural direction of ADR-Frontend-001; it operationalizes it.

## Rationale

- Create React App is deprecated, so remaining on `react-scripts` increases maintenance risk without adding architectural value.
- Vite offers the cleanest migration path for the current SPA and aligns directly with a modern Vitest-based test setup.
- Route composition is required before bounded feature modules can own navigation and integration surfaces cleanly.
- React guidance supports reducer-plus-context pairs, provider extraction, and custom hooks as a scaling pattern for larger applications.
- TanStack Query addresses concerns that custom fetch layers repeatedly re-implement poorly: caching, deduplication, invalidation, refetching, and async lifecycle handling.
- The repository already maintains an OpenAPI contract, so contract-generated types are a practical way to reduce duplicated request and response typing across the frontend.
- Streaming and WebSocket behavior are product-critical and should remain explicit, typed, and testable rather than hidden behind overly generic abstractions.
- PWA capabilities can add installability and shell resilience, but they do not replace modularization and they must be introduced with explicit freshness and cache-scope rules for finance-oriented workflows.
- A foundation-first sequence reduces rework because tooling, routing, typing, and test conventions are in place before module extraction accelerates.

## Consequences

### Positive

- Removes dependency on deprecated CRA tooling
- Creates a coherent stack for modular extraction rather than a piecemeal tool refresh
- Improves contract discipline between frontend and backend
- Reduces long-term duplication in API clients and request typing
- Establishes a modern test foundation before large-scale refactoring
- Supports later isolated UI workflows through MSW and Storybook without requiring them immediately
- Preserves the option to add installability and selective offline support later without changing the core SPA architecture

### Negative

- Requires coordinated migration of env handling from `REACT_APP_*` to `VITE_*`
- Requires a Node baseline review before Vite and Vitest adoption
- Introduces new tooling and conventions that the team must apply consistently
- Generated contract types and platform APIs need ownership to avoid drift or bypasses
- Some existing frontend implementation patterns will need cleanup before they fit the new structure cleanly
- Service-worker and caching behavior would require explicit governance if PWA support is added later

## Implementation Direction

Recommended sequence:

1. Audit the active frontend surface and confirm dead code or overlapping clients.
2. Migrate the frontend foundation from CRA to Vite and introduce Vitest.
3. Add the shell, route scaffolding, and initial platform layer.
4. Introduce contract-generated API types and move platform clients behind typed boundaries.
5. Extract the first bounded modules, starting with chat and model-management concerns.
6. Expand with MSW, Storybook, stronger module-boundary rules, and additional modules.
7. Evaluate optional PWA enablement only after shell, routing, and data-freshness policies are stable.

The preferred stack profile is the **contract-first modular SPA** described in the companion research report.

## Guardrails

- Do not keep dual long-term build systems; CRA should be removed once the Vite migration is complete.
- Do not expose secrets through client-side `VITE_*` variables.
- Do not reintroduce ad hoc feature-local API clients when platform clients already exist.
- Do not use one global store for concerns that can remain module-local.
- Keep streaming logic explicit and typed; do not force SSE or WebSocket flows into abstractions that reduce debuggability.
- Treat generated contract types as authoritative inputs at the platform boundary.
- Do not enable offline caching strategies for live or market-sensitive data without explicit freshness and invalidation rules.

## Alternatives Considered

### Continue modernizing on Create React App

Rejected because it preserves deprecated tooling and delays the same migration cost without adding strategic value.

### Move immediately to a framework-first SSR stack

Rejected because the current product pressures do not justify introducing SSR-oriented framework complexity as part of the first modernization step.

### Adopt a larger global-state solution first

Rejected because the current project needs clearer module boundaries and server-state handling more than a heavier global-state abstraction.

## Requirement Alignment

This decision serves the following system requirement families without owning them. Requirements are defined and governed in the [master system SRS](../../../system/SYSTEM_REQUIREMENTS_SPECIFICATION.md); this section records the traceability link only.

| Requirement Family | Relevance |
|--------------------|-----------|
| **SR-1**: User Interaction and Experience Continuity | Route composition and shared platform layer preserve session continuity and UX coherence during modernization |
| **SR-5**: Real-Time Delivery and Streaming Behavior | Typed streaming adapters and explicit SSE/WebSocket platform clients directly support streaming delivery obligations |
| **SR-8**: Contract Exposure and Integration Compatibility | Contract-generated TypeScript types from the OpenAPI specification enforce frontend-backend type synchronization |
| **SNR-4**: Maintainability, Modularity, and Evolvability | Modern build tooling (Vite), module-scoped state, and foundation-first sequencing directly support maintainability and evolvability |
| **SNR-7**: Usability, Accessibility, and Design Governance | CSS Modules plus design tokens establish baseline styling governance; Radix UI planned for later-phase accessibility primitives |
| **SNR-8**: Developer Experience, Testability, and Tooling | Vitest plus React Testing Library establish executable frontend quality gates before large-scale refactoring |

## Related Documents

- [ADR-Frontend-001: Adopt a Modular Application Frontend Before Any Micro-Frontend Decomposition](./ADR-FRONTEND-001-MODULAR-APPLICATION.md)
- [Frontend Modernization and Modularization Strategy Research](../../../frontend/frontend-modernization-and-modularization-strategy-research.md)
- [Frontend Architecture Evolution Report](../../../frontend/frontend-architecture-evolution-report.md)
- [Frontend Domain Technical Design](../TECHNICAL_DESIGN.md)
- [Master System SRS](../../../system/SYSTEM_REQUIREMENTS_SPECIFICATION.md)
- [Documentation Methodology](../../../study-hub/project-documentation-and-specification-methodology.md)

## References

- [Vite Guide](https://vite.dev/guide/)
- [React Router Installation](https://reactrouter.com/start/declarative/installation)
- [TanStack Query Overview](https://tanstack.com/query/latest/docs/framework/react/overview)
- [React: Scaling Up with Reducer and Context](https://react.dev/learn/scaling-up-with-reducer-and-context)
- [Vitest](https://vitest.dev/)
- [openapi-typescript Introduction](https://openapi-ts.dev/introduction)
- [MSW Documentation](https://mswjs.io/docs/)
- [Storybook Documentation](https://storybook.js.org/docs)
- [Radix UI](https://www.radix-ui.com/)
- [MDN: Progressive web apps](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [Vite PWA Guide](https://vite-pwa-org.netlify.app/guide/)

## Revision History

| Version | Date | Author | Change Summary |
|---------|------|--------|----------------|
| 0.1 | 2026-04-01 | Engineering | Initial ADR proposed |
| 0.2 | 2026-04-13 | Engineering | Standardized to project ADR discipline; migrated to `docs/domains/frontend/DECISIONS/`; added Document Control, Requirement Alignment, and Revision History |
