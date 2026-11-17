# Feature Specification: M-000 Frontend foundation core (delivery 1 of 2)

**Feature Branch**: `features/pitch-m000-B-frontend-foundation`

**Created**: 2026-11-17

**Status**: Draft

**Input**: Delivery 1 of Pitch B (M-000 Frontend foundation): slices B0 (agent instructions on the target stack), B1 (Vite shell and subtract, T0–T2), B2 (API client, OpenAPI types, SSE-only transport, Socket.IO removal: codegen + T3 + T8, client proven against an MSW stream fixture only), and thin B4 (dark tokens, vi-VN format module, i18n seam, self-hosted fonts, chart-import lint). B3 and B5 are a separate reserved feature. Source of truth: `specs/pitches/M-000-B-frontend-foundation.md`, with the frontend architecture, technical design, design lock, design system, ADR-FRONTEND-001..008, and ADR-SYS-001.

## Clarifications

### Session 2026-11-17

- Q: Which source governs light theme and contrast timing for this delivery? → A: The pitch and `docs/domains/frontend/TECHNICAL_DESIGN.md` govern. This delivery ships dark tokens plus the `data-theme` hook only. Light values, theme switching, and the contrast script move to M-001. `docs/domains/frontend/DESIGN_SYSTEM.md` sections "1. Principles" and "10. Quality", and `docs/domains/frontend/DESIGN_LOCK.md` — "4.2 Token groups", are stale on this point (follow-up doc fix, not edited here).
- Q: Which number-format mechanism is required? → A: Custom board-style formatters (`fmt.price`, `fmt.vnd`, change, and percent per rows B4-F1..F5 and P1..P4). `Intl` is used only for dates. ADR-FRONTEND-005's "everything through `Intl`" wording is stale (follow-up doc fix, not edited here).
- Q: Which labels should `tasks.md` use for the B1 Vite move, the types alignment, and the Vitest smoke? → A: `tasks.md` uses the pitch's T1/T2 labels and notes the matching `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step beside each.
- Q: Which slice enables lint rules 1–3 and `react/no-danger`? → A: Per the pitch, lint rules 1–3 and `react/no-danger` are enabled in B1.
- Q: Which folder names do the B0 instruction files use? → A: `features/` and `platform/`, per `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree (Target M-000)" and the pitch B0 rules. ADR-FRONTEND-001's `modules/` wording is stale (follow-up doc fix, not edited here).
- Q: Does B0 add a failing test, or is `grok inspect` plus the instruction search its only proof? → A: B0 is instruction files only and is exempt from the failing-test rule. Its proof is `grok inspect` plus the instruction search named in the pitch.
- Q: Does this delivery build the Storybook theme matrix? → A: Reserved with B5 (dark-only minimal set per the pitch). Not built in this delivery.
- Q: Which text governs a zero `Delta`? → A: Row P2 and `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules". Zero shows `0.00` and `0.00%`, no sign, coloured `market.ref`. The zero clause inside verbatim row B4-T3 is superseded by P2. Non-zero B4-T3 still requires a sign or arrow and an accessible name that includes the direction. Do not add a sign on zero. Product Owner resolution of analysis I1, 2026-11-17.
- Q: What is the Frontend CI workflow path, and where does the `gen:api` drift check sit? → A: `.github/workflows/frontend-ci.yml`. One job runs lint, then `tsc --noEmit`, then Vitest, then build, then `npm run gen:api && git diff --exit-code src/platform/api/generated`. Do not change the `on` trigger of `.github/workflows/build-push-dockerhub.yml`. Product Owner resolution of analysis G1, 2026-11-17.
- Q: What mechanism enforces lint rules 1 and 2? → A: Core ESLint `no-restricted-imports` path patterns. Do not add `eslint-plugin-boundaries`. Rule 3 and `react/no-danger` stay on the core ESLint mechanisms already named. Product Owner resolution of analysis G2, 2026-11-17.
- Q: How far do dark tokens go in this delivery? → A: Commit hand-written two-part dark CSS variables. `--market-up` is `#2EBD6B`. A two-part id such as `market.down` becomes `--market-down`. Do not name a generator, including Style Dictionary. Do not invent three-part custom property names for `ai.*`. Full B4-T1 generation of every dark value, and the `npm run tokens` drift check, stay out of this delivery. Product Owner resolution of analysis G3, 2026-11-17.
- Q: Which slice sets `data-density`? → A: This delivery's B4 sets `data-density="compact"` on `<html>` beside `data-theme="dark"`. Do not use another density. Product Owner resolution of analysis X1, 2026-11-17.

## User Scenarios & Testing *(mandatory)*

Stories follow slice order. B0 is P1, B1 is P2, and B2 and B4 are both P3 and proceed alongside after B1. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Slices" and "Delivery workflow (agentic)".

Each story is tested on its own. B2 and B4 assume the B1 toolchain exists, because their proving commands run from `frontend/` after that toolchain is in place. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Agent constraints for every slice".

### User Story 1 - Agent instructions on the target stack (B0) (Priority: P1)

The Software Engineer, and any later coding session on this repository, reads instruction files that describe the target Frontend stack. Today those files still describe Create React App, Jest, and Socket.IO. B0 rewrites that guidance before the toolchain changes, and it changes instruction files only.

**Why this priority**: Stale stack guidance is the largest regression risk for the slices that follow. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack".

**Independent Test**: From `frontend/`, `grok inspect` lists the new rules, and a search of instruction files finds no recommendation of Create React App, Jest, `REACT_APP_*`, or Socket.IO. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack" (Acceptance).

**Acceptance Scenarios**:

1. **Given** the repository instruction files still describe the current stack, **When** B0 is applied, **Then** `frontend/AGENTS.md` exists, is under 10,000 characters, and states the target rules below. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack".
2. **Given** the root `AGENTS.md` still has Frontend lines for the current stack, **When** B0 is applied, **Then** those Frontend lines describe the target stack. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack".
3. **Given** a stale `CLAUDE.md`, `.claude/rules`, or `.cursor/rules` entry that recommends the current stack, **When** B0 is applied, **Then** that entry is removed or rewritten so it does not recommend Create React App, Jest, `REACT_APP_*`, or Socket.IO. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack".
4. **Given** `.github/instructions/frontend-react.instructions.md`, **When** B0 is applied, **Then** that file matches the same target stack and does not drift from it. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack".
5. **Given** B0 has been applied, **When** `grok inspect` is run from `frontend/`, **Then** it lists the new rules. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack" (Acceptance).
6. **Given** B0 has been applied, **When** instruction files are searched, **Then** none of them recommend Create React App, Jest, `REACT_APP_*`, or Socket.IO. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack" (Acceptance).

Target rules the instruction files must state. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack":

- Vite and Vitest.
- `VITE_*` environment variables only.
- No `socket.io-client`, WebSocket, or EventSource.
- `fetch` only inside `platform/api` and `platform/stream`.
- The module tree and lint rules in `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree (Target M-000)" and "3.3 Boundary enforcement (Target G2)". Those instruction files name `features/` and `platform/`. They do not name `modules/`. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree (Target M-000)"; `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack". ADR-FRONTEND-001 — "Implementation Direction" (`modules/`) is stale on this point.

**Agent constraints** (copied from `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack"):

- T-steps: none.
- Instruction files only; no source, test, or config change. B0 is exempt from the failing-test rule. It does not add a test file. Its proof is `grok inspect` run from `frontend/` plus the instruction search named in the pitch Acceptance (scenarios 5 and 6). Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack" (Agent constraints and Acceptance).

---

### User Story 2 - Vite shell and subtract (B1) (Priority: P2)

The Software Engineer replaces the Create React App toolchain with Vite, deletes the unused unsafe formatter and the other unused files named for this step, and leaves a Vitest smoke path plus a Frontend CI skeleton. The Product Owner installs Node v26.13.1 locally before the first B1 run. The laptop has Node 22.18 today.

**Why this priority**: Later slices run their proving commands on this toolchain. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Delivery workflow (agentic)" and "B1 — Vite shell and subtract".

**Independent Test**: From `frontend/`, `npm run build` and `npm run dev` work on Vite, Vitest runs, the Docker image builds, and `rg -n "MessageFormatter|dangerouslySetInnerHTML|REACT_APP_" src` returns nothing. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Acceptance and Proving commands).

**Acceptance Scenarios**:

1. **Given** the Frontend package is still built with Create React App, **When** B1 finishes, **Then** `npm run build` and `npm run dev` work on Vite, and Create React App is no longer the build system. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Acceptance); ADR-FRONTEND-002 — "Decision" and "Guardrails".
2. **Given** the unused files listed in `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step T0, **When** B1 finishes, **Then** those files are deleted, `MessageFormatter.js` has no remaining references, and `rg -n "MessageFormatter|dangerouslySetInnerHTML|REACT_APP_" src` (run from `frontend/`) returns nothing. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.5 Safe rendering of Agent output" and "10.2 CRA → Vite migration".
3. **Given** the named Vite traps in the B1 agent-constraints block, **When** B1 finishes, **Then** each trap is resolved far enough that the Vite build, `tsc --noEmit`, and the Docker image build succeed. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Known traps, Acceptance).
4. **Given** Node v26.13.1 is installed locally, **When** `npm ci` runs in `frontend/` with `engine-strict=true`, **Then** it accepts that Node and the package declares `engines.node` of `">=26.13.0"`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Node pin).
5. **Given** the laptop Node is 22.18 and `engine-strict=true` is set, **When** `npm ci` runs before v26.13.1 is installed, **Then** it fails fast. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Risks".
6. **Given** the dev server is running, **When** the browser calls `/api`, **Then** Vite `server.proxy` sends `/api` to port 5000 on the same origin, `VITE_API_BASE_URL` defaults to empty, and the setup does not use credentialed CORS. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Architecture); ADR-SYS-001 — "Decision" (same-origin Backend-for-Frontend); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run".
7. **Given** Vitest is wired with jsdom, **When** the G1 smoke runs, **Then** a component test sends a chat and renders streamed tokens from an MSW SSE handler that uses the frames in `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.2 Today's stream contract". Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "9.2 Tests mapped to gates" (G1) and "10.2 CRA → Vite migration"; `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract"; SNR-6.1.4 (path only).
8. **Given** the Frontend CI skeleton in `.github/workflows/frontend-ci.yml`, **When** it runs, **Then** the order is lint, then `tsc --noEmit`, then Vitest, then build, then `npm run gen:api && git diff --exit-code src/platform/api/generated`, and the trigger of `.github/workflows/build-push-dockerhub.yml` is unchanged. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Acceptance) and "B5 — MSW, minimal Storybook, and Frontend CI"; Product Owner resolution of analysis G1, 2026-11-17.
9. **Given** the Frontend Docker image, **When** it builds, **Then** the image uses `node:26-alpine` and packages the Vite `dist` output. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Node pin and Known traps).
10. **Given** the B1 lint configuration, **When** lint runs, **Then** rules 1–3 in `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement (Target G2)" and `react/no-danger` are enabled. Rules 1 and 2 use core ESLint `no-restricted-imports`. This delivery does not add `eslint-plugin-boundaries`. Rule 4 and the chart-library part of rule 5 stay with B4. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement (Target G2)"; Product Owner resolution of analysis G2, 2026-11-17.

`tasks.md` uses the pitch's T1 and T2 labels and notes the matching `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step beside each (FR-032). B1 enables lint rules 1–3 and `react/no-danger` (FR-031). The combined B1 outcomes in the scenarios above stay in this delivery. Source: Product Owner clarification 2026-11-17; `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract".

**Agent constraints** (copied from `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract"):

- T-steps: T0–T2.
- Architecture (ADR-SYS-001, Backend-for-Frontend): Vite `server.proxy` sends `/api` to `:5000` on the same origin; `VITE_API_BASE_URL` defaults to empty; no credentialed CORS.
- Known traps the spec must name:
  - `frontend/Dockerfile` copies `/app/build`, but Vite writes `dist`.
  - `process.env.REACT_APP_*` at `config.ts:3,11`, `modelsApi.ts:11`, and `WebSocketTest.tsx:254` breaks under Vite.
  - `App.tsx:30` hard-codes `http://localhost:5000`, which bypasses the proxy.
  - TypeScript is not declared in `package.json` (4.9.5 arrives transitively; MSW 3 needs 5.9+).
  - `config-overrides.js` and `webpack.config.dev.js` are dead.
  - tsconfig has `target es5` and `moduleResolution node`.
  - The Dockerfile uses `node:20-alpine` (Node 20 is end-of-life).
- Node pin (Product Owner, 2026-11-17): Node 26, the current LTS line. `frontend/.nvmrc` = `26`; `engines.node` = `">=26.13.0"`; `frontend/.npmrc` with `engine-strict=true`; the Dockerfile uses `node:26-alpine`. jsdom is the Vitest DOM environment. Prerequisite: the Product Owner installs Node v26.13.1 locally before the first B1 run.
- Proving commands: `rg -n "MessageFormatter|dangerouslySetInnerHTML|REACT_APP_" src` returns nothing; the Docker build succeeds.

Files T0 deletes, when still unreferenced. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step T0:

- `components/OptimizedApp.js`
- `components/PerformanceProfiler.js`
- `components/WebSocketTest.tsx`
- `components/MessageFormatter.js`
- `services/apiService.ts`
- `utils/performance.js` if still unreferenced

`MessageFormatter.js` is unused and builds HTML with unescaped `dangerouslySetInnerHTML`. It is not patched in place. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.5 Safe rendering of Agent output"; `specs/pitches/M-000-B-frontend-foundation.md` — "Open questions" (decided 2026-11-10).

B1 also aligns `@types/react` and `@types/react-dom` with React 18 (they are currently `^19`) and declares TypeScript at 5.9 or newer so MSW 3 can run. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step "T1 types fix"; `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Known traps). `tasks.md` notes that row beside the types task and does not label it as the pitch's T1 (FR-032).

---

### User Story 3 - API client, OpenAPI types, and SSE-only transport (B2) (Priority: P3)

The Software Engineer generates Frontend API types from the OpenAPI contract, places one same-origin client in `platform/api`, places the chat stream reader in `platform/stream`, removes Socket.IO, and proves the client against an MSW stream fixture. The Backend stream is not changed.

**Why this priority**: B2 is the same rank as B4 and starts after B1. The client has to be ready for a later Backend heartbeat pitch without a second Frontend change. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Slices" and "B2 — API client, OpenAPI types, SSE-only transport, and Socket.IO removal".

**Independent Test**: `npm run gen:api && git diff --exit-code src/platform/api/generated` passes; `rg socket.io dist` returns nothing; a fake-timer idle-timeout test passes against an MSW stream fixture. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client, OpenAPI types, SSE-only transport, and Socket.IO removal" (Proving commands).

**Acceptance Scenarios**:

1. **Given** `docs/openapi.yaml` as the contract, **When** `npm run gen:api` runs, **Then** types are generated under `src/platform/api/generated`, the generated file is committed, and the fifth step of `.github/workflows/frontend-ci.yml` fails if the generated file drifts. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Acceptance); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.1 Typed REST client"; ADR-FRONTEND-002 — "Decision"; Product Owner resolution of analysis G1, 2026-11-17.
2. **Given** the one client in `platform/api`, **When** it sends any request, including the stream, **Then** the request uses `credentials: 'same-origin'`, adds `AuthAdapter.csrfHeaders()` on POST, PUT, PATCH, and DELETE, calls `onUnauthorized` on 401, and sends no `Authorization` header and no `X-User-ID` header. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Agent constraints); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.1 Typed REST client" and "3.4 Platform contracts"; ADR-SYS-001 — "Decision" and "Follow-ups".
3. **Given** this delivery's adapter, **When** tests or the app construct it, **Then** the slice ships `NoAuthAdapter` and tests use a fake adapter. No token is present in JavaScript, storage, or fixtures. `/api/auth/*` is not implemented here. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Agent constraints); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.4 Platform contracts" and "6.1 Typed REST client".
4. **Given** Pitch B's client, **When** it chooses a path, **Then** it calls only health, config, `models/*`, and chat. `sessionRef` is an opaque `{sessionId, conversationId}`. MSW covers only paths already in `docs/openapi.yaml`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Agent constraints); SR-1.4.2 (the `sessionRef` shape only; the shell store is out of scope).
5. **Given** `openChatStream(body, { signal, idleTimeoutMs })`, **When** the reader parses a frame, **Then** it keeps the `id`, `event`, and `retry` fields, ignores implementation of the stream via `EventSource`, and maps today's frames through `legacyChatAdapter` behind a `StreamAdapter` interface. Stream event names appear only in the `StreamEvent` union and the adapter. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Agent constraints); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.3 SSE client"; SR-5.1.2.
6. **Given** a chat stream is already open in the tab, **When** another chat stream opens, **Then** the previous one is aborted so only one chat stream is open per tab. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Agent constraints); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.3 SSE client".
7. **Given** live mode, **When** the idle timeout is read, **Then** it comes from `VITE_STREAM_IDLE_TIMEOUT_MS`, defaults to 60000 ms, and is not hard-coded. `frontend/.env.example` documents the 60 s default as a stopgap. Any received line, including `:` comments, resets the timer. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Idle timeout); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.2 Today's stream contract" and "10.1 Build and run".
8. **Given** an MSW stream fixture and fake timers with a 15000 ms idle timeout, **When** the idle window passes with no further line, **Then** the client accepts `:` comment lines and moves the stream to `interrupted`. The retry action's user-facing label is "Tạo lại" through `t()`. The Z4 draft and any partial message stay as they are. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Acceptance and Idle timeout); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.3 SSE client"; `docs/domains/frontend/DESIGN_LOCK.md` — "5. Zone state matrix".
9. **Given** the package after B2, **When** dependencies and the production bundle are inspected, **Then** `socket.io-client` is absent from `package.json` and from the bundle (`rg socket.io dist` returns nothing), and a lint rule stops Socket.IO from coming back. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Acceptance); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.4 Socket.IO removal"; ADR-FRONTEND-002 — "Carve-outs"; SNR-8.1.2; SR-5.2.1 and SR-5.2.2 (Superseded).
10. **Given** this delivery's stream evidence, **When** the result is recorded, **Then** SNR-8.1.2 is recorded as "Frontend part verified" against the MSW stream fixture. End-to-end verification waits for the later Backend pitch. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Acceptance) and "Done means"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "9.2 Tests mapped to gates" (G6).

**Agent constraints** (copied from `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client, OpenAPI types, SSE-only transport, and Socket.IO removal"):

- T-steps: codegen (`docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.1 Typed REST client") + T3 + T8.
- Architecture (ADR-SYS-001, Backend-for-Frontend): one client in `platform/api` sends `credentials: 'same-origin'` on every request, including the stream. A request hook adds `AuthAdapter.csrfHeaders()` to POST, PUT, PATCH, and DELETE; a 401 calls `onUnauthorized`. No `Authorization` header and no token in JavaScript, storage, or fixtures. The slice ships `NoAuthAdapter`; tests use a fake adapter. The `/api/auth/*` routes stay in Pitch A.
- No global `X-User-ID`. Pitch B calls only health, config, `models/*`, and chat. `sessionRef` is an opaque `{sessionId, conversationId}`. MSW covers only paths already in `docs/openapi.yaml`; `GET /api/market/prices/{symbol}` is out of Pitch B (M-001 S3).
- Stream API: `openChatStream(body, { signal, idleTimeoutMs })`. The parser keeps the `id`, `event`, and `retry` fields; `legacyChatAdapter` sits behind a `StreamAdapter` interface. Stream event names appear only in the `StreamEvent` union and the adapter, enforced by lint. Only one open chat stream per tab.
- Idle timeout (Product Owner, 2026-11-17): the value comes from `VITE_STREAM_IDLE_TIMEOUT_MS` and defaults to `60000` ms in live mode; it is configurable and never hard-coded, so the default can drop with no code change once the Backend sends a heartbeat in a later pitch (no ADR change needed). Any received line, including `:` comments, resets the timer. On timeout the stream aborts and moves to `interrupted` with the "Tạo lại" (Retry) action; the Z4 draft and any partial message stay as they are. `frontend/.env.example` documents the 60 s default as a stopgap that the later Backend heartbeat pitch will tighten. MSW tests use `15000` ms with fake timers.
- Proving commands: `npm run gen:api && git diff --exit-code src/platform/api/generated` passes; `rg socket.io dist` returns nothing; a fake-timer idle-timeout (heartbeat) test passes.

Removal set for T8, in addition to the package. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.4 Socket.IO removal":

- `webSocketService.ts` (used only by `WebSocketTest.tsx`, which T0 already deletes when it is still present).
- `socket.io-client` and `@types/socket.io-client`.
- `API_CONFIG.WEBSOCKET` from `config.ts`.
- A `no-restricted-imports` rule so the client cannot return.

The library used to implement the typed client, and the SSE parser library versus an in-house parser, stay Proposed. This spec requires the behavior above and does not choose those libraries. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.1 Typed REST client", "6.3 SSE client", and "12. Domain-specific constraints and open items".

---

### User Story 4 - Dark tokens, vi-VN format, i18n seam, fonts, and chart-import lint (B4) (Priority: P3)

The Software Engineer ships the dark token pipeline and the `data-theme` hook, one vi-VN message catalogue, one format module, self-hosted fonts, and the chart-library import lint. B4 is the same rank as B2 and proceeds alongside it after B1.

**Why this priority**: Later milestones otherwise hard-code colours and number formats. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Cut order inside the design criteria" and "B4 — Dark tokens, vi-VN format, i18n seam and chart-import lint".

**Independent Test**: The `fmt` exact outputs hold, a lint fixture fails on a planted `lightweight-charts` or `chart.js` import, and the generated dark CSS variables match the dark column of `docs/domains/frontend/DESIGN_SYSTEM.md` — "3. Palette". Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B4 — Dark tokens..." (Acceptance and Proving commands) and design rows B4-F1..F5, B4-T1.

**Acceptance Scenarios**:

1. **Given** the format module, **When** the calls in rows B4-F1..F5 and P1..P4 run, **Then** the outputs match those rows exactly, including the property test over 1,000 random values. `fmt.price`, `fmt.vnd`, `fmt.change`, `fmt.pct`, and `fmt.volume` are custom board-style formatters. They do not use `Intl`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B4: tokens, format, fonts" and "B4 — Dark tokens..."; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.3 i18n and locale seam"; `docs/domains/frontend/DESIGN_LOCK.md` — "8. Translation-ready copy"; ADR-FRONTEND-005 — "Decision" (price-board bullet); `docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md` — "SNR-7: Usability, Accessibility, and Responsive Behavior" (launch UI note).
2. **Given** a date or time value, **When** it is formatted, **Then** it uses standard `vi-VN` `Intl` formatting with time zone `Asia/Ho_Chi_Minh`. `Intl` is used only for dates. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B4 — Dark tokens..."; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.3 i18n and locale seam"; ADR-FRONTEND-005 — "Decision" (date clause).
3. **Given** any user-facing string, including "AI gợi ý", "Đã xác nhận", "Tạo lại", and the missing-value label "Không có dữ liệu", **When** it is shown, **Then** it comes from the vi-VN catalogue through `t()`. English is not shipped, and no i18n library is chosen. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Agent constraints for every slice" and "B4 — Dark tokens..." (Acceptance); ADR-FRONTEND-005 — "Decision"; `docs/domains/frontend/DESIGN_SYSTEM.md` — "3.6 Provenance" and "9. Content voice".
4. **Given** the token source, **When** B4 commits dark CSS variables, **Then** each two-part id matches the dark hex in `docs/domains/frontend/DESIGN_SYSTEM.md` — "3. Palette" (for example `--market-up` is `#2EBD6B` and `market.down` becomes `--market-down`), `<html>` carries `data-theme="dark"` and `data-density="compact"`, and light values are not committed. This delivery does not name a generator and does not invent three-part `ai.*` custom property names. Full B4-T1 generation and the `npm run tokens` drift check are out of this delivery. Theme switching and the contrast script are not in this delivery. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B4-T1 and "B4 — Dark tokens..."; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.1 Token pipeline" and "7. Accessibility and responsive behaviour"; ADR-FRONTEND-007 — "Decision"; Product Owner resolution of analysis G3 and X1, 2026-11-17.
5. **Given** the Tailwind config and the lint rules, **When** they are checked, **Then** row B4-T2 holds. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B4-T2; `docs/domains/frontend/DESIGN_SYSTEM.md` — "2. Token architecture"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement" rule 4; ADR-FRONTEND-007 — "Decision".
6. **Given** a positive or negative `Delta`, **When** it renders, **Then** it shows a sign or an arrow as well as colour, and its accessible name includes the direction. **Given** a zero `Delta`, **When** it renders, **Then** row P2 holds: `0.00` and `0.00%`, no sign, coloured `market.ref`. The zero clause inside verbatim row B4-T3 is superseded by P2. Source: `specs/pitches/M-000-B-frontend-foundation.md` — rows B4-T3 and P2; `docs/domains/frontend/DESIGN_SYSTEM.md` — "8. Patterns"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules".
7. **Given** any `fmt.*` output on screen and UI text on screen, **When** computed style and the network log are checked, **Then** row B4-T4 holds. Fonts are self-hosted from `public/fonts`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B4-T4; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.1 Token pipeline"; `docs/domains/frontend/DESIGN_SYSTEM.md` — "4. Typography".
8. **Given** a planted import of `lightweight-charts` or `chart.js` outside the adapter seams, **When** lint runs, **Then** it fails. Neither package is added to `package.json`. The `ChartEngine` and `stat-chart` interfaces are not built here. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B4 — Dark tokens..." (Acceptance); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement" rule 5 and "3.4 Platform contracts"; ADR-FRONTEND-004 — "Decision" and "Considered Options".

Design-row convention for these scenarios: user-facing text is a catalogue key through `t()`; tests select by `data-zone`, `data-state`, `data-origin`, and ARIA role, never by CSS class. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Design acceptance criteria (UX)".

#### Design acceptance criteria (copied verbatim)

Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B4: tokens, format, fonts". Copied verbatim as required for this delivery. Row B4-T1 stands: light values are deferred to M-001. Product Owner clarification 2026-11-17.

##### Format module (`fmt`): decided values

| # | Tier | Call | Exact output |
|---|---|---|---|
| B4-F1 | M | `fmt.price(25300)` | `25.30` |
| B4-F2 | M | `fmt.pct(0.0698)` | `+6.98%` |
| B4-F3 | M | `fmt.volume(1234500)` | `1,234,500` |
| B4-F4 | M | `fmt.vnd(25300000)` | `25,300,000 ₫` |
| B4-F5 | M | Any `fmt.*` output | the dot only ever marks a decimal and the comma only ever groups thousands (property test over 1,000 random values) |

##### Format module: edge cases, **decided by the Product Owner, 2026-11-17** (DESIGN_LOCK §8 v0.3.2)

| # | Case | Exact output | Why |
|---|---|---|---|
| P1 | Negative change | `fmt.change(-450) → −0.45` (positive: `fmt.change(1750) → +1.75`), `fmt.pct(-0.0698) → −6.98%` using the true minus `−` (U+2212), not a hyphen | Same width as `+` in IBM Plex Mono, so columns stay aligned; screen readers read it as "minus" |
| P2 | Zero change | `0.00` and `0.00%`, no sign, coloured `market.ref` | Matches the board convention: unchanged = reference colour |
| P3 | Missing value (`null`, `undefined`, `NaN`) | `—` (em dash) with `aria-label` key "Không có dữ liệu"; never `0`, never blank | A zero would be a false price |
| P4 | Volume zero | `0` | A real traded volume of zero is data, not missing |

P1–P4 are tier M and proven by Vitest exact-output tests, like B4-F1.

##### Tokens and type

| # | Tier | Given / When / Then | Proven by |
|---|---|---|---|
| B4-T1 | M | **Given** the token source file, **when** the build generates CSS variables, **then** every dark value equals the DESIGN_SYSTEM §3 tables (e.g. `--market-up` is `#2EBD6B`); light values are deferred to M-001; the expected values live in one test fixture copied from §3. | Vitest |
| B4-T2 | M | **Given** the Tailwind config, **then** it exposes no `market` or `state` colour utilities; **and** lint fails if `var(--market-*)` is read outside `PriceCell` / `Delta`, or `var(--state-*)` outside `StatusBadge`, or an arbitrary Tailwind colour value (`text-[#…]`, `bg-[var(--market-up)]`) appears outside `design-system/patterns/`. | Vitest (config) + ESLint |
| B4-T3 | M | **Given** a `Delta` with a positive, negative or zero value, **then** it always shows a sign or arrow as well as colour, and its accessible name includes the direction. | Vitest + RTL |

The zero clause inside verbatim B4-T3 is superseded by row P2 and `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules". Zero shows `0.00` and `0.00%` with no sign, coloured `market.ref`. Non-zero B4-T3 still holds. Do not add a sign on zero. Product Owner resolution of analysis I1, 2026-11-17.
| B4-T4 | M | **Given** any `fmt.*` output on screen, **then** its computed `font-family` starts with `IBM Plex Mono`; UI text starts with `Be Vietnam Pro`; **and** no request goes to a third-party font host (fonts are self-hosted). | Playwright (computed style + network log) |

`track.a` and `track.b` have no hex in `docs/domains/frontend/DESIGN_SYSTEM.md` — "3.2 Track". They are outside the dark-value fixture until the UX Designer sets them. Source: `docs/domains/frontend/DESIGN_SYSTEM.md` — "3.2 Track"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "12. Domain-specific constraints and open items".

The token generator named in the technical design (Style Dictionary) stays Proposed and is not selected. This delivery commits hand-written two-part dark variables (`--market-up` is `#2EBD6B`). It does not invent three-part `ai.*` custom property names. Full generation of every dark value in verbatim B4-T1, and the `npm run tokens` drift check, are out of this delivery. `<html>` carries `data-theme="dark"` and `data-density="compact"`. Product Owner resolution of analysis G3 and X1, 2026-11-17. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.1 Token pipeline" and "12. Domain-specific constraints and open items".

**Agent constraints** (copied from `specs/pitches/M-000-B-frontend-foundation.md` — "B4 — Dark tokens, vi-VN format, i18n seam and chart-import lint"):

- T-steps: T6 + part of T7 + `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.3 i18n and locale seam".
- Files: tokens, plus `format`, `i18n`, `chart`, and `stat-chart` lint seams under `platform/`.
- Proving commands: the `fmt` values above hold; a lint fixture fails on a planted chart-library import.

Additional files the design rows name for the pattern readers: `design-system/patterns/{PriceCell,Delta,StatusBadge}/**`, `public/fonts/**`, `tailwind.config.*`, and the ESLint config. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B4: tokens, format, fonts" (Files in scope).

---

### Edge Cases

- The Product Owner has not yet installed Node v26.13.1, and the laptop has 22.18. With `engine-strict=true`, `npm ci` fails fast. B1 does not start until v26.13.1 is installed. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Risks" and "B1 — Vite shell and subtract" (Node pin).
- A reasoning-model silence can pass the 60 s live idle timeout and move the stream to `interrupted` before the later Backend heartbeat exists. Recovery is the "Tạo lại" action. The Z4 draft and any partial message stay. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Risks" and "B2 — API client..." (Idle timeout).
- A `:` comment line, including a future `: ping`, resets the idle timer and is not dispatched as a chat event. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Idle timeout); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.3 SSE client".
- A malformed frame or an `{"error"}` frame becomes the stream `error` event. `[DONE]` ends the iterable. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.3 SSE client" (Event adapter).
- A second `openChatStream` in the same tab aborts the one already open. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.3 SSE client".
- HTTP 401 calls `onUnauthorized`. `NoAuthAdapter` sign-in methods are no-ops in this delivery. Tests supply a fake adapter. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.4 Platform contracts" and "6.1 Typed REST client"; `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Agent constraints).
- `fmt` receives `null`, `undefined`, or `NaN` and renders `—` with the accessible name key "Không có dữ liệu". A traded volume of zero renders `0`. A zero change renders `0.00` / `0.00%` with no sign. Source: `specs/pitches/M-000-B-frontend-foundation.md` — rows P2, P3, P4.
- Negative change and percent use U+2212. A hyphen is not the minus sign. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row P1.
- An MSW handler for a path that is not already in `docs/openapi.yaml` is not added. `GET /api/market/prices/{symbol}` is not added. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Agent constraints) and "No-gos".
- `App.tsx` hard-codes `http://localhost:5000`. That call bypasses the dev proxy until B1 removes it. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Known traps).
- The Docker build copies `/app/build` while Vite writes `dist`. The image build fails until B1 points the image at `dist`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Known traps).
- `track.a` and `track.b` have no hex yet. The dark-token fixture does not invent values for them. Source: `docs/domains/frontend/DESIGN_SYSTEM.md` — "3.2 Track".

## Requirements *(mandatory)*

### Test-first rule

- **FR-001**: For B1, B2, and B4, the Software Engineer MUST write the tests, confirm they fail, and only then implement, without editing those tests. B0 is exempt. B0 MUST NOT add a test file. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Delivery workflow (agentic)" (Spec Kit rules) and "B0 — Agent instructions on the target stack" (Agent constraints). Product Owner clarification 2026-11-17.

### Agent constraints for every in-scope slice

Copied from `specs/pitches/M-000-B-frontend-foundation.md` — "Delivery workflow (agentic)" (Agent constraints for every slice). All commands run from `frontend/`.

- Proving commands: `npm ci`, `npx tsc --noEmit`, `npx vitest run`, `npm run build`.
- Must not change: `backend/`; `docs/**`, including `docs/openapi.yaml`; the Accepted ADRs; `main`; the Product Owner's main tree (work in a worktree); the `wt/m001-s3` worktree.
- No `socket.io-client`, WebSocket, or EventSource; `fetch` only in `platform/api` and `platform/stream`; `VITE_*` environment variables only.
- "AI gợi ý" and "Đã xác nhận", like every user-facing string, go through `t()`.

- **FR-002**: Implementation of B0, B1, B2, and B4 MUST run in a named git worktree on `features/pitch-m000-B-frontend-foundation`. It MUST NOT modify `backend/`, `docs/**` (including `docs/openapi.yaml`), the Accepted ADRs, `main`, the Product Owner's main tree, or the `wt/m001-s3` worktree. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Delivery workflow (agentic)".
- **FR-003**: The target Frontend MUST NOT include `socket.io-client`, a WebSocket client, or `EventSource`. `fetch` MUST be used only in `platform/api` and `platform/stream`. Public build settings MUST be `VITE_*` only. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Agent constraints for every slice"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "2. Domain scope and boundaries"; ADR-FRONTEND-002 — "Carve-outs"; SNR-8.1.2.

### Functional Requirements

#### B0

- **FR-004**: B0 MUST add `frontend/AGENTS.md` under 10,000 characters and rewrite the Frontend lines in the root `AGENTS.md` so both state the target rules in User Story 1. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack".
- **FR-005**: B0 MUST remove or rewrite stale `CLAUDE.md`, `.claude/rules`, and `.cursor/rules` content that recommends Create React App, Jest, `REACT_APP_*`, or Socket.IO, and MUST update `.github/instructions/frontend-react.instructions.md` so it states the same target rules. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack".
- **FR-006**: After B0, `grok inspect` run from `frontend/` MUST list the new rules, and no instruction file MAY recommend Create React App, Jest, `REACT_APP_*`, or Socket.IO. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack" (Acceptance).
- **FR-007**: B0 MUST change instruction files only. It MUST NOT change application source, tests, or config. Its proof MUST be `grok inspect` run from `frontend/` plus a search of instruction files that finds no recommendation of Create React App, Jest, `REACT_APP_*`, or Socket.IO. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack" (Agent constraints and Acceptance).

#### B1

- **FR-008**: B1 MUST replace Create React App with Vite so `npm run build` and `npm run dev` work on Vite, and MUST remove the Create React App build path, including dead `config-overrides.js` and `webpack.config.dev.js`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract"; ADR-FRONTEND-002 — "Decision" and "Guardrails".
- **FR-009**: B1 MUST delete the unused files listed in User Story 2, including `MessageFormatter.js`, and MUST leave no reference that the proving `rg` command can find. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" and "6.5 Safe rendering of Agent output".
- **FR-010**: B1 MUST resolve every named trap in the B1 agent-constraints block so the Vite dev server, the production build, `tsc --noEmit`, and the Docker image build succeed. TypeScript MUST be a direct dependency at 5.9 or newer. `@types/react` and `@types/react-dom` MUST be aligned with React 18. The image MUST use `node:26-alpine` and MUST package `dist`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Known traps, Node pin); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step "T1 types fix".
- **FR-011**: B1 MUST add `frontend/.nvmrc` of `26`, `engines.node` of `">=26.13.0"`, and `frontend/.npmrc` with `engine-strict=true`. The Product Owner MUST install Node v26.13.1 locally before the first B1 run. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Node pin) and "Risks".
- **FR-012**: Vite `server.proxy` MUST send `/api` to port 5000 on the same origin. `VITE_API_BASE_URL` MUST default to empty. The dev setup MUST NOT use credentialed CORS. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Architecture); ADR-SYS-001 — "Decision"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.1 Build and run".
- **FR-013**: B1 MUST wire Vitest with jsdom (no happy-dom fallback), the MSW base setup used by tests, and the G1 chat smoke in `docs/domains/frontend/TECHNICAL_DESIGN.md` — "9.2 Tests mapped to gates". Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" and "Open questions" (jsdom, decided 2026-11-17); SNR-6.1.4 (path).
- **FR-014**: B1 MUST add `.github/workflows/frontend-ci.yml`. Its job order MUST be lint, then `tsc --noEmit`, then Vitest, then build, then `npm run gen:api && git diff --exit-code src/platform/api/generated`. It MUST NOT change the `on` trigger of `.github/workflows/build-push-dockerhub.yml`. The Docker image build MUST succeed. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Acceptance); Product Owner resolution of analysis G1, 2026-11-17.
- **FR-031**: B1 MUST enable lint rules 1–3 from `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement (Target G2)" and MUST enable `react/no-danger`. Rule 1 is dependency direction (`app` → `features` → `platform` / `design-system`, never reverse). Rule 2 is no sibling-feature or deep imports. Rules 1 and 2 MUST use core ESLint `no-restricted-imports` path patterns. This delivery MUST NOT add `eslint-plugin-boundaries`. Rule 3 is that only `platform` talks to the Backend. Rule 4 (market and state colour reads) stays with B4. The chart-library part of rule 5 stays with B4. Playwright and the axe baseline stay with B5. `MessageBody` and the XSS regression tests stay with B3. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement (Target G2)" (rules 1–3 and the Agent output row); Product Owner resolution of analysis G2, 2026-11-17.
- **FR-032**: `tasks.md` MUST label the B1 Vite move and the Vitest smoke with the pitch's T1 and T2 names from `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract". T1 is the Vite build, config, and environment move. T2 is Vitest, the MSW base setup, and the G1 smoke. Each of those tasks MUST note the matching step in `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" beside that pitch label. Pitch T1 notes the Vite replacement inside the "T2 Vite" row (`react-scripts` to Vite, root `index.html`, `REACT_APP_*` to `VITE_*`). Pitch T2 notes the Vitest, RTL, MSW, and first chat smoke inside that same "T2 Vite" row. The React 18 `@types/react` and `@types/react-dom` alignment stays in B1 and MUST be noted as the "T1 types fix" row from that section. It MUST NOT be labeled as the pitch's T1. Source: Product Owner clarification 2026-11-17; `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration".

#### B2

- **FR-015**: `npm run gen:api` MUST generate Frontend API types from `docs/openapi.yaml` into `src/platform/api/generated`. The generated file MUST be committed. The fifth step of `.github/workflows/frontend-ci.yml` MUST fail when it drifts. `npm run gen:api && git diff --exit-code src/platform/api/generated` MUST pass on a clean tree. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Acceptance and Proving commands); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.1 Typed REST client"; ADR-FRONTEND-002 — "Decision"; Product Owner resolution of analysis G1, 2026-11-17.
- **FR-016**: One client in `platform/api` MUST send `credentials: 'same-origin'` on every request, including the stream; MUST add `AuthAdapter.csrfHeaders()` on POST, PUT, PATCH, and DELETE; MUST call `onUnauthorized` on 401; and MUST NOT send `Authorization` or `X-User-ID`. No token MAY appear in JavaScript, storage, or fixtures. This delivery MUST ship `NoAuthAdapter` and tests MUST use a fake adapter. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Agent constraints); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.1 Typed REST client" and "3.4 Platform contracts"; ADR-SYS-001 — "Decision" and "Follow-ups".
- **FR-017**: The client MUST call only health, config, `models/*`, and chat. `sessionRef` MUST be an opaque `{sessionId, conversationId}`. MSW in this delivery MUST cover only paths already in `docs/openapi.yaml`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Agent constraints); SR-1.4.2 (`sessionRef` shape).
- **FR-018**: `openChatStream(body, { signal, idleTimeoutMs })` MUST parse WHATWG SSE fields, keep `id`, `event`, and `retry`, and adapt today's frames through `legacyChatAdapter` behind `StreamAdapter`. Stream event names MUST appear only in the `StreamEvent` union and the adapter, enforced by lint. Only one chat stream MAY be open per tab. `EventSource` MUST NOT be used. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Agent constraints); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.3 SSE client"; SR-5.1.2.
- **FR-019**: The idle timeout MUST come from `VITE_STREAM_IDLE_TIMEOUT_MS`, default 60000 ms in live mode, and MUST NOT be hard-coded. Any received line, including `:` comments, MUST reset it. On timeout the stream MUST abort and move to `interrupted`, the retry label MUST be "Tạo lại" through `t()`, and the Z4 draft and any partial message MUST stay as they are. `frontend/.env.example` MUST document the 60 s default as a stopgap. MSW tests MUST use 15000 ms with fake timers. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Idle timeout); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.2 Today's stream contract" and "6.3 SSE client".
- **FR-020**: B2 MUST remove `socket.io-client`, `@types/socket.io-client`, `webSocketService.ts`, and `API_CONFIG.WEBSOCKET`, and MUST add a lint rule that blocks their return. `rg socket.io dist` MUST return nothing. SR-5.2.1 and SR-5.2.2 stay Superseded. SNR-8.1.2 MUST be recorded as "Frontend part verified" against the MSW fixture. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Acceptance) and "Done means"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.4 Socket.IO removal" and "9.2 Tests mapped to gates" (G6); ADR-FRONTEND-002 — "Carve-outs"; SR-5.2.1; SR-5.2.2; SNR-8.1.2.
- **FR-021**: This delivery MUST NOT change Backend stream headers, heartbeat emission, or HTTP/2. The client is proven against an MSW stream fixture only. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." and "Risks"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.2 Today's stream contract".

#### B4

- **FR-022**: The format module MUST produce the exact strings in rows B4-F1..F5 and P1..P4 through custom board-style formatters: `fmt.price`, `fmt.vnd`, `fmt.change`, `fmt.pct`, and `fmt.volume`. Those formatters MUST NOT use `Intl`. Volume MUST NOT go through the price formatter. Across those outputs the dot MUST only mark a decimal and the comma MUST only group thousands. Source: `specs/pitches/M-000-B-frontend-foundation.md` — rows B4-F1..F5 and P1..P4 and "B4 — Dark tokens..."; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.3 i18n and locale seam"; `docs/domains/frontend/DESIGN_LOCK.md` — "8. Translation-ready copy"; ADR-FRONTEND-005 — "Decision" (price-board bullet); `docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md` — "SNR-7: Usability, Accessibility, and Responsive Behavior" (launch UI note).
- **FR-023**: Dates and times MUST use standard `vi-VN` `Intl` formatting with default time zone `Asia/Ho_Chi_Minh`. `Intl` MUST be used only for dates. Locale and time zone MUST be settings, with those launch defaults. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.3 i18n and locale seam"; ADR-FRONTEND-005 — "Decision" (date clause); `specs/pitches/M-000-B-frontend-foundation.md` — "B4 — Dark tokens...".
- **FR-024**: Every user-facing string MUST go through `t()` and the vi-VN catalogue. This delivery MUST NOT choose an i18n library and MUST NOT ship an English catalogue. Source: ADR-FRONTEND-005 — "Decision"; `specs/pitches/M-000-B-frontend-foundation.md` — "B4 — Dark tokens..." (Acceptance) and "Rabbit holes"; `docs/domains/frontend/DESIGN_LOCK.md` — "8. Translation-ready copy".
- **FR-025**: This delivery MUST commit hand-written two-part dark CSS variables that match the dark hex values in `docs/domains/frontend/DESIGN_SYSTEM.md` — "3. Palette". `--market-up` MUST be `#2EBD6B`. A two-part id such as `market.down` MUST become `--market-down`. The test fixture for those two-part values MUST be copied from that section. `<html>` MUST carry `data-theme="dark"` and `data-density="compact"`. This delivery MUST NOT select a token generator, MUST NOT invent three-part `ai.*` custom property names, and MUST NOT add an `npm run tokens` drift check. Full generation of every dark value in verbatim B4-T1 is out of this delivery. This delivery MUST NOT ship light token values, theme switching, or the contrast script. Those move to M-001 (rows B4-T5 and B4-T6). `track.a` and `track.b` MUST NOT receive invented hex values. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B4-T1, "B4 — Dark tokens...", and rows B4-T5 and B4-T6; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.1 Token pipeline" and "7. Accessibility and responsive behaviour"; ADR-FRONTEND-007 — "Decision"; `docs/domains/frontend/DESIGN_SYSTEM.md` — "3.2 Track" and "5. Density, space, radius"; Product Owner resolution of analysis G3 and X1, 2026-11-17.
- **FR-026**: The Tailwind config MUST expose no `market` or `state` colour utilities. Lint MUST fail when `var(--market-*)` is read outside `PriceCell` / `Delta`, when `var(--state-*)` is read outside `StatusBadge`, or when an arbitrary Tailwind colour value appears outside `design-system/patterns/`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B4-T2; `docs/domains/frontend/DESIGN_SYSTEM.md` — "2. Token architecture"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement" rule 4; ADR-FRONTEND-007 — "Decision".
- **FR-027**: A positive or negative `Delta` MUST show a sign or arrow as well as colour, and its accessible name MUST include the direction. A zero `Delta` MUST show `0.00` and `0.00%` with no sign, coloured `market.ref`, as row P2 and `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules". The zero clause inside verbatim row B4-T3 is superseded by P2. Source: `specs/pitches/M-000-B-frontend-foundation.md` — rows B4-T3 and P2; `docs/domains/frontend/DESIGN_SYSTEM.md` — "8. Patterns"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules".
- **FR-028**: `fmt.*` output on screen MUST compute to a `font-family` that starts with `IBM Plex Mono`. UI text MUST start with `Be Vietnam Pro`. Fonts MUST be self-hosted, and no request MAY go to a third-party font host. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B4-T4; `docs/domains/frontend/DESIGN_SYSTEM.md` — "4. Typography"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.1 Token pipeline".
- **FR-029**: Lint MUST fail on an import of `lightweight-charts` outside `platform/chart` and on an import of `chart.js` outside `platform/stat-chart`. This delivery MUST NOT add either package to `package.json` and MUST NOT build the `ChartEngine` or `StatChart` interfaces. The Frontend MUST NOT compute reference, ceiling, or floor prices. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B4 — Dark tokens..." and "No-gos"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.3 Boundary enforcement" rule 5 and "3.4 Platform contracts"; ADR-FRONTEND-004 — "Decision" and "Considered Options"; ADR-FRONTEND-005 — "Decision".
- **FR-030**: SNR-7.2.1 MUST stay P2. This delivery MUST NOT raise it to P1. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "No-gos" and "Done means"; SNR-7.2.1.

### Key Entities

- **Instruction set**: The Frontend rules a coding session loads, including `frontend/AGENTS.md` and the Frontend lines of the root instruction files. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack".
- **Generated API schema**: Types produced from `docs/openapi.yaml` into `src/platform/api/generated`. Hand edits are not the source of truth. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.1 Typed REST client".
- **Auth adapter**: `AuthAdapter` with `NoAuthAdapter` in this delivery (`getSession` → null, `csrfHeaders` → empty, sign-in and `onUnauthorized` no-ops). Pitch A replaces the implementation behind the same interface. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.4 Platform contracts".
- **Chat stream**: `openChatStream` yielding `StreamEvent` values adapted from SSE frames (`id`, `event`, `retry`, `data`). States used here include streaming and `interrupted`. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.3 SSE client".
- **sessionRef**: Opaque `{sessionId, conversationId}`. This delivery does not build the shell store that holds it. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Agent constraints); SR-1.4.2.
- **Format result**: The string produced by the custom board-style formatters `fmt.price`, `fmt.change`, `fmt.pct`, `fmt.volume`, and `fmt.vnd`, or by `fmt.dateTime` through `Intl`. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.3 i18n and locale seam"; `specs/pitches/M-000-B-frontend-foundation.md` — rows B4-F1..F5 and P1..P4.
- **Design tokens**: Hand-written two-part dark CSS variables from the UX Designer's palette, plus `data-theme="dark"` and `data-density="compact"` on `<html>`. Light values, a token generator, and three-part `ai.*` names are not in this delivery. `market.*` and `state.*` are read only by the named patterns. Source: ADR-FRONTEND-007 — "Decision"; `docs/domains/frontend/DESIGN_SYSTEM.md` — "3. Palette" and "5. Density, space, radius"; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.1 Token pipeline".
- **Message catalogue**: The vi-VN key set behind `t()`. Source: ADR-FRONTEND-005 — "Decision".

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: From `frontend/`, `grok inspect` lists the B0 rules, and a full search of instruction files finds zero recommendations of Create React App, Jest, `REACT_APP_*`, or Socket.IO. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack" (Acceptance) and "Done means".
- **SC-002**: From `frontend/` on Node v26.13.1, `npm ci`, `npx tsc --noEmit`, `npx vitest run`, `npm run build`, and `npm run dev` succeed, and the Docker image build succeeds. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Agent constraints for every slice" and "B1 — Vite shell and subtract" (Acceptance).
- **SC-003**: `rg -n "MessageFormatter|dangerouslySetInnerHTML|REACT_APP_" src` run from `frontend/` returns nothing. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Proving commands).
- **SC-004**: The G1 chat smoke passes: one component test renders streamed tokens from an MSW handler using the current chat frames. Source: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "9.2 Tests mapped to gates" (G1); SNR-6.1.4 (path).
- **SC-005**: `npm run gen:api && git diff --exit-code src/platform/api/generated` passes, and CI fails when that generated tree drifts. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Proving commands); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.1 Typed REST client".
- **SC-006**: `rg socket.io dist` returns nothing, and `socket.io-client` is absent from `package.json`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Proving commands); SNR-8.1.2.
- **SC-007**: The fake-timer MSW test at 15000 ms passes: comment lines are accepted, and silence past the idle window moves the stream to `interrupted` with the draft and partial message still present. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." (Proving commands and Idle timeout).
- **SC-008**: Vitest exact-output tests match B4-F1..F5 and P1..P4, including the 1,000-value property test. Source: `specs/pitches/M-000-B-frontend-foundation.md` — rows B4-F1..F5 and P1..P4.
- **SC-009**: A planted chart-library import fails lint. A dark-token test fixture copied from `docs/domains/frontend/DESIGN_SYSTEM.md` — "3. Palette" matches the generated dark variables, including `--market-up` = `#2EBD6B`. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B4 — Dark tokens..." (Proving commands) and rows B4-T1 and B4-T2.
- **SC-010**: The B4-T4 check passes: `fmt.*` text uses `IBM Plex Mono`, UI text uses `Be Vietnam Pro`, and the network log shows no third-party font host. Source: `specs/pitches/M-000-B-frontend-foundation.md` — row B4-T4.
- **SC-011**: For B1, B2, and B4, the test log shows a failing run of the new tests before the implementation change, and the test files are unchanged by that implementation. B0 is exempt. B0 is proven by `grok inspect` and the instruction search, not by a failing test. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Delivery workflow (agentic)" and "B0 — Agent instructions on the target stack" (Acceptance).

## Prerequisites

- The Product Owner installs Node v26.13.1 locally before the first B1 run. The laptop has Node 22.18 today. With `engine-strict=true`, `npm ci` fails on 22.18. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" (Node pin) and "Risks".
- B1's toolchain is in place before B2 and B4 proving commands run. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Delivery workflow (agentic)" (slice order).
- `docs/openapi.yaml` already describes the health, config, `models/*`, and chat paths the client calls. This delivery does not edit that file. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B2 — API client..." and "Agent constraints for every slice".
- The current chat stream contract remains the frames in `docs/domains/frontend/TECHNICAL_DESIGN.md` — "6.2 Today's stream contract" until a later Backend pitch. Source: that section and `specs/pitches/M-000-B-frontend-foundation.md` — "Risks".

## Out of Scope

This feature is delivery 1 of 2. The reserved feature owns B3 and B5. Source: Product Owner operating rule for this specification; `specs/pitches/M-000-B-frontend-foundation.md` — "Slices".

### B3 — Modular shell, state, and safe rendering (reserved)

Not in this delivery. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B3 — Modular shell, state, and safe rendering":

- React Router, Zustand, TanStack Query, and the URL-owned shareable state in ADR-FRONTEND-003.
- Zones Z1–Z4, zone landmarks, zone frames, and the zone state matrix as a rendered shell (design rows B3-D1..D9).
- `MessageBody` and the XSS regression tests as the T4 shell work. `react/no-danger` is enabled in B1 (FR-031). Deleting `MessageFormatter.js` stays in B1.
- The workspace context store that mirrors track, symbol, and `coreObjectRef` (SR-1.4.1 and the shell side of SR-1.4.2). This delivery only keeps `sessionRef` as an opaque pair on the client.
- The Z4 `sessionStorage` draft behavior as a shell feature. B2 only requires that an idle timeout leave any existing draft and partial message as they are.
- F6 zone-cycling tests.

### B5 — MSW, minimal Storybook, and Frontend CI (reserved)

Not in this delivery. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B5 — MSW, minimal Storybook, and Frontend CI":

- Storybook, the minimal story set, and rows B5-S1..B5-S4.
- The browser MSW worker and the build-time `VITE_USE_MOCKS` switch as the B5 acceptance ("the same MSW handlers work in the browser and in tests"). B1 still wires the MSW base setup that the G1 and B2 tests need.
- Playwright width runs at 1920, 1440, 1024, and 768, the axe baseline, and the keyboard-order test. Row B4-T4's own Playwright font check stays in this delivery because that row is a B4 acceptance.
- Extending the B1 CI skeleton with Storybook and Playwright. The B1 skeleton itself stays in this delivery.
- The production-bundle scan that proves `dist/` contains no `msw`, `mockServiceWorker.js`, or Storybook code (B5-S3). ADR-FRONTEND-008 still says neither tool ships to production; the formal scan is the reserved feature's proof.

The Storybook theme matrix is reserved with B5. The reserved set is the pitch's dark-only minimal set. The light half of the matrix and visual snapshots move to M-001. This delivery does not build Storybook. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B5: Storybook minimum, MSW, CI" (stories table and row B5-S4); `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules".

### Moved to M-001, or otherwise excluded

Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Cut order inside the design criteria", "Rabbit holes", "No-gos", and "Open questions" (cut line, 2026-11-17).

- B4-T5 (theme switch between dark and light) and B4-T6 (contrast script). Both rows are "Moved to M-001". This delivery keeps dark tokens and the `data-theme="dark"` hook only. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B4 — Dark tokens..." and rows B4-T5 and B4-T6; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.1 Token pipeline" and "7. Accessibility and responsive behaviour".
- Chart interfaces, price mocks, the docked chart proof of concept, and adding `lightweight-charts` or `chart.js` to `package.json` (M-001 S3). The chart-import lint stays in B4.
- Token Storybook pages, visual snapshots, and the light half of story matrices. The reserved B5 set is dark-only. This delivery does not build Storybook. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "B5: Storybook minimum, MSW, CI" and row B5-S4; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules".
- Identity, login, and owner-isolation product behavior (Pitch A; ADR-SYS-001). This delivery only keeps the same-origin client, `NoAuthAdapter`, CSRF hook, and 401 hook.
- A production market-data feed, licensed provider, or `GET /api/market/prices/{symbol}`.
- Computing reference, ceiling, or floor prices in the Frontend.
- Micro-frontends (ADR-FRONTEND-001 rejected this for now).
- Generated UI (ADR-FRONTEND-006, Proposed — Future).
- Choosing an i18n library or shipping an English catalogue (ADR-FRONTEND-005, Future).
- Saved layout presets (M-009).
- Typed stream events, resume, or cancel (later Backend contract).
- Backend stream headers, `: ping` emission, and HTTP/2 ingress.
- Raising SNR-7.2.1 from P2 to P1.
- Widths below 768 px (SNR-7.1.1, Future). Exercising 768–1920 px in Playwright is B5, not this delivery.
- Changes to `docs/**`, the pitch file, Accepted ADRs, `backend/`, or `specs/spec-traceability.yaml` as part of implementing this spec.

## Assumptions

- The behavior requirements above are fully sourced. Where a library is still marked Proposed in `docs/domains/frontend/TECHNICAL_DESIGN.md` — "12. Domain-specific constraints and open items" (`openapi-fetch`, `eslint-plugin-boundaries`, Style Dictionary, SSE parser), this spec does not select it.
- This delivery records the SNR-6.1.4 path (G1 smoke and Vitest) and the streaming-client portion of that requirement. It does not record the presentation shell or the workspace context store as verified. Those are B3. Source: SNR-6.1.4; `docs/domains/frontend/TECHNICAL_DESIGN.md` — "9.2 Tests mapped to gates" (G1, G2, G3); `specs/pitches/M-000-B-frontend-foundation.md` — "Slices".
- This delivery records SNR-8.1.2 as "Frontend part verified" only. Source: `specs/pitches/M-000-B-frontend-foundation.md` — "Done means".
- SNR-7.1.1's supported range is 768–1920 px with 1920 px primary. This delivery does not run that width matrix. Source: SNR-7.1.1; `specs/pitches/M-000-B-frontend-foundation.md` — "B5 — MSW, minimal Storybook, and Frontend CI".
- Colour values follow ADR-FRONTEND-007 and `docs/domains/frontend/DESIGN_SYSTEM.md` — "3. Palette". ADR-FRONTEND-007 replaces the colour bullet in ADR-FRONTEND-002. This spec does not restate that replaced bullet as a requirement.
- ADR-FRONTEND-008 replaces the "MSW and Storybook are later phases" bullet in ADR-FRONTEND-002. This delivery uses MSW in Vitest. Storybook and the browser-handler acceptance stay with the reserved B5 feature.

## Source conflicts

Resolved by the Product Owner on 2026-11-17. Each note names the text that governs this delivery and the older text that is stale. Stale documents are a follow-up doc fix. They are not edited here. The requirements above are the resolved behavior.

- **Light theme and contrast timing.** Resolved. The pitch and `docs/domains/frontend/TECHNICAL_DESIGN.md` govern: dark tokens plus the `data-theme` hook only; light values, theme switching, and the contrast script move to M-001. Stale: `docs/domains/frontend/DESIGN_SYSTEM.md` — "1. Principles" and "10. Quality"; `docs/domains/frontend/DESIGN_LOCK.md` — "4.2 Token groups" (light built on the same tokens and contrast-checked from day one, and not deferred).

- **Number-format mechanism.** Resolved. Custom board-style formatters (`fmt.price`, `fmt.vnd`, change, and percent per rows B4-F1..F5 and P1..P4). `Intl` is used only for dates. Stale: ADR-FRONTEND-005 — "Decision", the sentence that every number, price, percent, currency, and date goes through one helper built on `Intl`. The same Decision's later price-board bullet is the governing ADR text.

- **B1 step labels.** Resolved. `tasks.md` uses the pitch's T1/T2 labels from `specs/pitches/M-000-B-frontend-foundation.md` — "B1 — Vite shell and subtract" and notes the matching `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration" step beside each. The "10.2" step names stay as citations. They are not the `tasks.md` labels. No long-lived document is rewritten for this item.

- **Lint-rule timing.** Resolved. Per the pitch, lint rules 1–3 and `react/no-danger` are enabled in B1. Stale: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "10.2 CRA → Vite migration", the "T4 shell" clause that turns on `react/no-danger` there, and the "T7 boundary lint + a11y" placement of rules 1–3. Rule 4, the chart-library part of rule 5, and the rest of T7 are unchanged.

- **Feature folder name.** Resolved. B0 instruction files name `features/` and `platform/`. Governing: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree (Target M-000)" and `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack". Stale: ADR-FRONTEND-001 — "Implementation Direction", the `modules/` wording.

- **B0 and the test-first rule.** Resolved. B0 is instruction files only and is exempt from the failing-test rule. Its proof is `grok inspect` plus the instruction search named in the pitch. Governing: `specs/pitches/M-000-B-frontend-foundation.md` — "B0 — Agent instructions on the target stack" (Agent constraints and Acceptance). The blanket test-first sentence in that pitch's "Delivery workflow (agentic)" (Spec Kit rules) does not apply to B0. A follow-up note in that workflow section is a doc fix, not edited here.

- **Storybook theme matrix.** Resolved. Reserved with B5. The set is the pitch's dark-only minimal set. Not built in this delivery. The light half and visual snapshots move to M-001. Governing: `specs/pitches/M-000-B-frontend-foundation.md` — "B5: Storybook minimum, MSW, CI" (stories table and row B5-S4) and `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules". Stale: `docs/domains/frontend/DESIGN_SYSTEM.md` — "10. Quality" (pattern stories include both themes, and visual regression, from M-000).

- **Zero `Delta`.** Resolved. Row P2 and `docs/domains/frontend/TECHNICAL_DESIGN.md` — "8.2 Pattern rules" govern: `0.00` and `0.00%`, no sign, coloured `market.ref`. The zero clause inside verbatim row B4-T3 does not govern. Non-zero B4-T3 still requires a sign or arrow and an accessible name that includes the direction. The pitch row is not edited here.

## SRS mapping

| ID | Statement this delivery uses | Where it lands |
|---|---|---|
| SR-5.1.2 | SSE with `text/event-stream` for HTTP streaming | B2 client and stream reader. Backend unchanged. |
| SNR-8.1.2 | HTTPS+SSE event names and contracts centralized | B2 frontend part, recorded as "Frontend part verified" against an MSW fixture. End-to-end verification is the later Backend pitch. |
| SNR-6.1.4 | Automated Frontend unit and component tests for the shell and critical client seams | B1 covers the G1 path. B2 covers the streaming-client seam. The presentation shell and workspace store stay with B3. Coverage target remains TBD in the SRS text. |
| SNR-7.1.1 | Viewports 768–1920 px, 1920 px primary; below 768 px is Future | Recorded. Width exercises stay with B5. Priority stays P2. |
| SNR-7.2.1 | WCAG 2.2 AA target | Priority stays P2. The axe baseline stays with B5. The contrast script is row B4-T6 and moves to M-001. |
| SR-1.4.1 | Modular zone shell | Out of scope (B3). |
| SR-1.4.2 | In-session workspace context | Out of scope as a store (B3). B2 only uses the opaque `sessionRef` shape. |
| SR-5.2.1 | WebSocket real-time events | Remains Superseded. B2 removes the Socket.IO client. |
| SR-5.2.2 | WebSocket reconnection | Remains Superseded. B2 removes the Socket.IO client. |

Source for the allocation: `specs/pitches/M-000-B-frontend-foundation.md` — "Requirements covered", "Slices", and "Done means"; `docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md` — the rows cited above.

## References

Paths only. No document version numbers.

- `specs/pitches/M-000-B-frontend-foundation.md` — Problem; Appetite; Solution sketch (B0, B1, B2, B4); Delivery workflow (agentic); Design acceptance criteria (UX), including B4-F1..F5, P1..P4, B4-T1..T4; Rabbit holes; Risks; No-gos; Done means; Open questions
- `docs/domains/frontend/TECHNICAL_DESIGN.md` — 2. Domain scope and boundaries; 3.1 Module tree; 3.3 Boundary enforcement; 3.4 Platform contracts; 6.1 Typed REST client; 6.2 Today's stream contract; 6.3 SSE client; 6.4 Socket.IO removal; 6.5 Safe rendering of Agent output; 7. Accessibility and responsive behaviour; 8.1 Token pipeline; 8.2 Pattern rules; 8.3 i18n and locale seam; 9.2 Tests mapped to gates; 10.1 Build and run; 10.2 CRA → Vite migration; 12. Domain-specific constraints and open items
- `docs/domains/frontend/ARCHITECTURE.md` — 2. Scope & boundaries; 4.3 Building blocks; 5.1 Decided; 5.3 Carve-outs; 8.2 Gates G1–G6
- `docs/domains/frontend/DESIGN_LOCK.md` — 4.2 Token groups; 4.3 Colour and provenance rules; 5. Zone state matrix; 8. Translation-ready copy
- `docs/domains/frontend/DESIGN_SYSTEM.md` — 1. Principles; 2. Token architecture; 3. Palette; 3.2 Track; 3.6 Provenance; 4. Typography; 8. Patterns; 9. Content voice; 10. Quality
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-001-MODULAR-APPLICATION.md` — Decision; Implementation Direction; Guardrails
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-002-MODERNIZE-FRONTEND-FOUNDATION.md` — Decision; Carve-outs; Guardrails
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-003-URL-OWNED-SHAREABLE-STATE.md` — Decision (B3; cited as out of scope)
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-004-CHART-ENGINE-ADAPTER.md` — Decision; Considered Options
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-005-I18N-READINESS-SEAM.md` — Decision
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-006-GENERATED-UI-COMPONENT-REGISTRY.md` — Decision (Future; out of scope)
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-007-DESIGN-TOKEN-ARCHITECTURE.md` — Decision
- `docs/domains/frontend/DECISIONS/ADR-FRONTEND-008-MSW-AND-STORYBOOK-IN-M000.md` — Decision
- `docs/architecture/DECISIONS/ADR-SYS-001-IDENTITY-AND-PER-USER-ISOLATION.md` — Decision; Follow-ups
- `docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md` — SR-1.4.1; SR-1.4.2; SR-5.1.2; SR-5.2.1; SR-5.2.2; SNR-6.1.4; SNR-7.1.1; SNR-7.2.1; SNR-8.1.2; launch UI note under SNR-7
- `docs/openapi.yaml` — contract input for codegen; not edited by this delivery
