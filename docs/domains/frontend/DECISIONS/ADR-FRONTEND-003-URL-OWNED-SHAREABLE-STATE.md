# ADR-Frontend-003: The URL Owns Shareable Workspace State; the Store Mirrors It

## Document Control

| Field | Value |
|-------|-------|
| **ADR ID** | ADR-Frontend-003 |
| **Domain** | Frontend |
| **Standards Stance** | Practice-Based ADR discipline |
| **Status** | Accepted |
| **Date** | 2026-11-10 |
| **Last Updated** | 2026-11-13 |
| **Decision Owners** | Engineering · Architecture · Frontend maintainers |

## Context

[ADR-Frontend-002](./ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md) adopts React Router and a Zustand fast lane, and gate G3 puts `activeTrack`, `symbol` and `coreObjectRef` in a session store (**SR-1.4.2**). From M-003 onward the workspace opens Evidence, Theses, Decisions and Positions. An investor needs to reload, bookmark or share "this Thesis on this symbol" and land in the same place. If the same value lives in both the URL and the store with no owner, the two drift: back/forward navigation, reloads and deep links stop agreeing with what the zones show.

## Decision

- The **URL owns shareable, navigational state**: the open route, which carries `track`, `symbol` and `coreObjectRef`.
- The **store mirrors** those values for fast subscription and **never writes them back except by navigating**.
- The store **owns session-only state**: pane sizes and UI flags. It mirrors `track` from the route like the other URL values.
- The **store owns per-symbol context** as an investor preference, keyed by symbol or index code: the last open object, chart range, interval, series type and Z4 scroll position. It is not part of the URL. In M-000 it is kept in `sessionStorage`; a durable per-user copy follows identity (Pitch A) and saved layouts (M-009). Product Owner decision 2026-11-13.
- The Backend owns the Z4 thread and every Core object. `sessionRef` is the Backend session id plus conversation id (`docs/openapi.yaml`); the unsent Z4 draft is kept in `sessionStorage` per conversation. The active Backend workspace is a store-held reference, assuming one active workspace per investor until a Milestone needs more. The URL carries references, never Core content.
- A route that names an object the user cannot see renders a not-found state; access is decided by the Backend.

## Considered Options

| Option | Outcome |
|--------|---------|
| URL owns shareable state, store mirrors (chosen) | One source of truth; deep links and reloads work |
| Store owns everything, URL ignored | Rejected: no deep links, reload loses context |
| Store owns, URL synced both ways | Rejected: two writers, loop and drift risk |
| Chart range and per-symbol context in the URL | Rejected 2026-11-13: it is a personal preference, not link content |

## Consequences

- Positive: reload-safe and shareable workspace; browser history works; tests can start from a URL.
- Negative: route shapes become a public surface and need care when renamed.
- Negative: a shared link opens the object but not the sender's chart range or scroll position.
- Negative: [DESIGN_LOCK.md](../DESIGN_LOCK.md) §2 must change so it no longer lists `symbol` and `coreObjectRef` as store-owned (Designer follow-up).
- Route map and sync mechanism belong to [TECHNICAL_DESIGN.md](../TECHNICAL_DESIGN.md).

## Requirement Alignment

| Requirement | Relevance |
|-------------|-----------|
| **SR-1.4.2** In-session workspace context | Context survives track switch; URL adds reload safety |
| **SR-1.3.2** Context preserved on switching | Open work kept per track and per symbol or index |

## Related Documents

- [Frontend Domain Architecture](../ARCHITECTURE.md) §4.2, §6.1, §6.3a
- [ADR-Frontend-002](./ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md)

## References

- [React Router](https://reactrouter.com/)

## Revision History

| Version | Date | Author | Change Summary |
|---------|------|--------|----------------|
| 0.1 | 2026-11-10 | Software Architect Assistant | Proposed; horizon M-000 to M-009 agreed with the Product Owner |
| 0.2 | 2026-11-13 | Software Architect Assistant | Accepted by the Product Owner after the review round; per-symbol context owned by the store; `sessionRef` = session + conversation id; Z4 draft in `sessionStorage`; fast ticks removed (Future) |
| 0.3 | 2026-11-13 | Software Architect Assistant | Same-day correction before first commit: the track is part of the route, so the URL owns it and the store mirrors it (matches TECHNICAL_DESIGN §5 and DESIGN_LOCK) |
