# Pitch: M-000 Frontend foundation

| Field | Value |
|---|---|
| Milestone | [M-000 Platform foundation (identity + FE shell)](../../docs/system/PRODUCT_SPECIFICATION.md#m-000) |
| Priority | P0 (from M-000) |
| Requirements covered | FR: [SR-1.4.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-4-1), [SR-1.4.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-4-2) (shell store), [SR-5.1.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-5-1-2) · NFR: [SNR-6.1.4](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-6-1-4), [SNR-8.1.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-8-1-2), [SNR-7.1.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md), [SNR-7.2.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md) (priority stays P2) · [SR-5.2.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-5-2-1) / [SR-5.2.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-5-2-2) remain Superseded |
| Status | Shaped — ready for implementation (Product Owner, 2026-11-17; no open questions) |
| Appetite | 1 week (Product Owner, 2026-11-17; agentic delivery: Grok Build implements from Spec Kit slice specs) |
| Cost | Team time within the appetite; no paid service, licensed data provider or model spend expected (Product Owner, 2026-11-17) |
| Slices | Order: B0 → B1 → B2 alongside thin B4 → B3 → thin B5 (Product Owner, 2026-11-17). B0 agent-instructions — no T-step; B1 vite-shell-and-subtract — T0–T2, SNR-6.1.4 (path); B2 api-client-and-sse — codegen (TECHNICAL_DESIGN §6.1) + T3 + T8, SR-5.1.2, SNR-8.1.2 (Frontend part); B3 modular-shell-and-safe-render — T4 + T5, SR-1.4.1, SR-1.4.2; B4 tokens-format-and-lint-seams (thin) — T6 + part of T7 + §8.3, SNR-7, ADR-007 / 005 / 004; B5 msw-storybook-and-ci (thin) — T7 + Storybook, CI and Playwright, SNR-6.1.4, SNR-7.1.1, [ADR-FRONTEND-008](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-008-MSW-AND-STORYBOOK-IN-M000.md) (Accepted, 2026-11-13) |
| Last re-ranked | 2026-11-13 |
| References | Architecture: [frontend ARCHITECTURE](../../docs/domains/frontend/ARCHITECTURE.md), [ADR-FRONTEND-001](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-001-MODULAR-APPLICATION.md) (Accepted), [ADR-FRONTEND-002](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md) (Accepted), [ADR-FRONTEND-003](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-003-URL-OWNED-SHAREABLE-STATE.md) (Accepted), [ADR-FRONTEND-004](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-004-CHART-ENGINE-ADAPTER.md) (Accepted), [ADR-FRONTEND-005](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-005-I18N-READINESS-SEAM.md) (Accepted), [ADR-FRONTEND-007](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-007-DESIGN-TOKEN-ARCHITECTURE.md) (Accepted), [ADR-FRONTEND-008](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-008-MSW-AND-STORYBOOK-IN-M000.md) (Accepted, 2026-11-13) · Realization: [TECHNICAL_DESIGN](../../docs/domains/frontend/TECHNICAL_DESIGN.md) §6, §8–§10 · Design: [DESIGN_LOCK](../../docs/domains/frontend/DESIGN_LOCK.md), [DESIGN_SYSTEM](../../docs/domains/frontend/DESIGN_SYSTEM.md) · Contract: [`docs/openapi.yaml`](../../docs/openapi.yaml) · Sibling: [M-000 Identity and session](M-000-A-identity-and-session.md); [M-001](M-001-adaptive-visual-canvas.md) (Canvas waits on this shell) |

## Problem
[M-001 Adaptive Visual Canvas](M-001-adaptive-visual-canvas.md) needs a modular Frontend shell, design tokens, a locale-correct format seam, chart-adapter boundaries, an SSE-only transport, and a test baseline. The current app is still on deprecated Create React App, mixes JavaScript and TypeScript, has no route-based zone shell, no contract-generated API types, no automated Frontend tests, and still carries a Socket.IO client that the target has retired. Thin CRA-only prep was already rejected. Without this foundation, Canvas work would keep fighting the chat-era Frontend.

## Appetite
1 week (Product Owner, 2026-11-17): six thin slices (B0–B5), an initial stage that later Milestones build on: the agent-instruction rewrite, the CRA → Vite migration, the API client and SSE cut-over, the modular shell and safe Agent rendering, dark tokens / format / i18n / chart-import lint, and a minimal MSW + Storybook + CI baseline. The week assumes agentic delivery (see [Delivery workflow](#delivery-workflow-agentic)): a coding agent (Grok Build) implements each slice from its Spec Kit spec, and people shape, review and approve. The cut line (Product Owner, 2026-11-17) already moves the chart interfaces, price mocks, the light theme and theme switching, the contrast script, token Storybook pages, F6 zone-cycling tests and visual snapshots to [M-001](M-001-adaptive-visual-canvas.md). If the week still runs short, Playwright drops to 1920 and 768 px only; T0, the `MessageBody` XSS tests and the B2 client are never cut. Backend-side stream headers, heartbeat and HTTP/2 are a later Backend pitch and are not in this appetite. Identity and login are [Pitch A](M-000-A-identity-and-session.md), not this appetite.

## Solution sketch (foundation shell, not Canvas product UI)
Realization detail lives in [TECHNICAL_DESIGN](../../docs/domains/frontend/TECHNICAL_DESIGN.md) (gates G1–G6, steps T0–T8). This pitch is the bet, not a second technical design.

**Principle (Product Owner, 2026-11-17): fresh, clean rebuild.** This pitch is a fresh, clean redesign and reimplementation of the Frontend. Refactoring or replacing the current implementation is acceptable and expected, and legacy code is not preserved for its own sake; B1's deletions and replacements follow from this. The Accepted ADRs, the OpenAPI contract (`docs/openapi.yaml`) and `backend/` still must not change.

- **B0 — Agent instructions on the target stack (no T-step; first).** Today the agent instruction files still describe Create React App, Jest and Socket.IO, which is the largest regression risk for agentic delivery. Grok Build loads `AGENTS.md`, `AGENT.md` and `CLAUDE.md` files plus `.grok/rules/*.md`, and a nested file overrides its parent ([Grok Build project rules](https://docs.x.ai/build/features/project-rules)). B0 therefore adds a short `frontend/AGENTS.md` (under 10,000 characters), rewrites the frontend lines in the root `AGENTS.md`, removes or rewrites any stale `CLAUDE.md`, `.claude/rules` or `.cursor/rules` content, and updates `.github/instructions/frontend-react.instructions.md` (read by Copilot only) so it does not drift. Target rules: Vite and Vitest; `VITE_*` environment variables only; no `socket.io-client`, WebSocket or EventSource; `fetch` only inside `platform/api` and `platform/stream`; the TECHNICAL_DESIGN §3.1 / §3.3 module tree and lint rules.

  Acceptance: `grok inspect`, run from `frontend/`, lists the new rules; no instruction file still recommends CRA, Jest, `REACT_APP_*` or Socket.IO.

  Agent constraints — T-steps: none. Instruction files only; no source, test or config change.

- **B1 — Vite shell and subtract (T0–T2).** Replace Create React App with Vite per [ADR-FRONTEND-001](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-001-MODULAR-APPLICATION.md) and [ADR-FRONTEND-002](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md). Step **T0** deletes unused unsafe `MessageFormatter.js` (latent XSS via unescaped `dangerouslySetInnerHTML`; not imported today; Product Owner, 2026-11-10) and the other unused files listed in TECHNICAL_DESIGN §10.2. T1 moves the build, config and environment to Vite; T2 wires Vitest, the MSW base setup and the G1 smoke test ([SNR-6.1.4](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-6-1-4) path). B1 also adds a Frontend CI skeleton (lint, then `tsc --noEmit`, then Vitest, then build) and pulls lint rules 1–3 and `react/no-danger` forward from later slices.

  Acceptance: `npm run build` and `npm run dev` work on Vite; `MessageFormatter.js` is gone and has no remaining references; Vitest runs; the Docker image builds; the CI skeleton runs without changing the trigger of the existing Docker workflow.

  Agent constraints — T-steps: T0–T2.
  - Architecture ([ADR-SYS-001](../../docs/architecture/DECISIONS/ADR-SYS-001-IDENTITY-AND-PER-USER-ISOLATION.md), BFF): Vite `server.proxy` sends `/api` to `:5000` on the same origin; `VITE_API_BASE_URL` defaults to empty; no credentialed CORS.
  - Known traps the spec must name: `frontend/Dockerfile` copies `/app/build`, but Vite writes `dist`; `process.env.REACT_APP_*` at `config.ts:3,11`, `modelsApi.ts:11` and `WebSocketTest.tsx:254` breaks under Vite; `App.tsx:30` hard-codes `http://localhost:5000`, which bypasses the proxy; TypeScript is not declared in `package.json` (4.9.5 arrives transitively; MSW 3 needs 5.9+); `config-overrides.js` and `webpack.config.dev.js` are dead; tsconfig has `target es5` and `moduleResolution node`; the Dockerfile uses `node:20-alpine` (Node 20 is end-of-life).
  - Node pin (Product Owner, 2026-11-17): Node 26, the current LTS line. `frontend/.nvmrc` = `26`; `engines.node` = `">=26.13.0"`; `frontend/.npmrc` with `engine-strict=true`; the Dockerfile uses `node:26-alpine`. jsdom is the Vitest DOM environment. Prerequisite: the Product Owner installs Node v26.13.1 locally before the first B1 run.
  - Proving commands: `rg -n "MessageFormatter|dangerouslySetInnerHTML|REACT_APP_" src` returns nothing; the Docker build succeeds.

- **B2 — API client, OpenAPI types, SSE-only transport, and Socket.IO removal (codegen + T3 + T8).** Frontend API types are generated from [`docs/openapi.yaml`](../../docs/openapi.yaml) ([ADR-FRONTEND-002](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md), TECHNICAL_DESIGN §6.1); CI fails if the generated file drifts. Client transport is HTTPS + SSE only ([SR-5.1.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-5-1-2), [SNR-8.1.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-8-1-2); [SR-5.2.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-5-2-1) and [SR-5.2.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-5-2-2) stay Superseded). Step **T3** builds one client in `platform/api` and the stream reader in `platform/stream`; step **T8** removes `socket.io-client` and blocks its return (TECHNICAL_DESIGN §6.4). The Backend stream is not changed here: stream headers, heartbeat and HTTP/2 land in a later Backend pitch (Product Owner, 2026-11-17). This slice makes the client ready for them: it tolerates `:` comment lines, applies a configurable idle timeout, and is proven against an MSW stream fixture, so the Backend work can plug in without a Frontend change.

  Acceptance: generated types are committed and CI-checked; chat streams over SSE only; `socket.io-client` is absent from `package.json` and the bundle; against an MSW stream fixture the client accepts comment lines and moves the stream to `interrupted` when the idle timeout passes; a lint rule stops Socket.IO from coming back; SNR-8.1.2 is recorded as "Frontend part verified".

  Agent constraints — T-steps: codegen (TECHNICAL_DESIGN §6.1) + T3 + T8.
  - Architecture (ADR-SYS-001, BFF): one client in `platform/api` sends `credentials: 'same-origin'` on every request, including the stream. A request hook adds `AuthAdapter.csrfHeaders()` to POST, PUT, PATCH and DELETE; a 401 calls `onUnauthorized`. No `Authorization` header and no token in JavaScript, storage or fixtures. The slice ships `NoAuthAdapter`; tests use a fake adapter. The `/api/auth/*` routes stay in [Pitch A](M-000-A-identity-and-session.md).
  - No global `X-User-ID`. Pitch B calls only health, config, `models/*` and chat. `sessionRef` is an opaque `{sessionId, conversationId}`. MSW covers only paths already in `docs/openapi.yaml`; `GET /api/market/prices/{symbol}` is out of Pitch B (M-001 S3).
  - Stream API: `openChatStream(body, { signal, idleTimeoutMs })`. The parser keeps the `id`, `event` and `retry` fields; `legacyChatAdapter` sits behind a `StreamAdapter` interface. Stream event names appear only in the `StreamEvent` union and the adapter, enforced by lint. Only one open chat stream per tab.
  - Idle timeout (Product Owner, 2026-11-17): the value comes from `VITE_STREAM_IDLE_TIMEOUT_MS` and defaults to `60000` ms in live mode; it is configurable and never hard-coded, so the default can drop with no code change once the Backend sends a heartbeat in a later pitch (no ADR change needed). Any received line, including `:` comments, resets the timer. On timeout the stream aborts and moves to `interrupted` with the "Tạo lại" (Retry) action; the Z4 draft and any partial message stay as they are. `frontend/.env.example` documents the 60 s default as a stopgap that the later Backend heartbeat pitch will tighten. MSW tests use `15000` ms with fake timers.
  - Proving commands: `npm run gen:api && git diff --exit-code src/platform/api/generated` passes; `rg socket.io dist` returns nothing; a fake-timer idle-timeout (heartbeat) test passes.

- **B3 — Modular shell, state, and safe rendering (T4 + T5).** React Router, Zustand and TanStack Query implement the dual-speed state baseline ([ADR-FRONTEND-002](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md), [ADR-FRONTEND-003](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-003-URL-OWNED-SHAREABLE-STATE.md)). The shell hosts zones Z1–Z4 as distinct composition slots so later Canvas features can mount without rewriting it ([SR-1.4.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-4-1)). The in-session workspace context (active track, focused symbol, open Core-object reference, and Z4 `sessionRef`) is shared without copying Backend session state ([SR-1.4.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-4-2)); the URL owns shareable state and the store only mirrors it; the Z4 unsent draft lives in `sessionStorage`. The identity meaning of `sessionRef` is [Pitch A](M-000-A-identity-and-session.md). Step **T4** splits the current app into the shell and feature modules, adds `MessageBody` (`react-markdown`, no raw HTML, unsafe schemes blocked), and ships the XSS regression tests (TECHNICAL_DESIGN §6.5, §10.2); step **T5** completes the shell state and zone wiring. `react/no-danger` is an error.

  Acceptance: four zone landmarks render; a throw in one zone leaves the others standing; a deep link sets the store mirrors and the store does not change shareable state except by navigating; `MessageBody` renders the XSS cases inert (no event-handler attributes, no `script`, no `javascript:` href) while markdown still works; the "AI gợi ý" and "Đã xác nhận" labels come through `t()`; the zone frames meet the UX Designer's B3 criteria in [Design acceptance criteria](#design-acceptance-criteria-ux).

  Agent constraints — T-steps: T4 + T5. Files: `src/app/**`, `src/features/**`, `MessageBody`.
  - Proving commands: `npm run lint` passes with `react/no-danger`; the G2 / G3 and XSS tests pass.

- **B4 — Dark tokens, vi-VN format, i18n seam and chart-import lint (thin).** Design tokens per [ADR-FRONTEND-007](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-007-DESIGN-TOKEN-ARCHITECTURE.md): this week ships the dark tokens and the `data-theme` hook only; the light theme, theme switching, the contrast script and Tailwind / shadcn primitives beyond what the shell needs move to M-001. A vi-VN message catalogue and one format module per [ADR-FRONTEND-005](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-005-I18N-READINESS-SEAM.md): launch UI is `vi-VN` (`Asia/Ho_Chi_Minh`); board-style prices use a dot decimal and two places (`25.30`); percent change uses the same dot (`+6.98%`); volume is a whole number of shares with comma grouping, no decimals and no compact notation (`1,234,500`; Product Owner, 2026-11-13), so in a price row the dot always means a decimal; ₫ totals use comma grouping (`25,300,000 ₫`; Product Owner, 2026-11-13); across all numbers the dot is only a decimal and the comma only groups thousands. `fmt.price` and `fmt.vnd` are custom; only dates use `Intl` `vi-VN`. Edge cases (Product Owner, 2026-11-17): negatives use the true minus U+2212 (`−0.45`, `−6.98%`); zero shows `0.00` / `0.00%` with no sign; a missing value shows `—`, never `0`; a traded volume of zero stays `0`. Translation adoption stays Future. Viewport support is 768–1920 px, with 1920 px primary ([SNR-7.1.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md); below 768 px is Future). Chart work here is only a `no-restricted-imports` lint rule for `lightweight-charts` and `chart.js` ([ADR-FRONTEND-004](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-004-CHART-ENGINE-ADAPTER.md)); neither package goes into `package.json`, and the `ChartEngine` and `stat-chart` interfaces move to M-001 S3 with the docked chart proof of concept.

  Acceptance: `fmt.price(25300) === '25.30'`, `fmt.pct(0.0698) === '+6.98%'`, `fmt.volume(1234500) === '1,234,500'`, `fmt.vnd(25300000) === '25,300,000 ₫'`, `fmt.change(1750) === '+1.75'`, `fmt.change(-450) === '−0.45'`, `fmt.pct(-0.0698) === '−6.98%'`; zero, missing and zero-volume cases match the rules above; dates stay standard `vi-VN`; every user-facing string goes through `t()`; lint fails on a chart-library import; dark tokens are generated and match DESIGN_SYSTEM §3.

  Agent constraints — T-steps: T6 + part of T7 + TECHNICAL_DESIGN §8.3. Files: tokens, plus `format`, `i18n`, `chart` and `stat-chart` lint seams under `platform/`.
  - Proving commands: the `fmt` values above hold; a lint fixture fails on a planted chart-library import.

- **B5 — MSW, minimal Storybook, and Frontend CI (thin).** [ADR-FRONTEND-008](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-008-MSW-AND-STORYBOOK-IN-M000.md) (Accepted by the Product Owner, 2026-11-13) brings MSW and Storybook into M-000. MSW handlers, typed from the OpenAPI-generated types, serve the same fixtures in development and in Vitest; neither MSW nor Storybook ships in the production bundle; mock versus live is a build-time setting (`VITE_USE_MOCKS`). Storybook ships a minimal set of about 15 stories this week (Product Owner, 2026-11-17): zone states, `PriceCell`, `Delta`, `StatusBadge` and `MessageBody`; token pages wait for M-001. Frontend CI extends the B1 skeleton with Storybook and Playwright with axe at **1920, 1440, 1024 and 768** px ([SNR-6.1.4](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-6-1-4), [SNR-7.1.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md)), plus one keyboard-order test at 1920 px (skip link, then Z2, Z1, Z3, Z4). If the week runs short, Playwright runs at 1920 and 768 px only. F6 zone-cycling tests and visual snapshots move to M-001. The WCAG 2.2 AA target ([SNR-7.2.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md)) is exercised by axe and stays **P2** (not raised to P1).

  Acceptance: the same MSW handlers work in the browser and in tests; the production build does not bundle `src/mocks/` or Storybook; CI runs unit/component tests, Storybook and Playwright + axe at the agreed widths; axe reports no serious or critical issues on shell routes, without changing SNR-7.2.1's priority.

  Agent constraints — T-steps: T7 + Storybook, CI and Playwright.
  - The new CI file must not change the trigger of the existing Docker workflow.
  - Proving commands: `npx playwright test` and `npm run build-storybook` pass; `rg -l "msw|mockServiceWorker" dist` returns nothing.

## Delivery workflow (agentic)
Each slice goes through Spec Kit before any code: `spec.md` (Given/When/Then, including the UX Designer's criteria from [Design acceptance criteria](#design-acceptance-criteria-ux)), `plan.md` and `tasks.md`, from the templates in `.specify/templates`. The Product Owner approves each spec. A coding agent (Grok Build) then implements the tasks in a named worktree on `features/pitch-m000-B-frontend-foundation`, test first. Slice order: B0, then B1, then B2 alongside thin B4, then B3, then thin B5. People review the diff and the test output; nothing is committed or pushed without the Product Owner's approval.

Spec Kit rules for every slice:
- `spec.md` explicitly requires tests: write them, confirm they fail, then implement without editing the tests.
- Each `tasks.md` task names exact file paths and stays at about 2–5 files.
- Each phase checkpoint names its proving command; the agent stops there for review.
- Each spec copies its slice's "Agent constraints" block above, including the T-step mapping.

Agent constraints for every slice (all commands run from `frontend/`):
- Proving commands: `npm ci`, `npx tsc --noEmit`, `npx vitest run`, `npm run build`.
- Must not change: `backend/`; `docs/**`, including `docs/openapi.yaml`; the Accepted ADRs; `main`; the Product Owner's main tree (work in a worktree); the `wt/m001-s3` worktree.
- No `socket.io-client`, WebSocket or EventSource; `fetch` only in `platform/api` and `platform/stream`; `VITE_*` environment variables only.
- "AI gợi ý" and "Đã xác nhận", like every user-facing string, go through `t()`.

## Design acceptance criteria (UX)
The UX Designer's Given/When/Then criteria for B3, B4 and B5, aligned with the cut line above. Each slice's `spec.md` copies its block under "Acceptance". Each row names a value, a test and where it runs, so a coding agent can check it without asking. Sources: [DESIGN_LOCK](../../docs/domains/frontend/DESIGN_LOCK.md) v0.3.2 §1.1, §2, §4, §5, §6, §8 and [DESIGN_SYSTEM](../../docs/domains/frontend/DESIGN_SYSTEM.md) v0.3.1 §3, §4, §8, §10. Tiers: **M** means M-001 needs it, so it stays inside the week; **D** means it can move to the first days of M-001 if the week runs short.

Conventions for every criterion: user-facing text is a catalogue key through `t()`, not a literal; tests select by `data-zone`, `data-state`, `data-origin` and ARIA role, never by CSS class.

### B3: modular shell, zone frames, safe render

| # | Tier | Given / When / Then | Proven by |
|---|---|---|---|
| B3-D1 | M | **Given** the shell at `/` at 1920 px, **when** it renders, **then** there are four zones: Z2 `role=banner`, Z1 `role=navigation`, Z3 `role=main`, Z4 `role=complementary`, each with `data-zone="z1".."z4"` and an `aria-label` key. | Vitest + RTL |
| B3-D2 | M | **Given** the shell has loaded, **when** the user presses Tab repeatedly, **then** focus goes skip link first, then Z2 → Z1 → Z3 → Z4 (checked by the focused element's closest `data-zone`), and every focused element has a visible focus ring (`:focus-visible` outline ≥ 2 px). One Playwright test at 1920 px; F6 zone cycling and the full keyboard suite are deferred to M-001. | Playwright |
| B3-D3 | M | **Given** widths 1920, 1440, 1024, 768, **when** the shell renders, **then**: at ≥ 1440 all four zones are side by side; below 1440 Z4 is an overlay drawer opened from a Z2 toggle with `aria-expanded`; below 1024 Z1 is a 56 px rail where both track icons have an `aria-label`; at 768 Z3 is ≥ 712 px wide; zones never overlap (bounding boxes) and the page never scrolls horizontally (`scrollWidth <= clientWidth`). | Playwright, 4 widths |
| B3-D4 | M | **Given** a `ZoneFrame`, **when** `state` is each of `empty, loading, ready, stale, error, interrupted, streaming`, **then** it renders `data-state` with that value and the DESIGN_LOCK §5 frame: error has a retry button; interrupted shows the "Tạo lại" action and sends **no** request until clicked (MSW request count stays 0 for 5 s); streaming shows a stop button; loading has `aria-busy="true"`. | Vitest + RTL + MSW |
| B3-D5 | M | **Given** a component in one zone throws, **when** the shell renders, **then** that zone shows `data-state="error"` and the other three zones still render their content. | Vitest + RTL |
| B3-D6 | M | **Given** text typed in the Z4 input, **when** the page reloads in the same tab, **then** the text is restored from `sessionStorage` (key namespaced by `sessionRef`); **when** the message is sent, **then** the key is removed. | Playwright |
| B3-D7 | M | **Given** `MessageBody` renders a message with `data-origin="ai"`, **then** the edge is dashed and the "AI gợi ý" label is visible; with `data-origin="investor"` the edge is solid and "Đã xác nhận" is visible. Both labels come from `t()` keys, never JSX literals. Hue alone never carries the difference. | Vitest + RTL |
| B3-D8 | M | **Given** any file under `src/features/**`, **when** lint runs, **then** it fails on a hex, `rgb(` or `hsl(` colour literal, and on raw JSX text (`react/jsx-no-literals`). | ESLint in CI |
| B3-D9 | M | **Given** the clean rebuild (Product Owner, 2026-11-17: fresh frontend, refactoring the current app is acceptable), **when** the new shell ships, **then** the legacy `src/App.css` and `src/index.css` are deleted, the only global stylesheet is the token and base layer from B4, and no new module imports a legacy component from `src/components/**`. Legacy behaviour worth keeping is rebuilt on `ZoneFrame` and `MessageBody`, not restyled in place. | ESLint `no-restricted-imports` + file check in CI |

Files in scope (hint): `src/app/shell/**`, `src/platform/zone-frame/**`, `src/platform/message-body/**`. Must not change: `docs/**`, Backend code.

### B4: tokens, format, fonts

#### Format module (`fmt`): decided values

| # | Tier | Call | Exact output |
|---|---|---|---|
| B4-F1 | M | `fmt.price(25300)` | `25.30` |
| B4-F2 | M | `fmt.pct(0.0698)` | `+6.98%` |
| B4-F3 | M | `fmt.volume(1234500)` | `1,234,500` |
| B4-F4 | M | `fmt.vnd(25300000)` | `25,300,000 ₫` |
| B4-F5 | M | Any `fmt.*` output | the dot only ever marks a decimal and the comma only ever groups thousands (property test over 1,000 random values) |

#### Format module: edge cases, **decided by the Product Owner, 2026-11-17** (DESIGN_LOCK §8 v0.3.2)

| # | Case | Exact output | Why |
|---|---|---|---|
| P1 | Negative change | `fmt.change(-450) → −0.45` (positive: `fmt.change(1750) → +1.75`), `fmt.pct(-0.0698) → −6.98%` using the true minus `−` (U+2212), not a hyphen | Same width as `+` in IBM Plex Mono, so columns stay aligned; screen readers read it as "minus" |
| P2 | Zero change | `0.00` and `0.00%`, no sign, coloured `market.ref` | Matches the board convention: unchanged = reference colour |
| P3 | Missing value (`null`, `undefined`, `NaN`) | `—` (em dash) with `aria-label` key "Không có dữ liệu"; never `0`, never blank | A zero would be a false price |
| P4 | Volume zero | `0` | A real traded volume of zero is data, not missing |

P1–P4 are tier M and proven by Vitest exact-output tests, like B4-F1.

#### Tokens and type

| # | Tier | Given / When / Then | Proven by |
|---|---|---|---|
| B4-T1 | M | **Given** the token source file, **when** the build generates CSS variables, **then** every dark value equals the DESIGN_SYSTEM §3 tables (e.g. `--market-up` is `#2EBD6B`); light values are deferred to M-001; the expected values live in one test fixture copied from §3. | Vitest |
| B4-T2 | M | **Given** the Tailwind config, **then** it exposes no `market` or `state` colour utilities; **and** lint fails if `var(--market-*)` is read outside `PriceCell` / `Delta`, or `var(--state-*)` outside `StatusBadge`, or an arbitrary Tailwind colour value (`text-[#…]`, `bg-[var(--market-up)]`) appears outside `design-system/patterns/`. | Vitest (config) + ESLint |
| B4-T3 | M | **Given** a `Delta` with a positive, negative or zero value, **then** it always shows a sign or arrow as well as colour, and its accessible name includes the direction. | Vitest + RTL |
| B4-T4 | M | **Given** any `fmt.*` output on screen, **then** its computed `font-family` starts with `IBM Plex Mono`; UI text starts with `Be Vietnam Pro`; **and** no request goes to a third-party font host (fonts are self-hosted). | Playwright (computed style + network log) |
| B4-T5 | Moved to M-001 | **Given** `<html data-theme="dark">` or `"light"`, **when** the theme switches, **then** token variables change and no component re-renders with a hard-coded colour. | Playwright |
| B4-T6 | Moved to M-001 | **Given** the token source, **when** the contrast script runs, **then** text pairs meet DESIGN_SYSTEM §3.4 and every `state.*`/`market.*` pair is ≥ 10 dE2000 apart (§3.5). | Node script in CI |

Files in scope (hint): `src/platform/tokens/**`, `src/platform/format/**`, `design-system/patterns/{PriceCell,Delta,StatusBadge}/**` (the only readers, per DESIGN_SYSTEM §3), `public/fonts/**`, `tailwind.config.*`, `.eslintrc*`.

### B5: Storybook minimum, MSW, CI

The Storybook minimum that fits the week (about 15 stories):

| Tier | Stories |
|---|---|
| M | `ZoneFrame`: one story per state (7) |
| M | `PriceCell`, `Delta`, `StatusBadge`: up, down, zero, missing (the P1–P4 cases) |
| M | `MessageBody`: ai and investor origin, one XSS fixture |
| D | Primitives (button, input), dark theme only |
| Moved to M-001 | A theme toggle story, and the light half of the dark/light matrix for every story |

| # | Tier | Given / When / Then | Proven by |
|---|---|---|---|
| B5-S1 | M | **Given** the stories above, **when** CI runs, **then** every story renders without error and axe reports no serious or critical issue in it. | Storybook test runner / addon-vitest |
| B5-S2 | M | **Given** the shell route served by MSW, **when** Playwright runs at 1920, 1440, 1024 and 768 px, **then** B3-D3 holds and axe reports no serious or critical issue (SNR-7.2.1 stays P2). | Playwright + axe |
| B5-S3 | M | **Given** a production build, **then** `dist/` contains no `msw`, no `mockServiceWorker.js` and no Storybook code. | Script over `dist/` in CI |
| B5-S4 | Moved to M-001 | **Given** each `ZoneFrame` state story, **when** it renders in both themes, **then** the screenshot matches the approved baseline. | Visual snapshot (defer: flaky in week 1) |

### Cut order inside the design criteria
Cut the remaining D Storybook stories first. B4-T5, B4-T6 and B5-S4 are already moved to M-001. Chart seams have no rows here: per the architecture check, Pitch B adds only the `no-restricted-imports` lint for `lightweight-charts` and `chart.js`, and the interfaces move to M-001 S3. Keep every **M** row, because without them M-001 features would hard-code colours and number formats that cost more to remove later.

## Rabbit holes
- Growing this bet into M-001 Canvas zones, or building the docked chart proof of concept here (that is M-001 S3).
- **[ADR-FRONTEND-006](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-006-GENERATED-UI-COMPONENT-REGISTRY.md) (Proposed — Future).** GenUI stays out.
- Micro-frontend decomposition ([ADR-FRONTEND-001](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-001-MODULAR-APPLICATION.md) already rejected this for now).
- Raising [SNR-7.2.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md) from P2 to P1.
- Using Chart.js for price charts, or importing a chart library from feature code.
- Building the `ChartEngine` / `stat-chart` interfaces, price mocks, or adding `lightweight-charts` / `chart.js` to `package.json` here (M-001 S3).
- Inventing typed stream events, resume or cancel in this pitch (Backend follow-up on `docs/openapi.yaml`).
- Choosing an i18n library or shipping an English catalogue (Future, ADR-FRONTEND-005).
- Saved layout presets (Milestone [M-009](../../docs/system/PRODUCT_SPECIFICATION.md#m-009)).
- The light theme, theme switching, the contrast script, token Storybook pages, F6 zone-cycling tests and visual snapshots (moved to M-001 by the cut line, Product Owner 2026-11-17).

## Risks
- Stream headers, heartbeat and HTTP/2 ingress come in a later Backend pitch. The client is proven only against an MSW fixture here; end-to-end G6 delivery quality is shown when that pitch lands.
- Until Backend heartbeats ship, a long reasoning-model silence can pass the 60 s idle timeout and trigger a false `interrupted`. Recovery costs one click: "Tạo lại" retries, and the Z4 draft and any partial message are kept.
- The CRA → Vite move on a mixed JavaScript / TypeScript tree can overrun B1; the known traps are listed in its Agent constraints.
- B1 cannot run until Node v26.13.1 is installed locally; with `engine-strict=true`, `npm ci` fails fast on an older Node (the laptop has 22.18 today). The prerequisite sits in B1's Agent constraints.
- If T0 or T4 slips, the unused `MessageFormatter.js` XSS hole remains in the tree (latent, not live, but still a hole).
- One week for six thin slices depends on agent-ready slice specs. A vague spec makes the coding agent guess, and rework eats the week; slices that do not fit go to the Product Owner as a cut list.

## No-gos
- Identity, login, or owner-isolation product behavior ([Pitch A](M-000-A-identity-and-session.md); [ADR-SYS-001](../../docs/architecture/DECISIONS/ADR-SYS-001-IDENTITY-AND-PER-USER-ISOLATION.md)).
- M-001 zone layout, the docked chart proof-of-concept content, or a working Decision gate.
- A production market-data feed or licensed provider (M-001 S3 uses prepared mock data; provider choice stays with ADR-SYS-004).
- Computing reference, ceiling or floor prices in the Frontend.
- Socket.IO or WebSocket in the target transport.
- `GET /api/market/prices/{symbol}` or any MSW handler for a path not already in `docs/openapi.yaml` (M-001 S3).
- Micro-frontends; Pitch C (deferred).
- Raising WCAG 2.2 AA ([SNR-7.2.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md)) to P1.

## Done means
- [SR-1.4.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-4-1), the shell side of [SR-1.4.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-1-4-2), [SR-5.1.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#sr-5-1-2), [SNR-6.1.4](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-6-1-4) are `verified`; [SNR-8.1.2](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md#snr-8-1-2) is recorded as "Frontend part verified" against an MSW stream fixture, and end-to-end verification moves to the later Backend pitch. [SNR-7.1.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md) is exercised at 1920 / 1440 / 1024 / 768 (1920 / 768 if the fallback is used); [SNR-7.2.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md) has an axe baseline and stays P2.
- B0 is done: `grok inspect` from `frontend/` lists the new rules, and no agent instruction file points at CRA, Jest or Socket.IO.
- T0 (`MessageFormatter.js` gone) and T4 (`MessageBody` plus regression tests) are closed.
- [M-001](M-001-adaptive-visual-canvas.md) can start without another foundation rewrite.
- Given/When/Then acceptance, including the UX Designer's criteria, lives in each slice's `spec.md`.

## Open questions
- *Decided 2026-11-17:* Node pin is Node 26 LTS: `.nvmrc` `26`, `engines.node` `">=26.13.0"`, `.npmrc` `engine-strict=true`, Dockerfile `node:26-alpine`; the Product Owner installs v26.13.1 locally before B1. jsdom stays the DOM environment; no happy-dom fallback.
- *Decided 2026-11-17:* the Software Engineer role fixes the TECHNICAL_DESIGN gaps found in the feasibility check (the work happens in TECHNICAL_DESIGN, not this pitch): the heartbeat fixture still marked Transition / Follow-up (§6.3, §12); `VITE_USE_MOCKS` and `VITE_STREAM_IDLE_TIMEOUT_MS` (60 s stopgap) missing from the §10.1 env table; `App.tsx` size; no T-step owning the i18n / format and chart-lint seams; MSW split across T2 and T7.
- *Decided 2026-11-17:* cut line — all six slices thin, as an initial stage ready for later development. Deferred to M-001: chart interfaces (only the chart-import lint stays), price mocks, light theme and theme switching (B4 keeps the `data-theme` hook and dark tokens), contrast script, token Storybook pages, F6 zone-cycling tests, visual snapshots. One Playwright keyboard-order test at 1920 px stays. Fallback: Playwright at 1920 and 768 px only. T0, the `MessageBody` XSS tests and the B2 client are never cut.
- *Decided 2026-11-17:* Storybook ships a minimal set of about 15 stories this week (zone states, `PriceCell`, `Delta`, `StatusBadge`, `MessageBody`), per ADR-FRONTEND-008.
- *Decided 2026-11-17:* stream idle timeout comes from `VITE_STREAM_IDLE_TIMEOUT_MS`, default 60,000 ms in live mode, configurable and never hard-coded; any received line resets it; on timeout the stream aborts to `interrupted` with "Tạo lại" and keeps the Z4 draft and partial message; MSW tests use 15,000 ms with fake timers. No ADR change.
- *Decided 2026-11-17:* new slice B0 rewrites the agent instruction files to the target stack before B1.
- *Decided 2026-11-17:* number edge cases — true minus (`−0.45`, `−6.98%`), zero as `0.00` / `0.00%` with no sign, missing as `—` (never `0`), zero volume stays `0`.
- *Decided 2026-11-17:* `GET /api/market/prices/{symbol}` is out of Pitch B and goes to M-001 S3; MSW covers only paths already in `docs/openapi.yaml`.
- *Decided 2026-11-17:* appetite is 1 week, delivered agentically (Grok Build implements from Spec Kit slice specs).
- *Decided 2026-11-17:* cost is team time only.
- *Decided 2026-11-17:* Backend stream headers, heartbeat and HTTP/2 come in a later Backend pitch; this pitch makes the client ready and proves it against an MSW stream fixture.
- *Decided 2026-11-10:* the latent XSS in unused `MessageFormatter.js` is not patched as a one-off; T0 deletes the file and T4 adds `MessageBody` with regression tests (TECHNICAL_DESIGN §6.5, §10.2).
- *Decided 2026-11-13:* launch UI is `vi-VN`; prices use the board style (`25.30`); percent change uses the dot (`+6.98%`); volume is whole shares with comma grouping (`1,234,500`); ₫ totals use comma grouping (`25,300,000 ₫`); across all numbers the dot is only a decimal and the comma only groups thousands; dates stay standard `vi-VN`.
- *Decided 2026-11-13:* Chart.js is for non-price charts only, behind the `stat-chart` adapter; price charts stay on Lightweight Charts behind `ChartEngine` ([ADR-FRONTEND-004](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-004-CHART-ENGINE-ADAPTER.md)).
- *Decided 2026-11-13:* supported viewport is 768–1920 px, with 1920 px primary ([SNR-7.1.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md)); WCAG 2.2 AA ([SNR-7.2.1](../../docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md)) stays P2.
- *Decided 2026-11-13:* MSW and Storybook join M-000 ([ADR-FRONTEND-008](../../docs/domains/frontend/DECISIONS/ADR-FRONTEND-008-MSW-AND-STORYBOOK-IN-M000.md), Accepted). Neither ships to production.
- *Decided 2026-11-13:* `sessionRef` is the Backend session id plus the conversation id; the shell store (this pitch) holds the references only. Client transport is SSE only; SR-5.2.1 and SR-5.2.2 are Superseded.
