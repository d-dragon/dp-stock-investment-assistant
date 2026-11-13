# ADR-Frontend-002: Modernize the Frontend Foundation with a Contract-First Modular Stack

## Document Control

| Field | Value |
|-------|-------|
| **ADR ID** | ADR-Frontend-002 |
| **Domain** | Frontend |
| **Standards Stance** | Practice-Based ADR discipline |
| **Status** | Accepted |
| **Date** | 2026-04-01 |
| **Last Updated** | 2026-11-13 |
| **Replaced in part by** | [ADR-Frontend-007](./ADR-FRONTEND-007-DESIGN-TOKEN-ARCHITECTURE.md) (token-colour bullet) · [ADR-Frontend-004](./ADR-FRONTEND-004-CHART-ENGINE-ADAPTER.md) (chart capabilities: Lightweight Charts ships no indicators) · [ADR-Frontend-003](./ADR-FRONTEND-003-URL-OWNED-SHAREABLE-STATE.md) (G3: the URL owns track, `symbol` and `coreObjectRef`; the store mirrors them) · [ADR-Frontend-008](./ADR-FRONTEND-008-MSW-AND-STORYBOOK-IN-M000.md) (MSW and Storybook move into M-000) |
| **Decision Owners** | Engineering · Architecture · Frontend maintainers |

## Context

[ADR-Frontend-001](./ADR-FRONTEND-001-MODULAR-APPLICATION.md) establishes that the frontend should evolve as a modular application hosting an adaptive, resizable multi-pane financial canvas rather than adopt micro-frontends now. That architectural direction is necessary, but not sufficient. The repository also needs an explicit decision on the modernization foundation that will implement that architecture.

The current frontend foundation has several delivery and maintainability constraints:

- Create React App is deprecated and remains the active build tool
- there is no route-based shell composition or multi-pane canvas layout engine
- JavaScript and TypeScript coexist unevenly in active paths
- API access is duplicated across multiple clients
- frontend-backend types are not synchronized through the existing OpenAPI contract
- high-frequency market data updates (100ms–500ms ticks) risk re-render cascades if routed through naive React Context stores
- there is no formal Generative UI protocol to stream interactive financial metric cards and signals
- there is no frontend test foundation

The modernization research concludes that the best fit is a **contract-first modular SPA stack with a dual-speed state architecture and multi-pane financial canvas** that accelerates developer velocity while reinforcing the internal boundaries required by ADR-Frontend-001.

## Decision

- Modernize the frontend foundation with a contract-first modular SPA stack hosting an adaptive financial workspace.
- Replace Create React App with [Vite](https://vite.dev/guide/).
- Introduce [React Router](https://reactrouter.com/start/declarative/installation) for shell and route composition.
- Adopt [`react-resizable-panels`](https://github.com/bvaughn/react-resizable-panels) for adaptive panes on **Z1, Z3, Z4** only (**Z2 fixed chrome**); resize is **session-only** in Pitch B; saved layout presets belong to **M-009** (not localStorage in this bet).
- Adopt a **Dual-Speed State Architecture**:
  - **Fast Reactive Lane**: [Zustand](https://github.com/pmndrs/zustand) for high-frequency market ticks, active symbol synchronization, timeframe selection, and transient workspace layout state.
  - **Slow Server-State Lane**: [TanStack Query](https://tanstack.com/query/latest/docs/framework/react/overview) for REST-backed server-state caching, deduplication, and invalidation (historical OHLCV, quarterly financials, model catalog).
- Standardize financial visualization engines:
  - **Primary Canvas**: [TradingView Lightweight Charts](https://tradingview.github.io/lightweight-charts/) (`lightweight-charts`) for high-performance (60 FPS) OHLCV candlesticks, volume histograms, and indicators (RSI, MACD).
  - **Auxiliary Visualization**: [Chart.js](https://www.chartjs.org/) for macro graphs, solvency breakdown bars, and portfolio asset allocation donuts.
- **Defer** a Structured SSE Artifact Protocol / Generative UI Dispatcher to **Future** (not M-000 Pitch B); Pitch B streams companion/chat tokens over SSE without GenUI artifact cards.
- Adopt **Tailwind CSS + Radix UI primitives** with financial dark-mode design tokens (emerald green for gains, rose red for losses, cyan for copilot, slate-950 dark background) as the primary UI foundation.
- Generate frontend-backend TypeScript contracts from the existing OpenAPI specification via [openapi-typescript](https://openapi-ts.dev/introduction).
- Keep **HTTPS + SSE** flows explicit through typed platform clients and feature-facing hooks (**no Socket.IO / WebSocket** in the target; SNR-8.1.2).
- Adopt [Vitest](https://vitest.dev/) plus React Testing Library as the primary frontend test foundation.
- Adopt a **Value-Driven Vertical-Slice Delivery Strategy**: pair build tool modernization with early delivery of the **Z1–Z4 Adaptive Workspace shell and workspace context store** in Phase 2 (maiden TradingView chart deferred; chart-yield → **M-006**).
- Treat Progressive Web Application enablement as an optional later-phase capability layered on the SPA, not as a separate architecture choice.
- Treat [MSW](https://mswjs.io/docs/) and [Storybook](https://storybook.js.org/docs) as planned accelerators for later phases rather than phase-0 prerequisites.

## Decision Statement

The frontend modernization program will implement ADR-Frontend-001 through a vertical-slice migration built on:

- Vite for build and test integration
- React Router for shell and route composition
- `react-resizable-panels` for the adaptive multi-pane workspace
- Dual-speed state management: Zustand for fast reactive state and TanStack Query for server state
- Chart engines (`lightweight-charts`, Chart.js) remain the intended visualization stack when Canvas milestones land; **not** the Pitch B foundation proof
- HTTPS + SSE companion/chat streaming (GenUI artifact protocol deferred to Future)
- Tailwind CSS plus Radix UI primitives for accessible, high-velocity financial UI design
- contract-generated TypeScript types from OpenAPI for platform APIs
- typed streaming adapters for chat and real-time interactions
- Vitest plus React Testing Library for executable frontend quality gates
- optional later-phase PWA capability where installability and carefully scoped offline behavior are justified

This ADR defines the preferred modernization stack and delivery baseline. It operationalizes ADR-Frontend-001.


## Carve-outs (M-000 Pitch B)

These items are **not** delivered under this Accepted ADR for Pitch B:

| Item | Disposition |
|------|-------------|
| Socket.IO / WebSocket client | **Out** — target transport is HTTPS + SSE only (**SNR-8.1.2** amend) |
| GenUI / Structured SSE Artifact Protocol / Generative UI Dispatcher | **Future** |
| localStorage saved layout presets | **M-009** — Pitch B layout sizes are session-only |
| Chart-yield on Decision gate | **M-006** |
| Maiden TradingView chart as Phase-2 proof | **Deferred** — foundation Phase 2 = Z1–Z4 shell + workspace context store |
| Auth / Auth0 / **SR-10.1.x** | **Pitch A / ADR-SYS-001** |

`react-resizable-panels` applies to **Z1, Z3, and Z4 only**; **Z2 stays fixed chrome**.

## Rationale

- Create React App is deprecated, so remaining on `react-scripts` increases maintenance risk without adding architectural value.
- Vite offers the cleanest migration path for the current SPA and aligns directly with a modern Vitest-based test setup.
- Active traders require simultaneous access to live visual charts, indicators, and AI analysis; a resizable multi-pane canvas using `react-resizable-panels` delivers this workspace without clunky route-hopping.
- Real-time financial market ticks update at 100ms–500ms intervals. Pushing these through React Context triggers re-render storms across the component tree. Zustand provides fine-grained transient subscriptions that update the TradingView canvas directly at 60 FPS without re-rendering parent components.
- TradingView Lightweight Charts is the industry standard for lightweight, ultra-performant canvas charting (~45 KB), while Chart.js provides flexible support for secondary financial distributions and debt breakdowns.
- Structured SSE artifacts elevate the assistant from a plain-text chat to an actionable copilot capable of displaying interactive solvency cards, valuation metric badges, and trade alerts.
- Tailwind CSS combined with unstyled Radix UI primitives drastically accelerates component velocity over writing raw CSS Modules from scratch, while guaranteeing zero-runtime CSS overhead and full WCAG accessibility.
- The repository already maintains an OpenAPI contract, so contract-generated types are a practical way to eliminate request and response drift across the platform boundary.
- A vertical-slice delivery sequence avoids a multi-week feature hiatus by shipping the interactive chart canvas early in Phase 2 alongside the foundation upgrades.

## Consequences

### Positive

- Eliminates deprecated CRA tooling in favor of modern, high-speed Vite ESM tooling
- Delivers a professional, resizable financial trading workspace directly aligned with trader workflows and Figma specifications
- Prevents re-render lag during market tick streaming through the dual-speed state architecture
- Transforms plain-text chat into an interactive Generative UI experience with rich financial cards
- Accelerates UI feature velocity through Tailwind CSS and accessible Radix primitives
- Enforces compile-time type safety against backend OpenAPI contracts
- Establishes a modern test foundation (Vitest + RTL) before large-scale refactoring
- Delivers visible user value early in the modernization sequence

### Negative

- Requires coordinated migration of env handling from `REACT_APP_*` to `VITE_*`
- Introduces new dependencies (`react-resizable-panels`, `lightweight-charts`, `zustand`, `lucide-react`, `tailwindcss`) that must be governed
- Requires discipline to keep the fast state lane (Zustand) isolated from general server cache concerns (TanStack Query)
- Generated contract types and platform APIs need continuous ownership in CI to prevent drift
- SSE streaming backend must be extended to emit structured artifact event blocks

## Implementation Direction

Recommended sequence for **M-000 Pitch B** (aligns with Frontend Architecture gates G1–G6):

1. **G1 — Vite + chat smoke**: Migrate from CRA to Vite; keep existing chat path working over HTTPS+SSE.
2. **G2 — Z1–Z4 shell**: Scaffold Adaptive Workspace shell (IA §2.6); `react-resizable-panels` on Z1/Z3/Z4; Z2 fixed chrome.
3. **G3 — Workspace context store**: Zustand fast lane for track/symbol/`coreObjectRef`/session layout; Z4 holds Backend `sessionRef` only (**SR-1.4.2**).
4. **G4 — Design tokens wired**: Tailwind + Radix/shadcn primitives with IA-named tokens per `DESIGN_LOCK.md`.
5. **G5 — Vitest + RTL baseline**: Executable FE tests for shell and critical seams (**SNR-6.1.4**).
6. **G6 — Drop Socket.IO**: SSE-only transport conformance (**SNR-8.1.2**).

Later (out of this ADR’s Pitch B acceptance): GenUI artifacts (Future), saved layout presets (**M-009**), chart-yield (**M-006**), TradingView maiden chart under Canvas milestones, Auth0/session durability (**Pitch A / ADR-SYS-001**). MSW and Storybook remain later accelerators.

## Guardrails

- Do not keep dual long-term build systems; CRA must be removed once the Vite migration is complete.
- Do not route high-frequency market tick streams through React Context or slow server caches; use Zustand transient subscriptions or direct canvas updates.
- Do not expose secrets through client-side `VITE_*` variables.
- Do not reintroduce ad hoc feature-local API clients when platform clients already exist.
- Keep streaming logic explicit and typed over **HTTPS + SSE**; do not reintroduce Socket.IO/WebSocket clients in the target path. GenUI artifact schemas remain Future.
- Treat generated contract types as authoritative inputs at the platform boundary.
- Do not enable offline caching strategies for live or market-sensitive data without explicit freshness and invalidation rules.

## Alternatives Considered

### Continue modernizing on Create React App

Rejected because it preserves deprecated tooling and delays the same migration cost without adding strategic value.

### Rely exclusively on React Context for all client state

Rejected because live financial market ticks and streaming tokens trigger full-tree re-render cascades, degrading chart performance.

### Build custom multi-pane splitters and financial widgets with CSS Modules from scratch

Rejected because building resizable split panes, tooltips, and data grids from scratch is a significant velocity bottleneck compared to adopting `react-resizable-panels` and Tailwind + Radix primitives.

## Requirement Alignment

This decision serves the following system requirement families without owning them. Requirements are defined and governed in the [master system SRS](../../../system/SYSTEM_REQUIREMENTS_SPECIFICATION.md); this section records the traceability link only.

| Requirement Family | Relevance |
|--------------------|-----------|
| **SR-1** / **SR-1.4.2**: User Interaction; In-session workspace context | Z1–Z4 shell + Zustand workspace context (session-only until Pitch A) preserves simultaneous track/workspace/companion continuity (**SR-1.4.2**) |
| **SR-5** / **SNR-8.1.2**: Real-Time Delivery; Client streaming compatibility | Dual-speed state + typed **HTTPS+SSE** clients (no Socket.IO); GenUI artifact streaming deferred to Future |
| **SR-8**: Contract Exposure and Integration Compatibility | Contract-generated TypeScript types from OpenAPI specification enforce frontend-backend type synchronization |
| **SNR-4**: Maintainability, Modularity, and Evolvability | Vite tooling, modular domain boundaries, and vertical-slice sequencing directly support maintainability |
| **SNR-7**: Usability, Accessibility, and Design Governance | Tailwind CSS plus Radix UI primitives guarantee accessible (WCAG 2.2 AA) financial UI components |
| **SNR-8** / **SNR-6.1.4**: Developer Experience; Frontend testability baseline | Vitest + React Testing Library establish executable frontend quality gates (**SNR-6.1.4**) |

## Related Documents

- [ADR-Frontend-001: Adopt a Modular Application Frontend Before Any Micro-Frontend Decomposition](./ADR-FRONTEND-001-MODULAR-APPLICATION.md)
- [Frontend Modernization and Modularization Strategy Research](../../../frontend/frontend-modernization-and-modularization-strategy-research.md)
- [Frontend Architecture Evolution Report](../../../frontend/frontend-architecture-evolution-report.md)
- [Frontend Domain Architecture](../ARCHITECTURE.md)
- [Frontend Domain Technical Design](../TECHNICAL_DESIGN.md)
- [Master System SRS](../../../system/SYSTEM_REQUIREMENTS_SPECIFICATION.md)
- [Documentation Methodology](../../../study-hub/project-documentation-and-specification-methodology.md)

## References

- [Vite Guide](https://vite.dev/guide/)
- [react-resizable-panels](https://github.com/bvaughn/react-resizable-panels)
- [TradingView Lightweight Charts](https://tradingview.github.io/lightweight-charts/)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [TanStack Query Overview](https://tanstack.com/query/latest/docs/framework/react/overview)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Radix UI Primitives](https://www.radix-ui.com/)
- [Vitest](https://vitest.dev/)
- [openapi-typescript Introduction](https://openapi-ts.dev/introduction)
- [MSW Documentation](https://mswjs.io/docs/)
- [Storybook Documentation](https://storybook.js.org/docs)

## Revision History

| Version | Date | Author | Change Summary |
|---------|------|--------|----------------|
| 0.1 | 2026-04-01 | Engineering | Initial ADR proposed |
| 0.2 | 2026-04-13 | Engineering | Standardized to project ADR discipline; migrated to `docs/domains/frontend/DECISIONS/`; added Document Control, Requirement Alignment, and Revision History |
| 0.3 | 2026-09-03 | Engineering | Incorporated multi-pane canvas (`react-resizable-panels`), dual-speed state (`Zustand` + `TanStack Query`), `lightweight-charts`, Generative UI SSE artifacts, Tailwind+Radix, and vertical-slice delivery |
| 0.4 | 2026-11-05 | Software Architect Assistant | Amend+Accept for M-000 Pitch B - Vite/Router/panels/Zustand/TQ/Tailwind+Radix/Vitest; HTTPS+SSE only; carve-outs GenUI Future, layout presets M-009, chart-yield M-006, Auth to Pitch A; cites SR-1.4.2, SNR-6.1.4, SNR-8.1.2 |
| 0.5 | 2026-11-13 | Software Architect Assistant | History note only; decision text unchanged. Token-colour bullet replaced by ADR-007 and the indicator claim by ADR-004 (both Accepted 2026-11-13) |
| 0.6 | 2026-11-13 | Software Architect Assistant | History note: G3 replaced in part by ADR-Frontend-003 (URL owns shareable state) |
| 0.7 | 2026-11-13 | Software Architect Assistant | History note: the MSW / Storybook "later phases" bullet replaced in part by ADR-Frontend-008 |
