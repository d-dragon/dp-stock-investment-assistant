# Pitch: M-000 Frontend foundation

| Field | Value |
|---|---|
| Milestone | [M-000 Platform foundation (identity + FE shell)](../../docs/system/PRODUCT_SPECIFICATION.md#m-000) |
| Priority | P0 (from M-000) |
| Requirements covered | FR: [SR-1.4.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-4-1), [SR-1.4.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-4-2) (shell store), [SR-5.1.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-5-1-2) · NFR: [SNR-6.1.4](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-6-1-4), [SNR-8.1.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-8-1-2), [SNR-7.1.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md), [SNR-7.2.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md) (priority stays P2) · [SR-5.2.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-5-2-1) / [SR-5.2.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-5-2-2) remain Superseded |
| Status | Draft (shaped-draft) |
| Appetite | 3 weeks *(proposed, to confirm by Product Owner)* |
| Cost | Team time within the appetite; no paid service, licensed data provider or model spend expected *(estimate, Product Owner to confirm)* |
| Slices | B1 vite-shell-and-subtract — SNR-6.1.4 (path), T0; B2 api-types-and-sse — SR-5.1.2, SNR-8.1.2; B3 modular-shell-and-safe-render — SR-1.4.1, SR-1.4.2, T4; B4 tokens-i18n-and-chart-seams — SNR-7, ADR-007 / 005 / 004; B5 msw-storybook-and-ci — SNR-6.1.4, SNR-7.1.1, ADR-FRONTEND-008 *(proposed, may change in delivery; not created yet)* |
| Last re-ranked | 2026-11-13 |
| References | Architecture: [frontend ARCHITECTURE](../../docs/domains/frontend/ARCHITECTURE.md), [ADR-FRONTEND-001](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-001-MODULAR-APPLICATION.md) (Accepted), [ADR-FRONTEND-002](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md) (Accepted), [ADR-FRONTEND-003](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-003-URL-OWNED-SHAREABLE-STATE.md) (Accepted), [ADR-FRONTEND-004](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-004-CHART-ENGINE-ADAPTER.md) (Accepted), [ADR-FRONTEND-005](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-005-I18N-READINESS-SEAM.md) (Accepted), [ADR-FRONTEND-007](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-007-DESIGN-TOKEN-ARCHITECTURE.md) (Accepted), [ADR-FRONTEND-008](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-008-MSW-AND-STORYBOOK-IN-M000.md) (Accepted, 2026-11-13) · Realization: [TECHNICAL_DESIGN](../../docs/domains/frontend/TECHNICAL_DESIGN.md) §6, §8–§10 · Design: [DESIGN_LOCK](../../docs/domains/frontend/DESIGN_LOCK.md), [DESIGN_SYSTEM](../../docs/domains/frontend/DESIGN_SYSTEM.md) · Contract: [`docs/openapi.yaml`](../../docs/openapi.yaml) · Sibling: [M-000 Identity and session](M-000-A-identity-and-session.md); [M-001](M-001-adaptive-visual-canvas.md) (Canvas waits on this shell) |

## Problem
[M-001 Adaptive Visual Canvas](M-001-adaptive-visual-canvas.md) needs a modular Frontend shell, design tokens, a locale-correct format seam, chart-adapter boundaries, an SSE-only transport, and a test baseline. The current app is still on deprecated Create React App, mixes JavaScript and TypeScript, has no route-based zone shell, no contract-generated API types, no automated Frontend tests, and still carries a Socket.IO client that the target has retired. Thin CRA-only prep was already rejected. Without this foundation, Canvas work would keep fighting the chat-era Frontend.

## Appetite
3 weeks *(proposed, to confirm by Product Owner)*: five slices (B1–B5), covering the CRA → Vite migration, the API and SSE cut-over, the modular shell and safe Agent rendering, tokens / i18n / chart seams, and MSW + Storybook + CI. Product §5.3 already frames M-000 as "flexible / agentic OK"; three weeks is a shaping estimate and is tight for this breadth. If the bet runs over, Backend-side HTTP/2 / stream-contract work is the first to stay a follow-up rather than hold the Frontend slices. Identity and login are [Pitch A](M-000-A-identity-and-session.md), not this appetite.

## Solution sketch (foundation shell, not Canvas product UI)
Realization detail lives in [TECHNICAL_DESIGN](../../docs/domains/frontend/TECHNICAL_DESIGN.md) (gates G1–G6, steps T0–T8). This pitch is the bet, not a second technical design.

- **B1 — Vite shell and subtract (T0).** Replace Create React App with Vite per [ADR-FRONTEND-001](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-001-MODULAR-APPLICATION.md) and [ADR-FRONTEND-002](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md). Step **T0** deletes unused unsafe `MessageFormatter.js` (latent XSS via unescaped `dangerouslySetInnerHTML`; not imported today; Product Owner, 2026-11-10) and the other unused files listed in TECHNICAL_DESIGN §10.2. Vitest is wired so a first smoke test can run ([SNR-6.1.4](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-6-1-4) path).

  Acceptance: `npm run build` and `npm run dev` work on Vite; `MessageFormatter.js` is gone and has no remaining references; Vitest runs.

- **B2 — OpenAPI types, SSE-only transport, and Socket.IO removal.** Frontend API types are generated from [`docs/openapi.yaml`](../../docs/openapi.yaml) ([ADR-FRONTEND-002](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md)); CI fails if the generated file drifts. Client transport is HTTPS + SSE only ([SR-5.1.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-5-1-2), [SNR-8.1.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-8-1-2); [SR-5.2.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-5-2-1) and [SR-5.2.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-5-2-2) stay Superseded). The chat stream response sends `Cache-Control: no-cache` and `X-Accel-Buffering: no`, a comment heartbeat at least every 15 s (heartbeat ≤ 15 s), and ingress is HTTP/2 so open streams do not starve REST calls on HTTP/1.1's per-origin limit. The client treats a missed heartbeat window as `interrupted`. Step **T8** removes `socket.io-client` and blocks its return (TECHNICAL_DESIGN §6.4). Stream headers, heartbeat and HTTP/2 are a Backend contract ask; this slice delivers the Frontend client and the Socket.IO removal, and records the Backend follow-up.

  Acceptance: generated types are committed and CI-checked; chat streams over SSE only; `socket.io-client` is absent from `package.json` and the bundle; the client honours the heartbeat window; a lint rule stops Socket.IO from coming back.

- **B3 — Modular shell, state, and safe rendering (T4).** React Router, Zustand and TanStack Query implement the dual-speed state baseline ([ADR-FRONTEND-002](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md), [ADR-FRONTEND-003](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-003-URL-OWNED-SHAREABLE-STATE.md)). The shell hosts zones Z1–Z4 as distinct composition slots so later Canvas features can mount without rewriting it ([SR-1.4.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-4-1)). The in-session workspace context (active track, focused symbol, open Core-object reference, and Z4 `sessionRef`) is shared without copying Backend session state ([SR-1.4.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-4-2)); the URL owns shareable state and the store only mirrors it; the Z4 unsent draft lives in `sessionStorage`. The identity meaning of `sessionRef` is [Pitch A](M-000-A-identity-and-session.md). Step **T4** splits the current app into the shell and feature modules, adds `MessageBody` (`react-markdown`, no raw HTML, unsafe schemes blocked), and ships the XSS regression tests (TECHNICAL_DESIGN §6.5, §10.2). `react/no-danger` is an error.

  Acceptance: four zone landmarks render; a throw in one zone leaves the others standing; a deep link sets the store mirrors and the store does not change shareable state except by navigating; `MessageBody` renders the XSS cases inert (no event-handler attributes, no `script`, no `javascript:` href) while markdown still works.

- **B4 — Tokens, vi-VN format, and chart-adapter seams.** Tailwind CSS with shadcn/Radix primitives, and design tokens per [ADR-FRONTEND-007](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-007-DESIGN-TOKEN-ARCHITECTURE.md). A vi-VN message catalogue and one format module per [ADR-FRONTEND-005](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-005-I18N-READINESS-SEAM.md): launch UI is `vi-VN` (`Asia/Ho_Chi_Minh`); board-style prices use a dot decimal and two places (`25.30`); percent change uses the same dot (`+6.98%`); volume is a whole number of shares with comma grouping and no decimals (`1,234,500`; Product Owner, 2026-11-13), so in a price row the dot always means a decimal; ₫ totals use comma grouping (`25,300,000 ₫`; Product Owner, 2026-11-13); across all numbers the dot is only a decimal and the comma only groups thousands; dates stay standard `vi-VN`. Translation adoption stays Future. Viewport support is 768–1920 px, with 1920 px primary ([SNR-7.1.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md); below 768 px is Future). `ChartEngine` (price charts, Lightweight Charts) and `stat-chart` (non-price charts, Chart.js: macro graphs, breakdown bars, allocation donuts) land as adapter seams with lint rules so feature code cannot import either library directly ([ADR-FRONTEND-004](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-004-CHART-ENGINE-ADAPTER.md)). The docked chart proof of concept itself stays in M-001 S3; this slice only ships the seams.

  Acceptance: `fmt.price(25300) === '25.30'`, `fmt.pct(0.0698) === '+6.98%'`, `fmt.volume(1234500) === '1,234,500'`, `fmt.vnd(25300000) === '25,300,000 ₫'`; dates stay standard `vi-VN`; every user-facing string goes through `t()`; lint fails on a feature-level chart-library import; tokens are generated and themed.

- **B5 — MSW, Storybook, and Frontend CI.** [ADR-FRONTEND-008](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-008-MSW-AND-STORYBOOK-IN-M000.md) (Accepted by the Product Owner, 2026-11-13) brings MSW and Storybook into M-000. MSW handlers, typed from the OpenAPI-generated types, serve the same fixtures in development and in Vitest; neither MSW nor Storybook ships in the production bundle; mock versus live is a build-time setting. Storybook is the catalogue for platform and design-system components and zone states. Frontend CI runs Vitest and React Testing Library, plus Playwright with axe at **1920, 1440, 1024 and 768** px ([SNR-6.1.4](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-6-1-4), [SNR-7.1.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md)). The WCAG 2.2 AA target ([SNR-7.2.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md)) is exercised by axe and stays **P2** (not raised to P1).

  Acceptance: the same MSW handlers work in the browser and in tests; the production build does not bundle `src/mocks/` or Storybook; CI runs unit/component tests and Playwright + axe at the four widths; axe reports no serious or critical issues on shell routes, without changing SNR-7.2.1's priority.

## Rabbit holes
- Growing this bet into M-001 Canvas zones, or building the docked chart proof of concept here (that is M-001 S3).
- **[ADR-FRONTEND-006](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-006-GENERATED-UI-COMPONENT-REGISTRY.md) (Proposed — Future).** GenUI stays out.
- Micro-frontend decomposition ([ADR-FRONTEND-001](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-001-MODULAR-APPLICATION.md) already rejected this for now).
- Raising [SNR-7.2.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md) from P2 to P1.
- Using Chart.js for price charts, or importing a chart library from feature code.
- Inventing typed stream events, resume or cancel in this pitch (Backend follow-up on `docs/openapi.yaml`).
- Choosing an i18n library or shipping an English catalogue (Future, ADR-FRONTEND-005).
- Saved layout presets (Milestone [M-009](../../docs/system/PRODUCT_SPECIFICATION.md#m-009)).

## Risks
- Stream headers, heartbeat ≤ 15 s and HTTP/2 ingress are a Backend contract ask. The Frontend client can land without them; G6 delivery quality cannot be fully shown until the Backend follows.
- The CRA → Vite move on a mixed JavaScript / TypeScript tree can overrun B1.
- If T0 or T4 slips, the unused `MessageFormatter.js` XSS hole remains in the tree (latent, not live, but still a hole).
- Three weeks is tight for five slices; without a Product Owner confirm, the bet may need the "flexible / agentic OK" reading already in Product §5.3.

## No-gos
- Identity, login, or owner-isolation product behavior ([Pitch A](M-000-A-identity-and-session.md); [ADR-SYS-001](../../docs/architecture/DECISIONS/ADR-SYS-001-IDENTITY-AND-PER-USER-ISOLATION.md)).
- M-001 zone layout, the docked chart proof-of-concept content, or a working Decision gate.
- A production market-data feed or licensed provider (M-001 S3 uses prepared mock data; provider choice stays with ADR-SYS-004).
- Computing reference, ceiling or floor prices in the Frontend.
- Socket.IO or WebSocket in the target transport.
- Micro-frontends; Pitch C (deferred).
- Raising WCAG 2.2 AA ([SNR-7.2.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md)) to P1.

## Done means
- [SR-1.4.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-4-1), the shell side of [SR-1.4.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-4-2), [SR-5.1.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-5-1-2), [SNR-6.1.4](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-6-1-4) and [SNR-8.1.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-8-1-2) are `verified`. [SNR-7.1.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md) is exercised at 1920 / 1440 / 1024 / 768; [SNR-7.2.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md) has an axe baseline and stays P2.
- T0 (`MessageFormatter.js` gone) and T4 (`MessageBody` plus regression tests) are closed.
- [M-001](M-001-adaptive-visual-canvas.md) can start without another foundation rewrite.
- Given/When/Then acceptance, including the UX Designer's criteria, lives in each slice's `spec.md`.

## Open questions
- [NEEDS CLARIFICATION] Is the 3-week appetite right for B1–B5, or should this stay "flexible / agentic OK" as in Product §5.3?
- [NEEDS CLARIFICATION] Is the cost estimate right: team time only, with no paid service or model spend?
- [NEEDS CLARIFICATION] When will the Backend land stream headers (`Cache-Control: no-cache`, `X-Accel-Buffering: no`), a heartbeat ≤ 15 s, and HTTP/2 at ingress, so the G6 delivery requirements can be shown end-to-end?
- *Decided 2026-11-10:* the latent XSS in unused `MessageFormatter.js` is not patched as a one-off; T0 deletes the file and T4 adds `MessageBody` with regression tests (TECHNICAL_DESIGN §6.5, §10.2).
- *Decided 2026-11-13:* launch UI is `vi-VN`; prices use the board style (`25.30`); percent change uses the dot (`+6.98%`); volume is whole shares with comma grouping (`1,234,500`); ₫ totals use comma grouping (`25,300,000 ₫`); across all numbers the dot is only a decimal and the comma only groups thousands; dates stay standard `vi-VN`.
- *Decided 2026-11-13:* Chart.js is for non-price charts only, behind the `stat-chart` adapter; price charts stay on Lightweight Charts behind `ChartEngine` ([ADR-FRONTEND-004](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-004-CHART-ENGINE-ADAPTER.md)).
- *Decided 2026-11-13:* supported viewport is 768–1920 px, with 1920 px primary ([SNR-7.1.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md)); WCAG 2.2 AA ([SNR-7.2.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md)) stays P2.
- *Decided 2026-11-13:* MSW and Storybook join M-000 ([ADR-FRONTEND-008](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-008-MSW-AND-STORYBOOK-IN-M000.md), Accepted). Neither ships to production.
- *Decided 2026-11-13:* `sessionRef` is the Backend session id plus the conversation id; the shell store (this pitch) holds the references only. Client transport is SSE only; SR-5.2.1 and SR-5.2.2 are Superseded.
