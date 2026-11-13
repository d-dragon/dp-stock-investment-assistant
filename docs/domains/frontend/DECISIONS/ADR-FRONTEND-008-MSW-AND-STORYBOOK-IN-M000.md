# ADR-Frontend-008: MSW and Storybook Join the M-000 Foundation

## Document Control

| Field | Value |
|-------|-------|
| **ADR ID** | ADR-Frontend-008 |
| **Domain** | Frontend |
| **Standards Stance** | Practice-Based ADR discipline |
| **Status** | Accepted |
| **Date** | 2026-11-13 |
| **Last Updated** | 2026-11-13 |
| **Decision Owners** | Engineering · Architecture · UX / UI Designer |
| **Replaces in part** | [ADR-Frontend-002](./ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md) Decision bullet treating MSW and Storybook as accelerators for later phases |

## Context

[ADR-Frontend-002](./ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md) (Accepted) treats [MSW](https://mswjs.io/docs/) and [Storybook](https://storybook.js.org/docs) as accelerators for later phases, not M-000 prerequisites. Two Product Owner decisions on 2026-11-13 change that:

- The M-001 S3 chart proof of concept runs on **prepared mock data** in the Research Sandbox, not on a live market feed ([M-001 pitch](../../../../specs/pitches/M-001-adaptive-visual-canvas.md), H1). The browser needs a way to serve those fixtures through the same HTTP calls the real Backend will answer.
- The design system ([DESIGN_LOCK.md](../DESIGN_LOCK.md), [DESIGN_SYSTEM.md](../DESIGN_SYSTEM.md)) defines zone states (empty, loading, ready, stale, error, interrupted, streaming) and price-cell rules that need a place to be seen and checked component by component before a Backend exists.

## Decision

- **MSW enters M-000.** Network mocks are request handlers at the HTTP boundary, typed from the OpenAPI-generated types ([ADR-002](./ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md)). The same handlers and fixtures serve the browser in development and the Vitest suites, so a fixture is written once.
- **Fixtures are prepared data, not production data.** They follow the M-001 mock-data rules (reference, ceiling and floor bands; board-style prices) and carry no claim of market accuracy.
- **Storybook enters M-000** as the component catalogue for platform and design-system components and their zone states.
- **Neither ships to production.** Both stay out of the production bundle; the application code never imports MSW or Storybook.
- **Mock vs live is a build-time setting**, not a feature flag inside features. Features call the API layer the same way in both modes.
- Setup, file layout, scripts and whether Storybook also runs visual regression belong to [TECHNICAL_DESIGN.md](../TECHNICAL_DESIGN.md).
- This ADR replaces only ADR-002's MSW / Storybook "later phases" bullet; the rest of ADR-002 stands.

## Considered Options

| Option | Outcome |
|--------|---------|
| MSW and Storybook in M-000 (chosen) | One fixture source for browser and tests; components checked in isolation from day one |
| Static JSON imported by components | Rejected: bypasses the API layer, so swapping to the real Backend touches feature code |
| A local mock server process | Rejected: one more process to run; duplicates what MSW does in the browser and tests |
| Keep both for later phases (ADR-002 as written) | Rejected: blocks the M-001 S3 proof of concept on mock data |

## Consequences

- Positive: the M-001 chart and M-000 shell can be built and demonstrated without a Backend or market data provider.
- Positive: switching to the real Backend changes configuration, not features.
- Negative: two more dev dependencies to keep current; fixtures can drift from the OpenAPI contract unless handlers stay typed from it.
- Follow-up (Coding Orchestrator): MSW and Storybook setup in TECHNICAL_DESIGN; fixtures from the M-001 mock-data rules.

## Requirement Alignment

| Requirement | Relevance |
|-------------|-----------|
| **SR-1.3.5** Docked price chart (proof of concept) | Served from prepared fixtures in M-001 |
| **SNR-6.1.4** Frontend testability baseline | Same handlers in Vitest and the browser |
| **SNR-7** Usability, Accessibility, and Responsive Behavior | Zone states visible per component in Storybook |

## Related Documents

- [Frontend Domain Architecture](../ARCHITECTURE.md) §5.1
- [ADR-Frontend-002](./ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md), [ADR-Frontend-004](./ADR-FRONTEND-004-CHART-ENGINE-ADAPTER.md)
- [M-001 pitch](../../../../specs/pitches/M-001-adaptive-visual-canvas.md)

## References

- [MSW Documentation](https://mswjs.io/docs/)
- [Storybook Documentation](https://storybook.js.org/docs)

## Revision History

| Version | Date | Author | Change Summary |
|---------|------|--------|----------------|
| 0.1 | 2026-11-13 | Software Architect Assistant | Accepted by the Product Owner the same day it was proposed |
